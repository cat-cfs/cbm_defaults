import os
import numpy as np
import pandas as pd
from pandas import read_sql_query
import sqlalchemy

from cbm_defaults import helper
from cbm_defaults import schema
from cbm_defaults import cbm_defaults_database
from cbm_defaults import local_csv_table


logger = helper.get_logger()


def load_dataframe(
    engine: sqlalchemy.Engine,
    table_name: str,
    df: pd.DataFrame,
    variable_limit: int = None,
):
    logger.info(f"loading {table_name} to output db")
    to_sql_kwargs = dict(
        name=table_name, con=engine, if_exists="append", index=False
    )
    if variable_limit:
        max_rows = variable_limit // len(df.columns)
        to_sql_kwargs.update(dict(method="multi", chunksize=max_rows))
    df.to_sql(**to_sql_kwargs)


def _1x_to_2x_updates(input_db_path: str, output_db_path: str):
    output_path = os.path.abspath(output_db_path)
    logger.info("created database file: %s", output_path)
    cbm_defaults_database.create_database(output_path)

    input_db_engine = sqlalchemy.create_engine(f"sqlite:///{input_db_path}")
    output_db_engine = sqlalchemy.create_engine(f"sqlite:///{output_db_path}")
    try:
        # Run the DDL file on it to create all tables #
        schema_path = schema.get_ddl_path()
        logger.info("running DDL statements %s", schema_path)
        cbm_defaults_database.execute_ddl_file(schema_path, output_path)

        land_type_df = load_land_classes(input_db_engine, output_db_engine)

        load_disturbance_types(input_db_engine, output_db_engine, land_type_df)

        # copy all of the tables except those affected by the schema update
        load_other_tables(input_db_engine, output_db_engine)
    finally:
        input_db_engine.dispose()
        output_db_engine.dispose()


def load_other_tables(input_db_engine, output_db_engine):
    output_db_inspector = sqlalchemy.inspect(output_db_engine)
    for table in output_db_inspector.get_table_names():
        if table in [
            "disturbance_type",
            "land_class",
            "land_class_tr",
            "land_type",
        ]:
            continue
        load_dataframe(
            output_db_engine,
            table,
            read_sql_query(f"select * from {table}", input_db_engine),
        )


def load_disturbance_types(input_db_engine, output_db_engine, land_type_df):
    source_disturbance_type = read_sql_query(
        "select * from disturbance_type", input_db_engine
    )
    if "transition_land_class_id" not in source_disturbance_type.columns:
        raise ValueError(
            "expected disturbance_type.transition_land_class_id "
            "column in 1x schema"
        )

    source_land_class = read_sql_query(
        "select id, code from land_class", input_db_engine
    )

    source_land_class_land_type = (
        source_land_class["code"].str.split("_").apply(lambda x: x[-1])
    )
    source_land_class_land_type.loc[
        source_land_class_land_type == "PEATLAND"
    ] = "WLP"
    source_land_class["land_type"] = source_land_class_land_type
    source_lc_dist_merge = (
        source_land_class[["id", "land_type"]]
        .merge(
            source_disturbance_type,
            left_on="id",
            right_on="transition_land_class_id",
        )
        .merge(
            land_type_df.rename(columns={"id": "land_type_id"}),
            left_on="land_type",
            right_on="land_type",
        )
    )
    if source_lc_dist_merge.isnull().any().any():
        raise ValueError("landtype, landclass, disturbance_type merge failed")
    transition_land_class_id_update_map = {
        row["transition_land_class_id"]: row["land_type_id"]
        for _, row in source_lc_dist_merge.iterrows()
    }
    # check that the update map is a superset of the values (other than null)
    # that exist in source_disturbance_type
    missing_values = set(
        transition_land_class_id_update_map.keys()
    ).difference(
        source_disturbance_type.dropna()[
            "transition_land_class_id"
        ].drop_duplicates()
    )

    if missing_values:
        raise ValueError(
            f"missing transition_land_class_id values {missing_values}"
        )

    output_disturbance_type = source_disturbance_type.copy()
    output_disturbance_type["land_type_id"] = output_disturbance_type[
        "transition_land_class_id"
    ].map(transition_land_class_id_update_map)

    output_disturbance_type = output_disturbance_type.drop(
        columns=["transition_land_class_id"]
    )
    load_dataframe(
        output_db_engine, "disturbance_type", output_disturbance_type
    )


def load_land_classes(input_db_engine, output_db_engine):
    landclass_df = pd.read_csv(
        os.path.join(local_csv_table.get_tables_dir(), "landclass.csv")
    )
    load_dataframe(output_db_engine, "land_class", landclass_df)
    input_db_locales = read_sql_query(
        "select id, code from locale", input_db_engine
    )
    land_class_tr_id_base = 0
    for _, input_db_locale_row in input_db_locales.iterrows():
        land_class_tr_path = os.path.join(
            local_csv_table.get_tables_dir(),
            local_csv_table.get_localized_csv_file_path(
                "landclass.csv", input_db_locale_row["code"]
            ),
        )
        land_class_tr_df = pd.read_csv(land_class_tr_path)
        land_class_tr_df.insert(
            0,
            "id",
            np.arange(
                land_class_tr_id_base + 1,
                land_class_tr_id_base + len(land_class_tr_df.index) + 1,
            ),
        )
        land_class_tr_df.insert(2, "locale_id", input_db_locale_row["id"])
        land_class_tr_id_base += len(land_class_tr_df.index)
        load_dataframe(
            output_db_engine,
            "land_class_tr",
            land_class_tr_df.rename(columns={"landclass_id": "land_class_id"}),
        )
    land_type_df = pd.read_csv(
        os.path.join(local_csv_table.get_tables_dir(), "landtype.csv")
    )
    load_dataframe(output_db_engine, "land_type", land_type_df)
    return land_type_df


def update(
    update_process: str, input_db_path: str, output_db_path: str
) -> None:
    if update_process == "1x_to_2x":
        _1x_to_2x_updates(input_db_path, output_db_path)
    else:
        raise ValueError(f"unknown update_process '{update_process}'")

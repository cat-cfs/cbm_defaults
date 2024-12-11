import pandas as pd
import numpy as np
import itertools


def process_dm_values(
    rows: list, colnames: list[str], pool_cross_walk: dict[int, int]
) -> pd.DataFrame:

    # rows is a list of dicts with the following keys:
    # tblDMValuesLookup.DMID,
    # tblDMValuesLookup.DMRow,
    # tblDMValuesLookup.DMColumn,
    # tblDMValuesLookup.Proportion

    aidb_dm_values = pd.DataFrame(
        columns=colnames,
        data=rows
    )

    # drop DM values where the CBM-CFS3 pool cross walk maps to -1
    # this affects the following CBM-CFS3 pools that are not carried forward
    # into the libcbm/cbmdefaults database:
    #
    #   CBM3 Pool                 CBM3 Pool ID
    #   ________________________  ____________
    #   Softwood Submerchantable      4
    #   Hardwood Submerchantable     10
    #   Black Carbon                 24
    #   Peat                         25

    aidb_dm_values["DMRow"] = aidb_dm_values["DMRow"].map(pool_cross_walk)
    if pd.isnull(aidb_dm_values["DMRow"]).any():
        raise ValueError("pool_cross_walk DMRow mapping failure")
    aidb_dm_values["DMColumn"] = aidb_dm_values["DMColumn"].map(
        pool_cross_walk
    )
    if pd.isnull(aidb_dm_values["DMColumn"]).any():
        raise ValueError("pool_cross_walk DMColumn mapping failure")
    drop_loc = (aidb_dm_values["DMRow"] == -1) | (
        aidb_dm_values["DMColumn"] == -1
    )

    # now compensate for a GCBM supported format that does not work in libcbm:
    # the diagonal matrix values may be omitted in GBCM but not in libcbm
    # the following code adds the validated diagonal values based on the
    # off-diagonal values present in the data
    aidb_dm_values = aidb_dm_values[~drop_loc].reset_index(drop=True)
    unique_dmids = aidb_dm_values["DMID"].drop_duplicates()
    all_unique_pool_ids = [
        p_id
        for p_id in pool_cross_walk.values()
        if p_id not in [-1, 22, 23, 24, 25, 26]
        # exclude the unmapped, and emission pools so they dont
        # appear in the diagonal to match CBM-CFS3 format
    ]
    dmid_pool_id_combinations = list(
        itertools.product(unique_dmids, all_unique_pool_ids)
    )

    off_diag_rowsums = (
        aidb_dm_values.loc[
            aidb_dm_values["DMRow"] != aidb_dm_values["DMColumn"]
        ][["DMID", "DMRow", "Proportion"]]
        .groupby(["DMID", "DMRow"])
        .sum()
        .reset_index()
    )

    off_diag_rowsums_dict = {
        (int(row["DMID"]), int(row["DMRow"])): float(row["Proportion"])
        for _, row in off_diag_rowsums.iterrows()
    }

    diag_proportions: list[float] = []
    diag_dmids: list[int] = []
    diag_dmrow_dmcol: list[int] = []
    for combo in dmid_pool_id_combinations:
        diag_dmids.append(int(combo[0]))
        diag_dmrow_dmcol.append(int(combo[1]))
        key = (int(combo[0]), int(combo[1]))
        if key in off_diag_rowsums_dict:
            row_sum = off_diag_rowsums_dict[key]
            retention = 1.0 - row_sum
            if np.isclose(abs(retention), 0.0, atol=1.e-6):
                diag_proportions.append(0.0)
            else:
                diag_proportions.append(retention)
        else:
            diag_proportions.append(1.0)

    diag_dm_values = pd.DataFrame(
        columns=["DMID", "DMRow", "DMColumn", "Proportion"],
        data={
            "DMID": diag_dmids,
            "DMRow": diag_dmrow_dmcol,
            "DMColumn": diag_dmrow_dmcol,
            "Proportion": diag_proportions,
        },
    )

    # merge onto the source data:
    dm_value_merged = aidb_dm_values.merge(
        diag_dm_values,
        left_on=["DMID", "DMRow", "DMColumn"],
        right_on=["DMID", "DMRow", "DMColumn"],
        how="outer",
        suffixes=("_cbm3", "_diag"),
    )

    output_dm_values = pd.DataFrame(
        data={
            "DMID": dm_value_merged["DMID"],
            "DMRow": dm_value_merged["DMRow"],
            "DMColumn": dm_value_merged["DMColumn"],
            "Proportion": np.where(
                pd.isnull(dm_value_merged["Proportion_cbm3"]),
                dm_value_merged["Proportion_diag"],
                dm_value_merged["Proportion_cbm3"],
            ),
        }
    )

    # CBM3 dm values format also does not include 0 diagonal values
    diag_zeros_loc = (
        (output_dm_values["DMRow"] == output_dm_values["DMColumn"])
        & (output_dm_values["Proportion"] == 0.0)
    )
    output_dm_values = output_dm_values[~diag_zeros_loc]

    # qaqc check:
    rowsums = (
        output_dm_values[["DMID", "DMRow", "Proportion"]]
        .groupby(["DMID", "DMRow"])
        .sum()["Proportion"]
    )
    if not np.allclose(rowsums, 1.0):
        raise ValueError("rowsums not close to 1.0")

    return output_dm_values.sort_values(
        by=["DMID", "DMRow", "DMColumn"]
    ).reset_index(drop=True)

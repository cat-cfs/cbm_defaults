import pandas as pd
from cbm_defaults import dm_values_processor
from cbm_defaults import local_csv_table


def test_dm_values_processor():
    pool_cross_walk: dict[int, int] = {}
    for row in local_csv_table.read_csv_file("pool_cross_walk.csv"):
        pool_cross_walk[int(row["cbm3_pool_code"])] = int(
            row["cbm3_5_pool_code"]
        )
    input = pd.DataFrame(
        columns=["DMID", "DMRow", "DMColumn", "Proportion"],
        data=[
            [506, 12, 14, 0.25],
            [506, 11, 16, 0.25],
            [506, 10, 23, 0.25],
            [506, 9, 23, 0.25],
            [506, 8, 13, 0.25],
            [506, 7, 22, 0.25],
            [506, 6, 14, 0.25],
            [506, 5, 16, 0.25],
            [506, 4, 21, 0.25],
            [506, 3, 21, 0.25],
            [506, 2, 13, 0.25],
            [506, 1, 20, 0.25],
            [10, 1, 20, 1],
            [10, 2, 13, 0.9],
            [10, 2, 26, 0.1],
            [10, 3, 21, 1],
            [10, 4, 21, 1],
            [10, 5, 15, 0.5],
            [10, 5, 16, 0.5],
            [10, 6, 13, 0.5],
            [10, 6, 14, 0.5],
            [10, 7, 22, 1],
            [10, 8, 13, 0.9],
            [10, 8, 26, 0.1],
            [10, 9, 23, 1],
            [10, 10, 23, 1],
            [10, 11, 15, 0.5],
            [10, 11, 16, 0.5],
            [10, 12, 13, 0.5],
            [10, 12, 14, 0.5],
            [10, 13, 13, 1],
            [10, 14, 14, 1],
            [10, 15, 15, 1],
            [10, 16, 16, 1],
            [10, 17, 17, 1],
            [10, 18, 18, 1],
            [10, 19, 19, 1],
            [10, 20, 20, 1],
            [10, 21, 21, 1],
            [10, 22, 22, 1],
            [10, 23, 23, 1],
            [10, 24, 24, 1],
            [10, 25, 25, 1],
        ]

    )

    missing_expected_506_values = pd.DataFrame(
        columns=["DMID", "DMRow", "DMColumn", "Proportion"],
        data=[
            [506, 12, 12, 0.75],
            [506, 11, 11, 0.75],
            [506, 10, 10, 0.75],
            [506, 9, 9, 0.75],
            [506, 8, 8, 0.75],
            [506, 7, 7, 0.75],
            [506, 6, 6, 0.75],
            [506, 5, 5, 0.75],
            [506, 4, 4, 0.75],
            [506, 3, 3, 0.75],
            [506, 2, 2, 0.75],
            [506, 1, 1, 0.75],
            [506, 13, 13, 1.0],
            [506, 14, 14, 1.0],
            [506, 15, 15, 1.0],
            [506, 16, 16, 1.0],
            [506, 17, 17, 1.0],
            [506, 18, 18, 1.0],
            [506, 19, 19, 1.0],
            [506, 20, 20, 1.0],
            [506, 21, 21, 1.0],
            [506, 22, 22, 1.0],
            [506, 23, 23, 1.0],
            [506, 24, 24, 1.0],
            [506, 25, 25, 1.0],
        ]
    )
    expected_result = pd.concat([
        input, missing_expected_506_values
    ])

    expected_result["DMRow"] = expected_result["DMRow"].map(
        pool_cross_walk
    )
    expected_result["DMColumn"] = expected_result["DMColumn"].map(
        pool_cross_walk
    )
    expected_result = expected_result.loc[
        (
            (expected_result["DMRow"] > 0)
            & (expected_result["DMColumn"] > 0)
        )
    ]

    result = dm_values_processor.process_dm_values(
        input.to_dict("records"),
        ["DMID", "DMRow", "DMColumn", "Proportion"],
        pool_cross_walk
    )

    pd.testing.assert_frame_equal(
        expected_result.sort_values(
            by=["DMID", "DMRow", "DMColumn"]
        ).reset_index(drop=True),
        result
    )


def test_dm_values_processor_zero_retentions():

    # check that when the retention is zero, or close to zero, the the output
    # retention is exactly zero
    pool_cross_walk: dict[int, int] = {}
    for row in local_csv_table.read_csv_file("pool_cross_walk.csv"):
        pool_cross_walk[int(row["cbm3_pool_code"])] = int(
            row["cbm3_5_pool_code"]
        )
    input = pd.DataFrame(
        columns=["DMID", "DMRow", "DMColumn", "Proportion"],
        data=[
            [506, 12, 14, 0.25],
            [506, 11, 16, 0.25],
            [506, 10, 23, 0.25],
            [506, 9, 23, 0.25],
            [506, 8, 13, 0.25],
            [506, 7, 22, 0.25],
            [506, 6, 14, 0.25],
            [506, 5, 16, 0.25],
            [506, 4, 21, 0.25],
            # the 3, 21 and 3, 20 pool flows sum to < 1.0 resulting in a
            # slightly positive retention,
            [506, 3, 21, 0.25],
            [506, 3, 20, 0.749999],
            # the 2,13 and 2,14 pool flows sum to > 1.0 resulting in a
            # slightly negative retention.
            [506, 2, 13, 0.25],
            [506, 2, 14, 0.750001],
            [506, 1, 20, 0.25],
            [506, 1, 21, 0.75],
            [10, 1, 20, 1],
            [10, 2, 13, 0.9],
            [10, 2, 26, 0.1],
            [10, 3, 21, 1],
            [10, 4, 21, 1],
            [10, 5, 15, 0.5],
            [10, 5, 16, 0.5],
            [10, 6, 13, 0.5],
            [10, 6, 14, 0.5],
            [10, 7, 22, 1],
            [10, 8, 13, 0.9],
            [10, 8, 26, 0.1],
            [10, 9, 23, 1],
            [10, 10, 23, 1],
            [10, 11, 15, 0.5],
            [10, 11, 16, 0.5],
            [10, 12, 13, 0.5],
            [10, 12, 14, 0.5],
            [10, 13, 13, 1],
            [10, 14, 14, 1],
            [10, 15, 15, 1],
            [10, 16, 16, 1],
            [10, 17, 17, 1],
            [10, 18, 18, 1],
            [10, 19, 19, 1],
            [10, 20, 20, 1],
            [10, 21, 21, 1],
            [10, 22, 22, 1],
            [10, 23, 23, 1],
            [10, 24, 24, 1],
            [10, 25, 25, 1],
        ]

    )

    missing_expected_506_values = pd.DataFrame(
        columns=["DMID", "DMRow", "DMColumn", "Proportion"],
        data=[
            [506, 12, 12, 0.75],
            [506, 11, 11, 0.75],
            [506, 10, 10, 0.75],
            [506, 9, 9, 0.75],
            [506, 8, 8, 0.75],
            [506, 7, 7, 0.75],
            [506, 6, 6, 0.75],
            [506, 5, 5, 0.75],
            [506, 4, 4, 0.75],
            [506, 13, 13, 1.0],
            [506, 14, 14, 1.0],
            [506, 15, 15, 1.0],
            [506, 16, 16, 1.0],
            [506, 17, 17, 1.0],
            [506, 18, 18, 1.0],
            [506, 19, 19, 1.0],
            [506, 20, 20, 1.0],
            [506, 21, 21, 1.0],
            [506, 22, 22, 1.0],
            [506, 23, 23, 1.0],
            [506, 24, 24, 1.0],
            [506, 25, 25, 1.0],
        ]
    )
    expected_result = pd.concat([
        input, missing_expected_506_values
    ])

    expected_result["DMRow"] = expected_result["DMRow"].map(
        pool_cross_walk
    )
    expected_result["DMColumn"] = expected_result["DMColumn"].map(
        pool_cross_walk
    )
    expected_result = expected_result.loc[
        (
            (expected_result["DMRow"] > 0)
            & (expected_result["DMColumn"] > 0)
        )
    ]

    result = dm_values_processor.process_dm_values(
        input.to_dict("records"),
        ["DMID", "DMRow", "DMColumn", "Proportion"],
        pool_cross_walk
    )

    pd.testing.assert_frame_equal(
        expected_result.sort_values(
            by=["DMID", "DMRow", "DMColumn"]
        ).reset_index(drop=True),
        result
    )

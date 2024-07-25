import pandas as pd
from cbm_defaults import dm_values_processor


def test_dm_values_processor():

    input = pd.DataFrame(
        columns=["DMID", "DMRow", "DMColumn", "Proportion"],
        data = [
            []
        ]
    )
    dm_values_processor.process_dm_values()
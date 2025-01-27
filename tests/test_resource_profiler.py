import unittest
import pandas as pd
from pyinsights import Connector
from pyinsights.organisational_profiling import ResourceProfiler
import os
from dotenv import load_dotenv


class ResourceTester(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.celonis_url = os.getenv("URL_CFI")
        self.api_token = os.getenv("TOKEN_CFI")
        self.key_type = os.getenv("KEY_TYPE_CFI")

    def test_resource_profile(self):
        """
        tests resource profile
        :return:
        """
        # define connector and connect to celonis
        connector = Connector(api_token=self.api_token,
                              url=self.celonis_url, key_type=self.key_type)
        deviation_log = os.getenv("ID_DEVIATION_LOG")
        connector.set_parameters(
            model_id=deviation_log, end_timestamp='end_time', resource_column="Resource")
        # compute resource profile
        profiler = ResourceProfiler(connector=connector)
        resource_profile = profiler.resource_profile(
            time_unit="HOURS", reference_unit="DAY")

        expected_profile = pd.DataFrame(
            {
                connector.case_col(): [1, 1, 1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 9],
                connector.activity_col(): ["a", "b", "c", "a", "a", "c", "a", "a", "a", "a", "a", "a", "a"],
                "Resource": ["Pete", "Pete", "Pete", "Pete", "Pete", "Pete", "Pete", "Pete", "Pete", "Pete",
                             "Pete", "Pete", "Pete"],
                "# this HOURS": [1, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 7],
                "# this DAY": [1, 1, 1, 2, 2, 1, 7, 7, 7, 7, 7, 7, 7]

            })

        # assert that profile equals expected output
        self.assertTrue(resource_profile[[connector.case_col(), connector.activity_col(), "Resource",
                                          "# this HOURS", "# this DAY"]].equals(expected_profile))

    def test_cases_with_batches(self):
        """
        tests identification of cases with batches
        :return:
        """
        # define connector and connect to celonis
        connector = Connector(api_token=self.api_token,
                              url=self.celonis_url, key_type=self.key_type)
        deviation_log = os.getenv("ID_DEVIATION_LOG")
        connector.set_parameters(
            model_id=deviation_log, end_timestamp='end_time', resource_column="Resource")
        # compute cases with batches
        profiler = ResourceProfiler(connector=connector)
        cases_df = profiler.cases_with_batches(time_unit="HOURS", reference_unit="DAY", min_batch_size=2,
                                               grouped_by_batches=True, batch_types=True)
        expected_cases = pd.DataFrame(
            {
                connector.case_col(): [3, 4, 5, 6, 7, 8, 9],
                connector.activity_col(): ["a", "a", "a", "a", "a", "a", "a"],
                "Resource": ["Pete", "Pete", "Pete", "Pete", "Pete", "Pete", "Pete"],
                "# this HOURS": [7, 7, 7, 7, 7, 7, 7],
                "# this DAY": [7, 7, 7, 7, 7, 7, 7],
                "batch type": ["simultaneous", "simultaneous", "simultaneous", "simultaneous",
                               "simultaneous", "simultaneous", "simultaneous"]

            })

        # assert that cases with batches equal expected output
        self.assertTrue(cases_df[[connector.case_col(), connector.activity_col(), "Resource",
                                  "# this HOURS", "# this DAY", "batch type"]].equals(expected_cases))


if __name__ == '__main__':
    unittest.main()

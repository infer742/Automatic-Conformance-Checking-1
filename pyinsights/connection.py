from pycelonis import get_celonis, __version__
from pycelonis.celonis_api.pql.pql import PQL, PQLColumn, PQLFilter


class Connector:
    """
Encapsulates connection to celonis
provides datamodel, activity_table, case_col, activity_col, timestamp

:param api_key: Celonis api token
:type api_key: string

:param url: Celonis url
:type url: string

:param key_type: Celonis key type
:type key_type: string

"""

    end_time = None

    def __init__(self, api_token, url, key_type):
        self.datamodel = None
        self.datapool = None
        self.api_token = api_token
        self.url = url
        self.key_type = key_type
        self.resource_col = None

        global end_time
        end_time = None

        try:
            self.celonis = get_celonis(
                api_token=self.api_token, url=self.url, key_type=self.key_type, permissions=False)
            if (len(self.celonis.pools) > 0):
                self.datapool = self.celonis.pools[0]
            if (len(self.celonis.datamodels) > 0):
                self.datamodel = self.celonis.datamodels[0]
        except Exception as e:
            self.celonis = None
            print(e)
            raise Exception

    def connect(self):
        """
        Connects to Celonis
        """

        try:
            self.celonis = get_celonis(
                api_token=self.api_token, url=self.url, key_type=self.key_type, permissions=False)
        except:
            self.celonis = None
            print("celonis error")

    def activity_table(self):
        """
           returns name of activity table
           """
        process = self.datamodel.process_configurations[0]
        return process.activity_table.source_name

    def case_col(self):
        """
        returns name of case column
        """

        process_config = self.datamodel.process_configurations[0]
        case_col = process_config.case_column

        return case_col

    def activity_col(self):
        """
        returns name of activity column
        """

        process_config = self.datamodel.process_configurations[0]
        act_col = process_config.activity_column

        return act_col

    def columns(self):
        process = self.datamodel.process_configurations[0]
        return process.activity_table.columns

    def end_timestamp(self):
        """
        returns name of end timestamp column or none
        :return:
        """
        if self.end_time is not None:
            return self.end_time
        else:
            return self.timestamp()

    def timestamp(self):
        """
           returns name of timestamp column
           """
        process_config = self.datamodel.process_configurations[0]
        timestamp = process_config.timestamp_column

        return timestamp

    def set_parameters(self, pool_id=None, model_id=None, end_timestamp=None, resource_column=None):
        """
            sets celonis data parameters
            :param model_id: id of datamodel
            :type model_id: string
            """
        if pool_id is not None:
            self.datapool = self.celonis.pools.find(pool_id)

        if model_id is not None:
            self.datamodel = self.celonis.get_datamodel(model_id)

        if end_timestamp == "":
            self.end_time = None
        elif end_timestamp is not None:
            self.end_time = end_timestamp

        if resource_column is not None:
            self.resource_col = resource_column

    def has_end_timestamp(self):
        """
        returns true if datamodel has end-timestamp
        :return: bool
        """
        return self.end_time is not None

    def has_resource_column(self):
        """returns true if datamodel has resource column
        """

        return self.resource_col is not None

    def resource_column(self):
        return self.resource_col

    def events(self):
        """
             returns all events as dataframe
        """
        query = PQL()
        query.add(PQLColumn(name=self.case_col(),
                  query=f"\"{self.activity_table()}\".\"{self.case_col()}\""))
        query.add(PQLColumn(name=self.activity_col(),
                  query=f"\"{self.activity_table()}\".\"{self.activity_col()}\""))
        query.add(PQLColumn(name=self.timestamp(),
                  query=f""" "{self.activity_table()}"."{self.timestamp()}"  """))

        events = self.datamodel.get_data_frame(query)

        return events

# This class manages both the offline data and online data 
from .Singleton import Singleton
from .csv_data_manager import CSVDataManager
from .azure_data_manager import AzureDataManager
from .data_store import DataStore

# User either connects to Azure with connection info 
# OR User can import data from data files 
# depending on the mode, this class should return the same data
# it is a DataManager type resource


# User clicks Connect, Or Load, Goal is the same, load data from azure or files 
# and give the user some basic info to show the connection / import worked.
# now connected, user can load different sets of resources and view then in different ways.

@Singleton
class DataManager:
    def __init__(self):
        print("DataManager Created.")
        self._dataStore = DataStore.instance()
        self._offlineDataManager = CSVDataManager()
        self._onlineDataManager = AzureDataManager()
        self._dataStore.Load_Config_Data()
        self.refresh_data()

    def load_csv_files(self):
        self._dataStore._sourceOfData = "OfflineData"
        self._dataStore.Save_Config_Data()
        self._offlineDataManager.loadFiles()
        self.process_data()

    def load_from_api(self):
        self._dataStore._sourceOfData = "LiveAzureAPI"
        self._dataStore.Save_Config_Data()
        
        #Load data from Cloud API
        self._onlineDataManager.load_data()

        #Aggregate the info
        self.process_data()

    def refresh_data(self):
        if self._dataStore._sourceOfData =="OfflineData":
            self.load_csv_files()
            print("CSV Data Refreshed.")
        elif self._dataStore._sourceOfData == "LiveAzureAPI":
            self.load_from_api()
            print("Live Data Refreshed.")

    #Aggregate subscription, resources counts to DataManager Dictionaries
    def process_data(self):  
        print("Processing Data...")

        for key in self._dataStore._resources:
            obj = self._dataStore._resources[key]

            #Count per Sub
            if obj["subscription"] not in self._dataStore._subscription_count.keys():
                self._dataStore._subscription_count[obj["subscription"]] = 1
            else:
                self._dataStore._subscription_count[obj["subscription"]] = self._dataStore._subscription_count[obj["subscription"]] + 1
            
            #Count per Location
            if obj["location"] not in self._dataStore._location_count.keys():
                self._dataStore._location_count[obj["location"]] = 1
            else:
                self._dataStore._location_count[obj["location"]] = self._dataStore._location_count[obj["location"]] + 1

            #Count per Type
            if obj["type"] not in self._dataStore._type_count.keys():
                self._dataStore._type_count[obj["type"]] = 1
            else:
                self._dataStore._type_count[obj["type"]] = self._dataStore._type_count[obj["type"]] + 1

            #Count per Group
            if obj["group"] not in self._dataStore._group_count.keys():
                self._dataStore._group_count[obj["group"]] = 1
            else:
                self._dataStore._group_count[obj["group"]] = self._dataStore._group_count[obj["group"]] + 1


            #Count per Tags
            #if obj["tag"] not in self._dataStore._tag_count.keys():
            #    self._dataStore._tag_count[obj["tag"]] = 1
            #else:
            #    self._dataStore._tag_count[obj["tag"]] = self._dataStore._tag_count[obj["tag"]] + 1


        #output aggregation results to console
        print("Data loaded from Files...")

    #passthrough to csv manager
    def select_file(self, fileType: str):
        self._offlineDataManager.select_file(fileType=fileType)

#-- SINGLETON SUPPORT

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

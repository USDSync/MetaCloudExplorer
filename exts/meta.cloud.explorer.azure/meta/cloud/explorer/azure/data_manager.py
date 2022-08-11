# This class manages both the offline data and online data 
from .Singleton import Singleton

from .offline_data_manager import OfflineDataManager
from .azure_resource_manager import OnlineDataManager

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

        #NAME,SUBSCRIPTION,LOCATION
        self._groups = {}

        #NAME,TYPE,RESOURCE GROUP,LOCATION,SUBSCRIPTION
        self._resources = {}        

        #aggregated data
        self._subscription_count = {}
        self._location_count = {}
        self._group_count = {}
        self._type_count = {}
        self._tag_count = {}

        self._offlineDataManager = OfflineDataManager()
        self._onlineDataManager = OnlineDataManager()

        self._sourceOfData = None
        
    def load_csv_files(self):
        self._offlineDataManager.loadFiles()

    def load_from_api(self):
        self._onlineDataManager.loadData()

    #Aggregate subscription, resources counts to DataManager Dictionaries
    def process_data(self):  
        print("Processing CSV Data...")

        for key in self._resources:
            obj = self._resources[key]

            #Count per Sub
            if obj["subscription"] not in self._subscription_count.keys():
                self._subscription_count[obj["subscription"]] = 1
            else:
                self._subscription_count[obj["subscription"]] = self._subscription_count[obj["subscription"]] + 1
            
            #Count per Location
            if obj["location"] not in self._location_count.keys():
                self._location_count[obj["location"]] = 1
            else:
                self._location_count[obj["location"]] = self._location_count[obj["location"]] + 1

            #Count per Type
            if obj["type"] not in self._type_count.keys():
                self._type_count[obj["type"]] = 1
            else:
                self._type_count[obj["type"]] = self._type_count[obj["type"]] + 1

            #Count per Group
            if obj["group"] not in self._group_count.keys():
                self._group_count[obj["group"]] = 1
            else:
                self._group_count[obj["group"]] = self._group_count[obj["group"]] + 1

            #Count per Tags
            if obj["tag"] not in self._tag_count.keys():
                self._tag_count[obj["tag"]] = 1
            else:
                self._tag_count[obj["tag"]] = self._tag_count[obj["tag"]] + 1



        #output aggregation results to console
        print("Groups: " + str(len(self._group_count)))
        print("Locations: " + str(len(self._location_count)))
        print("Subs: " + str(len(self._subscription_count)))


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

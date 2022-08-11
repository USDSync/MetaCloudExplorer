# This class manages both the offline data and online data 
from .Singleton import Singleton

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

        #datasets
        self._groups = {}
        self._resources = {}        

        #aggregated data
        self._subscription_count = {}
        self._location_count = {}
        self._group_count = {}

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

    #Aggregate subscription, resources counts to DataManager Dictionaries
    def process_data(self):  
        print("Processing CSV Data...")

        for key in self._resources:
            obj = self._resources[key]

            if obj["subscription"] not in self._subscription_count.keys():
                self._subscription_count[obj["subscription"]] = 1
            else:
                self._subscription_count[obj["subscription"]] = self._subscription_count[obj["subscription"]] + 1
            
            if obj["location"] not in self._location_count.keys():
                self._location_count[obj["location"]] = 1
            else:
                self._location_count[obj["location"]] = self._location_count[obj["location"]] + 1

            if obj["group"] not in self._group_count.keys():
                self._group_count[obj["group"]] = 1
            else:
                self._group_count[obj["group"]] = self._group_count[obj["group"]] + 1

        #output aggregation results to console
        print("Groups: " + str(len(self._group_count)))
        print("Locations: " + str(len(self._location_count)))
        print("Subs: " + str(len(self._subscription_count)))


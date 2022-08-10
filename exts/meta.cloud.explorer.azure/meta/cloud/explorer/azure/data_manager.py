# This class manages both the offline data and online data 



# User either connects to Azure with connection info 
# OR User can import data from data files 
# depending on the mode, this class should return the same data
# it is a DataManager type resource


# User clicks Connect, Or Load, Goal is the same, load data from azure or files 
# and give the user some basic info to show the connection / import worked.
# now connected, user can load different sets of resources and view then in different ways.


class DataManager():
    def __init__(self):

        #datasets
        self._groups = {}
        self._resources = {}        

        #aggregated data
        self._subscription_count = {}
        self._location_count = {}
        self._group_count = {}


    #Aggregate subscription, resources counts to DataManager Dictionaries
    def process_data(self):  
        print("Processing CSV Data...")

        for key in self._dataManager._resources:
            obj = self._dataManager._resources[key]

            if obj["subscription"] not in self._dataManager._subscription_count.keys():
                self._dataManager._subscription_count[obj["subscription"]] = 1
            else:
                self._dataManager._subscription_count[obj["subscription"]] = self._dataManager._subscription_count[obj["subscription"]] + 1
            
            if obj["location"] not in self._dataManager._location_count.keys():
                self._dataManager._location_count[obj["location"]] = 1
            else:
                self._dataManager._location_count[obj["location"]] = self._dataManager._location_count[obj["location"]] + 1

            if obj["group"] not in self._dataManager._group_count.keys():
                self._dataManager._group_count[obj["group"]] = 1
            else:
                self._dataManager._group_count[obj["group"]] = self._dataManager._group_count[obj["group"]] + 1

        #output aggregation results to console
        print("Groups: " + str(len(self._dataManager._group_count)))
        print("Locations: " + str(len(self._dataManager._location_count)))
        print("Subs: " + str(len(self._dataManager._subscription_count)))


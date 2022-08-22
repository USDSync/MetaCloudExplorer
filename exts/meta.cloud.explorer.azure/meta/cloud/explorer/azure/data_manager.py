# This class manages both the offline data and online data 
from .Singleton import Singleton
from .csv_data_manager import CSVDataManager
from .azure_data_manager import AzureDataManager
from .data_store import DataStore
from .prim_utils import cleanup_prim_path, draw_image
from .azure_resource_map import shape_usda_name
from .pillow_text import draw_text_on_image_at_position_async, draw_text_on_image_at_position
from pathlib import Path
from pxr import Sdf

from  .prim_utils import get_font_size_from_length
import omni.kit.notification_manager as nm
import omni
import asyncio
import asyncbg
import logging
import shutil
import locale 


# User either connects to Azure with connection info 
# OR User can import data from data files 
# depending on the mode, this class should return the same data
# it is a DataManager type resource

# User clicks Connect, Or Load, Goal is the same, load data from azure or files 
# and give the user some basic info to show the connection / import worked.
# now connected, user can load different sets of resources and view then in different ways.

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.joinpath("temp")

@Singleton
class DataManager:
    def __init__(self):

        logging.getLogger("asyncio").setLevel(logging.WARNING)

        print("DataManager Created.")
        self._dataStore = DataStore.instance()
        self._offlineDataManager = CSVDataManager()
        self._onlineDataManager = AzureDataManager()
        self._dataStore.Load_Config_Data()
        self.refresh_data()

    def load_csv_files(self):
        #self._dataStore._groups.clear()
        #self._dataStore._resources.clear()
        self._dataStore._source_of_data = "OfflineData"
        self._dataStore.Save_Config_Data()
        self._offlineDataManager.loadFiles()
        self.process_data()

    def load_from_api(self):
        #self._dataStore._groups.clear()
        #self._dataStore._resources.clear()
        self._dataStore._source_of_data = "LiveAzureAPI"
        self._dataStore.Save_Config_Data()
        
        #Load data from Cloud API
        self._onlineDataManager.connect()
        self._onlineDataManager.load_data()

        #Aggregate the info
        self.process_data()

    def wipe_data(self):
        self._dataStore._groups.clear()
        self._dataStore._resources.clear()

        self._dataStore._subscription_count = {}
        self._dataStore._location_count = {}
        self._dataStore._group_count = {}
        self._dataStore._type_count = {}
        self._dataStore._tag_count = {}

        self._dataStore._subscription_cost = {}
        self._dataStore._location_cost = {}
        self._dataStore._group_cost = {}
        self._dataStore._type_cost = {}
        self._dataStore._tag_cost = {}
        
        print("Data Cleared.")

    def refresh_data(self):
        if self._dataStore._source_of_data =="OfflineData":
            self.load_csv_files()
            print("CSV Data Refreshed.")
        elif self._dataStore._source_of_data == "LiveAzureAPI":
            self.load_from_api()
            print("Live Data Refreshed.")

    #Aggregate subscription, resources counts to DataManager Dictionaries
    def process_data(self):  
        print("Processing Data...")

        #For every resrouce...
        for key in self._dataStore._resources:
            obj = self._dataStore._resources[key]

            ### AGGREGATE COUNTS
            self.AggregateCounts(obj)

            ### AGGREGATE COSTS
            self.AggregateCosts(obj)
            
            ### MAP RESOURCES TO AGGREGATES
            self.MapResourcesToGroups(obj)

        self.ScoreCosts()

        #Pre-create images for the groups
        asyncio.ensure_future(self.CreateImagesForGroups())

        #output aggregation results to console
        print("Data processing complete..")
        print(self._dataStore._source_of_data + " data refreshed.")     
        print(str(len(self._dataStore._resources)) + " Resources loaded from " + self._dataStore._source_of_data)
        print(str(len(self._dataStore._groups)) + " Groups loaded from " + self._dataStore._source_of_data)

    # async def image_tesk(self):
    #     loop = self.get_or_create_eventloop()
    #     response = loop.run_until_complete(await self.CreateImagesForGroups())
    #     loop.close()
    #     # assert your response

    # def get_or_create_eventloop():
    #     try:
    #         return asyncio.get_event_loop()
    #     except RuntimeError as ex:
    #         if "There is no current event loop in thread" in str(ex):
    #             loop = asyncio.new_event_loop()
    #             asyncio.set_event_loop(loop)
    #             return asyncio.get_event_loop()       

    #Create Images for all the maps
    async def CreateImagesForGroups(self):

        print("Processing images.")

        #go through all the maps and create images 
        #this will save a ton of time later 
        src_file = self._dataStore._bg_file_path 

        #SUBSCRIPTIONS
        #We need to create images for each group
        for rec in self._dataStore._map_subscription:

            #Let the Ui breathe ;)
            await omni.kit.app.get_app().next_update_async()

            output_file = DATA_PATH.joinpath(rec + ".png")
            cost_output_file = DATA_PATH.joinpath(rec + "-cost.png")
            textToDraw = rec
            costToDraw =""

            #We dont care here if the user wants costs or not, we are pre-making images
            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
                costToDraw = locale.currency(self._dataStore._subscription_cost[rec])
            except:
                costToDraw=""

            draw_image(self, output_file=output_file, src_file=src_file, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=output_file, src_file=src_file, textToDraw=textToDraw, costToDraw=costToDraw)


        #LOCATIONS
        #We need to create images for each group
        for rec in self._dataStore._map_location:

            #Let the Ui breathe ;)
            await omni.kit.app.get_app().next_update_async()

            temp_file = rec + ".png"
            output_file = DATA_PATH.joinpath(temp_file)
            cost_output_file = DATA_PATH.joinpath(rec + "-cost.png")
            textToDraw = rec
            costToDraw =""

            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

                costToDraw = locale.currency(self._dataStore._location_cost[rec])      
            except:
                costToDraw=""

            draw_image(self, output_file=output_file, src_file=src_file, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=cost_output_file, src_file=src_file, textToDraw=textToDraw, costToDraw=costToDraw)


        #RESOURCE GROUPS
        #We need to create images for each group
        for rec in self._dataStore._map_group:

            #Let the Ui breathe ;)
            await omni.kit.app.get_app().next_update_async()

            output_file = DATA_PATH.joinpath(rec + ".png")
            cost_output_file = DATA_PATH.joinpath(rec + "-cost.png")
            textToDraw = rec
            costToDraw =""

            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

                costToDraw = locale.currency(self._dataStore._group_cost[rec])
            except:
                costToDraw=""

            draw_image(self, output_file=output_file, src_file=src_file, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=cost_output_file, src_file=src_file, textToDraw=textToDraw, costToDraw=costToDraw)

        #TYPES
        #We need to create images for each group
        for rec in self._dataStore._map_type:

            #Let the Ui breathe ;)
            await omni.kit.app.get_app().next_update_async()

            output_file = DATA_PATH.joinpath(rec + ".png")
            cost_output_file = DATA_PATH.joinpath(rec + "-cost.png")
            textToDraw = rec
            costToDraw =""

            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

                costToDraw = locale.currency(self._dataStore._type_cost[rec])
            except:
                costToDraw=""

            draw_image(self, output_file=output_file, src_file=src_file, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=cost_output_file, src_file=src_file, textToDraw=textToDraw, costToDraw=costToDraw)

        #TAGS
        #We need to create images for each group
        for rec in self._dataStore._map_tag:

            #Let the Ui breathe ;)
            await omni.kit.app.get_app().next_update_async()

            output_file = DATA_PATH.joinpath(rec + ".png")
            cost_output_file = DATA_PATH.joinpath(rec + "-cost.png")
            textToDraw = rec
            costToDraw =""

            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

                costToDraw = locale.currency(self._dataStore._tag_cost[rec])

            except:
                costToDraw=""

            draw_image(self, output_file=output_file, src_file=src_file, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=cost_output_file, src_file=src_file, textToDraw=textToDraw, costToDraw=costToDraw)

        print("Processing images complete..")

    #Calculate the low, min, max, mean costs and score each group according to its peers
    def ScoreCosts(self):
        pass
        

    def AggregateCosts(self, obj):

        ### AGGREGATE COSTS
        #Cost per Sub
        if obj["subscription"] not in self._dataStore._subscription_cost.keys():
            self._dataStore._subscription_cost[obj["subscription"]] = float(obj["lmcost"])
        else:
            self._dataStore._subscription_cost[obj["subscription"]] = float(self._dataStore._subscription_cost[obj["subscription"]]) + float(obj["lmcost"])
        
        #Cost per Location
        if obj["location"] not in self._dataStore._location_cost.keys():
            self._dataStore._location_cost[obj["location"]] = float(obj["lmcost"])
        else:
            self._dataStore._location_cost[obj["location"]] = float(self._dataStore._location_cost[obj["location"]]) + float(obj["lmcost"])
        
        #Cost per Type
        if obj["type"] not in self._dataStore._type_cost.keys():
            self._dataStore._type_cost[obj["type"]] = float(obj["lmcost"])
        else:
            self._dataStore._type_cost[obj["type"]] = float(self._dataStore._type_cost[obj["type"]]) + float(obj["lmcost"])

        #Cost per Group
        if obj["group"] not in self._dataStore._group_cost.keys():
            self._dataStore._group_cost[obj["group"]] = float(obj["lmcost"])
        else:
            self._dataStore._group_cost[obj["group"]] =float(self._dataStore._group_cost[obj["group"]]) + float(obj["lmcost"])

        #your_dictionary = {'Australia':1780, 'England':6723, 'Tokyo': 1946}

#        new_maximum_val = max([obj["subscription"]].values(), key=(lambda new_k: your_dictionary[new_k]))
#        print('Maximum Value: ',your_dictionary[new_maximum_val])
#        new_minimum_val = min(your_dictionary.keys(), key=(lambda new_k: your_dictionary[new_k]))
#        print('Minimum Value: ',your_dictionary[new_minimum_val])






    def AggregateCounts(self, obj):

        ### AGGREGATE COUNTS
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


    #Given a resource, Map it to all the groups it belongs to.
    def MapResourcesToGroups(self, obj):
        
        #Get the mapped shape and figure out the prim path for the map
        # Set a default
        shape_to_render = "omniverse://localhost/Resources/3dIcons/scene.usd"

        try:
            typeName = cleanup_prim_path(self,  obj["type"])
            shape_to_render = shape_usda_name[typeName]   
        except:
            print("No matching prim found - " + typeName)                                  

        # SUBSCRIPTION MAP
        self.map_objects(typeName, "/Subs" ,shape_to_render, self._dataStore._map_subscription, obj, "subscription")

        # GROUP MAP
        self.map_objects(typeName, "/RGrp", shape_to_render, self._dataStore._map_group, obj, "group")

        # TYPE MAP
        self.map_objects(typeName, "/Type", shape_to_render, self._dataStore._map_type, obj, "type")

        # LOCATION MAP
        self.map_objects(typeName, "/Loc", shape_to_render, self._dataStore._map_location, obj, "location")

        #TODO TAGMAP
        #self.map_objects(typeName, "/Tag", shape_to_render, self._dataStore._tag_map, obj, "tag")


    #Maps objects to create to each aggregate
    def map_objects(self, typeName, root, shape, map, obj, field:str):
        
        prim_path = cleanup_prim_path(self, Name=obj[field])
        print(prim_path)
        sub_prim_path = Sdf.Path(root)
        sub_prim_path = Sdf.Path(sub_prim_path).AppendPath(prim_path)
        flat_prim_path = cleanup_prim_path(self, str(sub_prim_path))
        
        map_obj = {"type":typeName,"shape":shape}

        if obj[field] not in map.keys():
            
            #new map!
            mapObj = { obj[field] : [ map_obj ] }
            map[obj[field]] = { flat_prim_path : mapObj}
        else:
            #get the map for this group, add this item
            mapObj = map[obj[field]]
            map[flat_prim_path] = mapObj
        


    #passthrough to csv manager
    def select_file(self, fileType: str):
        self._offlineDataManager.select_file(fileType=fileType)
   


    def clicked_ok(self):
        pass


    def sendNotify(self, message:str, status:nm.NotificationStatus):
        
        # https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.kit.notification_manager/docs/index.html?highlight=omni%20kit%20notification_manager#

        import omni.kit.notification_manager as nm
        ok_button = nm.NotificationButtonInfo("OK", on_complete=self.clicked_ok)

        nm.post_notification(
            message,
            hide_after_timeout=True,
            duration=5,
            status=status,
            button_infos=[ok_button]
        )        


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

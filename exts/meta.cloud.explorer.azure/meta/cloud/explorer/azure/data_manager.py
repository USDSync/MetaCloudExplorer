# This class manages both the offline data and online data 
from typing import Dict
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
import carb


# User either connects to Azure with connection info 
# OR User can import data from data files 
# depending on the mode, this class should return the same data
# it is a DataManager type resource

# User clicks Connect, Or Load, Goal is the same, load data from azure or files 
# and give the user some basic info to show the connection / import worked.
# now connected, user can load different sets of resources and view then in different ways.
ASYNC_ENABLED = True
CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.joinpath("temp")
RES_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data\\resources")
IMPORTS_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data\\import")

@Singleton
class DataManager:
    def __init__(self):

        self._callbacks = []

        logging.getLogger("asyncio").setLevel(logging.WARNING)

        carb.log_info("DataManager Created.")
        self._dataStore = DataStore.instance()
        self._offlineDataManager = CSVDataManager()
        self._onlineDataManager = AzureDataManager()
        self._dataStore.Load_Config_Data()
        self.refresh_data()

    #shut it down...
    def destroy(self):
        carb.log_info("DataManager Destroyed.")
        self._callbacks = []
        self._offlineDataManager = None
        self._onlineDataManager = None
        self._dataStore = None

    #add a callback for model changed
    def add_model_changed_callback(self, func):
        self._callbacks.append(func)

    #Invoke the callbacks that want to know when the data changes
    def _model_changed(self):
        for c in self._callbacks:
            c()

    #Load data from file
    def load_csv_files(self):
        self._dataStore._groups.clear()
        self._dataStore._resources.clear()
        self._lcl_sizes = [] 
        self._lcl_groups = [] 
        self._lcl_resources = [] 

        self._dataStore._source_of_data = "OfflineData"
        self._dataStore.Save_Config_Data()
        
        #Load data from Cloud API
        self._offlineDataManager.loadFiles()

        #Aggregate the info, wait for it
        if len(self._dataStore._groups) >0:
            asyncio.ensure_future(self.process_data())

    #Load data from Azure API
    def load_from_api(self):
        self._dataStore._groups.clear()
        self._dataStore._resources.clear()
        self._lcl_sizes = [] 
        self._lcl_groups = [] 
        self._lcl_resources = [] 
        self._dataStore._source_of_data = "LiveAzureAPI"
        self._dataStore.Save_Config_Data()
        
        #Load the data and process it
        if self._onlineDataManager.connect():
            self._onlineDataManager.load_data()
            #wait for data to finish loading

        if len(self._dataStore._groups) >0:
            asyncio.ensure_future(self.process_data())

    def wipe_data(self):
        self._dataStore.wipe_data()
        self._model_changed()

    def refresh_data(self):
        if self._dataStore._source_of_data =="OfflineData":
            self.load_csv_files()
            carb.log_info("CSV Data Refreshed.")
        elif self._dataStore._source_of_data == "LiveAzureAPI":
            self.load_from_api()
            carb.log_info("Live Data Refreshed.")

    #Load a sample company data
    def load_sample():
        pass

    #Load the "All resources (Shapes) set"
    #This sample contains 1 resource per group
    def load_sample_resources(self):

        self._dataStore.wipe_data()
        src_filel = IMPORTS_PATH.joinpath("TestShapes_RG.csv")
        src_file2 = IMPORTS_PATH.joinpath("TestShapes_all.csv")

        self.load_and_process_manual(src_filel, src_file2)


    #Load the "All resources (Shapes) set"
    #This sample contains 1 resource per group
    def load_sample_company(self):

        self._dataStore.wipe_data()
        src_filel = IMPORTS_PATH.joinpath("SolidCloud_RG.csv")
        src_file2 = IMPORTS_PATH.joinpath("SolidCloud_all.csv")

        self.load_and_process_manual(src_filel, src_file2)

    #load the files async
    def load_and_process_manual(self, grpFile, rgFIle ):
    
        #load the files
        self._offlineDataManager.loadFilesManual(grpFile, rgFIle)

        #Aggregate the info
        if len(self._dataStore._groups) >0:
            asyncio.ensure_future(self.process_data())


    #Aggregate subscription, resources counts to DataManager Dictionaries
    async def process_data(self):  
        carb.log_info("Processing Data...")

        #For every resrouce...
        for key in self._dataStore._resources:
            obj = self._dataStore._resources[key]
            
            #yield control
            await asyncio.sleep(0)

            ### AGGREGATE COUNTS
            await self.AggregateCountsAsync(obj)

            ### AGGREGATE COSTS
            await self.AggregateCostsAsync(obj)
            
            ### MAP RESOURCES TO AGGREGATES
            await self.MapResourcesToGroupsAsync(obj)

        #Pre-create images for the groups
        carb.log_info("Creating images..")        
        await self.CreateImagesForGroups()
        carb.log_info("Creating images complete..")        

        #let everyone know, stuff changed...
        self._model_changed()

        #output aggregation results to console
        carb.log_info("Data processing complete..")
        carb.log_info(self._dataStore._source_of_data + " data refreshed.")     
        carb.log_info(str(len(self._dataStore._resources)) + " Resources loaded from " + self._dataStore._source_of_data)
        carb.log_info(str(len(self._dataStore._groups)) + " Groups loaded from " + self._dataStore._source_of_data)


    #Create Images for all the maps
    async def CreateImagesForGroups(self):

        carb.log_info("Processing images async.")

        #go through all the maps and create images 
        #this will save a ton of time later 
        if self._dataStore._bgl_file_path is None:
            return

        if self._dataStore._bgm_file_path is None:
            return

        if self._dataStore._bgh_file_path is None:
            return

        src_filel = RES_PATH.joinpath(self._dataStore._bgl_file_path)
        src_filem = RES_PATH.joinpath(self._dataStore._bgm_file_path)
        src_fileh = RES_PATH.joinpath(self._dataStore._bgh_file_path)
        src_image = src_filel

        #SUBSCRIPTIONS
        #We need to create images for each group
        for rec in self._dataStore._map_subscription:

            recText = rec #Name of subscription

            #Let the Ui breathe ;)
            #TODO async
            #await omni.kit.app.get_app().next_update_async()
            output_file = DATA_PATH.joinpath(recText + ".png")
            cost_output_file = DATA_PATH.joinpath(recText + "-cost.png")
            textToDraw = recText
            costToDraw =""

            #We dont care here if the user wants costs or not, we are pre-making images
            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
                rawCost = float(self._dataStore._subscription_cost[recText])
                costToDraw = locale.currency(self._dataStore._subscription_cost[recText])

                carb.log_info ("RawCost: " + recText + " $" + str(rawCost))
                carb.log_info ("Cost: " + recText + " $" + str(costToDraw))

                if rawCost < 500:
                    src_image = src_filel
                if rawCost > 500 and rawCost < 1500:
                    src_image = src_filem
                if rawCost > 1500:
                    src_image = src_fileh
            except:
                costToDraw=""

            #todo change image based on score

            draw_image(self, output_file=output_file, src_file=src_image, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=cost_output_file, src_file=src_image, textToDraw=textToDraw, costToDraw=costToDraw)

        #LOCATIONS
        #We need to create images for each group
        for rec in self._dataStore._map_location:

            recText = rec
            #Let the Ui breathe ;)

            #await omni.kit.app.get_app().next_update_async()

            temp_file = recText + ".png"
            output_file = DATA_PATH.joinpath(temp_file)
            cost_output_file = DATA_PATH.joinpath(recText + "-cost.png")
            textToDraw = recText
            costToDraw =""

            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
                rawCost = float(self._dataStore._location_cost[recText])
                costToDraw = locale.currency(self._dataStore._location_cost[recText])      

                carb.log_info ("RawCost: " + recText + " $" + str(rawCost))
                carb.log_info ("Cost: " + recText + " $" + str(costToDraw))

                if rawCost < 500:
                    src_image = src_filel
                if rawCost > 500 and rawCost < 1500:
                    src_image = src_filem
                if rawCost > 1500:
                    src_image = src_fileh
            except:
                costToDraw=""

            draw_image(self, output_file=output_file, src_file=src_image, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=cost_output_file, src_file=src_image, textToDraw=textToDraw, costToDraw=costToDraw)

        #RESOURCE GROUPS
        #We need to create images for each group
        for rec in self._dataStore._map_group:

            recText = rec
            #Let the Ui breathe ;)
            #await omni.kit.app.get_app().next_update_async()

            output_file = DATA_PATH.joinpath(recText + ".png")
            cost_output_file = DATA_PATH.joinpath(recText + "-cost.png")
            textToDraw = recText
            costToDraw =""

            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
                rawCost = float(self._dataStore._group_cost[rec])
                costToDraw = locale.currency(self._dataStore._group_cost[recText])

                carb.log_info ("RawCost: " + recText + " $" + str(rawCost))
                carb.log_info ("Cost: " + recText + " $" + str(costToDraw))

                if rawCost < 500:
                    src_image = src_filel
                if rawCost > 500 and rawCost < 1500:
                    src_image = src_filem
                if rawCost > 1500:
                    src_image = src_fileh                
            except:
                costToDraw=""

            draw_image(self, output_file=output_file, src_file=src_image, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=cost_output_file, src_file=src_image, textToDraw=textToDraw, costToDraw=costToDraw)

        #TYPES
        #We need to create images for each group
        for rec in self._dataStore._map_type:

            recText = rec
            #Let the Ui breathe ;)
            #await omni.kit.app.get_app().next_update_async()

            output_file = DATA_PATH.joinpath(recText + ".png")
            cost_output_file = DATA_PATH.joinpath(recText + "-cost.png")
            textToDraw = recText
            costToDraw =""

            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
                rawCost = float(self._dataStore._type_cost[recText])
                costToDraw = locale.currency(self._dataStore._type_cost[recText])
                carb.log_info ("RawCost: " + recText + " $" + str(rawCost))
                carb.log_info ("Cost: " + recText + " $" + str(costToDraw))
                if rawCost < 500:
                    src_image = src_filel
                if rawCost > 500 and rawCost < 1500:
                    src_image = src_filem
                if rawCost > 1500:
                    src_image = src_fileh                
            except:
                costToDraw=""

            draw_image(self, output_file=output_file, src_file=src_image, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=cost_output_file, src_file=src_image, textToDraw=textToDraw, costToDraw=costToDraw)

        #TAGS
        #We need to create images for each group
        for rec in self._dataStore._map_tag:

            recText = rec
            #Let the Ui breathe ;)
            #await omni.kit.app.get_app().next_update_async()

            output_file = DATA_PATH.joinpath(recText + ".png")
            cost_output_file = DATA_PATH.joinpath(recText + "-cost.png")
            textToDraw = recText
            costToDraw =""

            try:
                locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
                rawCost = float(self._dataStore._tag_cost[recText])
                costToDraw = locale.currency(self._dataStore._tag_cost[recText])

                carb.log_info ("RawCost: " + recText + " $" + str(rawCost))
                carb.log_info ("Cost: " + recText + " $" + str(costToDraw))

                if rawCost < 500:
                    src_image = src_filel
                if rawCost > 500 and rawCost < 1500:
                    src_image = src_filem
                if rawCost > 1500:
                    src_image = src_fileh                

            except:
                costToDraw=""

            draw_image(self, output_file=output_file, src_file=src_image, textToDraw=textToDraw, costToDraw="")
            draw_image(self, output_file=cost_output_file, src_file=src_image, textToDraw=textToDraw, costToDraw=costToDraw)

        carb.log_info("Processing images complete..")

    #Calculate the low, min, max, mean costs and score each group according to its peers
    def ScoreCosts(self):
        pass

    #Async context
    async def AggregateCostsAsync(self, obj):

        ### AGGREGATE COSTS
        #Cost per Sub
        subKey = cleanup_prim_path(self, obj["subscription"])
        if subKey not in self._dataStore._subscription_cost.keys():
            self._dataStore._subscription_cost[subKey] = float(obj["lmcost"])
        else:
            self._dataStore._subscription_cost[subKey] = float(self._dataStore._subscription_cost[subKey]) + float(obj["lmcost"])
        
        #Cost per Location
        locKey = cleanup_prim_path(self, obj["location"])
        if locKey not in self._dataStore._location_cost.keys():
            self._dataStore._location_cost[locKey] = float(obj["lmcost"])
        else:
            self._dataStore._location_cost[locKey] = float(self._dataStore._location_cost[locKey]) + float(obj["lmcost"])
        
        #Cost per Type
        typeKey = cleanup_prim_path(self, obj["type"])
        if typeKey not in self._dataStore._type_cost.keys():
            self._dataStore._type_cost[typeKey] = float(obj["lmcost"])
        else:
            self._dataStore._type_cost[typeKey] = float(self._dataStore._type_cost[typeKey]) + float(obj["lmcost"])

        #Cost per Group
        grpKey = cleanup_prim_path(self, obj["group"])
        if grpKey not in self._dataStore._group_cost.keys():
            self._dataStore._group_cost[grpKey] = float(obj["lmcost"])
        else:
            self._dataStore._group_cost[grpKey] = float(self._dataStore._group_cost[grpKey]) + float(obj["lmcost"])

    #Async Context
    async def AggregateCountsAsync(self, obj):

        ### AGGREGATE COUNTS
        #Count per Sub
        subKey = cleanup_prim_path(self, obj["subscription"])
        if subKey not in self._dataStore._subscription_count.keys():
            self._dataStore._subscription_count[subKey] = 1
        else:
            self._dataStore._subscription_count[subKey] = self._dataStore._subscription_count[subKey] + 1
        
        #Count per Location
        locKey = cleanup_prim_path(self, obj["location"])
        if locKey not in self._dataStore._location_count.keys():
            self._dataStore._location_count[locKey] = 1
        else:
            self._dataStore._location_count[locKey] = self._dataStore._location_count[locKey] + 1

        #Count per Type
        typeKey = cleanup_prim_path(self, obj["type"])
        if typeKey not in self._dataStore._type_count.keys():
            self._dataStore._type_count[typeKey] = 1
        else:
            self._dataStore._type_count[typeKey] = self._dataStore._type_count[typeKey] + 1

        #Count per Group
        grpKey = cleanup_prim_path(self, obj["group"])
        if grpKey not in self._dataStore._group_count.keys():
            self._dataStore._group_count[grpKey] = 1
        else:
            self._dataStore._group_count[grpKey] = self._dataStore._group_count[grpKey] + 1

    #Given a resource, Map it to all the groups it belongs to.
    async def MapResourcesToGroupsAsync(self, obj):
        
        #Get the mapped shape and figure out the prim path for the map
        # Set a default
        shape_to_render = "omniverse://localhost/Resources/3dIcons/scene.usd"

        try:
            resName = obj["name"]
            typeName = cleanup_prim_path(self,  obj["type"])
            shape_to_render = shape_usda_name[typeName]   
        except:
            carb.log_info("No matching prim found - " + typeName)                                  

        # SUBSCRIPTION MAP
        await self.map_objects(resName, typeName, "/Subs" ,shape_to_render, self._dataStore._map_subscription, obj, "subscription")

        # GROUP MAP
        await self.map_objects(resName, typeName, "/RGrps", shape_to_render, self._dataStore._map_group, obj, "group")

        # TYPE MAP
        await self.map_objects(resName, typeName, "/Types", shape_to_render, self._dataStore._map_type, obj, "type")

        # LOCATION MAP
        await self.map_objects(resName, typeName, "/Locs", shape_to_render, self._dataStore._map_location, obj, "location")

        #TODO TAGMAP
        #self.map_objects(typeName, "/Tag", shape_to_render, self._dataStore._tag_map, obj, "tag")


    #Maps objects to create to each aggregate
    async def map_objects(self, resName, typeName, root, shape, map, obj, field:str):
        
        cleaned_group_name = cleanup_prim_path(self, Name=obj[field])
        carb.log_info(cleaned_group_name)
        
        map_obj = {"name": resName, "type":typeName, "shape":shape}

        if cleaned_group_name not in map.keys():
            #new map!
            map[cleaned_group_name] = [map_obj]
        else:
            #get the map for this group, add this item
            mapObj = map[cleaned_group_name]
            mapObj.append(map_obj)


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

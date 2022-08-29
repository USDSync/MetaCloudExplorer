# This class is intended to manage the stage

# Using the requested view and the loaded dataset, we need to translate data into Prims

# There are 2 variables here.  The prims you want to see, and the way you want to see them

# the data gives resource counts by subscription, group, or location.
# it also contains resource group data and data about all the raw resources
# we need to put the resource prims in groups on the stage, floating islands ?

# I want to try and build a floating island for each resource group, IE a plane that prims can rest on.
# The islands will be 2d planes in 3d space, big enough to accomidate the resources in said group.

# the more resources the bigger the island.
#we can then postion the islands in novel ways for exploration
# Model related
# Python built-in
from textwrap import fill
import time
from cgitb import text
import os.path
from unicodedata import name
import carb
import locale 
from pathlib import Path
# external python lib
import csv
import itertools
# USD imports
from pxr import Gf, UsdGeom, UsdLux, Usd, Sdf
# omniverse
import omni.client
import omni.kit.app
import omni.ui as ui
import omni.usd
import omni.kit.commands
import shutil
import os
import asyncio
import omni.kit.notification_manager as nm

from  .prim_utils import create_plane
from  .prim_utils import cleanup_prim_path
from  .prim_utils import get_font_size_from_length

from .packer import Node, Block, Packer

from omni.kit.window.file_importer import get_file_importer
from omni.ui import color as cl

#import utilities
from .azure_resource_map import shape_usda_name
from .data_manager import DataManager
from .data_store import DataStore
from .scatter_complex import distributePlanes

#Import View Models
from .group_aad import AADGrpView
from .group_group import ResGrpView
from .group_sub import SubGrpView
from .group_location import LocGrpView
from .group_type import TypeGrpView
from .group_tag import TagGrpView


CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.joinpath("temp")

# The Stage Manager is responsible for drawing the stage based on the ViewType
# It will start from scratch and create the Ground plane and groups on the plane
# It will render the resources in each group on individual planes
class StageManager():
    def __init__(self):

        self._dataManager = DataManager.instance() # Get A Singleton instance
        self._dataStore = DataStore.instance() # Get A Singleton instance
       
        self.stage_unit_per_meter = 1

        #Get Composition Options from UI
        try:
            self._scale = self._dataStore._scale_model
        except:
            self._scale=1.0
        try:
            self._use_packing_algo = self._dataStore._use_packing_algo
        except:
            self._use_packing_algo = False
        try:
            self._use_symmetric_planes = self._dataStore._use_symmetric_planes
        except:
            self._use_symmetric_planes = False
        try:
            self._last_view_type =  self._dataStore._last_view_type
        except:
            self._last_view_type = "ByGroup"

        if self._last_view_type is None:
            self._last_view_type = "ByGroup"

        self._upAxis="Z"
        self._shapeUpAxis="Z"
        self.ActiveView = self.SetActiveView(self._last_view_type)

    def SetActiveView(self, viewType:str):

                #Set a subclass to handle the View Creation    
        if viewType == "ByGroup":
            #asyncio.ensure_future(self.sendNotify("Group View loaded...", nm.NotificationStatus.INFO))   
            view = ResGrpView(viewPath="RGrps", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)
            
        if viewType == "ByLocation":    
            #asyncio.ensure_future(self.sendNotify("Location View loaded...", nm.NotificationStatus.INFO))
            view = LocGrpView(viewPath="Locs", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)
            
        if viewType == "ByType":    
            #asyncio.ensure_future(self.sendNotify("Type View loaded...", nm.NotificationStatus.INFO))
            view = TypeGrpView(viewPath="Types", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)
            
        if viewType == "BySub":    
            #asyncio.ensure_future(self.sendNotify("Subscription View loaded..", nm.NotificationStatus.INFO))
            view = SubGrpView(viewPath="Subs", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)
            
        if viewType == "ByTag":    
            #asyncio.ensure_future(self.sendNotify("Tag View loaded..", nm.NotificationStatus.INFO))
            view = TagGrpView(viewPath="Tags", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)

        return view

                
    #Invoked from UI - Show the Stages based on the View.
    def ShowStage(self, viewType:str):

        #Reset view data
        self._dataStore._lcl_sizes = [] 
        self._dataStore._lcl_groups = [] 
        self._dataStore._lcl_resources = [] 

        self.ActiveView = self.SetActiveView(viewType)

        #populate the stage
        self.ActiveView.initializeStage(self.stage_unit_per_meter) #Base Method
        self.ActiveView.calcGroupPlaneSizes() #Abstract Method
        self.ActiveView.calulateCosts() #Abstract Method

        transforms = self.getTransforms() #Cooredinates for the group planes

        #sort the groups to add largest first
        self._dataStore._lcl_groups.sort(key=lambda element: element['size'], reverse=True)
        self._dataStore._lcl_sizes.sort(reverse=True)

        #Create the groups in an async loop
        if (len(self._dataStore._lcl_groups)) >0 :
            asyncio.ensure_future(self.ActiveView.CreateGroups(transforms=transforms))
        

    def LoadResources(self, viewType:str):
        
        self.ActiveView = self.SetActiveView(viewType)

        self.ActiveView.initializeStage(self.stage_unit_per_meter) #Base Method
        self.ActiveView.calcGroupPlaneSizes() #Abstract Method
        self.ActiveView.calulateCosts() #Abstract Method

        #View is already set, show resources for specific or all paths
        if self.ActiveView is None:
            self.ActiveView = self.SetActiveView(self._last_view_type)

        self.ActiveView.loadResources() #Abstract Method           

    #Gets the x,y,z coordinates to place the grouping planes
    def getTransforms(self):
        if (self._dataStore._use_packing_algo):

            #Use Packer Algorithm to determine positioning
            transforms = []
            blocks = []
            sorted_sizes = sorted(self._dataStore._lcl_sizes, reverse=True)
            for size in sorted_sizes:
                sz = (size*2) #double the size end to end
                blocks.append(Block((sz,sz)))

            pack = Packer()
            pack.fit(blocks)

            for block in blocks:
                if block.fit:
                    fitX = block.fit.location[0]
                    fitY = block.fit.location[1]
                    fitZ = 0
                    transforms.append(Gf.Vec3f(fitX, fitY ,fitZ))
                    #print("size: {} loc: {},{}".format(str(block.size[0]), str(block.fit.location[0]), str(block.fit.location[1])))
                else:
                    print("not fit: {}".format(block.size[0]))
            
            return transforms

        else:
            #Use the scatter distribution method
            maxDims = (self._dataStore._options_count_models[0].as_float * self._dataStore._options_count_models[1].as_float * self._dataStore._options_count_models[2].as_float)
            grpCnt = len(self._dataStore._lcl_groups)
            if grpCnt > maxDims:
                asyncio.ensure_future(self.sendNotify("Not enough dimensions for ..." + str(grpCnt) + "res groups, Max Dims: " + str(maxDims), nm.NotificationStatus.WARNING))   
                return

            #Use Customized Scatter algorithm get coordinates for varying sized planes
            transforms = distributePlanes(
                UpAxis=self._upAxis,
                count=[m.as_int for m in self._dataStore._options_count_models],
                distance=[m.as_float for m in self._dataStore._options_dist_models],
                sizes=self._dataStore._lcl_sizes,
                randomization=[m.as_float for m in self._dataStore._options_random_models],
                seed=0,
                scaleFactor=self._dataStore._composition_scale_model.as_float)

            return transforms


    def Select_Planes(self):

        if self.ActiveView is None:
            self.ActiveView = self.SetActiveView(self._last_view_type)
            self.ActiveView.selectGroupPrims()
        else:
            self.ActiveView.selectGroupPrims()

    def get_size(self, element):
        return element['size']      

    def ShowCosts(self):
        if self.ActiveView is None:
            self.ActiveView = self.SetActiveView(self._last_view_type)
            self.ActiveView.showHideCosts()
        else:
            self.ActiveView.showHideCosts()



    # Set Color
    # next_shape.GetDisplayColorAttr().Set(
    #     category_colors[int(cluster) % self.max_num_clusters])           



    def clicked_ok(self):
        pass


    async def sendNotify(self, message:str, status:nm.NotificationStatus):
        
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
        
        #Let the Ui breathe ;)
        for x in range(5):
            await omni.kit.app.get_app().next_update_async()    



    #log the vectors
    def log_transforms(self, vectors):
        for v in vectors:
            logdata = str(vectors[v][0]) + "," + str(vectors[v][1]) + "," + str(vectors[v][2])
            print(logdata)
    

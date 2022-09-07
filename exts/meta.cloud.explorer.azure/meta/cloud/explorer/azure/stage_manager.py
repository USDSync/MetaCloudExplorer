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
from .math_utils import calcPlaneSizeForGroup

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
        #self._dataManager.add_model_changed_callback(self.model_changed)
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
            view = ResGrpView(viewPath="RGrps", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)
            
        if viewType == "ByLocation":    
            view = LocGrpView(viewPath="Locs", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)
            
        if viewType == "ByType":    
            view = TypeGrpView(viewPath="Types", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)
            
        if viewType == "BySub":    
            view = SubGrpView(viewPath="Subs", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)
            
        if viewType == "ByTag":    
            view = TagGrpView(viewPath="Tags", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, 
                symPlanes=self._dataStore._symmetric_planes_model.as_bool, binPack=self._use_packing_algo)

        return view

    # def model_changed():
    #     pass
                
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

        self.transforms = self.getTransforms() #Cooredinates for the group planes

        #sort the groups to add largest first
        self._dataStore._lcl_groups.sort(key=lambda element: element['size'], reverse=True)
        self._dataStore._lcl_sizes.sort(reverse=True)

        #Sanity check!!
        #Guard, check settings
        if self.checkSettingsBeforeLoad() == True:
            self.approved_settings()
        else:
            pass #The user needs to OK or Cancel the Notification

    #Load the resources by group
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

            if len(self._dataStore._lcl_sizes) >0:
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
                self.sendNotify("Not enough dimensions for ..." + str(grpCnt) + "res groups, Max Dims: " + str(maxDims), nm.NotificationStatus.WARNING)
                return

            if grpCnt >0:
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

    async def AddLightsToStage(self):

        stage = omni.usd.get_context().get_stage()

        try:
            omni.kit.commands.execute('DeletePrimsCommand',
                paths=['/Environment/sky'])
        except:
            pass #ignore this

        await omni.kit.app.get_app().next_update_async()

        omni.kit.commands.execute('CreateDynamicSkyCommand',
            sky_url='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Skies/Dynamic/NightSky.usd',
            sky_path='/Environment/sky')

        omni.kit.commands.execute('ChangeProperty',
            prop_path=Sdf.Path('/Environment/sky.xformOp:rotateZYX'),
            value=Gf.Vec3f(90.0, 0.0, 0.0),
            prev=Gf.Vec3f(0.0, 0.0, 0.0))

    #Sanity check on settings
    def checkSettingsBeforeLoad(self):

        grpCnt = len(self._dataStore._lcl_groups)
        largestPlane = self._dataStore._lcl_sizes[0]
        smallestGroup = 0
        largestGroup = 0
        xDistance = self._dataStore._options_dist_models[0].as_float
        yDistance = self._dataStore._options_dist_models[1].as_float
        xCount = self._dataStore._options_count_models[0].as_int
        yCount = self._dataStore._options_count_models[1].as_int
        
        #Assume there isn't gonna be a problem
        isSane = True
        sanityDesc = ""

        #is Use symmetric planes checked, but not bin packer?
        if self._dataStore._use_symmetric_planes ==True and self._use_packing_algo == False: 

            #Recalc the sizes before symettric planes applied
            lcl_sizes = []
            _lcl_groups = []
            gpz = self._dataStore._group_count.copy()

            for grp in gpz:
                size = calcPlaneSizeForGroup(
                        scaleFactor=self._scale, 
                        resourceCount=self._dataStore._group_count.get(grp)
                    )
                #record group size extents
                if size < smallestGroup:
                    smallestGroup = size
                elif size > largestGroup:
                    largestGroup = size

                #mixed plane sizes
                lcl_sizes.append(size)
                grp = cleanup_prim_path(self, grp)
                _lcl_groups.append({ "group":grp, "size":size })

            #Sanity checks
            if grpCnt > 1 and xCount > 1 and xDistance < largestPlane:
                sanityDesc = "Groups will overlap on X Axis, suggest you increase X Distance [" + str(xDistance) + "] to at least [" + str(largestPlane) + "] to not cause planes to overlap."
                isSane = False
            
            if grpCnt > 1 and yCount > 1 and yDistance < largestPlane:
                sanityDesc = sanityDesc + " Groups will overlap on Y Axis, suggest you increase Y Distance [" + str(yDistance) + "] to at least [" + str(largestPlane) + "] to not cause planes to overlap."
                isSane = False
            
            #Additional Sanity Checks here
            
            if isSane == False:
                #let the user know.
                
                self.sendbadSettingsNotify("MCE: OVERLAP WARNING: " + sanityDesc, nm.NotificationStatus.WARNING)            
                return False
            else:
                return True
        else:
            return True


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

        asyncio.ensure_future(self.ActiveView.showHideCosts())


    # Set Color
    # next_shape.GetDisplayColorAttr().Set(
    #     category_colors[int(cluster) % self.max_num_clusters])           

    def approved_settings(self):

        #Create the groups in an async loop
        grpCnt = len(self._dataStore._lcl_groups)
        if (grpCnt) >0 :
            asyncio.ensure_future(self.AddLightsToStage())
            asyncio.ensure_future(self.ActiveView.CreateGroups(self.transforms))
        
        self.ActiveView.loadResources() #Abstract Method             
        self.sendNotify("Stage loading complete: " + str(grpCnt) + " groups loaded.", nm.NotificationStatus.INFO)


    def cancel_bad_settings(self):
        self.sendNotify("Rendering cancelled.", nm.NotificationStatus.INFO)
    

    
    def clicked_ok():
        carb.log_info("User clicked ok")



    def sendbadSettingsNotify(self, message:str, status:nm.NotificationStatus):
        
        # https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.kit.notification_manager/docs/index.html?highlight=omni%20kit%20notification_manager#

        import omni.kit.notification_manager as nm
        proceed_button = nm.NotificationButtonInfo("I understand, Proceed.", on_complete=self.approved_settings) #on_complete=self.approved_settings(transforms))
        cancel_button = nm.NotificationButtonInfo("Cancel", on_complete=self.cancel_bad_settings)

        nm.post_notification(
            message,
            hide_after_timeout=False,
            duration=5,
            status=status,
            button_infos=[proceed_button, cancel_button]
        )        


    def sendNotify(self, message:str, status:nm.NotificationStatus):
        
        # https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.kit.notification_manager/docs/index.html?highlight=omni%20kit%20notification_manager#

        import omni.kit.notification_manager as nm
        ok_button = nm.NotificationButtonInfo("OK", on_complete=self.clicked_ok)

        nm.post_notification(
            message,
            hide_after_timeout=True,
            duration=5,
            status=status,
            button_infos=[]
        )        
        


    #log the vectors
    def log_transforms(self, vectors):
        for v in vectors:
            logdata = str(vectors[v][0]) + "," + str(vectors[v][1]) + "," + str(vectors[v][2])
            print(logdata)
    

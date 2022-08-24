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
from omni.ui import scene as sc
from omni.ui import color as cl

from .azure_resource_map import shape_usda_name
from .math_utils import calcPlaneSizeForGroup
from .data_manager import DataManager
from .data_store import DataStore
from .scatter_complex import distributePlanes
from .scatter_on_planes import scatterOnFixedPlane
from .omni_utils import create_prims, create_shaders
from .group_base import AADGrpView, ResGrpView, SubGrpView, LocGrpView, TypeGrpView, TypeTagView

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.joinpath("temp")

# The Stage Manager is responsible for drawing the stage based on the ViewType
# It will start from scratch and create the Ground plane and groups on the plane
# It will render the resources in each group on individual planes
class StageManager():
    def __init__(self):
        #pass

        #moved to abstract base GroupBase
        self._dataManager = DataManager.instance() # Get A Singleton instance
        self._dataStore = DataStore.instance() # Get A Singleton instance
       
        # # # stage_unit defines the number of unit per meter
        self.stage_unit_per_meter = 1

               #Get Composition Options from UI
        try:
            self._scale = self._dataStore._composition_scale_model.as_float
        except:
            self._scale=1.0
        try:
            self._upAxis = self._dataStore._primary_axis_model.get_current_item().as_string
        except:
            self._upAxis="Z"
        try:
            self._shapeUpAxis = self._dataStore._shape_up_axis_model.get_current_item().as_string
        except:
            self._shapeUpAxis="Z"
        try:
            self._use_symmetric_planes = self._dataStore._use_symmetric_planes().as_bool
        except:
            self._use_symmetric_planes = False
        try:
            self._last_view_type =  self._dataStore._last_view_type().as_string
        except:
            self._last_view_type = "ByGroup"
     
        #Set a subclass to handle the View Creation    
        if self._dataStore._last_view_type == "ByGroup":
            #asyncio.ensure_future(self.sendNotify("Group View loaded...", nm.NotificationStatus.INFO))   
            self.ActiveView = ResGrpView(viewPath="/RGrp", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)
            
        if self._dataStore._last_view_type == "ByLocation":    
            #asyncio.ensure_future(self.sendNotify("Location View loaded...", nm.NotificationStatus.INFO))
            self.ActiveView = LocGrpView(viewPath="/Loc", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)
            
        if self._dataStore._last_view_type == "ByType":    
            #asyncio.ensure_future(self.sendNotify("Type View loaded...", nm.NotificationStatus.INFO))
            self.ActiveView = TypeGrpView(viewPath="/Type", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)
            
        if self._dataStore._last_view_type == "BySub":    
            #asyncio.ensure_future(self.sendNotify("Subscription View loaded..", nm.NotificationStatus.INFO))
            self.ActiveView = SubGrpView(viewPath="/Subs", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)
            
        if self._dataStore._last_view_type == "ByTag":    
            #asyncio.ensure_future(self.sendNotify("Tag View loaded..", nm.NotificationStatus.INFO))
            self.ActiveView = TypeTagView(viewPath="/Tag", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)

                
    #Invoked from UI - Show the Stages based on the View.
    def ShowStage(self, viewType:str):

        #Set a subclass to handle the View Creation    
        if viewType == "ByGroup":
            #asyncio.ensure_future(self.sendNotify("Group View loaded...", nm.NotificationStatus.INFO))   
            self.ActiveView = ResGrpView(viewPath="/RGrp", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)
            
        if viewType == "ByLocation":    
            #asyncio.ensure_future(self.sendNotify("Location View loaded...", nm.NotificationStatus.INFO))
            self.ActiveView = LocGrpView(viewPath="/Loc", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)
            
        if viewType == "ByType":    
            #asyncio.ensure_future(self.sendNotify("Type View loaded...", nm.NotificationStatus.INFO))
            self.ActiveView = TypeGrpView(viewPath="/Type", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)
            
        if viewType == "BySub":    
            #asyncio.ensure_future(self.sendNotify("Subscription View loaded..", nm.NotificationStatus.INFO))
            self.ActiveView = SubGrpView(viewPath="/Subs", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)
            
        if viewType == "ByTag":    
            #asyncio.ensure_future(self.sendNotify("Tag View loaded..", nm.NotificationStatus.INFO))
            self.ActiveView = TypeTagView(viewPath="/Tag", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes)

        #Are the options compatible with the data?
        maxDims = (self._dataStore._options_count_models[0].as_float * self._dataStore._options_count_models[1].as_float * self._dataStore._options_count_models[2].as_float)
        grpCnt = len(self._dataStore._groups)
        if grpCnt > maxDims:
            asyncio.ensure_future(self.sendNotify("Not enough dimensions for ..." + str(grpCnt) + "res groups, Max Dims: " + str(maxDims), nm.NotificationStatus.WARNING))   
            return

        #populate the stage
        self.ActiveView.initializeStage(self.stage_unit_per_meter) #Base Method
        self.ActiveView.calcPlaneGroupSettings() #Abstract Method
        self.ActiveView.calulateCosts() #Abstract Method

        #sortd = dict(sorted(self.ActiveView._groups["group"]["size"], key=lambda item: item[1]))

        #Use Packer Algorythm to determine positioning
        transforms =[]
        blocks = []
        sorted_sizes = sorted(self.ActiveView._sizes, reverse=True)
        for size in sorted_sizes:
            sz = (size*2) #double the size end to end
            blocks.append(Block((sz,sz)))
            #blocks.append(Block(sz,sz))

        pack = Packer()
        pack.fit(blocks)

        for block in blocks:
            if block.fit:
                transforms.append(Gf.Vec3f(block.fit.location[0], block.fit.location[1] ,0))
                print("size: {} loc: {}".format(block.size, block.fit.location))
            else:
                print("not fit: {}".format(block.size))


        #Use Customized Scatter algorythm get coordinates for varying sized planes
        # transforms = distributePlanes(
        #     UpAxis=self._upAxis,
        #     count=[m.as_int for m in self._dataStore._options_count_models],
        #     distance=[m.as_float for m in self._dataStore._options_dist_models],
        #     sizes=self.ActiveView._sizes,
        #     randomization=[m.as_float for m in self._dataStore._options_random_models],
        #     seed=0,
        #     scaleFactor=self._dataStore._composition_scale_model.as_float
        # )

        self.ActiveView._groups.sort(key=lambda element: element['size'], reverse=True)
        self.ActiveView._sizes.sort(reverse=True)

        #Create the groups in an async loop
        if (len(self.ActiveView._groups)) >0 :

            #TODO Async
            self.ActiveView.CreateGroups(
                basePath=self.ActiveView.view_path,
                upAxis=self._upAxis,
                groups=self.ActiveView._groups,
                transforms=transforms,
                sizes=self.ActiveView._sizes
            )

    def get_size(self, element):
        return element['size']

    def LoadResources(self):
        
        #Get Stage
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        paths = []

        #Get Selected paths, if any?
        selected_prims = usd_context.get_selection().get_selected_prim_paths()

        if selected_prims is not None:           
            # Loop through all selected prims, remove the Meshs from path
            for s in selected_prims:
                path = str(s).replace("/CollisionMesh" "")
                paths.append(path)                       
        else:
            pass
            #Load them all
            
        #View is already set, show resources for specific or all paths
        self.ActiveView.LoadResources(paths) #Base Method


    #Draw a GroundPlane for the Resources to sit on.
    def DrawStage(self, Path:str, Name: str, Size: int, Location: Gf.Vec3f, Color:Gf.Vec3d):      
        create_plane(self,Path, Name, Size, Location, Color)


    def Select_Planes(self):
        self.ActiveView.selectGroupPrims()
        #change the shaders to non-cost


    def ShowCosts(self):
        self.ActiveView.show_hide_costs()



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
    

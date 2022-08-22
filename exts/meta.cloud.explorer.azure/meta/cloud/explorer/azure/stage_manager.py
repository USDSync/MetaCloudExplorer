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
from .pillow_text import create_image_with_text
from .pillow_text import draw_text_on_image_at_position

from  .prim_utils import create_plane
from  .prim_utils import cleanup_prim_path
from  .prim_utils import get_font_size_from_length


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
        #Subclasses for the different aggragation types
        # self.AADView = AADGrpView()
        # self.ResView = ResGrpView()
        # self.SubView = SubGrpView()
        # self.LocView = LocGrpView()
        # self.TypeView = TypeGrpView()
        # self.TagView = TypeTagView()

        # #Default View is by resource group
        # self.ActiveView = self.ResView
   
        #moved to abstract base GroupBase
        self._dataManager = DataManager.instance() # Get A Singleton instance
        self._dataStore = DataStore.instance() # Get A Singleton instance

        # # #Track the Groups and Resources so we can selectively add/remove them
        # self._group_prims = {}
        # self._resource_prims = {}

        # #root prim paths
        # self.root_path = Sdf.Path('/World')
        # self.view_path = ""
        # self.aad_layer_root_path = Sdf.Path(self.root_path.AppendPath('AAD'))
        # self.sub_layer_root_path = Sdf.Path(self.root_path.AppendPath('Subs'))
        # self.res_layer_root_path = Sdf.Path(self.root_path.AppendPath('RGrp'))
        # self.loc_layer_root_path = Sdf.Path(self.root_path.AppendPath('Loc'))
        # self.type_layer_root_path = Sdf.Path(self.root_path.AppendPath('Type'))
        # self.cost_layer_root_path = Sdf.Path(self.root_path.AppendPath('Tag'))
        
        # # # stage_unit defines the number of unit per meter
        self.stage_unit_per_meter = 1
               
        # # # limit the number of rows read
        # self.max_elements = 5000
        # self.base_prim_size = 75
        
        # self.x_threshold = 5000
        # self.y_threshold = 5000
        # self.z_threshold = 5000
        # self.x_extent = 0
        # self.y_extent = 0
        # self.z_extent = 0
    
    #Intialize the Stage
    # def InitStage(self):
    #     self._stage = omni.usd.get_context().get_stage()
    #     root_prim = self._stage.GetPrimAtPath(self.root_path)
        
    #     #  set the up axis
    #     UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.z)

    #     #  set the unit of the world
    #     UsdGeom.SetStageMetersPerUnit(self._stage, self.stage_unit_per_meter)
    #     self._stage.SetDefaultPrim(root_prim)

    #     # add a light
    #     light_prim_path = self.root_path.AppendPath('DomeLight')
    #     light_prim = UsdLux.DistantLight.Define(self._stage, str(light_prim_path))
    #     light_prim.CreateAngleAttr(0.53)
    #     light_prim.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 0.745))
    #     light_prim.CreateIntensityAttr(500.0)

    #Invoked from UI - Show the Stages based on the View.
    def ShowStage(self, viewType: str):
        
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
            self._show_cost_data =  self._dataStore._show_cost_data().as_bool
        except:
            self._show_cost_data = False
     
        #Set a subclass to handle the View Creation    
        if viewType == "ByGroup":
            asyncio.ensure_future(self.sendNotify("Group View loaded...", nm.NotificationStatus.INFO))   
            self.ActiveView = ResGrpView(viewPath="/RGrp", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes, showCosts=self._show_cost_data)
            
        if viewType == "ByLocation":    
            asyncio.ensure_future(self.sendNotify("Location View loaded...", nm.NotificationStatus.INFO))
            self.ActiveView = LocGrpView(viewPath="/Loc", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes, showCosts=self._show_cost_data)
            
        if viewType == "ByType":    
            asyncio.ensure_future(self.sendNotify("Type View loaded...", nm.NotificationStatus.INFO))
            self.ActiveView = TypeGrpView(viewPath="/Type", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes, showCosts=self._show_cost_data)
            
        if viewType == "BySub":    
            asyncio.ensure_future(self.sendNotify("Subscription View loaded..", nm.NotificationStatus.INFO))
            self.ActiveView = SubGrpView(viewPath="/Subs", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes, showCosts=self._show_cost_data)
            
        if viewType == "ByTag":    
            asyncio.ensure_future(self.sendNotify("Tag View loaded..", nm.NotificationStatus.INFO))
            self.ActiveView = TypeTagView(viewPath="/Tag", scale=self._scale, upAxis=self._upAxis, shapeUpAxis=self._shapeUpAxis, symPlanes=self._use_symmetric_planes, showCosts=self._show_cost_data)

        #populate the stage
        self.ActiveView.initializeStage(self.stage_unit_per_meter) #Base Method
        self.ActiveView.calcPlaneGroupSettings() #Abstract Method
        self.ActiveView.calulateCosts() #Abstract Method

        #Use Customized Scatter algorythm get coordinates for varying sized planes
        transforms = distributePlanes(
            UpAxis=self._upAxis,
            count=[m.as_int for m in self._dataStore._options_count_models],
            distance=[m.as_float for m in self._dataStore._options_dist_models],
            sizes=self.ActiveView._sizes,
            randomization=[m.as_float for m in self._dataStore._options_random_models],
            seed=0,
            scaleFactor=self._dataStore._composition_scale_model.as_float
        )

        #Create the groups in an async loop
        if (len(self.ActiveView._groups)) >0 :

            asyncio.ensure_future(self.ActiveView.CreateGroups(
                basePath=self.ActiveView.view_path,
                upAxis=self._upAxis,
                groups=self.ActiveView._groups,
                sizes=self.ActiveView._sizes,
                transforms=transforms
            ))


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

        #View is already set, show resources for specific or all paths
        self.ActiveView.LoadResources(paths) #Base Method


    #Draw a GroundPlane for the Resources to sit on.
    def DrawStage(self, Path:str, Name: str, Size: int, Location: Gf.Vec3f, Color:Gf.Vec3d):      
        create_plane(self,Path, Name, Size, Location, Color)


    def ShowCosts(self):
        pass
        #change the shaders to non-cost


    def HideCosts(self):
        pass
        #change the shaders to cost shaders based on score







    #Load Stage Mesh Images to Shaders
    # def AddPlaneLabelShaders(self, viewType: str, sizes, groups):

        
    #         if viewType == "ByLocation":
    #             #Get the cost for this location
    #             if self._dataStore._show_costs_model.as_bool:
    #                 locale.setlocale(locale.LC_ALL, '')
    #                 try:
    #                     cost = str(locale.currency(self._dataStore._location_cost[g]))
    #                 except:
    #                     cost = "" # blank not 0, blank means dont show it at all     
    #             else:
    #                 cost = ""

    #         if viewType == "ByType":
    #             #Get the cost for this group
    #             if self._dataStore._show_costs_model.as_bool:
    #                 locale.setlocale(locale.LC_ALL, '')
    #                 try:
    #                     cost = str(locale.currency(self._dataStore._type_cost[g]))
    #                 except:
    #                     cost = "" # blank not 0, blank means dont show it at all     
    #             else:
    #                 cost = ""


    #         if viewType == "BySub":
    #             #Get the cost for this sub
    #             if self._dataStore._show_costs_model.as_bool:
    #                 locale.setlocale(locale.LC_ALL, '')
    #                 try:
    #                     cost = str(locale.currency(self._dataStore._subscription_cost[g]))
    #                 except:
    #                     cost = "" # blank not 0, blank means dont show it at all     
    #             else:
    #                 cost = ""


    #         if viewType == "ByTag":
    #             #Get the cost for this tag
    #             if self._dataStore._show_costs_model.as_bool:
    #                 locale.setlocale(locale.LC_ALL, '')
    #                 try:
    #                     cost = str(locale.currency(self._dataStore._cost[g]))
    #                 except:
    #                     cost = "" # blank not 0, blank means dont show it at all     
    #             else:
    #                 cost = ""
        
            
    #         #MAKE A TEMP COPY OF THE BASE IMAGE TEXTURE SO THAT WE CAN DRAW TEXT ON THE COPY
            
    #         #src_file = DATA_PATH.joinpath("tron_grid_test.png")
    #         src_file = self._dataStore._bg_file_path 
    #         output_file = DATA_PATH.joinpath(g + ".png")

    #         shutil.copyfile(src_file, output_file)

    #         font_size = get_font_size_from_length(len(g))

    #         draw_text_on_image_at_position(
    #             input_image_path=output_file,
    #             output_image_path=output_file, 
    #             textToDraw=g, 
    #             costToDraw=cost,
    #             x=180, y=1875, fillColor="Yellow", fontSize=font_size )

    #         #Get Stage
    #         stage = omni.usd.get_context().get_stage()

    #         #Find the /Looks root
    #         curr_prim = stage.GetPrimAtPath("/")
    #         looks_path = ""
    #         for prim in Usd.PrimRange(curr_prim):

    #             if prim.GetPath() == "/Looks":
    #                 looks_path = "/Looks"
    #                 continue
    #             elif prim.GetPath() == "/World/Looks":
    #                 looks_path = "/World/Looks"
    #                 continue

    #         #print("Looks root is: " +looks_path)
    #         #Get the Shader and set the image property
    #         if (looks_path == ""):
    #             looks_path = "/Looks"

    #         shader_path = Sdf.Path(looks_path)
    #         shader_path = Sdf.Path(shader_path.AppendPath(g))
    #         shader_path = Sdf.Path(shader_path.AppendPath("Shader"))

    #         #select the shader
    #         selection = omni.usd.get_context().get_selection()
    #         selection.set_selected_prim_paths([str(shader_path)], False)         

    #         #Get the Shader
    #         shader_prim = stage.GetPrimAtPath(str(shader_path))

    #         # print("Shader Attributes:-----" + str(shader_path))
    #         # print(shader_prim.GetAttributes())

    #         try:
    #             shader_prim.CreateAttribute("inputs:diffuse_texture", Sdf.ValueTypeNames.Asset)
                                    
    #             omni.kit.commands.execute('ChangeProperty',
    #                 prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
    #                 value=str(output_file), prev=str(output_file))
    #         except:
    #             #Do it again!
    #             omni.kit.commands.execute('ChangeProperty',
    #             prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
    #             value=str(output_file),prev=str(output_file))


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


    def SelectPlanes(self, viewType:str):

        paths = []

        omni.kit.commands.execute('SelectPrims',
            old_selected_paths=['/World'],
            new_selected_paths=['/World/RGrp'],
            expand_in_stage=True)




    #log the vectors
    def log_transforms(self, vectors):
        for v in vectors:
            logdata = str(vectors[v][0]) + "," + str(vectors[v][1]) + "," + str(vectors[v][2])
            print(logdata)
    

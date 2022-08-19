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


CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.joinpath("temp")

# The Stage Manager is responsible for drawing the stage based on the ViewType
# It will start from scratch and create the Ground plane and groups on the plane
# It will render the resources in each group on individual planes
class StageManager():
    def __init__(self):

        self._dataManager = DataManager.instance() # Get A Singleton instance
        self._dataStore = DataStore.instance() # Get A Singleton instance

        #Track the Groups and Resources so we can selectively add/remove them
        self._group_prims = {}
        self._resource_prims = {}

        #root prim paths
        self.root_path = Sdf.Path('/World')
        self.view_path = ""
        self.aad_layer_root_path = Sdf.Path(self.root_path.AppendPath('AAD'))
        self.sub_layer_root_path = Sdf.Path(self.root_path.AppendPath('Subs'))
        self.res_layer_root_path = Sdf.Path(self.root_path.AppendPath('RGrp'))
        self.loc_layer_root_path = Sdf.Path(self.root_path.AppendPath('Loc'))
        self.type_layer_root_path = Sdf.Path(self.root_path.AppendPath('Type'))
        self.cost_layer_root_path = Sdf.Path(self.root_path.AppendPath('Cost'))
        
        # stage_unit defines the number of unit per meter
        self.stage_unit_per_meter = 1
               
        # limit the number of rows read
        self.max_elements = 5000
        self.base_prim_size = 75
        
        self.x_threshold = 5000
        self.y_threshold = 5000
        self.z_threshold = 5000
        self.x_extent = 0
        self.y_extent = 0
        self.z_extent = 0
    
    #Intialize the Stage
    def InitStage(self):
        self._stage = omni.usd.get_context().get_stage()
        root_prim = self._stage.GetPrimAtPath(self.root_path)
        
        #  set the up axis
        UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.z)

        #  set the unit of the world
        UsdGeom.SetStageMetersPerUnit(self._stage, self.stage_unit_per_meter)
        self._stage.SetDefaultPrim(root_prim)

        # add a light
        light_prim_path = self.root_path.AppendPath('DomeLight')
        light_prim = UsdLux.DistantLight.Define(self._stage, str(light_prim_path))
        light_prim.CreateAngleAttr(0.53)
        light_prim.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 0.745))
        light_prim.CreateIntensityAttr(500.0)

    #Invoked from UI - Show the Stages based on the View.
    def ShowStage(self, viewType: str):
        self.InitStage()

        #Calc Plane sizes based on items in group
        sizes = []
        groups = [] #literally, whatever the group is, not just Resource Groups

        try:
            scale = self._dataStore._composition_scale_model.as_float
            upAxis = self._dataStore._primary_axis_model.get_current_item().as_string
        except:
            scale=1.0
            upAxis="Z"

        #Cycle through the grouping aggregates creating planes for each of them
        if viewType == "ByGroup":

            if len(self._dataStore._group_count) == 0:
                self._dataManager.refresh_data()

            self.view_path = self.res_layer_root_path

            #temp group list to prep for planes, adds to main aggregate
            gpz = self._dataStore._group_count.copy()
            for grp in gpz:
                sizes.append(calcPlaneSizeForGroup(scaleFactor=scale, resourceCount=self._dataStore._group_count.get(grp)))
                grp = cleanup_prim_path(self, grp)
                groups.append(grp)

        if viewType == "ByLocation":

            if len(self._dataStore._location_count) == 0:
                self._dataManager.refresh_data()

            self.view_path = self.loc_layer_root_path

            #temp group list to prep for planes, adds to main aggregate
            gpz = self._dataStore._location_count.copy()
            for grp in gpz:
                sizes.append(calcPlaneSizeForGroup(scaleFactor=scale, resourceCount=self._dataStore._location_count.get(grp)))
                grp = cleanup_prim_path(self, grp)
                groups.append(grp)

        if viewType == "ByType":

            if len(self._dataStore._type_count) == 0:
                self._dataManager.refresh_data()

            self.view_path = self.type_layer_root_path

            #temp group list to prep for planes, adds to main aggregate
            gpz = self._dataStore._type_count.copy()
            for grp in gpz:
                sizes.append(calcPlaneSizeForGroup(scaleFactor=scale, resourceCount=self._dataStore._type_count.get(grp)))
                grp = cleanup_prim_path(self, grp)
                groups.append(grp)
        
        if viewType == "BySub":
            if len(self._dataStore._subscription_count) == 0:
                self._dataManager.refresh_data()

            self.view_path = self.type_layer_root_path

            #temp group list to prep for planes, adds to main aggregate
            gpz = self._dataStore._subscription_count.copy()
            for grp in gpz:
                sizes.append(calcPlaneSizeForGroup(scaleFactor=scale, resourceCount=self._dataStore._subscription_count.get(grp)))
                grp = cleanup_prim_path(self, grp)
                groups.append(grp)

        if viewType == "ByCost":
            pass

        #Use Customized Scatter algorythm to position varying sized planes
        transforms = distributePlanes(
            UpAxis=upAxis,
            count=[m.as_int for m in self._dataStore._options_count_models],
            distance=[m.as_float for m in self._dataStore._options_dist_models],
            sizes=sizes,
            randomization=[m.as_float for m in self._dataStore._options_random_models],
            seed=0,
            scaleFactor=self._dataStore._composition_scale_model.as_float
        )

        if (len(groups)) >0 :

            asyncio.ensure_future(self.CreateGroups(
                viewType=viewType,
                basePath=self.view_path,
                upAxis=upAxis,
                groups=groups,
                sizes=sizes,
                transforms=transforms
            ))


    #This takes a bit, best to do it async..
    async def CreateGroups(self, viewType:str, basePath:Sdf.Path, upAxis:str, groups:list, transforms, sizes):

        if (len(groups)) >0 :

            #Create new prims and then transform them
            create_prims(
                transforms=transforms,
                prim_names=groups,
                parent_path=str(basePath),
                up_axis=upAxis,
                plane_size=sizes
            )

            #Create shaders for each plane
            for g in groups:
                await create_shaders(base_path=basePath.AppendPath(g), prim_name=g)

            #Draw shaders on the stages
            self.AddPlaneLabelShaders(viewType, sizes, groups)

            #Change the View
            omni.kit.commands.execute('SelectPrims',
                old_selected_paths=['/World'],
                new_selected_paths=['/World/RGrp'],
                expand_in_stage=True)



    #Draw a GroundPlane for the Resources to sit on.
    def DrawStage(self, Path:str, Name: str, Size: int, Location: Gf.Vec3f, Color:Gf.Vec3d):      
        create_plane(self,Path, Name, Size, Location, Color)

    #Load Stage Mesh Images to Shaders
    def AddPlaneLabelShaders(self, viewType: str, sizes, groups):

        #Create shaders for each plane
        for g in groups:

            i=0

            if viewType == "ByGroup":
                #Get the cost for this group
                if self._dataStore._show_costs_model.as_bool:
                    locale.setlocale(locale.LC_ALL, '')
                    try:
                        cost = str(locale.currency(self._dataStore._group_cost[g]))
                    except:
                        cost = "" # blank not 0, blank means dont show it at all     
                else:
                    cost = ""

            if viewType == "ByLocation":
                #Get the cost for this location
                if self._dataStore._show_costs_model.as_bool:
                    locale.setlocale(locale.LC_ALL, '')
                    try:
                        cost = str(locale.currency(self._dataStore._location_cost[g]))
                    except:
                        cost = "" # blank not 0, blank means dont show it at all     
                else:
                    cost = ""

            if viewType == "ByType":
                #Get the cost for this group
                if self._dataStore._show_costs_model.as_bool:
                    locale.setlocale(locale.LC_ALL, '')
                    try:
                        cost = str(locale.currency(self._dataStore._type_cost[g]))
                    except:
                        cost = "" # blank not 0, blank means dont show it at all     
                else:
                    cost = ""


            if viewType == "BySub":
                #Get the cost for this sub
                if self._dataStore._show_costs_model.as_bool:
                    locale.setlocale(locale.LC_ALL, '')
                    try:
                        cost = str(locale.currency(self._dataStore._subscription_cost[g]))
                    except:
                        cost = "" # blank not 0, blank means dont show it at all     
                else:
                    cost = ""


            if viewType == "ByTag":
                #Get the cost for this tag
                if self._dataStore._show_costs_model.as_bool:
                    locale.setlocale(locale.LC_ALL, '')
                    try:
                        cost = str(locale.currency(self._dataStore._tag_cost[g]))
                    except:
                        cost = "" # blank not 0, blank means dont show it at all     
                else:
                    cost = ""
        
            
            #MAKE A TEMP COPY OF THE BASE IMAGE TEXTURE SO THAT WE CAN DRAW TEXT ON THE COPY
            
            #src_file = DATA_PATH.joinpath("tron_grid_test.png")
            src_file = self._dataStore._bg_file_path 
            output_file = DATA_PATH.joinpath(g + ".png")

            shutil.copyfile(src_file, output_file)

            font_size = get_font_size_from_length(len(g))

            draw_text_on_image_at_position(
                input_image_path=output_file,
                output_image_path=output_file, 
                textToDraw=g, 
                costToDraw=cost,
                x=180, y=1875, fillColor="Yellow", fontSize=font_size )

            #Get Stage
            stage = omni.usd.get_context().get_stage()

            #Find the /Looks root
            curr_prim = stage.GetPrimAtPath("/")
            looks_path = ""
            for prim in Usd.PrimRange(curr_prim):

                if prim.GetPath() == "/Looks":
                    looks_path = "/Looks"
                    continue
                elif prim.GetPath() == "/World/Looks":
                    looks_path = "/World/Looks"
                    continue

            #print("Looks root is: " +looks_path)
            #Get the Shader and set the image property
            if (looks_path == ""):
                looks_path = "/Looks"

            shader_path = Sdf.Path(looks_path)
            shader_path = Sdf.Path(shader_path.AppendPath(g))
            shader_path = Sdf.Path(shader_path.AppendPath("Shader"))

            #select the shader
            selection = omni.usd.get_context().get_selection()
            selection.set_selected_prim_paths([str(shader_path)], False)         

            #Get the Shader
            shader_prim = stage.GetPrimAtPath(str(shader_path))

            # print("Shader Attributes:-----" + str(shader_path))
            # print(shader_prim.GetAttributes())

            try:
                shader_prim.CreateAttribute("inputs:diffuse_texture", Sdf.ValueTypeNames.Asset)
                                    
                omni.kit.commands.execute('ChangeProperty',
                    prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
                    value=str(output_file), prev=str(output_file))
            except:
                #Do it again!
                omni.kit.commands.execute('ChangeProperty',
                prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
                value=str(output_file),prev=str(output_file))



    #load the resource prims to the stages
    def LoadResources(self, viewType: str):

        #Load Resources depending on the current view
        
        if viewType == "ByGroup": 
            
            groups = self._dataStore._group_count.copy()

        if viewType == "ByLocation":
            
            groups = self._dataStore._location_count.copy()

        if viewType == "ByType":
            groups = self._dataStore._type_count.copy()
        
        if viewType == "BySub":
            pass

        if viewType == "ByCost":
            pass

        if (len(groups) >0):
            stage =  omni.usd.get_context().get_stage()

            #Get Group Prim to place resources on 
            for group in groups:
                
                #Cleanup the group name for a prim path
                group_prim_path = self.res_layer_root_path.AppendPath(cleanup_prim_path(self, group))

                #Get the Group Prim
                group_prim = stage.GetPrimAtPath(str(group_prim_path))
                resource_count = groups[group]

                self.scale_factor=self._dataStore._composition_scale_model.as_float                

                #ex 400.0 -> 800 - 400 plane is 800x800
                plane_size = (calcPlaneSizeForGroup(scaleFactor=self.scale_factor, resourceCount=resource_count)*2) 
                plane_class = (plane_size/100)/2
                
                #distance of objects depending on grid size..  
                dist = plane_size / plane_class
                upAxis = self._dataStore._primary_axis_model.get_current_item().as_string

                #Use NVIDIAs Scatter algo to position on varying sized planes
                transforms = scatterOnFixedPlane(
                    upAxis=upAxis,
                    count=[int(plane_class), int(plane_class), 1], # Distribute accross the plane size
                    distance=[dist,dist,dist],
                    scaleFactor=self.scale_factor
                )

                self.log_transforms(transforms)

                i=0
                if (group_prim_path is not None):
                    
                    #Lets get the resources to place
                    for k, v in self._dataStore._resources.items():
                        if (v["group"] == group):

                            #Cleanup Resource Name - Max path is 84?
                            resName = cleanup_prim_path(self, k)

                            prim_len = len(str(group_prim_path)) + len(resName)
                            if (prim_len) > 70:
                                diff = prim_len - 70 # say its 89..  this gives 5 
                                trim = len(resName) - diff 
                                resName = resName[:trim] #trim off that 5

                            resName=cleanup_prim_path(self, resName)
                            print("Creating new prim: " + resName)
                            
                            #Place a new Prim in position X,Y,Z with A = Axis up                           
                            shape_prim_path = group_prim_path.AppendPath(resName)

                            # Create prim to add the reference to.
                            prim = stage.DefinePrim(shape_prim_path)

                            # Set a default
                            shape_to_render = "omniverse://localhost/Resources/3dIcons/scene.usd"

                            try:
                                typeName = cleanup_prim_path(self,  v["type"])
                                shape_to_render = shape_usda_name[typeName]   
                            except:
                                print("No matching prim found - " + typeName)                                  

                            prim.GetReferences().AddReference(shape_to_render)

                            my_new_prim = stage.GetPrimAtPath(shape_prim_path)

                            prim_vector = transforms[i]

                            #calculate the scale of the prim
                            scale = (self.scale_factor*self.base_prim_size)

                            #Are we still set to default? Change cube size and position
                            if shape_to_render == "omniverse://localhost/Resources/3dIcons/scene.usd":
                                scale = 3.75 * self.scale_factor
                                
                                if upAxis == "X":
                                    prim_vector[0] = prim_vector[0] + 37.5
                                if upAxis == "Y":
                                    prim_vector[1] = prim_vector[1] + 37.5
                                if upAxis == "Z":
                                    prim_vector[2] = prim_vector[2] + 37.5


                            print("Placing prim: " + v["type"] + " " + shape_to_render + " | " + str(shape_prim_path) + " @ " 
                                + str(prim_vector[0]) + "," + str(prim_vector[1]) + "," + str(prim_vector[2]))           

                            # Create tranform, rotate, scale attributes
                            for name in my_new_prim.GetPropertyNames():
                                if name == "xformOp:translate":
                                    my_new_prim.RemoveProperty("xformOp:translate")

                                if name == "xformOp:rotateXYZ":
                                    my_new_prim.RemoveProperty("xformOp:rotateXYZ")

                                if name == "xformOp:scale":
                                    my_new_prim.RemoveProperty("xformOp:scale")
                                
                            #     if name == "xformOpOrder":
                            #         my_new_prim.RemoveProperty("xformOp:scale")

                            #this might error
                            try:
                                properties = my_new_prim.GetPropertyNames()
                                if 'xformOp:scale' not in properties:
                                    UsdGeom.Xformable(my_new_prim).AddScaleOp()
                                if 'xformOp:rotateXYZ' not in properties:
                                    UsdGeom.Xformable(my_new_prim).AddRotateXYZOp()
                                if 'xformOp:translate' not in properties:
                                    UsdGeom.Xformable(my_new_prim).AddTranslateOp()
                            except:
                                pass

                            # Set your transform, rotate, scale attributes, ORDER MATTERS!!!
                            # Create SCALE, TRANSLATE, ROATATE - in that order..
                            try:
                                my_new_prim.GetAttribute('xformOp:translate').Set(prim_vector)
                                my_new_prim.GetAttribute('xformOp:rotateXYZ').Set(Gf.Vec3f(0.0, 0.0, 0.0))
                                my_new_prim.GetAttribute('xformOp:scale').Set(Gf.Vec3f(scale,scale,scale))
                            
                                #print("before: " + str(my_new_prim.GetAttribute("xformOpOrder").Get()))
                                my_new_prim.GetAttribute("xformOpOrder").Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])
                                #print("after: " + str(my_new_prim.GetAttribute("xformOpOrder").Get()))
                            except:
                                pass                          
                            #my_new_prim.GetAttribute('xformOpOrder').Set(["xformOp:translate, xformOp:rotateXYZ, xformOp:scale"])

                            i=i+1 # Current shape



    # Set Color
    # next_shape.GetDisplayColorAttr().Set(
    #     category_colors[int(cluster) % self.max_num_clusters])           


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
    

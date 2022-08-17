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
from .stage_position import scatterWithPlaneSize
from .stage_creator import create_prims


CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.joinpath("temp")

# The Stage Manager is responsible for drawing the stage based on the ViewType
# It will start from scratch and create the Ground plane and groups on the plane
# It will render the resources in each group on individual planes
class StageManager():
    def __init__(self):

        self._dataManager = DataManager.instance() # Get A Singleton instance
        self._dataStore = DataStore.instance() # Get A Singleton instance

        #root prim paths
        self.root_path = Sdf.Path('/World')
        self.aad_layer_root_path = Sdf.Path(self.root_path.AppendPath('AAD'))
        self.sub_layer_root_path = Sdf.Path(self.root_path.AppendPath('Subscriptions'))
        self.res_layer_root_path = Sdf.Path(self.root_path.AppendPath('Resource_Groups'))
        
        #tracking where we put stuff so we dont have to calculate it again.
        self._stage_matrix = {}

        # stage_unit defines the number of unit per meter
        self.stage_unit_per_meter = 1
               
        # Scale factor so that the shapes are well spaced
        self.scale_factor = 10.0
      
        # limit the number of rows read
        self.max_elements = 5000
        
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
        light_prim_path = self.root_path.AppendPath('DistantLight')
        light_prim = UsdLux.DistantLight.Define(self._stage, str(light_prim_path))
        light_prim.CreateAngleAttr(0.53)
        light_prim.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 0.745))
        light_prim.CreateIntensityAttr(3000.0)

    #Invoked from UI - Show the Stages based on the View.
    def ShowStage(self, viewType: str):
        self.InitStage()

        #Cycle through the groups creating planes for each of them
        #Track plane positioning in some map for resource placement later..
        if viewType == "ByGroup":
            
                #Calc Plane sizes based on items in group
                sizes = []
                groups = []

                if len(self._dataStore._group_count) == 0:
                    self._dataManager.refresh_data()

                gpz = self._dataStore._group_count.copy()
                for grp in gpz:
                    sizes.append(calcPlaneSizeForGroup(scaleFactor=self._dataStore._composition_scale_model.as_float, resourceCount=self._dataStore._group_count.get(grp)))
                    grp = cleanup_prim_path(self, grp)
                    groups.append(grp)

                #Use NVIDIAs Scatter algorytm to 
                transforms = scatterWithPlaneSize(
                    count=[m.as_int for m in self._dataStore._options_count_models],
                    distance=[m.as_float for m in self._dataStore._options_dist_models],
                    sizes=sizes,
                    randomization=[m.as_float for m in self._dataStore._options_random_models],
                    id_count=len(self._dataStore._group_count),
                    seed=0,
                    scaleFactor=self._dataStore._composition_scale_model.as_float
                )

                if (len(groups)) >0 :

                    #Create new prims and then transform them
                    create_prims(
                        transforms=transforms,
                        prim_names=groups,
                        parent_path=str(self.res_layer_root_path),
                        up_axis=self._dataStore._primary_axis_model.get_current_item().as_string,
                        plane_size=sizes
                    )
               
                #Create shaders for each plane
                for g in groups:
                    i=0
                    prim_path = self.res_layer_root_path.AppendPath(g)

                    #Select a Plane
                    omni.kit.commands.execute('SelectPrims',
                        old_selected_paths=[''],
                        new_selected_paths=[str(prim_path)],
                        expand_in_stage=True)

                    print("Creating Shader: " + str(prim_path))

                    #Create a Shader for the plane
                    omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
                        mdl_name='OmniPBR.mdl',
                        mtl_name='OmniPBR',
                        prim_name=g,
                        mtl_created_list=None,
                        bind_selected_prims=True)

                #Draw shaders on the stages
                #self.LabelLabels(viewType)

        if viewType == "ByLocation":
            for loc in self._dataStore._location_count:
                pass

        if viewType == "ByType":
            pass
        
        if viewType == "ByNetwork":
            pass

        if viewType == "ByCost":
            pass

        if viewType == "Template":
            pass

    #Load Stage Mesh Images to Shaders
    def LabelLabels(self, viewType: str):

        #Calc Plane sizes based on items in group
        sizes = []
        groups = []

        gpz = self._dataStore._group_count.copy()
        for grp in gpz:
            sizes.append(calcPlaneSizeForGroup(scaleFactor=self._dataStore._composition_scale_model.as_float, resourceCount=self._dataStore._group_count.get(grp)))
            grp = cleanup_prim_path(self, grp)
            groups.append(grp)

        #Create shaders for each plane
        for g in groups:
            i=0
            prim_path = self.res_layer_root_path.AppendPath(g)
            
            #MAKE A TEMP COPY OF THE BASE IMAGE TEXTURE SO THAT WE CAN DRAW TEXT ON THE COPY
            src_file = DATA_PATH.joinpath("tron_grid.png")
            output_file = DATA_PATH.joinpath(g + ".png")
            shutil.copyfile(src_file, output_file)

            font_size = get_font_size_from_length(len(g))

            draw_text_on_image_at_position(
                input_image_path=output_file,
                output_image_path=output_file, 
                textToDraw=g, 
                x=50, y=400, fillColor="Yellow", fontSize=font_size )

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

            print("Looks root is: " +looks_path)
            #Get the Shader and set the image property
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

            
            #shader_prim.GetAttribute("inputs:diffuse_texture").Set(base_image, )

            #props_path = Sdf.Path(shader_path).AppendPath(".inputs:diffuse_texture")
            #print("Setting Shader property: " + str(props_path) + " " + str(output_file))
            #omni.kit.commands.execute('ChangeProperty', prop_path=props_path, value=str(output_file),  prev=str(output_file))

        #f:\source\github\mce\metacloudexplorer\exts\meta.cloud.explorer.azure\meta\cloud\explorer\azure\temp\backups.png

            # stage = omni.usd.get_context().get_stage()

            # if shader_prim is not None:
            #     print("Setting shader image: " + str(shader_path) + " " + str(output_file))
            #     shader_prim.CreateAttribute("inputs:diffuse_texture", Sdf.ValueTypeNames.Asset).Set(str(output_file))
            # else:
            #     print("Can't get prim " + str(shader_path))
            
    #Draw a GroundPlane for the Resources to sit on.
    def DrawStage(self, Path:str, Name: str, Size: int, Location: Gf.Vec3f, Color:Gf.Vec3d):      
        create_plane(self,Path, Name, Size, Location, Color)


    #load the resource prims to the stages
    def LoadResources(self, viewType: str):

        if viewType == "ByGroup": 
            
            groups = self._dataStore._group_count.copy()
            if (len(groups) >0):
                stage =  omni.usd.get_context().get_stage()

                #Get Group Prim to place resources on 
                for group in groups:
                    
                    #Cleanup the group name for a prim path
                    group_prim_path = self.res_layer_root_path.AppendPath(cleanup_prim_path(self, group))

                    #Get the Group Prim
                    group_prim_path = stage.GetPrimAtPath(str(group_prim_path))

                    resCount = groups[group]

                    #Calculate the positions to place x resources on this group plane



                    if (group_prim_path is not None):
                        
                        #Lets get the resources to place
                        for resource in self._dataStore._resources:
                            if (self._dataStore._resources["group"] == group):

                                #Cleanup Resource Name
                                resName = cleanup_prim_path(self, self._dataStore._resources["name"])


                                #Place a new Prim in position X,Y,Z with A = Axis up                           
                                shape_prim_path = Sdf.Path(group_prim_path).AppendPath(resName)

                                # Create prim to add the reference to.
                                ref_shape = stage.DefinePrim(shape_prim_path)

                                # Add the reference
                                ref_shape.GetReferences().AddReference(shape_usda_name[self._dataStore._resources["type"]])
                                                
                                # Get mesh from shape instance
                                next_shape = UsdGeom.Mesh.Get(stage, shape_prim_path)

                                #Set location
                                next_shape.AddTranslateOp().Set(
                                    Gf.Vec3f(
                                        self.scale_factor*x, 
                                        self.scale_factor*y,
                                        self.scale_factor*z))








        if viewType == "ByLocation":
            for loc in self._dataStore._location_count:
                pass

        if viewType == "ByType":
            pass
        
        if viewType == "ByNetwork":
            pass

        if viewType == "ByCost":
            pass

        if viewType == "Template":
            pass





    #def Draw_Prims(self):
        #TODO Salvage any of this
        # Iterate over each row in the CSV file
                #   Skip the header row
                #   Don't read more than the max number of elements
                #   Create the shape with the appropriate color at each coordinate
                # for row in itertools.islice(csv_reader, 1, self.max_elements):
                #     id = row[0]
                #     name = row[1]
                #     subs = row[2]
                #     location = row[3]
                #     count = row[4]
                #     x = float(row[5])
                #     y = float(row[6])
                #     z = float(row[7])
                    
                #     if (name == "Total"):
                #         continue;

                #     # root prim
                #     cluster_prim_path = self.root_path                  
                #     cluster_prim = stage.GetPrimAtPath(cluster_prim_path)

                #     # create the prim if it does not exist
                #     if not cluster_prim.IsValid():
                #         UsdGeom.Xform.Define(stage, cluster_prim_path)
                        
                #     shape_prim_path = cluster_prim_path + self.rg_layer_root_path + name
                #     shape_prim_path = shape_prim_path.replace(" ", "_")
                #     shape_prim_path = shape_prim_path.replace(".", "_")

                #     # Create prim to add the reference to.
                #     ref_shape = stage.DefinePrim(shape_prim_path)

                #     # Add the reference
                #     ref_shape.GetReferences().AddReference(str(self.rg_shape_file_path))
                                    
                #     # Get mesh from shape instance
                #     next_shape = UsdGeom.Mesh.Get(stage, shape_prim_path)

                #     # Set location
                #     next_shape.AddTranslateOp().Set(
                #         Gf.Vec3f(
                #             self.scale_factor*x, 
                #             self.scale_factor*y,
                #             self.scale_factor*z))

                    # Set Color
                   #next_shape.GetDisplayColorAttr().Set(
                   #     category_colors[int(cluster) % self.max_num_clusters])           


    #Add AAD Instance
    def ShowAAD(self, Name: str, Location: Gf.Vec3f):
        print("Show AAD")

        # root prim
        cluster_prim_path = self.root_path                  
        cluster_prim = self._stage.GetPrimAtPath(cluster_prim_path)

        # create the prim if it does not exist
        if not cluster_prim.IsValid():
            UsdGeom.Xform.Define(self._stage, cluster_prim_path)
            
        shape_prim_path = cluster_prim_path + '/AAD_' + Name

        # Create prim to add the reference to.
        ref_shape = self._stage.OverridePrim(shape_prim_path)

        # Add the reference
        ref_shape.GetReferences().AddReference(shape_usda_name["AAD"])
                        
        # Get mesh from shape instance
        next_shape = UsdGeom.Mesh.Get(self._stage, shape_prim_path)

        # Set location at home point
        next_shape.AddTranslateOp().Set(Location)
            # Gf.Vec3f(
            #     self.scale_factor*0, 
            #     self.scale_factor*0,
            #     self.scale_factor*0))


    def ShowSubscriptions(self):
        #HOW BIG OF A STAGE DO WE NEED?  LETS CALCULATE
        pass
        # TEST Label
        #with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
        #    with sc.Transform(scale_to=sc.Space.SCREEN):
            # Move it 5 points more to the top in the screen space
        #        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, 0)):
        #            sc.Label("Test", alignment=ui.Alignment.CENTER_BOTTOM)
            # Set Color
            #next_shape.GetDisplayColorAttr().Set(
            #     category_colors[int(cluster) % self.max_num_clusters])                  

    def ShowGroups():
        print ("subs")

    def ShowLocations():
        print ("locations")

    def ShowAllResources():
        #place resources on resource group specific planes.  or the same plane with bounding boxes...
        print ("all")


    

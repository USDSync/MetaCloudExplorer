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
import os.path
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

from .pillow_text import create_image_with_text

from  .prim_utils import create_plane
from  .prim_utils import cleanup_prim_path

from omni.kit.window.file_importer import get_file_importer
from omni.ui import scene as sc
from omni.ui import color as cl

from .resource_map import shape_usda_name
from .math_utils import calcPlaneSizeForGroup
from .data_manager import DataManager
from .data_store import DataStore


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
        
        self.x_threshold = 60
        self.x_extent = 0
        self.y_extent = 0
    
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


    #Invoked from UI - Show the Stage based on the View.
    def ShowStage(self, viewType: str):
        self.InitStage()

        #Cycle through the groups creating planes for each of them
        #Track plane positioning in some map for resource placement later..
        x=0.0
        y=0.0
        z=0.0

        xpadding=10
        ypadding=10
        previous_stage_size = 0
        previous_x = 0

        if viewType == "ByGroup":
            for group in self._dataStore._group_count:
                stagesize = calcPlaneSizeForGroup(self.scale_factor, self._dataStore._group_count[group])
                grp = cleanup_prim_path(self, Name=group)

                #Figure out where to put it
                if (x > self.x_threshold): #have we passed the X threshold?
                    x =0 # reset x, incerement y
                    y = y + (stagesize*2) + ypadding
                    if y > self.y_extent: self.y_extent = y #track the highest y

                else: #Keep going on X
                    x = (previous_x + previous_stage_size) + (stagesize*2 + 1) #where to put the new stage
                    if x > self.x_extent: self.x_extent = x #track the highest x extent

                #Create the Stages
                prim_path = str(self.res_layer_root_path.AppendPath(grp))
                print("Drawing " + str(stagesize) + " sized prim: " + prim_path + " @" + str(x) + ":" + str(y) +":"  + str(z))
                self.DrawStage(Path=prim_path,Name=grp, Size=stagesize, Location=Gf.Vec3f(x,y,z))

                #record the size and postion for the next stage
                previous_stage_size = stagesize
                previous_x = x

                self.DrawLabelOnStage(prim_path, grp, stagesize, 44, "left", "black" )

                self._stage_matrix[group] = {"name": group, "size": stagesize, "x": x, "y": y, "z": z }

            #self.DrawGround()

            #TODO
            #Draw all the Prims on the Stage
            #NAME,TYPE,RESOURCE GROUP,LOCATION,SUBSCRIPTION

            #for group in self._dataStore._groups:
                #for resource in self._dataStore._resources:
                    #if group["NAME"] == resource["RESOURCE GROUP"]:
                        #pass


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


    
    def DrawLabelOnStage(self, prim_path: str, prim_name: str, stageSize:int, fontSize:int, align:str, color:str):
        #Use the Pillow text library to create an image with the text on it, sized right for the prim stage
        #This will be displayed by the stage prim shader, once we create and set it.
        #create_image_with_text("temp\\output2.jpg", "Mmmuuuurrrrrrrrrr", 10,525,575,575,"white", "left", "black")

        output_file = DATA_PATH. joinpath(prim_name + ".png")   
        create_image_with_text(output_file, prim_name, int(10),int(10),(stageSize*10), (stageSize*10),"white", "left", "black", "temp\\airstrike.ttf", 44 )
       
        #Select the Plane
        omni.kit.commands.execute('SelectPrims',
            old_selected_paths=[''],
            new_selected_paths=[prim_path],
            expand_in_stage=True)

        omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
            mdl_name='OmniPBR.mdl',
            mtl_name='OmniPBR',
            prim_name=prim_name,
            mtl_created_list=None,
            bind_selected_prims=True)

        #Get the Shader and set the image property
        shader_path = self.root_path.AppendPath("Looks")
        shader_path = shader_path.AppendPath(prim_name)
        shader_path = shader_path.AppendPath("Shader")

        stage = omni.usd.get_context().get_stage()

        image_path = "C:\\tmp\\cryptobabies.png"

        shader = stage.GetPrimAtPath(str(shader_path))
        print(shader.GetAttributes())
        
        shader.GetAttribute("inputs:diffuse_texture").Set(str(image_path))
        print(shader.GetAttribute("inputs:diffuse_texture"))

        #img_file = output_file._str
        #attr = shader.CreateAttribute(shader_path.pathString, "inputs:diffuse_texture")
        #attr.Set(img_file)
    
        # omni.kit.commands.execute('ChangeProperty',
	    #     prop_path=Sdf.Path('/World/Looks/cryptobabies/Shader.inputs:diffuse_texture'),
	    #     value=Sdf.AssetPath('F:/Source/Github/mce/MetaCloudExplorer/exts/meta.cloud.explorer.azure/meta/cloud/explorer/azure/temp/cryptobabies.png'),
	    #     prev=None)


    #Draw a GroundPlane for the Resources to sit on.
    def DrawStage(self, Path:str, Name: str, Size: int, Location: Gf.Vec3f):
        
        create_plane(self,Path, Name, Size, Location)

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



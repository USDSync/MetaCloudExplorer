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
from pxr import Gf, UsdGeom, UsdLux
# omniverse
import omni.client
import omni.kit.app
import omni.ui as ui
from  .prim_utils import create_plane
from  .prim_utils import cleanup_prim_path

from omni.kit.window.file_importer import get_file_importer
from omni.ui import scene as sc
from omni.ui import color as cl

from .resource_map import shape_usda_name
from .math_utils import calcPlaneSizeForGroup
from .data_manager import DataManager

# The Stage Manager is responsible for drawing the stage based on the ViewType
# It will start from scratch and create the Ground plane and groups on the plane
# It will render the resources in each group on individual planes
class StageManager():
    def __init__(self):

        self._dataManager = DataManager.instance() # Get A Singleton instance

        #root prim paths
        self.root_path = '/World'
        self.aad_layer_root_path = '/AAD'
        self.sub_layer_root_path = '/SUB'
        self.res_layer_root_path = '/RES'
        
        # stage_unit defines the number of unit per meter
        self.stage_unit_per_meter = 1
               
        # Scale factor so that the shapes are well spaced
        self.scale_factor = 1.0
      
        # limit the number of rows read
        self.max_elements = 5000
        
        self.x_threshold = 60
    
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
        light_prim_path = self.root_path + '/DistantLight'
        light_prim = UsdLux.DistantLight.Define(self._stage, light_prim_path)
        light_prim.CreateAngleAttr(0.53)
        light_prim.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 0.745))
        light_prim.CreateIntensityAttr(3000.0)


    #Show the Stage based on the View.
    def ShowStage(self, viewType: str):
        self.InitStage()

        #Cycle through the groups creating planes for each of them
        #Track plane positioning in some map for resource placement later..
        x=0.0
        y=0.0
        z=0.0
        padding=2

        if viewType == "ByGroup":
            for group in self._dataManager._group_count:
                stagesize = calcPlaneSizeForGroup(self._dataManager._group_count[group])
                grp = cleanup_prim_path(self, Name=group)

                #Create the Stages
                stagesize = calcPlaneSizeForGroup(self._dataManager._group_count[group])
                print("Drawing " + str(stagesize) + " sized prim: " + group + " " + str(x) + ":" + str(y) +":"  + str(z))
                self.DrawStage(Name="/RG/" + grp, Size=stagesize, Location=Gf.Vec3f(x,y,z))

                #Depenmding on the size of the last stage, shift our position to accomidate the next one
                if (x > self.x_threshold):
                    x =0
                    y = y + (stagesize) + padding

                x = x + (stagesize) + padding


        if viewType == "ByLocation":
            for loc in self._dataManager._location_count:
                pass

        if viewType == "ByType":
            pass
        
        if viewType == "ByNetwork":
            pass

        if viewType == "ByCost":
            pass

        if viewType == "Template":
            pass

    #Draw a GroundPlane for the Resources to sit on.
    def DrawStage(self, Name: str, Size: int, Location: Gf.Vec3f):

        create_plane(self, Name, Size, Location)






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


        # TEST Label
        #with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
        #    with sc.Transform(scale_to=sc.Space.SCREEN):
            # Move it 5 points more to the top in the screen space
        #        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, 0)):
        #            sc.Label("Test", alignment=ui.Alignment.CENTER_BOTTOM)

        #Create the prims
        # root prim
        cluster_prim_path = self.root_path                  
        cluster_prim = stage.GetPrimAtPath(cluster_prim_path)

        # create the prim if it does not exist
        if not cluster_prim.IsValid():
            UsdGeom.Xform.Define(stage, cluster_prim_path)
        
        for sub in self._dataManager._subscription_count:
                
            name = sub.name.replace(" ", "_")
            name = name.replace("/", "_")

            shape_prim_path = cluster_prim_path + '/SUB_' + name
            shape_prim_path = shape_prim_path.replace(" ", "_")
            shape_prim_path = shape_prim_path.replace(".", "_")

            # Create prim to add the reference to.
            ref_shape = stage.DefinePrim(shape_prim_path)

            # Add the reference
            ref_shape.GetReferences().AddReference(shape_usda_name["Subscription"])
                            
            # Get mesh from shape instance
            next_shape = UsdGeom.Mesh.Get(stage, shape_prim_path)

            # Set location, where do we put them ??  they no longer have coordinates from c# input, need to implement this
            next_shape.AddTranslateOp().Set(
                Gf.Vec3f(
                    self.scale_factor*x, 
                    self.scale_factor*y,
                    self.scale_factor*z))

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



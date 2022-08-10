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

from omni.kit.window.file_importer import get_file_importer
from omni.ui import scene as sc
from omni.ui import color as cl

from .resource_map import shape_usda_name
from .data_manager import DataManager

class StageManager():
    def __init__(self):

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
        
        #  max number of different color clusters
        self.max_num_clusters = 10

        #Is this creating a new instance?  need a singleton....  where do I get it ?  need to pass it in? we'll see
        self._dataManager = DataManager()

    def ShowSubscriptions(self):
        
        # Clear the stage
        stage = omni.usd.get_context().get_stage()
        root_prim = stage.GetPrimAtPath(self.root_path)
        
        #  set the up axis
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

        #  set the unit of the world
        UsdGeom.SetStageMetersPerUnit(stage, self.stage_unit_per_meter)
        stage.SetDefaultPrim(root_prim)

        # add a light
        light_prim_path = self.root_path + '/DistantLight'
        light_prim = UsdLux.DistantLight.Define(stage, light_prim_path)
        light_prim.CreateAngleAttr(0.53)
        light_prim.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 0.745))
        light_prim.CreateIntensityAttr(2500.0)

        #Add AAD Instance
         # root prim
        cluster_prim_path = self.root_path                  
        cluster_prim = stage.GetPrimAtPath(cluster_prim_path)

        # create the prim if it does not exist
        if not cluster_prim.IsValid():
            UsdGeom.Xform.Define(stage, cluster_prim_path)
            
        shape_prim_path = cluster_prim_path + '/AAD'

        # Create prim to add the reference to.
        ref_shape = stage.OverridePrim(shape_prim_path)

        # Add the reference
        ref_shape.GetReferences().AddReference(shape_usda_name["AAD"])
                        
        # Get mesh from shape instance
        next_shape = UsdGeom.Mesh.Get(stage, shape_prim_path)

        # Set location at home point
        next_shape.AddTranslateOp().Set(
            Gf.Vec3f(
                self.scale_factor*0, 
                self.scale_factor*0,
                self.scale_factor*0))

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



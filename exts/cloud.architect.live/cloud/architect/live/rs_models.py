# Model related
# Python built-in
import os.path
import carb
import numpy as np
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

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.parent.parent.parent.joinpath("data\export")

class ResourceModel():
    def __init__(self, company):
        
        #root prim paths
        self.company = company
        self.root_path = '/World'
        self.aad_layer_root_path = '/AAD'
        self.sub_layer_root_path = '/SUB'
        self.rgData = {} #Dictionary of resources
        self.typeString = ''
        
        # stage_unit defines the number of unit per meter
        self.stage_unit_per_meter = 1

        # Default CSV Path (sample file deployed with extension)
        self.csv_file_path = DATA_PATH.joinpath(company + '_Res.csv')
        
        # Scale factor so that the shapes are well spaced
        self.scale_factor = 1.0

        # limit the number of rows read
        self.max_elements = 5000
        
        #  max number of different color clusters
        self.max_num_clusters = 10


    def loadResourcesFromCSV(self):
         # check that CSV exists
        if os.path.exists(self.csv_file_path):
            # Read CSV file
            #with open(self.csv_file_path, newline='') as csvfile:
            #    csv_reader = csv.reader(csvfile, delimiter=',')
            i = 1

            #Name,Type,Group,Location,Subscription,x,y,z
            with open(self.csv_file_path) as file:
                reader = csv.DictReader(file, delimiter=',')
                for row in reader:
                    name = row["Name"]
                    type = row["Type"]
                    group = row["Group"]
                    location = row["Location"]
                    subscription = row["Subscription"]
                    x = float(row["x"])
                    y = float(row["y"])
                    z = float(row["z"])

                    
    def generate(self):
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
            
        shape_prim_path = cluster_prim_path + '/AAD_' + self.company

        # Create prim to add the reference to.
        ref_shape = stage.DefinePrim(shape_prim_path)

        # Add the reference
        ref_shape.GetReferences().AddReference(shape_usda_name["AAD"])

        # Create tranform, rotate, scale attributes
        properties = ref_shape.GetPropertyNames()
        if 'xformOp:translate' not in properties:
            UsdGeom.Xformable(ref_shape).AddTranslateOp()
        # if 'xformOp:rotateZYX' not in properties:
        #     UsdGeom.Xformable(ref_shape).AddRotateZYXOp()
        if 'xformOp:scale' not in properties:
            UsdGeom.Xformable(ref_shape).AddScaleOp()

        # Set your tranform, rotate, scale attributes
        #ref_shape.GetAttribute('xformOp:rotateZYX').Set(Gf.Vec3f(1.0, 2.0, 4.0))
        ref_shape.GetAttribute('xformOp:translate').Set(Gf.Vec3f(
                self.scale_factor*0, 
                self.scale_factor*0,
                self.scale_factor*0))
        ref_shape.GetAttribute('xformOp:scale').Set(Gf.Vec3f(1.0, 1.0, 1.0))

        # Get mesh from shape instance
        #next_shape = UsdGeom.XformOp.Get(stage, shape_prim_path)

        # check that CSV exists
        if os.path.exists(self.csv_file_path):
            # Read CSV file
            with open(self.csv_file_path, newline='') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')
                i = 1
            
                #Name,Type,Group,Location,Subscription,x,y,z
                with open(self.csv_file_path) as file:
                    reader = csv.DictReader(file, delimiter=',')
                    for row in reader:
                        name = row["Name"]
                        type = row["Type"]
                        group = row["Group"]
                        location = row["Location"]
                        subscription = row["Subscription"]
                        x = float(row["x"])
                        y = float(row["y"])
                        z = float(row["z"])
                   
                        if (name == "Total"):
                            continue;

                        # root prim
                        cluster_prim_path = self.root_path                  
                        cluster_prim = stage.GetPrimAtPath(cluster_prim_path)

                        # create the prim if it does not exist
                        if not cluster_prim.IsValid():
                            UsdGeom.Xform.Define(stage, cluster_prim_path)
                            
                        self.typeString = type.replace(" ", "_")
                        self.typeString = self.typeString.replace("-", "_")

                        shape_prim_path = cluster_prim_path + '/' + self.typeString + str(i) + name
                        shape_prim_path = shape_prim_path.replace(" ", "_")
                        shape_prim_path = shape_prim_path.replace(".", "_")
                        shape_prim_path = shape_prim_path.replace("-", "_")
                        shape_prim_path = shape_prim_path.replace("(", "_")
                        shape_prim_path = shape_prim_path.replace(")", "_")

                        print("Creating Prim...")
                        print(shape_prim_path)

                        # Create prim to add the reference to.
                        ref_shape = stage.DefinePrim(shape_prim_path)

                        ref_shape.GetReferences().AddReference(shape_usda_name[type])
                                        
                        # Get mesh from shape instance
                        #next_shape = UsdGeom.Mesh.Get(stage, shape_prim_path)

                        # Create tranform, rotate, scale attributes
                        properties = ref_shape.GetPropertyNames()
                        if 'xformOp:translate' not in properties:
                            UsdGeom.Xformable(ref_shape).AddTranslateOp()
                        # if 'xformOp:rotateZYX' not in properties:
                        #     UsdGeom.Xformable(ref_shape).AddRotateZYXOp()
                        if 'xformOp:scale' not in properties:
                            UsdGeom.Xformable(ref_shape).AddScaleOp()

                        # Set your tranform, rotate, scale attributes
                        #ref_shape.GetAttribute('xformOp:rotateZYX').Set(Gf.Vec3f(1.0, 2.0, 4.0))
                        ref_shape.GetAttribute('xformOp:translate').Set(Gf.Vec3f(
                                self.scale_factor*x, 
                                self.scale_factor*y,
                                self.scale_factor*z))

                        ref_shape.GetAttribute('xformOp:scale').Set(Gf.Vec3f(1.0, 1.0, 1.0))

                    # Set Color
                   #next_shape.GetDisplayColorAttr().Set(
                   #     category_colors[int(cluster) % self.max_num_clusters])                  
               
    # Handles the click of the Load button
    def select_file(self):
        self.file_importer = get_file_importer()
        self.file_importer.show_window(
            title="Select a CSV File",
            import_button_label="Select",
            import_handler=self._on_click_open,
            file_extension_types=[(".csv", "CSV Files (*.csv)")],
            file_filter_handler=self._on_filter_item
            )

    # Handles the click of the open button within the file importer dialog
    def _on_click_open(self, filename: str, dirname: str, selections):
        
        # File name should not be empty.
        filename = filename.strip()
        if not filename:
            carb.log_warn(f"Filename must be provided.")
            return

        # create the full path to csv file
        if dirname:
            fullpath = f"{dirname}{filename}"
        else:
            fullpath = filename

        self.csv_file_path = fullpath
        self.csv_field_model.set_value(str(fullpath))

    # Handles the filtering of files within the file importer dialog
    def _on_filter_item(self, filename: str, filter_postfix: str, filter_ext: str) -> bool:
        if not filename:
            return True
        # Show only .csv files
        _, ext = os.path.splitext(filename)
        if ext == filter_ext:
            return True
        else:
            return False

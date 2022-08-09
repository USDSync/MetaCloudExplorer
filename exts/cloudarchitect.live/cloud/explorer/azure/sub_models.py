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
from .data_model import DataModelFactory

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.parent.parent.parent.joinpath("data\export")

class SubscriptionModel():
    def __init__(self, company):
        
        #root prim paths
        self.company = company
        self.root_path = '/World'
        self.aad_layer_root_path = '/AAD'
        self.sub_layer_root_path = '/SUB'
        
        # stage_unit defines the number of unit per meter
        self.stage_unit_per_meter = 1

        #self.dataFactory = DataModelFactory(DATA_PATH, company)

        # Default CSV Path (sample file deployed with extension)
        #self.csv_file_path = DATA_PATH.joinpath(company + '_Subs.csv')
        
        # path to basic shape
        #self.aad_shape_file_path = "omniverse://localhost/Resources/AzureAAD_1_1.usda"
        #self.sub_shape_file_path = "omniverse://localhost/Resources/Subscriptions_1_3.usda"
        
        # Scale factor so that the shapes are well spaced
        self.scale_factor = 1.0

        # limit the number of rows read
        self.max_elements = 5000
        
        #  max number of different color clusters
        self.max_num_clusters = 10

    def generate(self):
        # Clear the stage
        stage = omni.usd.get_context().get_stage()
        root_prim = stage.GetPrimAtPath(self.root_path)
        
        stage = omni.usd.get_context().get_stage()
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

         # Label
        with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
            with sc.Transform(scale_to=sc.Space.SCREEN):
            # Move it 5 points more to the top in the screen space
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, 0)):
                    sc.Label("Test", alignment=ui.Alignment.CENTER_BOTTOM)

        #load the sub data
        #self.dataFactory.loaddata()
        #print(self.dataFactory.group_count_by_location())

        # check that CSV exists
        if os.path.exists(self.csv_file_path):
            # Read CSV file
            with open(self.csv_file_path, newline='') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')
                i = 1
                # Iterate over each row in the CSV file
                #   Skip the header row
                #   Don't read more than the max number of elements
                #   Create the shape with the appropriate color at each coordinate
                for row in itertools.islice(csv_reader, 1, self.max_elements):
                    id = row[0]
                    name = row[1]
                    desc = row[2]
                    parent = row[3]
                    count = row[4]
                    x = float(row[5])
                    y = float(row[6])
                    z = float(row[7])
                    
                    if (name == "Total"):
                        continue;

                    # root prim
                    cluster_prim_path = self.root_path                  
                    cluster_prim = stage.GetPrimAtPath(cluster_prim_path)

                    # create the prim if it does not exist
                    if not cluster_prim.IsValid():
                        UsdGeom.Xform.Define(stage, cluster_prim_path)
                        
                    shape_prim_path = cluster_prim_path + '/SUB_' + name
                    shape_prim_path = shape_prim_path.replace(" ", "_")
                    shape_prim_path = shape_prim_path.replace(".", "_")

                    # Create prim to add the reference to.
                    ref_shape = stage.DefinePrim(shape_prim_path)

                    # Add the reference
                    ref_shape.GetReferences().AddReference(str(self.sub_shape_file_path))
                                    
                    # Get mesh from shape instance
                    next_shape = UsdGeom.Mesh.Get(stage, shape_prim_path)

                    # Set location
                    next_shape.AddTranslateOp().Set(
                        Gf.Vec3f(
                            self.scale_factor*x, 
                            self.scale_factor*y,
                            self.scale_factor*z))

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

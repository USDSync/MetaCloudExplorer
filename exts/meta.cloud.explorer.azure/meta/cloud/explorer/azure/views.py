#  import from omniverse
from ctypes import alignment
from omni.ui.workspace_utils import TOP

#  import from other extension py
from .combo_box_model import ComboBoxModel
from .style_button import button_styles
from .style_meta import meta_window_style
from .data_manager import DataManager
from .data_store import DataStore

import sys
import webbrowser
#from turtle import width
import omni.ext
import omni.ui as ui
from omni.ui import color as cl
from omni.ui import scene as sc
import os
import omni.kit.commands
import omni.kit.pipapi
from pxr import Sdf, Usd, Gf, UsdGeom
import omni
from pathlib import Path
from .omni_utils import get_selection
from .combo_box_model import ComboBoxModel
from .omni_utils import duplicate_prims
from .stage_manager import StageManager

import random
LABEL_WIDTH = 120
SPACING = 4

class MainView(ui.Window):
    """The class that represents the window"""
    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH

        super().__init__(title, **kwargs)

        #Helper Class instances
        self._stageManager = StageManager()
        self._dataManager = DataManager.instance()
        self._dataStore = DataStore.instance()

        #UI Models
        self._options_model_x_max = ui.SimpleIntModel()
        self._options_model_y_max = ui.SimpleIntModel()
        self._options_model_z_max = ui.SimpleIntModel()
        self._options_model_scale = ui.SimpleIntModel()

        #Defaults
        self._groundPlaneAdded = False
        self._root_path = "/World"

        # Apply the style to all the widgets of this window
        self.frame.style = meta_window_style
       
        # Set the function that is called to build widgets when the window is visible
        self.frame.set_build_fn(self._build_fn)

    def destroy(self):
        # It will destroy all the children
        super().destroy()        
        
    @property
    def label_width(self):
        """The width of the attribute label"""
        return self.__label_width

    @label_width.setter
    def label_width(self, value):
        """The width of the attribute label"""
        self.__label_width = value
        self.frame.rebuild()

    #___________________________________________________________________________________________________
    # Function Definitions
    #___________________________________________________________________________________________________

    def on_docs():
        webbrowser.open_new("https://github.com/CloudArchitectLive/MetaCloudExplorer/wiki")

    def on_code():
        webbrowser.open_new("http://metacloudexplorer.com")

    def on_help():
        webbrowser.open_new("https://github.com/CloudArchitectLive/MetaCloudExplorer/issues")

    def load_account_info(self):
        print("Connect to Azure API")
        #todo

    def on_resource():
        print("On Resource")

    def on_network():
        print("On Network")

    def on_cost():
        print("On Cost")

    def on_group():
        print("On Group")

    def load_stage(self, viewType: str):
        self._stageManager.ShowStage(viewType)

    def load_resource_groups(self):
        self._stageManager.ShowGroups()

    def load_locations(self):
        self._stageManager.ShowLocations()

    def load_all_resources(self):
        self._stageManager.ShowAllResources()

    # Clear the stage
    def clear_stage(self):
        stage = omni.usd.get_context().get_stage()
        root_prim = stage.GetPrimAtPath(self._root_path)
        if (root_prim.IsValid()):
            stage.RemovePrim(self._root_path)                    
        
        ground_prim = stage.GetPrimAtPath('/GroundPlane')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/GroundPlane')                    

        ground_prim = stage.GetPrimAtPath('/Resource_Groups')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Resource_Groups')

    def destroy(self):
        self._window.destroy()
        self._window = None
        self._usd_context = None


    #___________________________________________________________________________________________________
    # Window UI Definitions
    #___________________________________________________________________________________________________

    def _build_fn(self):
        """The method that is called to build all the UI once the window is visible."""
        with ui.ScrollingFrame():
            with ui.VStack(height=0):
                self._build_new_header()
                self._build_connection()
                self._build_import()

    #Pieces of UI Elements
    def _build_new_header(self):
        """Build the widgets of the "Source" group"""
        with ui.ZStack():
            #Background
            ui.Image("omniverse://localhost/Resources/images/meta_cloud_explorer.png", height=220)

            #Foreground
            with ui.VStack():
                ui.Spacer(height=30)
                ui.Label("Meta Cloud Explorer", style={"color": 0xFFFFFFFF, "font_size":36}, alignment=ui.Alignment.CENTER, height=0)

            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=150)
                with ui.HStack(style=button_styles):
                    ui.Button("Load Resources to Stage", clicked_fn=lambda: self.load_stage("ByGroup"), name="subs", height=15, width=250, alignment=ui.Alignment.LEFT)
                    ui.Button("Clear the Stage", clicked_fn=lambda: self.clear_stage(), name="clear", height=15, width=250, alignment=ui.Alignment.RIGHT)

            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=200)
                with ui.HStack():
                    ui.Button("Type View", clicked_fn=lambda: self.load_stage("ByType"), height=15)
                    ui.Button("Location View", clicked_fn=lambda: self.load_stage("ByLocation"), height=15)
                    ui.Button("Group View", clicked_fn=lambda: self.load_stage("ByGroup"), height=15)
                with ui.HStack():
                    ui.Button("Network View", clicked_fn=lambda: self.load_stage("ByNetwork"), height=15)
                    ui.Button("Cost View", clicked_fn=lambda: self.load_stage("ByCost"), height=15)
                    ui.Button("Template View", clicked_fn=lambda: self.load_stage("Template"), height=15)
                with ui.HStack():
                    ui.Button("Docs", clicked_fn=lambda: self.on_docs(), height=15)
                    ui.Button("Code", clicked_fn=lambda: self.on_code(), height=15)
                    ui.Button("Help", clicked_fn=lambda: self.on_help(), height=15)           


    #Pieces of UI Elements
    def _build_header(self):
        """Build the widgets of the "Source" group"""
        with ui.VStack():
            ui.Label("Meta Cloud Explorer (Azure)", style={"color": 0xFF008976, "font_size":36}, alignment=ui.Alignment.LEFT, height=0)
            ui.Label("An Omniverse Scene Authoring extension", height=10, name="TItle", alignment=ui.Alignment.LEFT)
            ui.Line(style={"color": 0xff00b976}, height=20)

    def _build_commands(self):
        """Build the widgets of the "Commands" group"""
        with ui.CollapsableFrame("Explorer Commands", name="group"):
            with ui.VStack(height=0, spacing=SPACING):
                with ui.HStack(style=button_styles):
                    ui.Button("Load Resources to Stage", clicked_fn=lambda: self.load_stage("ByGroup"), name="subs", height=15, width=250, alignment=ui.Alignment.CENTER)
                    ui.Button("Clear the Stage", clicked_fn=lambda: self.clear_stage(), name="clear", height=15, width=250, alignment=ui.Alignment.CENTER)

    def _build_import(self):
        with ui.CollapsableFrame("Import Offline Files", name="group", collapsed=True):
            with ui.VStack():
                ui.Label("Resource Groups file path:", height=10, width=120)             
                with ui.HStack():                   
                    self._rg_data_import_field = ui.StringField(height=10)
                    self._rg_data_import_field.enabled = True
                    self._rg_data_import_field.model.set_value(str(self._dataStore._rg_csv_file_path))
                    self._dataStore._rg_csv_field_model = self._rg_data_import_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("rg"))
            
                ui.Label("All Resources file path:", height=10, width=120)             
                with ui.HStack():
                    self._rs_data_import_field = ui.StringField(height=10)
                    self._rs_data_import_field.enabled = True
                    self._rs_data_import_field.model.set_value(str(self._dataStore._rs_csv_file_path))
                    self._dataStore._rs_csv_field_model = self._rs_data_import_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("res"))

                ui.Button("Import Data Files", clicked_fn=lambda: self._dataManager.load_csv_files())            

    def _build_connection(self):
        with ui.CollapsableFrame("Live Connection", name="group", collapsed=True):
            with ui.VStack():
                ui.Label("Tenant Id")
                self._tenant = ui.StringField()
                ui.Label("Client Id")
                self._client = ui.StringField()
                ui.Label("Client Secret")
                self._secret = ui.StringField()
                ui.Button("Connect to Azure", clicked_fn=lambda: self._dataManager.load_from_api())

    def _build_options(self):
        with ui.CollapsableFrame("Composition", name="group", collapsed=True):
            with ui.VStack():
                with ui.HStack():
                    ui.Label("X-Axis Max", name="attribute_name", width=self.label_width)
                    ui.IntDrag(model=self._options_model_x_max, min=1, max=100)

                with ui.HStack():
                    ui.Label("Y-Axis Max", name="attribute_name", width=self.label_width)
                    ui.IntDrag(model=self._options_model_y_max, min=1, max=100)

                with ui.HStack():
                    ui.Label("Z-Axis Max", name="attribute_name", width=self.label_width)
                    ui.IntDrag(model=self._options_model_z_max, min=1, max=100)                   

    def _build_groups(self):
        with ui.VStack():
            ui.Label("Views")
            with ui.HStack():
                ui.Button("Type View", clicked_fn=lambda: self.load_stage("ByType"), height=15)
                ui.Button("Location View", clicked_fn=lambda: self.load_stage("ByLocation"), height=15)
                ui.Button("Group View", clicked_fn=lambda: self.load_stage("ByGroup"), height=15)

    def _build_views(self):
        with ui.HStack():
            ui.Button("Network View", clicked_fn=lambda: self.load_stage("ByNetwork"), height=15)
            ui.Button("Cost View", clicked_fn=lambda: self.load_stage("ByCost"), height=15)
            ui.Button("Template View", clicked_fn=lambda: self.load_stage("Template"), height=15)

    def _build_help(self):
        ui.Line(style={"color": 0xff00b976}, height=20)

        with ui.VStack():
            with ui.HStack():
                ui.Button("Docs", clicked_fn=lambda: self.on_docs(), height=15)
                ui.Button("Code", clicked_fn=lambda: self.on_code(), height=15)
                ui.Button("Help", clicked_fn=lambda: self.on_help(), height=15)           
                    


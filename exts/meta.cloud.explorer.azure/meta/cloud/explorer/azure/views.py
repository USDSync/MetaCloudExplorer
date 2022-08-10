#  import from omniverse
from omni.ui.workspace_utils import TOP

#  import from other extension py
from .sub_models import SubscriptionModel
from .rg_models import ResourceGroupModel
from .rs_models import ResourceModel
from .combo_box_model import ComboBoxModel
from .style_button import button_styles
from .style_meta import meta_window_style
from .offline_data_manager import OfflineDataManager

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
from .utils import get_selection
from .combo_box_model import ComboBoxModel
from .utils import duplicate_prims

import random
LABEL_WIDTH = 120
SPACING = 4

class MainView(ui.Window):
    """The class that represents the window"""
    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH

        super().__init__(title, **kwargs)

        #ToDepricate
        self._rs_model = ResourceModel("Company1")
        self._rg_model = ResourceGroupModel("Company1")
        self._sub_model = SubscriptionModel("Company1")

        #UI Models
        self._dataManager = OfflineDataManager()
        self._dataManager.sub_field_model = None
        self._dataManager.res_field_model = None
        self._dataManager.rg_field_model = None
        self._data_mode_model = ComboBoxModel("Live API", "Offline data")

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

    def create_ground_plane(self):
        #if (self._groundPlaneAdded == False):
        stage_ref = omni.usd.get_context().get_stage()

        omni.kit.commands.execute('AddGroundPlaneCommand',
        stage=stage_ref,
        planePath='/GroundPlane',
        axis="Z",
        size=2500.0,
        position=Gf.Vec3f(0,0,0),
        color=Gf.Vec3f(0.5, 0.5, 0.5))
        self._groundPlaneAdded = True

    def load_subscriptions(self):
        self._sub_model.generate()

    def load_resource_groups(self):
        self._rg_model.generate()

    def load_all_resources(self):
        self._rs_model.generate()

    # Clear the stage
    def clear_stage(self):
        stage = omni.usd.get_context().get_stage()
        root_prim = stage.GetPrimAtPath(self._root_path)
        if (root_prim.IsValid()):
            stage.RemovePrim(self._root_path)                    
        
        ground_prim = stage.GetPrimAtPath('/GroundPlane')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/GroundPlane')                    

    def destroy(self):
        self._window.destroy()
        self._window = None
        self._usd_context = None

    def import_data_files(self):
        print("Load the CSV files")
        #todo

    #___________________________________________________________________________________________________
    # Window UI Definitions
    #___________________________________________________________________________________________________

    def _build_fn(self):
        """The method that is called to build all the UI once the window is visible."""
        with ui.ScrollingFrame():
            with ui.VStack(height=0):
                self._build_header()
                self._build_commands()
                self._build_import()
                self._build_connection()

    def _build_header(self):
        """Build the widgets of the "Source" group"""
        with ui.VStack():
            ui.Label("Meta Cloud Explorer (Azure)", style={"color": 0xFF008976, "font_size":36}, alignment=ui.Alignment.CENTER, height=0)
            ui.Line(style={"color": 0xff00b976}, height=20)

    def _build_commands(self):
        """Build the widgets of the "Commands" group"""
        with ui.CollapsableFrame("Commands", name="group"):
            with ui.VStack(height=0, spacing=SPACING):
                with ui.HStack(style=button_styles):
                    ui.Button("Load Subscriptions", clicked_fn=lambda: self.load_subscriptions(self), name="subs", height=15)
                    ui.Button("Load Resource Groups", clicked_fn=lambda: self.load_resource_groups(self), name="rg", height=15)
                    ui.Button("Load All Resources", clicked_fn=lambda: self.load_all_resources(self), name="rs", height=15)
                with ui.HStack():
                    ui.Button("Clear Stage", clicked_fn=lambda: self.clear_stage(self), height=15)
                    ui.Button("Add Ground", clicked_fn=lambda: self.create_ground_plane(self), height=15)

    def _build_import(self):
        with ui.CollapsableFrame("Import Files", name="group"):
            with ui.VStack():
                ui.Label("Sub file path:", height=10, width=120)             
                with ui.HStack(height=20):           
                    self.csv_field = ui.StringField(height=10)
                    self.csv_field.enabled = True
                    self.csv_field.model.set_value(str(self._dataManager._sub_csv_file_path))
                    self._dataManager.sub_csv_field_model = self.csv_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("sub"))

                ui.Label("Resource Groups file path:", height=10, width=120)             
                with ui.HStack():                   
                    self._rg_data_import_field = ui.StringField(height=10)
                    self._rg_data_import_field.enabled = True
                    self._rg_data_import_field.model.set_value(str(self._dataManager._rg_csv_file_path))
                    self._dataManager.rg_csv_field_model = self._rg_data_import_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("rg"))
            
                ui.Label("All Resources file path:", height=10, width=120)             
                with ui.HStack():
                    self._rs_data_import_field = ui.StringField(height=10)
                    self._rs_data_import_field.enabled = True
                    self._rs_data_import_field.model.set_value(str(self._dataManager._rs_csv_file_path))
                    self._dataManager.rs_csv_field_model = self._rs_data_import_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("res"))

                ui.Button("Import Data Files", clicked_fn=lambda: self._dataManager.loadFiles(self))            


    def _build_connection(self):
        with ui.CollapsableFrame("Connection", name="group", collapsed=True):
            with ui.VStack():
                ui.Label("Tenant Id")
                self._tenant = ui.StringField()
                ui.Label("Client Id")
                self._client = ui.StringField()
                ui.Label("Client Secret")
                self._secret = ui.StringField()
                ui.Button("Connect to Azure", clicked_fn=lambda: self.load_account_info(self))

    def _build_groups(self):
        with ui.VStack():
            with ui.HStack():
                ui.Button("Group By Type", clicked_fn=lambda: self.on_group(), height=15)
                ui.Button("Group By Region", clicked_fn=lambda: self.on_group(), height=15)
                ui.Button("Group By Group", clicked_fn=lambda: self.on_group(), height=15)

                
    def _build_views(self):
        with ui.HStack():
            ui.Button("Network View", clicked_fn=lambda: self.on_network(), height=15)
            ui.Button("Resource View", clicked_fn=lambda: self.on_resource(), height=15)
            ui.Button("Cost View", clicked_fn=lambda: self.on_cost(), height=15)

    def _build_help(self):
        ui.Line(style={"color": 0xff00b976}, height=20)

        with ui.VStack():
            with ui.HStack():
                ui.Button("Docs", clicked_fn=lambda: self.on_docs(), height=15)
                ui.Button("Code", clicked_fn=lambda: self.on_code(), height=15)
                ui.Button("Help", clicked_fn=lambda: self.on_help(), height=15)           
                    


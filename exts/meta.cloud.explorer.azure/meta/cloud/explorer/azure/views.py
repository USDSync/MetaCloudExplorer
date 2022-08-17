#  import from omniverse
from ctypes import alignment
from omni.ui.workspace_utils import TOP

#  import from other extension py
from .combo_box_model import ComboBoxModel
from .style_button import button_styles
from .style_meta import meta_window_style, get_gradient_color, build_gradient_image
from .style_meta import cl_combobox_background, cls_temperature_gradient, cls_color_gradient, cls_tint_gradient, cls_grey_gradient, cls_button_gradient

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

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data\\resources")


class MainView(ui.Window):
    """The class that represents the window"""
    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH

        super().__init__(title, **kwargs)

        #Helper Class instances
        self._stageManager = StageManager()
        self._dataManager = DataManager.instance()
        self._dataStore = DataStore.instance()

        # Apply the style to all the widgets of this window
        self.frame.style = meta_window_style
       
        # Set the function that is called to build widgets when the window is visible
        self.frame.set_build_fn(self._build_fn)

    def destroy(self):
        super().destroy() 
        self._usd_context = None
        
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

    def on_docs(self):
        webbrowser.open_new("https://github.com/CloudArchitectLive/MetaCloudExplorer/wiki/Meta-Cloud-Explorer-(Azure)")

    def on_code(self):
        webbrowser.open_new("http://metacloudexplorer.com")

    def on_help(self):
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


    #Load a fresh stage
    def load_stage(self, viewType: str):
        self.clear_stage()
        self._stageManager.ShowStage(viewType)

    #load the resource onto the stage
    def load_resources(self, viewType: str):
        self._stageManager.LoadResources(viewType)

    #GROUP VIEW
    def load_resource_groups(self):
        
        self._stageManager.ShowGroups()

    #LOCATION VIEW
    def load_locations(self):
        
        self._stageManager.ShowLocations()

    #ALL RESOURCES
    def load_all_resources(self):
        
        self._stageManager.ShowAllResources()

    # Clear the stage
    def clear_stage(self):

        stage = omni.usd.get_context().get_stage()
        root_prim = stage.GetPrimAtPath("/World")
        if (root_prim.IsValid()):
            stage.RemovePrim("/World")
        
        ground_prim = stage.GetPrimAtPath('/GroundPlane')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/GroundPlane')                    

        ground_prim = stage.GetPrimAtPath('/Resource_Groups')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Resource_Groups')

        ground_prim = stage.GetPrimAtPath('/Locations')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Locations')

        ground_prim = stage.GetPrimAtPath('/Looks')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Looks')

    #___________________________________________________________________________________________________
    # Window UI Definitions
    #___________________________________________________________________________________________________


    def onRadioValueChanged (self, uiFieldModel, uiLabel):
        if not uiFieldModel or not uiLabel:
            return

        v = uiFieldModel.get_value_as_int()
        uiLabel.text = "Select Type : " + str(v)

    def _build_fn(self):
        """The method that is called to build all the UI once the window is visible."""
        with ui.ScrollingFrame():
            with ui.VStack(height=0):
                self._build_new_header()
                self._build_options()
                self._build_axis(0, "Groups on X Axis")
                self._build_axis(1, "Groups on Y Axis")
                self._build_axis(2, "Groups on Z Axis")
                self._build_connection()
                self._build_import()

    #Pieces of UI Elements
    def _build_new_header(self):
        """Build the widgets of the "Source" group"""
        with ui.ZStack():
            #Background
            ui.Image(style={'image_url': "omniverse://localhost/Resources/images/meta_cloud_explorer_800.png", 'fill_policy': ui.FillPolicy.PRESERVE_ASPECT_CROP, 'alignment': ui.Alignment.CENTER_BOTTOM, 'fill_policy':ui.FillPolicy.PRESERVE_ASPECT_CROP})
            
            #Foreground
            with ui.VStack():
                ui.Spacer(height=5)
                ui.Label("Meta Cloud Explorer", style={"color": cl("#ffcc33"), "font_size":36}, alignment=ui.Alignment.CENTER, height=0)
                ui.Label("Cloud Infrastructure Scene Authoring Extension", style={"color": cl("#33FFCC"), "font_size":18}, alignment=ui.Alignment.CENTER, height=0)

            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=70)
                with ui.HStack(style=button_styles):
                    ui.Button("Load Groups", clicked_fn=lambda: self.load_stage("ByGroup"), name="subs", height=15)
                    ui.Button("Show/Hide Resources", clicked_fn=lambda: self.load_resources("ByGroup"), name="clr", height=15)
                    ui.Button("Clear the Stage", clicked_fn=lambda: self.clear_stage(), name="clr", height=15)
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=100)
                with ui.HStack():
                    ui.Button("Type View", clicked_fn=lambda: self.load_stage("ByType"), height=15)
                    ui.Button("Location View", clicked_fn=lambda: self.load_stage("ByLocation"), height=15)
                    ui.Button("Group View", clicked_fn=lambda: self.load_stage("ByGroup"), height=15)
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=130)
                with ui.HStack():
                    ui.Button("View All Types", clicked_fn=lambda: self.load_stage("AllTypes"), height=15)
                    ui.Button("View Templates", clicked_fn=lambda: self.load_stage("Templates"), height=15)
                    ui.Button("Show/Hide Costs", clicked_fn=lambda: self.load_stage("Network"), height=15)
                # with ui.HStack():
                #     ui.Button("Network View", clicked_fn=lambda: self.load_stage("ByNetwork"), height=15)
                #     ui.Button("Cost View", clicked_fn=lambda: self.load_stage("ByCost"), height=15)
                #     ui.Button("Template View", clicked_fn=lambda: self.load_stage("Template"), height=15)
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

    def _build_import(self):
        with ui.CollapsableFrame("Import Offline Files", name="group", collapsed=True):
            with ui.VStack():
                ui.Label("Resource Groups file path:", height=10, width=120)             
                with ui.HStack():                   
                    self._rg_data_import_field = ui.StringField(height=15)
                    self._rg_data_import_field.enabled = True
                    self._rg_data_import_field.model.set_value(str(self._dataStore._rg_csv_file_path))
                    self._dataStore._rg_csv_field_model = self._rg_data_import_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("rg"))
            
                ui.Label("All Resources file path:", height=10, width=120)             
                with ui.HStack():
                    self._rs_data_import_field = ui.StringField(height=15)
                    self._rs_data_import_field.enabled = True
                    self._rs_data_import_field.model.set_value(str(self._dataStore._rs_csv_file_path))
                    self._dataStore._rs_csv_field_model = self._rs_data_import_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("res"))

                ui.Button("Import Data Files", clicked_fn=lambda: self._dataManager.load_csv_files())            

    def _build_connection(self):
        with ui.CollapsableFrame("Cloud Connectors", name="group", collapsed=True):
            with ui.VStack():
                with ui.CollapsableFrame("Azure API Connection", name="group", collapsed=True):
                    with ui.VStack():
                        ui.Label("Tenant Id",width=self.label_width)
                        self._tenant_import_field = ui.StringField(height=15)
                        self._tenant_import_field.enabled = True
                        self._tenant_import_field.model.set_value(str(self._dataStore._azure_tenant_id))
                        self._dataStore._azure_tenant_id_model = self._tenant_import_field.model
                        ui.Label("Client Id",width=self.label_width)
                        self._client_import_field = ui.StringField(height=15)
                        self._client_import_field.enabled = True
                        self._client_import_field.model.set_value(str(self._dataStore._azure_client_id))
                        self._dataStore._azure_client_id_model = self._client_import_field.model
                        ui.Label("Subscription Id",width=self.label_width)
                        self._subscription_id_field = ui.StringField(height=15)
                        self._subscription_id_field.enabled = True
                        self._subscription_id_field.model.set_value(str(self._dataStore._azure_subscription_id))
                        self._dataStore._azure_subscription_id_model = self._subscription_id_field.model
                        ui.Label("Client Secret",width=self.label_width)
                        self._client_secret_field = ui.StringField(height=15, password_mode=True)
                        self._client_secret_field.enabled = True
                        self._client_secret_field.model.set_value(str(self._dataStore._azure_client_secret))
                        self._dataStore._azure_client_secret_model = self._client_secret_field.model
                        ui.Button("Connect to Azure", clicked_fn=lambda: self._dataManager.load_from_api())
                with ui.CollapsableFrame("AWS API Connection", name="group", collapsed=True):
                    with ui.VStack():
                        ui.Label("COMING SOON!",width=self.label_width)
                        #ui.Button("Connect to AWS", clicked_fn=lambda: self._dataManager.load_from_api())
                with ui.CollapsableFrame("GCP API Connection", name="group", collapsed=True):
                    with ui.VStack():
                        ui.Label("COMING SOON!",width=self.label_width)
                        #ui.Button("Connect to AWS", clicked_fn=lambda: self._dataManager.load_from_api())


    def _build_axis(self, axis_id, axis_name):
        """Build the widgets of the "X" or "Y" or "Z" group"""
        with ui.CollapsableFrame(axis_name, name="group", collapsed=True):
            with ui.VStack(height=0, spacing=SPACING):
                with ui.HStack():
                    ui.Label("Group Count", name="attribute_name", width=self.label_width)
                    ui.IntDrag(model=self._dataStore._options_count_models[axis_id], min=1, max=500)
                with ui.HStack():
                    ui.Label("Distance", name="attribute_name", width=self.label_width)
                    ui.FloatDrag(self._dataStore._options_dist_models[axis_id], min=250, max=5000)
                with ui.HStack():
                    ui.Label("Randomness", name="attribute_name", width=self.label_width)
                    ui.FloatDrag(self._dataStore._options_random_models[axis_id], min=1.0, max=10.0)

    def _build_options(self):
        with ui.CollapsableFrame("Composition", name="group", collapsed=True):
            with ui.VStack():
                with ui.HStack(height=15):
                    #self._dataStore._composition_scale_model = self._build_gradient_float_slider("Scale Factor", default_value=10, min=1, max=100)
                    ui.Label("Object Scale", name="attribute_name", width=self.label_width, min=1, max=100)
                    ui.FloatDrag(self._dataStore._composition_scale_model, min=1, max=100)
                    ui.Label("Up Axis", name="attribute_name", width=self.label_width)
                    ui.ComboBox(self._dataStore._primary_axis_model)


    def _build_help(self):
        ui.Line(style={"color": 0xff00b976}, height=20)

        with ui.VStack():
            with ui.HStack():
                ui.Button("Docs", clicked_fn=lambda: self.on_docs(), height=15)
                ui.Button("Code", clicked_fn=lambda: self.on_code(), height=15)
                ui.Button("Help", clicked_fn=lambda: self.on_help(), height=15)           
                    

    def __build_value_changed_widget(self):
        with ui.VStack(width=20):
            ui.Spacer(height=3)
            rect_changed = ui.Rectangle(name="attribute_changed", width=15, height=15, visible= False)
            ui.Spacer(height=4)
            with ui.HStack():
                ui.Spacer(width=3)
                rect_default = ui.Rectangle(name="attribute_default", width=5, height=5, visible= True)
        return rect_changed, rect_default    

    def _build_gradient_float_slider(self, label_name, default_value=0, min=0, max=1):
        def _on_value_changed(model, rect_changed, rect_defaul):
            if model.as_float == default_value:
                rect_changed.visible = False
                rect_defaul.visible = True
            else:
                rect_changed.visible = True
                rect_defaul.visible = False

        def _restore_default(slider):
            slider.model.set_value(default_value)

        with ui.HStack():
            ui.Label(label_name, name=f"attribute_name", width=self.label_width)
            with ui.ZStack():
                button_background_gradient = build_gradient_image(cls_button_gradient, 22, "button_background_gradient")
                with ui.VStack():
                    ui.Spacer(height=1.5)
                    with ui.HStack(width=200):
                        slider = ui.FloatSlider(name="float_slider", height=0, min=min, max=max)
                        slider.model.set_value(default_value)
                        ui.Spacer(width=1.5)
            ui.Spacer(width=4)
            rect_changed, rect_default = self.__build_value_changed_widget()
            # switch the visibility of the rect_changed and rect_default to indicate value changes
            slider.model.add_value_changed_fn(lambda model: _on_value_changed(model, rect_changed, rect_default))
            # add call back to click the rect_changed to restore the default value
            rect_changed.set_mouse_pressed_fn(lambda x, y, b, m: _restore_default(slider))
        return button_background_gradient
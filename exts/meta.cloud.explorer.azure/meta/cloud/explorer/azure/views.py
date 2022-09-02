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
from .button import SimpleImageButton

import sys
import asyncio
import webbrowser
#from turtle import width
import omni.ext
import omni.ui as ui
from omni.ui import color as cl
import os
import carb
import omni.kit.commands
import omni.kit.pipapi
from pxr import Sdf, Usd, Gf, UsdGeom
import omni
from pathlib import Path
import omni.kit.notification_manager as nm

from .omni_utils import get_selection
from .combo_box_model import ComboBoxModel
from .omni_utils import duplicate_prims
from .stage_manager import StageManager
from .import_fbx import convert_asset_to_usd
from .prim_utils import create_plane


import random
LABEL_WIDTH = 120
WINDOW_NAME = "Meta Cloud Explorer"
SPACING = 4

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data\\resources")


class MainView(ui.Window):
    """The class that represents the window"""
    def __init__(self, title: str, menu_path):
        self.__label_width = LABEL_WIDTH

        super().__init__(title, width=640, height=480)

        #Helper Class instances
        self._stageManager = StageManager()
        self._dataManager = DataManager.instance()
        self._dataStore = DataStore.instance()

        self._menu_path = menu_path
        self.set_visibility_changed_fn(self._on_visibility_changed)
        self._build_fn()

        self._dataManager.add_model_changed_callback(self.model_changed)
                
        # Apply the style to all the widgets of this window
        self.frame.style = meta_window_style
       
        # Set the function that is called to build widgets when the window is visible
        self.frame.set_build_fn(self._build_fn)

    def on_shutdown(self):
        self._win = None

    def show(self):
        self.visible = True
        self.focus()

    def hide(self):
        self.visible = False

    
    def _on_visibility_changed(self, visible):
        omni.kit.ui.get_editor_menu().set_value(self._menu_path, visible)
       
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

    #Callback invoked when data model changes
    def model_changed(self):
        carb.log_info("Model changed!")
        if (hasattr(self, "_grpLbl")):
            self._grpLbl.text = "GROUPS: " + str(len(self._dataStore._groups))
        if (hasattr(self, "_resLbl")):
            self._resLbl.text = "RESOURCES: " + str(len(self._dataStore._resources))


    def set_defaults(self, defType:str):
        if defType == "tower":
            asyncio.ensure_future(self.sendNotify("Tower defaults set... Select a VIEW", nm.NotificationStatus.INFO))   
            self._dataStore._symmetric_planes_model.set_value(True)
            self._dataStore._packing_algo_model.set_value(False)
            self._dataStore._options_count_models[0].set_value(2)
            self._dataStore._options_count_models[1].set_value(2)
            self._dataStore._options_count_models[2].set_value(60)
            self._dataStore._options_dist_models[0].set_value(500.0)
            self._dataStore._options_dist_models[1].set_value(500.0)
            self._dataStore._options_dist_models[2].set_value(250.0)
            self._dataStore._options_random_models[0].set_value(1)
            self._dataStore._options_random_models[1].set_value(1)
            self._dataStore._options_random_models[2].set_value(1)
            self.clear_stage()
        if defType == "symmetric":
            asyncio.ensure_future(self.sendNotify("Symmetric defaults set... Select a VIEW", nm.NotificationStatus.INFO))   
            self._dataStore._symmetric_planes_model.set_value(True)
            self._dataStore._packing_algo_model.set_value(False)
            self._dataStore._options_count_models[0].set_value(4)
            self._dataStore._options_count_models[1].set_value(4)
            self._dataStore._options_count_models[2].set_value(40)
            self._dataStore._options_dist_models[0].set_value(500.0)
            self._dataStore._options_dist_models[1].set_value(500.0)
            self._dataStore._options_dist_models[2].set_value(250.0)
            self._dataStore._options_random_models[0].set_value(1)
            self._dataStore._options_random_models[1].set_value(1)
            self._dataStore._options_random_models[2].set_value(1)
            self.clear_stage()
        if defType == "islands":
            asyncio.ensure_future(self.sendNotify("Island defaults set... Select a VIEW", nm.NotificationStatus.INFO))   
            self._dataStore._symmetric_planes_model.set_value(False)
            self._dataStore._packing_algo_model.set_value(False)
            self._dataStore._options_count_models[0].set_value(20)
            self._dataStore._options_count_models[1].set_value(4)
            self._dataStore._options_count_models[2].set_value(4)
            self._dataStore._options_dist_models[0].set_value(500.0)
            self._dataStore._options_dist_models[1].set_value(500.0)
            self._dataStore._options_dist_models[2].set_value(250.0)
            self._dataStore._options_random_models[0].set_value(1)
            self._dataStore._options_random_models[1].set_value(1)
            self._dataStore._options_random_models[2].set_value(1)
            self.clear_stage()
        if defType == "packer":
            asyncio.ensure_future(self.sendNotify("Packer algo enabled... Select a VIEW", nm.NotificationStatus.INFO))   
            self._dataStore._symmetric_planes_model.set_value(False)
            self._dataStore._packing_algo_model.set_value(True)
            self._dataStore._options_count_models[0].set_value(4)
            self._dataStore._options_count_models[1].set_value(4)
            self._dataStore._options_count_models[2].set_value(20)
            self._dataStore._options_dist_models[0].set_value(500.0)
            self._dataStore._options_dist_models[1].set_value(500.0)
            self._dataStore._options_dist_models[2].set_value(250.0)
            self._dataStore._options_random_models[0].set_value(1)
            self._dataStore._options_random_models[1].set_value(1)
            self._dataStore._options_random_models[2].set_value(1)
            self.clear_stage()

    def select_planes(self):
        self._stageManager.Select_Planes()

    #Load a fresh stage
    def load_stage(self, viewType: str):
        self._dataStore._last_view_type = viewType
        self._dataStore.Save_Config_Data()

        self.clear_stage()
        
        self._stageManager.ShowStage(viewType)

    #load the resource onto the stage
    def load_resources(self):
        self._stageManager.LoadResources(self._dataStore._last_view_type)

    #change the background shaders to reflect costs
    def showHideCosts(self):
        self._stageManager.ShowCosts()

    # Clear the stage
    def clear_stage(self):

        stage = omni.usd.get_context().get_stage()
        root_prim = stage.GetPrimAtPath("/World")
        if (root_prim.IsValid()):
            stage.RemovePrim("/World")
            
        ground_prim = stage.GetPrimAtPath('/GroundPlane')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/GroundPlane')                
            
        ground_prim = stage.GetPrimAtPath('/RGrp')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/RGrp')
            
        ground_prim = stage.GetPrimAtPath('/Loc')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Loc')
            
        ground_prim = stage.GetPrimAtPath('/AAD')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/AAD') 
            
        ground_prim = stage.GetPrimAtPath('/Subs')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Subs')
            
        ground_prim = stage.GetPrimAtPath('/Type')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Type')
            
        ground_prim = stage.GetPrimAtPath('/Cost')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Cost')
            
        ground_prim = stage.GetPrimAtPath('/Looks')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Looks')
            
        ground_prim = stage.GetPrimAtPath('/Tag')
        if (ground_prim.IsValid()):
            stage.RemovePrim('/Tag')
            

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
                self._build_image_presets()
                self._build_options()
                self._build_connection()
                self._build_import()
                #self._build_about()

    # slider = ui.FloatSlider(min=1.0, max=150.0)
    # slider.model.as_float = 10.0
    # label = ui.Label("Omniverse", style={"color": ui.color(0), "font_size": 7.0})
    

    #Pieces of UI Elements
    def _build_new_header(self):
        """Build the widgets of the "Source" group"""
        #with ui.ZStack():
            #Background
            #ui.Image(style={'image_url': "omniverse://localhost/Resources/images/meta_cloud_explorer_800.png", 'fill_policy': ui.FillPolicy.PRESERVE_ASPECT_CROP, 'alignment': ui.Alignment.CENTER_BOTTOM, 'fill_policy':ui.FillPolicy.PRESERVE_ASPECT_CROP})
            
            #Foreground
        with ui.VStack():
            with ui.HStack():
                with ui.VStack():
                    with ui.HStack():
                        with ui.VStack():
                            ui.Label("Meta Cloud Explorer", style={"color": cl("#d85318"), "font_size":36 }, alignment=ui.Alignment.LEFT, height=0)
                            ui.Label("Cloud Infrastructure Scene Authoring Extension", style={"color": cl("#3f84a5"), "font_size":18}, alignment=ui.Alignment.LEFT, height=0)                              
                        with ui.VStack():
                            ui.Spacer(height=10)                                    

                            self._grpLbl = ui.Label("GROUPS: " + str(len(self._dataStore._groups)),style={"color": 0xFF008976, "font_size":18 }, alignment=ui.Alignment.RIGHT, height=0)
                            self._resLbl = ui.Label("RESOURCES: " + str(len(self._dataStore._resources)), style={"color": 0xFF008976, "font_size":18}, alignment=ui.Alignment.RIGHT, height=0)

        with ui.VStack(height=0, spacing=SPACING):
            #ui.Spacer(height=80)
            with ui.HStack(style=button_styles):
                ui.Button("Group VIEW", clicked_fn=lambda: self.load_stage("ByGroup"), name="subs", height=35)
                ui.Button("Type VIEW", clicked_fn=lambda: self.load_stage("ByType"), name="subs",height=35)
                ui.Button("Show Resources", clicked_fn=lambda: self.load_resources(), name="clr", height=35)
                
        with ui.VStack(height=0, spacing=SPACING):
            #ui.Spacer(height=120)
            with ui.HStack(style=button_styles):
                ui.Button("Location VIEW", clicked_fn=lambda: self.load_stage("ByLocation"), name="subs", height=35)
                ui.Button("Subscription VIEW", clicked_fn=lambda: self.load_stage("BySub"), name="subs", height=15)
                ui.Button("Clear Stage", clicked_fn=lambda: self.clear_stage(), name="clr", height=35)
                
                
        with ui.VStack(height=0, spacing=SPACING):
            #ui.Spacer(height=160)
            with ui.HStack(style=button_styles):
                ui.Button("Show/Hide Costs", clicked_fn=lambda: self.showHideCosts(),name="subs", height=35)
                ui.Button("Show Templates", clicked_fn=lambda: self.load_stage("Templates"),name="subs", height=15)
                ui.Button("Select All Groups", clicked_fn=lambda: self.select_planes(),name="clr", height=35)
            
            # with ui.HStack():
            #     ui.Button("Network View", clicked_fn=lambda: self.load_stage("ByNetwork"), height=15)
            #     ui.Button("Cost View", clicked_fn=lambda: self.load_stage("ByCost"), height=15)
            #     ui.Button("Template View", clicked_fn=lambda: self.load_stage("Template"), height=15)
       

    def _build_import(self):
        with ui.CollapsableFrame("Import Offline Files", name="group", collapsed=True, style={"color": 0xFF008976, "font_size":20}):
            with ui.VStack(style={"color": 0xFFFFFFFF, "font_size":16}):
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
                with ui.HStack():
                    ui.Button("Clear imported Data", clicked_fn=lambda: self._dataManager.wipe_data())            
                    ui.Button("Import Data Files", clicked_fn=lambda: self._dataManager.load_csv_files())            
                with ui.HStack():
                    ui.Button("Load Sample Dataset", clicked_fn=lambda: self._dataManager.load_sample())            
                    ui.Button("Load Sample Resources", clicked_fn=lambda: self._dataManager.load_sample_resources())                                

    def _build_connection(self):

        def _on_value_changed(field:str, value):
            if field == "tenant":
                self._dataStore._azure_tenant_id = value
            if field == "client":
                self._dataStore._azure_client_id = value
            if field == "subid":
                self._dataStore._azure_subscription_id = value
            if field == "secret":
                self._dataStore._azure_client_secret = value


        # def setText(label, text):
        #     '''Sets text on the label'''
        #     # This function exists because lambda cannot contain assignment
        #     label.text = f"You wrote '{text}'"

        with ui.CollapsableFrame("Cloud API Connection", name="group", collapsed=True, style={"color": 0xFF008976, "font_size":20}):
            with ui.VStack(style={"color": 0xFFFFFFFF, "font_size":16}):
                # with ui.CollapsableFrame("Azure API Connection", name="group", collapsed=True):
                #     with ui.VStack():
                        ui.Label("Tenant Id",width=self.label_width)
                        self._tenant_import_field = ui.StringField(height=15)
                        self._tenant_import_field.enabled = True
                        self._tenant_import_field.model.set_value(str(self._dataStore._azure_tenant_id))
                        self._tenant_import_field.model.add_value_changed_fn(lambda m: _on_value_changed("tenant", m.get_value_as_string()))
                        
                        ui.Label("Client Id",width=self.label_width)
                        self._client_import_field = ui.StringField(height=15)
                        self._client_import_field.enabled = True
                        self._client_import_field.model.set_value(str(self._dataStore._azure_client_id))
                        self._client_import_field.model.add_value_changed_fn(lambda m: _on_value_changed("client", m.get_value_as_string()))

                        ui.Label("Subscription Id",width=self.label_width)
                        self._subscription_id_field = ui.StringField(height=15)
                        self._subscription_id_field.enabled = True
                        self._subscription_id_field.model.set_value(str(self._dataStore._azure_subscription_id))
                        self._subscription_id_field.model.add_value_changed_fn(lambda m: _on_value_changed("subid", m.get_value_as_string()))
                        
                        ui.Label("Client Secret",width=self.label_width)
                        self._client_secret_field = ui.StringField(height=15, password_mode=True)
                        self._client_secret_field.enabled = True
                        self._client_secret_field.model.set_value(str(self._dataStore._azure_client_secret))
                        self._client_secret_field.model.add_value_changed_fn(lambda m: _on_value_changed("secret", m.get_value_as_string()))
                        
                        ui.Button("Connect to Azure", clicked_fn=lambda: self._dataManager.load_from_api())



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


    def _build_image_presets(self):
        def _on_clicked(self, source):
            self.set_defaults(source)
#style={"color": 0xFF008976, "font_size":20}
        with ui.CollapsableFrame("Quickstarts", name="group", collapsed=True, style={"font_size":20}): 
            with ui.VStack():
                with ui.HStack(style={}):
                    with ui.VStack():
                        ui.Label("TOWER", name="attribute_name", width=self.label_width)
                        SimpleImageButton(image="omniverse://localhost/Resources/images/tower.png", size=150, name="twr_btn", clicked_fn=lambda: _on_clicked(self, source="tower"))
                    with ui.VStack():
                        ui.Label("ISLANDS", name="attribute_name", width=self.label_width)
                        SimpleImageButton(image="omniverse://localhost/Resources/images/islands.png", size=150, name="isl_btn", clicked_fn=lambda: _on_clicked(self, source="islands"))
                    with ui.VStack():
                        ui.Label("SYMMETRIC", name="attribute_name", width=self.label_width)
                        SimpleImageButton(image="omniverse://localhost/Resources/images/Symmetric.png", size=150, name="sym_btn", clicked_fn=lambda: _on_clicked(self, source="symmetric"))
                    with ui.VStack():
                        ui.Label("BIN PACKER", name="attribute_name", width=self.label_width)
                        SimpleImageButton(image="omniverse://localhost/Resources/images/packer.png", size=150, name="row_btn",clicked_fn=lambda: _on_clicked(self, source="packer"))

                    #ui.Image("../../../data/Resources/images/tower.png", fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT, alignment=ui.Alignment.CENTER,style={'border_radius':10})
                    #ui.Image("omniverse://localhost/Resources/images/Symmetric.png", fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT, alignment=ui.Alignment.CENTER,style={'border_radius':10})
                    #ui.Image("omniverse://localhost/Resources/images/rows.png", fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT, alignment=ui.Alignment.CENTER,style={'border_radius':10})


    def _build_image_options(self):
        with ui.CollapsableFrame("Group Images", name="group", collapsed=True):        
            with ui.VStack(height=0, spacing=SPACING):
                with ui.HStack():
                    ui.Label("BG Low Cost", name="attribute_name", width=self.label_width)
                    self._bgl_data_import_field = ui.StringField(height=15)
                    self._bgl_data_import_field.enabled = True
                    self._bgl_data_import_field.model.set_value(str(self._dataStore._bgl_file_path))
                    self._dataStore._bgl_field_model = self._bgl_data_import_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("bgl"))
                    
                with ui.HStack():
                    ui.Label("Bg Mid Cost", name="attribute_name", width=self.label_width)
                    self._bgm_data_import_field = ui.StringField(height=15)
                    self._bgm_data_import_field.enabled = True
                    self._bgm_data_import_field.model.set_value(str(self._dataStore._bgm_file_path))
                    self._dataStore._bgm_field_model = self._bgm_data_import_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("bgm"))
                    
                with ui.HStack():
                    ui.Label("BgHighCost", name="attribute_name", width=self.label_width)
                    self._bgh_data_import_field = ui.StringField(height=15)
                    self._bgh_data_import_field.enabled = True
                    self._bgh_data_import_field.model.set_value(str(self._dataStore._bgh_file_path))
                    self._dataStore._bgh_field_model = self._bgh_data_import_field.model
                    ui.Button("Load", width=40, clicked_fn=lambda: self._dataManager.select_file("bgh"))                    


    def _build_options(self, default_value=0, min=0, max=1):
        def _on_value_changed_bp(model):
            self._dataStore._use_packing_algo = model.as_bool
        def _on_value_changed_sg(model):
            self._dataStore._use_symmetric_planes = model.as_bool

        with ui.CollapsableFrame("Scene Composition Options", name="group", collapsed=True, style={"color": 0xFF008976, "font_size":20}): 
            with ui.VStack(height=0, spacing=SPACING, style={"color": 0xFFFFFFFF, "font_size":16}):
                with ui.HStack():
                    #self._dataStore._composition_scale_model = self._build_gradient_float_slider("Scale Factor", default_value=10, min=1, max=100)
                    ui.Label("Object Scale", name="attribute_name", width=self.label_width, min=1, max=100)
                    ui.FloatDrag(self._dataStore._composition_scale_model, min=1, max=100)
                    self._dataStore._composition_scale_model.set_value(self._dataStore._scale_model)
                with ui.HStack():
                    ui.Label("Use Symmetric groups?", name="attribute_name", width=self.label_width)
                    cb1 = ui.CheckBox(self._dataStore._symmetric_planes_model)                    
                    cb1.model.add_value_changed_fn(lambda model: _on_value_changed_sg(model))
                with ui.HStack():
                    ui.Label("Use Bin Packing?", name="attribute_name", width=self.label_width)
                    cb2 = ui.CheckBox(self._dataStore._packing_algo_model)                    
                    cb2.model.add_value_changed_fn(lambda model: _on_value_changed_bp(model))

                self._build_image_options()

                self._build_axis(0, "Groups on X Axis")
                self._build_axis(1, "Groups on Y Axis")
                self._build_axis(2, "Groups on Z Axis")


                    
    # def _build_about(self):
    #     with ui.VStack():
    #         ui.Label("Meta Cloud Explorer (Azure)", style={"color": 0xFF008976, "font_size":36}, alignment=ui.Alignment.LEFT, height=0)
    #         ui.Label("An Omniverse Scene Authoring extension", height=10, name="TItle", alignment=ui.Alignment.LEFT)
    #         ui.Line(style={"color": 0xff00b976}, height=20)

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

    
    async def sendNotify(self, message:str, status:nm.NotificationStatus):
        
        # https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.kit.notification_manager/docs/index.html?highlight=omni%20kit%20notification_manager#

        import omni.kit.notification_manager as nm
        ok_button = nm.NotificationButtonInfo("OK", on_complete=self.clicked_ok)

        nm.post_notification(
            message,
            hide_after_timeout=True,
            duration=5,
            status=status,
            button_infos=[]
        )        
        
        #Let the Ui breathe ;)
        for x in range(5):
            await omni.kit.app.get_app().next_update_async()    

    def clicked_ok(self):
        pass

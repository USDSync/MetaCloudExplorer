
__all__ = ["Save_Config_Data", "Load_Config_Data"]

import carb
from .Singleton import Singleton
import omni.ui as ui
from .combo_box_model import ComboBoxModel
from pathlib import Path
import os

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.joinpath("temp")
RES_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data\\resources")


@Singleton
class DataStore():
    def __init__(self):

        print("DataStore initialized")

        #Azure Resoruce Groups
        #NAME,SUBSCRIPTION,LOCATION
        self._groups = {}

        #All the reosurces
        #NAME,TYPE,RESOURCE GROUP,LOCATION,SUBSCRIPTION, LMCOST
        self._resources = {}        

        #aggregated data (counts)
        self._aad_count = {}
        self._subscription_count = {}
        self._location_count = {}
        self._group_count = {}
        self._type_count = {}
        self._tag_count = {}

        #aggregated data (costs)
        self._aad_cost = {}
        self._subscription_cost = {}
        self._location_cost = {}
        self._group_cost = {}
        self._type_cost = {}
        self._tag_cost = {}

        #mapped resources (indexes)
        self._map_aad = {}
        self._map_subscription = {}
        self._map_location = {}
        self._map_group = {}
        self._map_type = {}
        self._map_tag = {}

        #track where the data last came from (state)
        self._source_of_data = ""
        self._use_symmetric_planes = False
        self._use_packing_algo = True
        self._show_info_widgets = True
        self._last_view_type = "ByGroup" # ByGroup, ByLocation, ByType, BySub, ByTag
        self._scale_model = 1.0

        #temporary arrays
        #Calc Plane sizes based on items in group
        self._lcl_sizes = [] #Plane  sizes determined by resource counts
        self._lcl_groups = [] #Group data for creating planes
        self._lcl_resources = [] #Resources to show on stage


        #Variables for files to import (UI settings)
        self._rg_csv_file_path = ""
        self._rg_csv_field_model = ui.SimpleStringModel()
        self._rs_csv_file_path = ""        
        self._rs_csv_field_model = ui.SimpleStringModel()
        self._bgl_file_path = ""        
        self._bgl_field_model = ui.SimpleStringModel()
        self._bgm_file_path = ""        
        self._bgm_field_model = ui.SimpleStringModel()
        self._bgh_file_path = ""        
        self._bgh_field_model = ui.SimpleStringModel()

        #azure connection info 
        self._azure_tenant_id = ""
        self._azure_tenant_id_model =ui.SimpleStringModel()
        self._azure_client_id = ""
        self._azure_client_id_model = ui.SimpleStringModel()
        self._azure_client_secret = ""
        self._azure_client_secret_model = ui.SimpleStringModel()
        self._azure_subscription_id = ""
        self._azure_subscription_id_model = ui.SimpleStringModel()

        #composition options (UI settings)
        self._symmetric_planes_model = ui.SimpleBoolModel(False)
        self._packing_algo_model = ui.SimpleBoolModel(True)
        self._show_info_widgets_model = ui.SimpleBoolModel(True)
        self._primary_axis_model = ComboBoxModel("Z", "X", "Y") # track which Axis is up
        self._shape_up_axis_model = ComboBoxModel("Z", "X", "Y") # track which Axis is up for the shape placement
        self._composition_scale_model = ui.SimpleFloatModel()
        self._options_count_models = [ui.SimpleIntModel(), ui.SimpleIntModel(), ui.SimpleIntModel()]
        self._options_dist_models = [ui.SimpleFloatModel(), ui.SimpleFloatModel(), ui.SimpleFloatModel()]
        self._options_random_models = [ui.SimpleFloatModel(), ui.SimpleFloatModel(), ui.SimpleFloatModel()]

        self._composition_scale_model.as_float = 1.0
        self._options_count_models[0].as_int = 10
        self._options_count_models[1].as_int = 10
        self._options_count_models[2].as_int = 1
        self._options_dist_models[0].as_float = 250
        self._options_dist_models[1].as_float = 250
        self._options_dist_models[2].as_float = 250
        self._options_random_models[0].as_float = 1.0
        self._options_random_models[1].as_float = 1.0
        self._options_random_models[2].as_float = 1.0
        self.Load_Config_Data()

    def wipe_data(self):
        self._groups.clear()
        self._resources.clear()

        self._subscription_count = {}
        self._location_count = {}
        self._group_count = {}
        self._type_count = {}
        self._tag_count = {}

        self._subscription_cost = {}
        self._location_cost = {}
        self._group_cost = {}
        self._type_cost = {}
        self._tag_cost = {}
        
        self._map_aad = {}
        self._map_subscription = {}
        self._map_location = {}
        self._map_group = {}
        self._map_type = {}
        self._map_tag = {}

        self._lcl_sizes = [] 
        self._lcl_groups = [] 
        self._lcl_resources = [] 

        carb.log_info("Data Cleared.")


    def Save_Config_Data(self):
        settings = carb.settings.get_settings()
        if self._rg_csv_file_path != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/rg_csv_file_path", self._rg_csv_file_path)
        if self._rs_csv_file_path != "":            
            settings.set("/persistent/exts/meta.cloud.explorer.azure/rs_csv_file_path", self._rs_csv_file_path)
        if self._azure_tenant_id != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/azure_tenant_id", self._azure_tenant_id)
        if self._azure_client_id != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/azure_client_id", self._azure_client_id)
        if self._azure_subscription_id != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/azure_subscription_id", self._azure_subscription_id)
        if self._source_of_data != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/last_data_source", self._source_of_data)
        if self._bgl_file_path != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/bgl_file_path", self._bgl_file_path)
        if self._bgm_file_path != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/bgm_file_path", self._bgm_file_path)
        if self._bgh_file_path != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/bgh_file_path", self._bgh_file_path)
        if self._last_view_type != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/last_view_type", self._last_view_type)
        if self._options_count_models[0].as_int >0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/x_group_count", self._options_count_models[0].as_int)
        if self._options_count_models[1].as_int >0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/y_group_count", self._options_count_models[1].as_int)
        if self._options_count_models[2].as_int >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/z_group_count", self._options_count_models[2].as_int)            
        if self._options_dist_models[0].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/x_dist_count", self._options_dist_models[0].as_float)
        if self._options_dist_models[1].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/y_dist_count", self._options_dist_models[1].as_float)
        if self._options_dist_models[2].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/z_dist_count", self._options_dist_models[2].as_float)            
        if self._options_random_models[0].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/x_random_count", self._options_random_models[0].as_float)
        if self._options_random_models[1].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/y_random_count", self._options_random_models[1].as_float)
        if self._options_random_models[2].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/z_random_count", self._options_random_models[2].as_float)                        

        settings.set("/persistent/exts/meta.cloud.explorer.azure/show_info_widgets", self._show_info_widgets)                        


    #Load Saved config data                        
    def Load_Config_Data(self):
        settings = carb.settings.get_settings()
        self._rg_csv_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/rg_csv_file_path")
        self._rs_csv_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/rs_csv_file_path")
        self._azure_tenant_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_tenant_id")
        self._azure_client_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_client_id")
        self._azure_subscription_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_subscription_id")

        try:
            self._azure_client_secret = os.getenv('MCE_CLIENT_SECRET')
        except:
            self._azure_client_secret= ""
            
        self._source_of_data = settings.get("/persistent/exts/meta.cloud.explorer.azure/last_data_source")
        self._bgl_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/bgl_file_path")
        self._bgm_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/bgm_file_path")
        self._bgh_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/bgh_file_path")
        self._last_view_type= settings.get("/persistent/exts/meta.cloud.explorer.azure/last_view_type")
        self._show_info_widgets= settings.get("/persistent/exts/meta.cloud.explorer.azure/show_info_widgets")

        try:
            self._options_count_models[0].set_value(int(settings.get("/persistent/exts/meta.cloud.explorer.azure/x_group_count")))
            self._options_count_models[1].set_value(int(settings.get("/persistent/exts/meta.cloud.explorer.azure/y_group_count")))
            self._options_count_models[2].set_value(int(settings.get("/persistent/exts/meta.cloud.explorer.azure/z_group_count")))
            self._options_dist_models[0].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/x_dist_count")))
            self._options_dist_models[1].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/y_dist_count")))
            self._options_dist_models[2].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/z_dist_count")))
            self._options_random_models[0].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/x_random_count")))
            self._options_random_models[1].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/y_random_count")))
            self._options_random_models[2].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/z_random_count")))
        except: #set defualts
            self._last_view_type = "ByGroup"
            self._composition_scale_model.set_value(1.0)
            self._options_count_models[0].set_value(10)
            self._options_count_models[1].set_value(10)
            self._options_count_models[2].set_value(1)
            self._options_dist_models[0].set_value(250)
            self._options_dist_models[1].set_value(250)
            self._options_dist_models[2].set_value(250)
            self._options_random_models[0].set_value(1.0)
            self._options_random_models[1].set_value(1.0)
            self._options_random_models[2].set_value(1)

        #set defaults
        if self._bgl_file_path is None: 
            self._bgl_file_path = RES_PATH.joinpath("grid_green.png")
            self._bgm_file_path = RES_PATH.joinpath("grid_blue.png")
            self._bgh_file_path = RES_PATH.joinpath("grid_red.png")
            self.Save_Config_Data()


#-- SINGLETON SUPPORT

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

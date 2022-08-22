import carb
from .Singleton import Singleton
import omni.ui as ui
from .combo_box_model import ComboBoxModel

@Singleton
class DataStore():
    def __init__(self):

        print("DataStore initialized")
        #Azure Resoruce Groups
        #NAME,SUBSCRIPTION,LOCATION
        self._groups = {}

        #All the reosurces
        #NAME,TYPE,RESOURCE GROUP,LOCATION,SUBSCRIPTION
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
        self._show_cost_data = False
        self._use_symmetric_planes = False

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
        self._show_costs_model = ui.SimpleBoolModel(False)
        self._symmetric_planes_model = ui.SimpleBoolModel(False)
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

    #Serialize persistant config data
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
        if self._bg_file_path != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/bg_file_path", self._bg_file_path)
                        
    #Load Saved config data                        
    def Load_Config_Data(self):
        settings = carb.settings.get_settings()
        self._rg_csv_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/rg_csv_file_path")
        self._rs_csv_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/rs_csv_file_path")
        self._azure_tenant_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_tenant_id")
        self._azure_client_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_client_id")
        self._azure_subscription_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_subscription_id")
        self._source_of_data = settings.get("/persistent/exts/meta.cloud.explorer.azure/last_data_source")
        self._bg_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/bg_file_path")

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

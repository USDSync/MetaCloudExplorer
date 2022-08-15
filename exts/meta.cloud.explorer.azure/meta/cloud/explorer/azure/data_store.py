import carb
from .Singleton import Singleton
import omni.ui as ui
from .combo_box_model import ComboBoxModel

@Singleton
class DataStore():
    def __init__(self):

        print("DataStore initialized")
        #NAME,SUBSCRIPTION,LOCATION
        self._groups = {}

        #NAME,TYPE,RESOURCE GROUP,LOCATION,SUBSCRIPTION
        self._resources = {}        

        #aggregated data
        self._subscription_count = {}
        self._location_count = {}
        self._group_count = {}
        self._type_count = {}
        self._tag_count = {}

        #Variables for giles to import
        self._rg_csv_file_path = ""
        self._rs_csv_file_path = ""
        self._rg_csv_field_model = ""
        self._rs_csv_field_model = ""

        #azure connection info
        self._azure_tenant_id = ""
        self._azure_tenant_id_model =""
        self._azure_client_id = ""
        self._azure_client_id_model = ""
        self._azure_client_secret = ""
        self._azure_client_secret_model = ""
        self._azure_subscription_id = ""
        self._azure_subscription_id_model = ""

        #composition options
        self._primary_axis_model = ComboBoxModel("X", "Y", "Z") # track which Axis is up
        self._composition_scale_model = ui.SimpleFloatModel()
        self._options_count_models = [ui.SimpleIntModel(), ui.SimpleIntModel(), ui.SimpleIntModel()]
        self._options_dist_models = [ui.SimpleFloatModel(), ui.SimpleFloatModel(), ui.SimpleFloatModel()]
        self._options_random_models = [ui.SimpleFloatModel(), ui.SimpleFloatModel(), ui.SimpleFloatModel()]

        self._composition_scale_model.as_float = 1.0
        self._options_count_models[0].as_int = 10
        self._options_count_models[1].as_int = 10
        self._options_count_models[2].as_int = 10
        self._options_dist_models[0].as_float = 500
        self._options_dist_models[1].as_float = 500
        self._options_dist_models[2].as_float = 500

        self.Load_Config_Data()

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


    def Load_Config_Data(self):
        settings = carb.settings.get_settings()
        self._rg_csv_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/rg_csv_file_path")
        self._rs_csv_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/rs_csv_file_path")
        self._azure_tenant_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_tenant_id")
        self._azure_client_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_client_id")
        self._azure_subscription_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_subscription_id")

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

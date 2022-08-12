from .Singleton import Singleton

@Singleton
class DataStore():
    def __init__(self):

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

        self._rg_csv_file_path = ""
        self._rs_csv_file_path = ""
        self._rg_csv_field_model = ""
        self._rs_csv_field_model = ""

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

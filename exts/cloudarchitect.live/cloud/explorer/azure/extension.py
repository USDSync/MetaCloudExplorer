import sys
import carb
import omni.ext
from .sub_models import SubscriptionModel
from .rg_models import ResourceGroupModel
from .rs_models import ResourceModel
from .views import MainView
import asyncio
from functools import partial
import omni.ext
import omni.kit.ui
import omni.ui as ui
import omni.kit.pipapi

#omni.kit.pipapi.install("pandas", module="pandas", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
sys.path.append("D:/python37/lib/site-packages")
#print(sys.modules.keys())

omni.kit.pipapi.install("azure-identity", module="azure-identity", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
omni.kit.pipapi.install("azure-mgmt-resource", module="azure-mgmt-resource", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )

company = "Company1"

from azure.mgmt.resource import ResourceManagementClient
from azure.identity import AzureCliCredential

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`)
# will be instantiated when extension gets enabled and `on_startup(ext_id)` will be called.
# Later when extension gets disabled on_shutdown() is called
class AzureDigitalTwinExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.

    WINDOW_NAME = "Cloud Explorer (Azure)"
    MENU_PATH = f"Window/{WINDOW_NAME}"

    def on_startup(self, ext_id):
        carb.log_info(f"[cloud.explorer.azure]] Cloud Explorer startup")

        Model = SubscriptionModel(company)
        RGModel = ResourceGroupModel(company)
        RSModel = ResourceModel(company)
        self._window = MainView(Model, RGModel, RSModel, '/World')

        ui.Workspace.set_show_window_fn(AzureDigitalTwinExtension.WINDOW_NAME, partial(self.show_window, None))

        # Put the new menu
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(
                AzureDigitalTwinExtension.MENU_PATH, self.show_window, toggle=True, value=True
            )

        # Show the window. It will call `self.show_window`
        ui.Workspace.show_window(AzureDigitalTwinExtension.WINDOW_NAME)

    def on_shutdown(self):
        carb.log_info(f"[cloud.explorer.azure]] Cloud Explorer shutdown")
        
        self._menu = None
        if self._window:
            self._window.destroy()
            self._window = None

        # Deregister the function that shows the window from omni.ui
        ui.Workspace.set_show_window_fn(AzureDigitalTwinExtension.WINDOW_NAME, None)


    def _set_menu(self, value):
        """Set the menu to create this window on and off"""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(AzureDigitalTwinExtension.MENU_PATH, value)

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None

    def _visiblity_changed_fn(self, visible):
        # Called when the user pressed "X"
        self._set_menu(visible)
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, menu, value):
        if value:
            self._window = MainView(SubscriptionModel(company), ResourceGroupModel(company), ResourceModel(company), '/World')
            self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
        elif self._window:
            self._window.visible = False

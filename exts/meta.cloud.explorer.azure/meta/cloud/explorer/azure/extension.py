import sys
import carb
import omni.ext
import asyncio
from functools import partial
import omni.ext
import omni.kit.ui
import omni.ui as ui
import omni.kit.pipapi
from .views import MainView, WINDOW_NAME

omni.kit.pipapi.install("azure-identity", module="azure-identity", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
omni.kit.pipapi.install("azure-mgmt-resource", module="azure-mgmt-resource", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )

#omni.kit.pipapi.install("pandas", module="pandas", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
#sys.path.append("D:/python37/lib/site-packages")
#print(sys.modules.keys())

from azure.mgmt.resource import ResourceManagementClient
from azure.identity import AzureCliCredential

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`)
# will be instantiated when extension gets enabled and `on_startup(ext_id)` will be called.
# Later when extension gets disabled on_shutdown() is called
class MetaCloudExplorerAzure(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.

    MENU_PATH = f"Window/{WINDOW_NAME}"

    def on_startup(self, ext_id):

        carb.log_info("[meta.cloud.explorer.azure.extension] MetaCloudExplorer startup")

        self._menu_path = f"Window/{WINDOW_NAME}"
        self._window = None
        self._menu = omni.kit.ui.get_editor_menu().add_item(self._menu_path, self._on_menu_click, True)


    def on_shutdown(self):
        carb.log_info("[meta.cloud.explorer.azure.extension] MetaCloudExplorer shutdown")

        omni.kit.ui.get_editor_menu().remove_item(self._menu)
        if hasattr(self, "_window"):
            if self._window is not None:
                self._window.destroy()
                self._window = None

    def _on_menu_click(self, menu, toggled):
        """Handles showing and hiding the window from the 'Windows' menu."""
        if toggled:
            if self._window is not None:
                self._window.show()
            else:
                self._window = MainView(WINDOW_NAME, self._menu_path)
        else:
            if hasattr(self, "_window"):
                self._window.hide()

        # Deregister the function that shows the window from omni.ui
        #ui.Workspace.set_show_window_fn(MetaCloudExplorerAzure.WINDOW_NAME, None)


import sys
import carb
import omni.ext
import asyncio
from functools import partial
import omni.ext
import omni.kit.ui
import omni.ui as ui
import omni.kit.pipapi
# Requires Code 2022.1.2+ - Blocked by typing_extensions incompatibility
#from omni.kit.viewport.utility import get_active_viewport_window
import omni.kit.viewport_legacy as vp


from .views import MainView, WINDOW_NAME
from .viewport_scene import ViewportScene
from .object_info_model import ObjectInfoModel

#omni.kit.pipapi.install("azure-identity", module="azure-identity", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
#omni.kit.pipapi.install("azure-mgmt-resource", module="azure-mgmt-resource", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )

#omni.kit.pipapi.install("pandas", module="pandas", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
sys.path.append("D:/python37/lib/site-packages")
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
        self._ext_id = ext_id
        self._menu_path = f"Window/{WINDOW_NAME}"
        self._window = None
        self._menu = omni.kit.ui.get_editor_menu().add_item(self._menu_path, self._on_menu_click, True)

    #for second, third viewport
    @staticmethod
    def create_new_viewport_overlay(vp_win):
        obj_info_model = ObjectInfoModel()
        viewport_scene = ViewportScene(vp_win=vp_win,model=obj_info_model)
        viewport_scene.build_viewport_overlay()

    @staticmethod
    def on_window_created(win_handle):
        """Add a new ReticleOverlay whenever a new viewport window is created.

        Args:
            win_handle (WindowHandle): The window that was created.
        """
        if win_handle.title.startswith("Viewport"):
            MetaCloudExplorerAzure.create_new_obj_info_overlay(win_handle)

    def on_shutdown(self):
        carb.log_info("[meta.cloud.explorer.azure.extension] MetaCloudExplorer shutdown")

        omni.kit.ui.get_editor_menu().remove_item(self._menu)
        if self._window is not None:
            self._window.destroy()
            self._window = None

    def _on_menu_click(self, menu, toggled):
        """Handles showing and hiding the window from the 'Windows' menu."""
        if toggled:
            if self._window is None:
                windows = ui.Workspace.get_windows()
                for window in windows:
                    if window.title.startswith("Viewport"):
                        self._viewport_window = window
                        continue
                
                ui.Workspace.set_window_created_callback(MetaCloudExplorerAzure.on_window_created)
                
                 # Build out the scene
                model = ObjectInfoModel()
                self._viewport_scene = ViewportScene(vp_win=self._viewport_window,model=model)
                self._window = MainView(WINDOW_NAME, obj_info_model=model)

            else:
                self._window.show()
        else:
            if self._window is not None:
                self._window.hide()

        # Deregister the function that shows the window from omni.ui
        #ui.Workspace.set_show_window_fn(MetaCloudExplorerAzure.WINDOW_NAME, None)


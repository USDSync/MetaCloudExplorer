import sys
import carb
import omni.ext
from .views import MainView
import asyncio
from functools import partial
import omni.ext
import omni.kit.ui
import omni.ui as ui
import omni.kit.pipapi

#omni.kit.pipapi.install("azure-identity", module="azure-identity", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
#omni.kit.pipapi.install("azure-mgmt-resource", module="azure-mgmt-resource", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )

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

    WINDOW_NAME = "Meta Cloud Explorer"
    MENU_PATH = f"Window/{WINDOW_NAME}"

    def on_startup(self, ext_id):

        # The ability to show up the window if the system requires it. We use it in QuickLayout.
        ui.Workspace.set_show_window_fn(MetaCloudExplorerAzure.WINDOW_NAME, partial(self.show_window, None))

        # Put the new menu
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(
                MetaCloudExplorerAzure.MENU_PATH, self.show_window, toggle=True, value=True
            )

        # Show the window. It will call `self.show_window`
        ui.Workspace.show_window(MetaCloudExplorerAzure.WINDOW_NAME)

        # # show the window in the usual way if the stage is loaded
        # if self.stage:
        #     self._window.deferred_dock_in("Property")
        # else:
        #     # otherwise, show the window after the stage is loaded
        #     self._setup_window_task = asyncio.ensure_future(self._dock_window())


    def on_shutdown(self):
        carb.log_info(f"[meta.cloud.explorer.azure]] Meta Cloud Explorer shutdown")     
        self._menu = None
        if self._window is not None:
            self._window.destroy()
            self._window = None

        # Deregister the function that shows the window from omni.ui
        ui.Workspace.set_show_window_fn(MetaCloudExplorerAzure.WINDOW_NAME, None)

    def _set_menu(self, value):
        """Set the menu to create this window on and off"""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(MetaCloudExplorerAzure.MENU_PATH, value)

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window is not None:
            self._window.destroy()
            self._window = None

    async def _dock_window(self):
        property_win = None

        frames = 3
        while frames > 0:
            if not property_win:
                property_win = ui.Workspace.get_window("Property")
            if property_win:
                break  # early out

            frames = frames - 1
            await omni.kit.app.get_app().next_update_async()

        # Dock to Property window after 5 frames. It's enough for window to appear.
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()

        if property_win:
            self._window.deferred_dock_in("Property")
        self._setup_window_task = None
        
    def _visiblity_changed_fn(self, visible):
        # Called when the user pressed "X"
        self._set_menu(visible)
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, menu, value):
        if value:
            self._window = MainView(MetaCloudExplorerAzure.WINDOW_NAME, width=600, height=500)
            self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
        elif self._window is not None:
            self._window.visible = False

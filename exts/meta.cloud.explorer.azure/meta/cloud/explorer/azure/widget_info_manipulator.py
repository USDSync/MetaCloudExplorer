## Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["WidgetInfoManipulator"]

from omni.ui import color as cl
from omni.ui import scene as sc
import omni.ui as ui
import carb

class _ViewportLegacyDisableSelection:
    """Disables selection in the Viewport Legacy"""

    def __init__(self):
        self._focused_windows = None
        focused_windows = []
        try:
            # For some reason is_focused may return False, when a Window is definitely in fact is the focused window!
            # And there's no good solution to this when mutliple Viewport-1 instances are open; so we just have to
            # operate on all Viewports for a given usd_context.
            import omni.kit.viewport_legacy as vp

            vpi = vp.acquire_viewport_interface()
            for instance in vpi.get_instance_list():
                window = vpi.get_viewport_window(instance)
                if not window:
                    continue
                focused_windows.append(window)
            if focused_windows:
                self._focused_windows = focused_windows
                for window in self._focused_windows:
                    # Disable the selection_rect, but enable_picking for snapping
                    window.disable_selection_rect(True)
        except Exception:
            pass


class _DragPrioritize(sc.GestureManager):
    """Refuses preventing _DragGesture."""

    def can_be_prevented(self, gesture):
        # Never prevent in the middle of drag
        return gesture.state != sc.GestureState.CHANGED

    def should_prevent(self, gesture, preventer):
        if preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED:
            return True


class _DragGesture(sc.DragGesture):
    """"Gesture to disable rectangle selection in the viewport legacy"""

    def __init__(self):
        super().__init__(manager=_DragPrioritize())

    def on_began(self):
        # When the user drags the slider, we don't want to see the selection
        # rect. In Viewport Next, it works well automatically because the
        # selection rect is a manipulator with its gesture, and we add the
        # slider manipulator to the same SceneView.
        # In Viewport Legacy, the selection rect is not a manipulator. Thus it's
        # not disabled automatically, and we need to disable it with the code.
        self.__disable_selection = _ViewportLegacyDisableSelection()

    def on_ended(self):
        # This re-enables the selection in the Viewport Legacy
        self.__disable_selection = None


class WidgetInfoManipulator(sc.Manipulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #self.destroy()

        self._radius = 2
        self._distance_to_top = 5
        self._thickness = 2
        self._radius_hovered = 20

    def destroy(self):
        self._root = None
        self._path_label = None
        self._name_label = None
        self._grp_label = None
        self._type_label = None
        self._location_label = None
        self._sub_label = None
        self._cost_label = None

    def _on_build_widgets(self):
        carb.log_info("WidgetInfoManipulator - on_build_widgets")
        with ui.ZStack():
            ui.Rectangle(
                style={
                    "background_color": cl(0.2),
                    "border_color": cl(0.7),
                    "border_width": 2,
                    "border_radius": 4,
                }
            )
            with ui.VStack(style={"font_size": 24}):
                ui.Spacer(height=4)
                with ui.ZStack(style={"margin": 1}, height=30):
                    ui.Rectangle(
                        style={
                            "background_color": cl(0.0),
                        }
                    )
                    ui.Line(style={"color": cl(0.7), "border_width": 2}, alignment=ui.Alignment.BOTTOM)
                    ui.Label("MCE: Resource Information", height=0, alignment=ui.Alignment.LEFT)

                ui.Spacer(height=4)
                self._path_label = ui.Label("Path:", height=0, alignment=ui.Alignment.LEFT)
                self._name_label = ui.Label("Name:", height=0, alignment=ui.Alignment.LEFT)
                self._grp_label = ui.Label("RGrp:", height=0, alignment=ui.Alignment.LEFT)
                self._type_label = ui.Label("Type:", height=0, alignment=ui.Alignment.LEFT)
                self._location_label = ui.Label("Location:", height=0, alignment=ui.Alignment.LEFT)
                self._sub_label = ui.Label("Sub:", height=0, alignment=ui.Alignment.LEFT)
                self._cost_label = ui.Label("Cost:", height=0, alignment=ui.Alignment.LEFT)
                

        self.on_model_updated(None)

        # Additional gesture that prevents Viewport Legacy selection
        self._widget.gestures += [_DragGesture()]

    def on_build(self):
        carb.log_info("WidgetInfoManipulator - on_build")
        """Called when the model is chenged and rebuilds the whole slider"""

        self._root = sc.Transform(visible=False)
        with self._root:
            with sc.Transform(scale_to=sc.Space.SCREEN):
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                    # Label
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        self._widget = sc.Widget(600, 250, update_policy=sc.Widget.UpdatePolicy.ON_MOUSE_HOVERED)
                        self._widget.frame.set_build_fn(self._on_build_widgets)
                        self._on_build_widgets()
       
    def on_model_updated(self, _):

        try:
            # if we don't have selection then show nothing
            if not self.model or not self.model.get_item("name"):
                if hasattr(self, "_root"):
                    self._root.visible = False
                    return
            else:
                # Update the shapes
                position = self.model.get_as_floats(self.model.get_item("position"))
                self._root.transform = sc.Matrix44.get_translation_matrix(*position)
                self._root.visible = True

        except:
            return 

        #how to select parent ?
        # name = self.model.get_item('name')
        # if name.find("Collision") != -1:
        #     return

        # Update the shape name
        if hasattr(self, "_name_label"):
            
            name = self.model.get_item('name')

            infoBlurb = name.replace("/World/RGrps/", "")
            infoBlurb = infoBlurb.replace("/World/Subs/", "")
            infoBlurb = infoBlurb.replace("/World/Locs/", "")
            infoBlurb = infoBlurb.replace("/World/Types/", "")

        try:
            self._path_label.text = f"{infoBlurb}"
        except:
            self._path_label = ui.Label("Path:", height=20, alignment=ui.Alignment.LEFT)
        try:
            self._name_label.text = "Name: " + self.model.get_custom('res_name')
        except:
            self._name_label = ui.Label("Name:" , height=40, alignment=ui.Alignment.LEFT)
        try:
            self._grp_label.text = "ResGrp: " + self.model.get_custom('res_grp')
        except:
            self._grp_label = ui.Label("RGrp:", height=60, alignment=ui.Alignment.LEFT)
        try:
            self._type_label.text = "Type: " + self.model.get_custom('res_type')
        except:
            self._type_label = ui.Label("Type: ", height=80, alignment=ui.Alignment.LEFT)
        try:
            self._location_label.text = "Location: " + self.model.get_custom('res_loc')
        except:
            self._location_label = ui.Label("Location: ", height=100, alignment=ui.Alignment.LEFT)
        try:
            self._sub_label.text = "Sub: " + self.model.get_custom('res_sub')
        except:
            self._sub_label = ui.Label("Sub: " , height=120, alignment=ui.Alignment.LEFT)
        try:
            self._cost_label.text = "Cost: " + self.model.get_custom('res_cost')
        except:
            self._cost_label = ui.Label("Cost:", height=140, alignment=ui.Alignment.LEFT)

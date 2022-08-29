from .constant import COLORS, LightColors, DarkColors, MouseKey
from .style import get_ui_style
from .rectangle import DashRectangle, OpaqueRectangle
from omni import ui


class InvisibleButton(ui.Button):
    STYLE = {
        "InvisibleButton": {"background_color": COLORS.TRANSPARENT},
        "InvisibleButton.Label": {"color": COLORS.TRANSPARENT},
    }

    def __init__(self, *arg, **kwargs):
        kwargs["style"] = self.STYLE
        kwargs["style_type_name_override"] = "InvisibleButton"
        super().__init__("##INVISIBLE", **kwargs)


class DashButton:
    def __init__(
        self,
        height=0,
        name=None,
        image_source=None,
        image_size=16,
        image_padding=7,
        dash_padding_x=2,
        padding=6,
        clicked_fn=None,
        alignment=ui.Alignment.LEFT,
    ):
        self._on_clicked_fn = clicked_fn

        with ui.ZStack(height=height):
            self._rectangle = OpaqueRectangle(height=height, name=name, style_type_name_override="Button")
            with ui.HStack(spacing=0):
                ui.Spacer(width=dash_padding_x + padding)
                if alignment == ui.Alignment.CENTER:
                    ui.Spacer()
                    self._build_image_label(
                        image_source=image_source, name=name, image_size=image_size, image_padding=image_padding
                    )
                    ui.Spacer()
                elif alignment == ui.Alignment.RIGHT:
                    ui.Spacer()
                    self._build_image_label(
                        image_source=image_source, name=name, image_size=image_size, image_padding=image_padding
                    )
                else:
                    self._build_image_label(
                        image_source=image_source, name=name, image_size=image_size, image_padding=image_padding
                    )
                    ui.Spacer()
                ui.Spacer(width=dash_padding_x)
            DashRectangle(500, height, padding_x=dash_padding_x)

        if clicked_fn:
            self._rectangle.set_mouse_pressed_fn(lambda x, y, btn, flag: self._on_clicked())

    @property
    def enabled(self):
        return self._label.enabled

    @enabled.setter
    def enabled(self, value):
        self._label.enabled = value

    def _build_image_label(self, image_source=None, name=None, image_size=16, image_padding=7):
        if image_source:
            with ui.VStack(width=image_size + 2 * image_padding):
                ui.Spacer()
                ui.Image(
                    image_source,
                    width=image_size,
                    height=image_size,
                    name=name,
                    style_type_name_override="Button.Image",
                )
                ui.Spacer()

        self._label = ui.Label("Add", width=0, name=name, style_type_name_override="Button.Label")

    def _on_clicked(self):
        if self._label.enabled:
            if self._on_clicked_fn is not None:
                self._on_clicked_fn()


class ImageButton:
    LIGHT_STYLE = {
        "ImageButton": {"background_color": COLORS.TRANSPARENT, "border_width": 0, "border_radius": 2.0},
        "ImageButton:hovered": {"background_color": LightColors.ButtonHovered},
        "ImageButton:pressed": {"background_color": LightColors.ButtonPressed},
        "ImageButton:selected": {"background_color": LightColors.ButtonSelected},
    }
    DARK_STYLE = {
        "ImageButton": {"background_color": COLORS.TRANSPARENT, "border_width": 0, "border_radius": 2.0},
        "ImageButton:hovered": {"background_color": 0xFF373737},
        "ImageButton:selected": {"background_color": 0xFF1F2123},
    }
    UI_STYLES = {"NvidiaLight": LIGHT_STYLE, "NvidiaDark": DARK_STYLE}

    def __init__(
        self,
        name,
        width,
        height,
        image,
        clicked_fn,
        tooltip=None,
        visible=True,
        enabled=True,
        activated=False,
        tooltip_fn=None,
    ):
        self._name = name
        self._width = width
        self._height = height
        self._tooltip = tooltip
        self._tooltip_fn = tooltip_fn
        self._visible = visible
        self._enabled = enabled
        self._image = image
        self._clicked_fn = clicked_fn
        self._activated = activated
        self._panel = None
        self._bkground_widget = None
        self._image_widget = None

        self._mouse_x = 0
        self._mouse_y = 0

    def create(self, style=None, padding_x=2, padding_y=2):
        ww = self.get_width()
        hh = self.get_height()
        if style is None:
            style = ImageButton.UI_STYLES[get_ui_style()]
        self._panel = ui.ZStack(spacing=0, width=ww, height=hh, style=style)
        with self._panel:
            with ui.Placer(offset_x=0, offset_y=0):
                self._bkground_widget = ui.Rectangle(
                    name=self._name, style_type_name_override="ImageButton", width=ww, height=hh
                )
            self._bkground_widget.visible = self._visible and self._enabled

            with ui.Placer(offset_x=padding_x, offset_y=padding_y):
                self._image_widget = ui.Image(
                    self._image,
                    width=ww - padding_x * 2,
                    height=hh - padding_y * 2,
                    fill_policy=ui.FillPolicy.STRETCH,
                    mouse_pressed_fn=(lambda x, y, key, m: self._on_mouse_pressed(x, y, key)),
                    mouse_released_fn=(lambda x, y, key, m: self._on_mouse_released(x, y, key)),
                    opaque_for_mouse_events=True,
                )

        if self._bkground_widget is None or self._image_widget is None:
            return

        if self._tooltip:
            self._image_widget.set_tooltip(self._tooltip)
        if self._tooltip_fn:
            self._tooltip_fn(self._image_widget, self._tooltip)

        if not self._enabled:
            self._bkground_widget.enabled = False
            self._image_widget.enabled = False

    def destroy(self):
        if self._panel:
            self._panel.clear()
        if self._bkground_widget:
            self._bkground_widget = None
        if self._image_widget:
            self._image_widget = None

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self.enable(value)

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_widget_pos(self):
        x = self._bkground_widget.screen_position_x
        y = self._bkground_widget.screen_position_y
        return (x, y)

    def enable(self, enabled):
        if self._enabled != enabled:
            self._enabled = enabled

            self._bkground_widget.visible = enabled and self._visible
            self._image_widget.enabled = enabled
        return False

    def set_tooltip(self, tooltip):
        self._tooltip = tooltip
        if self._image_widget is not None:
            self._image_widget.set_tooltip(self._tooltip)

    def set_tooltip_fn(self, tooltip_fn: callable):
        self._tooltip_fn = tooltip_fn
        if self._image_widget is not None:
            self._image_widget.set_tooltip_fn(lambda w=self._image_widget, name=self._tooltip: tooltip_fn(w, name))

    def is_visible(self):
        return self._visible

    def set_visible(self, visible=True):
        if self._visible != visible:
            self._visible = visible
            self._bkground_widget.visible = visible and self._enabled
            self._image_widget.visible = visible

    def identify(self, name):
        return self._name == name

    def get_name(self):
        return self._name

    def is_activated(self):
        return self._activated

    def activate(self, activated=True):
        if self._activated == activated:
            return False

        self._activated = activated
        if self._bkground_widget is not None:
            self._bkground_widget.selected = activated

    def set_image(self, image):
        if self._image != image:
            self._image = image
            self._image_widget.source_url = image
        return False

    def _on_mouse_pressed(self, x, y, key):
        if not self._enabled:
            return

        # For left button, we do trigger the click event on mouse_released.
        # For other buttons, we trigger the click event right now since Widget will never has
        # mouse_released event for any buttons other than left.
        if key != MouseKey.LEFT:
            self._clicked_fn(key, x, y)
        else:
            self._mouse_x = x
            self._mouse_y = y

    def _on_mouse_released(self, x, y, key):
        if self._enabled:
            if key == MouseKey.LEFT:
                self._clicked_fn(MouseKey.LEFT, x, y)


class SimpleImageButton(ImageButton):
    def __init__(self, image, size, clicked_fn=None, name=None, style=None, padding=2):
        self._on_clicked_fn = clicked_fn
        if name is None:
            name = "default_image_btn"
        super().__init__(name, size, size, image, self._on_clicked)
        self.create(style=style, padding_x=padding, padding_y=padding)

    @property
    def clicked_fn(self):
        return self._on_clicked_fn

    @clicked_fn.setter
    def clicked_fn(self, value):
        self._on_clicked_fn = None

    def _on_clicked(self, button, x, y):
        if self._on_clicked_fn:
            self._on_clicked_fn()


class BoolImageButton(ImageButton):
    def __init__(self, true_image, false_image, size, state=True, clicked_fn=None):
        self._true_image = true_image
        self._false_image = false_image
        self._state = state
        self._on_clicked_fn = clicked_fn
        super().__init__("default_image_btn", size, size, self._get_image(), self._on_clicked)
        self.create()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self.set_state(value, notify=False)

    def set_state(self, state, notify=False):
        self._state = state
        self.set_image(self._get_image())
        if notify and self._on_clicked_fn:
            self._on_clicked_fn(self._state)

    def _on_clicked(self, button, x, y):
        self.set_state(not self._state, notify=True)

    def _get_image(self):
        return self._true_image if self._state else self._false_image

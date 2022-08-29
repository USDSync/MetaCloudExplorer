from .constant import COLORS, LightColors, DarkColors, FontSize
from omni import ui
import carb.settings


def get_ui_style():
    settings = carb.settings.get_settings()
    style = settings.get_as_string("/persistent/app/window/uiStyle")
    if not style:
        style = "NvidiaDark"
    return style


class DefaultWidgetStyle:
    LIGHT = {
        "Button": {
            "background_color": LightColors.Button,
            "border_radius": 2.0,
            "stack_direction": ui.Direction.LEFT_TO_RIGHT,
        },
        "Button.Label": {"color": LightColors.Background},
        "Button:hovered": {"background_color": LightColors.ButtonHovered},
        "Button:pressed": {"background_color": LightColors.ButtonPressed},
        "CollapsableFrame": {
            "color": COLORS.TRANSPARENT,
            "background_color": COLORS.TRANSPARENT,
            "secondary_color": COLORS.TRANSPARENT,
        },
        "CollapsableFrame:hovered": {"secondary_color": COLORS.TRANSPARENT},
        "CollapsableFrame:pressed": {"secondary_color": COLORS.TRANSPARENT},
        "ComboBox": {
            "color": LightColors.Text,
            "background_color": LightColors.Background,
            "selected_color": LightColors.BackgroundSelected,
            "border_radius": 1,
            "padding_width": 0,
            "padding_height": 4,
            "secondary_padding": 8,
        },
        "ComboBox:disabled": {"color": LightColors.TextDisabled},
        "Field": {"background_color": LightColors.Background, "color": LightColors.Text, "border_radius": 2},
        "Plot": {"background_color": LightColors.Background, "color": LightColors.TextSelected, "border_radius": 1},
        "Triangle": {"background_color": LightColors.Background},
    }

    DARK = {
        "Button": {
            "background_color": DarkColors.Button,
            "border_radius": 2.0,
            "stack_direction": ui.Direction.LEFT_TO_RIGHT,
        },
        "Button.Label": {"color": DarkColors.Text},
        "Button:hovered": {"background_color": DarkColors.ButtonHovered},
        "Button:pressed": {"background_color": DarkColors.ButtonPressed},
        "CollapsableFrame": {
            "color": COLORS.TRANSPARENT,
            "background_color": COLORS.TRANSPARENT,
            "secondary_color": COLORS.TRANSPARENT,
        },
        "CollapsableFrame:hovered": {"secondary_color": COLORS.TRANSPARENT},
        "CollapsableFrame:pressed": {"secondary_color": COLORS.TRANSPARENT},
        "ComboBox": {
            "color": DarkColors.Text,
            "background_color": DarkColors.Background,
            "selected_color": DarkColors.BackgroundSelected,
            "border_radius": 1,
        },
        "ComboBox:disabled": {"color": DarkColors.TextDisabled},
        "Field": {"background_color": DarkColors.Background, "color": DarkColors.Text, "border_radius": 2},
        "Plot": {"background_color": DarkColors.Background, "color": DarkColors.TextSelected, "border_radius": 1},
        "Triangle": {"background_color": DarkColors.Background},
    }

    @staticmethod
    def get_style(ui_style=None):
        if ui_style is None:
            ui_style = get_ui_style()

        if ui_style == "NvidiaDark":
            return DefaultWidgetStyle.DARK
        else:
            return DefaultWidgetStyle.LIGHT

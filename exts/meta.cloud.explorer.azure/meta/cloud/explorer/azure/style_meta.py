# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["meta_window_style"]

from omni.ui import color as cl
from omni.ui import constant as fl
from omni.ui import url
import omni.kit.app
import omni.ui as ui
import pathlib

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)

# Pre-defined constants. It's possible to change them runtime.
cl.meta_window_hovered = cl("#2b2e2e")
cl.meta_window_text = cl("#9e9e9e")
fl.meta_window_attr_hspacing = 10
fl.meta_window_attr_spacing = 1
fl.meta_window_group_spacing = 2

# Pre-defined constants. It's possible to change them runtime.
fl_attr_hspacing = 10
fl_attr_spacing = 1
fl_group_spacing = 5

cl_attribute_dark = cl("#202324")
cl_attribute_red = cl("#ac6060")
cl_attribute_green = cl("#60ab7c")
cl_attribute_blue = cl("#35889e")
cl_line = cl("#404040")
cl_text_blue = cl("#5eb3ff")
cl_text_gray = cl("#707070")
cl_text = cl("#a1a1a1")
cl_text_hovered = cl("#ffffff")
cl_field_text = cl("#5f5f5f")
cl_widget_background = cl("#1f2123")
cl_attribute_default = cl("#505050")
cl_attribute_changed = cl("#55a5e2")
cl_slider = cl("#383b3e")
cl_combobox_background = cl("#252525")
cl_main_background = cl("#2a2b2c")

cls_temperature_gradient = [cl("#fe0a00"), cl("#f4f467"), cl("#a8b9ea"), cl("#2c4fac"), cl("#274483"), cl("#1f334e")]
cls_color_gradient = [cl("#fa0405"), cl("#95668C"), cl("#4b53B4"), cl("#33C287"), cl("#9fE521"), cl("#ff0200")]
cls_tint_gradient = [cl("#1D1D92"), cl("#7E7EC9"), cl("#FFFFFF")]
cls_grey_gradient = [cl("#020202"), cl("#525252"), cl("#FFFFFF")]
cls_button_gradient = [cl("#232323"), cl("#656565")]

# The main style dict
meta_window_style = {
    "Label::attribute_name": {
        "color": cl.meta_window_text,
        "margin_height": fl.meta_window_attr_spacing,
        "margin_width": fl.meta_window_attr_hspacing,
    },
    "CollapsableFrame::group": {"margin_height": fl.meta_window_group_spacing},
    "CollapsableFrame::group:hovered": {"secondary_color": cl.meta_window_hovered},

    # for Gradient Image
    "ImageWithProvider::gradient_slider":{"border_radius": 4, "corner_flag": ui.CornerFlag.ALL},
    "ImageWithProvider::button_background_gradient": {"border_radius": 3, "corner_flag": ui.CornerFlag.ALL},

}



#Functions from NVIDIA
def hex_to_color(hex: int) -> tuple:
    # convert Value from int
    red = hex & 255
    green = (hex >> 8) & 255
    blue = (hex >> 16) & 255
    alpha = (hex >> 24) & 255
    rgba_values = [red, green, blue, alpha]
    return rgba_values

def _interpolate_color(hex_min: int, hex_max: int, intep):
    max_color = hex_to_color(hex_max)
    min_color = hex_to_color(hex_min)
    color = [int((max - min) * intep) + min for max, min in zip(max_color, min_color)]
    return (color[3] << 8 * 3) + (color[2] << 8 * 2) + (color[1] << 8 * 1) + color[0]

def get_gradient_color(value, max, colors):
    step_size = len(colors) - 1
    step = 1.0/float(step_size)
    percentage = value / float(max)

    idx = (int) (percentage / step)
    if idx == step_size:
        color = colors[-1]
    else:
        color = _interpolate_color(colors[idx], colors[idx+1], percentage)
    return color

def generate_byte_data(colors):
    data = []
    for color in colors:
        data += hex_to_color(color)

    _byte_provider = ui.ByteImageProvider()
    _byte_provider.set_bytes_data(data, [len(colors), 1])
    return _byte_provider

def build_gradient_image(colors, height, style_name):
    byte_provider = generate_byte_data(colors)
    ui.ImageWithProvider(byte_provider,fill_policy=omni.ui.IwpFillPolicy.IWP_STRETCH, height=height, name=style_name)
    return byte_provider
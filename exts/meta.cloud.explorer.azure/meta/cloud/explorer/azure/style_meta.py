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

# The main style dict
meta_window_style = {
    "Label::attribute_name": {
        "color": cl.meta_window_text,
        "margin_height": fl.meta_window_attr_spacing,
        "margin_width": fl.meta_window_attr_hspacing,
    },
    "CollapsableFrame::group": {"margin_height": fl.meta_window_group_spacing},
    "CollapsableFrame::group:hovered": {"secondary_color": cl.meta_window_hovered},
}

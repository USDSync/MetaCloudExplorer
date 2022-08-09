# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ComboBoxModel"]

from typing import Optional
import omni.ui as ui


class ListItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, text):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)

    def __repr__(self):
        return f'"{self.name_model.as_string}"'

    @property
    def as_string(self):
        """Return the string of the name model"""
        return self.name_model.as_string


class ComboBoxModel(ui.AbstractItemModel):
    """
    Represents the model for lists. It's very easy to initialize it
    with any string list:
        string_list = ["Hello", "World"]
        model = ComboBoxModel(*string_list)
        ui.ComboBox(model)
    """

    def __init__(self, *args, default=0):
        super().__init__()
        self._children = [ListItem(t) for t in args]
        self._default = ui.SimpleIntModel()
        self._default.as_int = default
        # Update the combo box when default is changed
        self._default.add_value_changed_fn(lambda _: self._item_changed(None))

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self._children

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item: Optional[ListItem], column_id):
        """
        Return value model.
        It's the object that tracks the specific value.
        In our case we use ui.SimpleStringModel.
        """
        if item is None:
            return self._default

        return item.name_model

    def get_current_item(self) -> ListItem:
        """Returns the currently selected item in ComboBox"""
        return self._children[self._default.as_int]

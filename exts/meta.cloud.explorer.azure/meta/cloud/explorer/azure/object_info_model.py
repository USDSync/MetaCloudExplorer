# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ObjectInfoModel"]

from pxr import Tf
from pxr import Usd
from pxr import UsdGeom

from omni.ui import scene as sc
import omni.usd
from .prim_utils import only_select_parent_prims

# The distance to raise above the top of the object's bounding box
TOP_OFFSET = 5


class ObjectInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """
    class PositionItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because we take the position directly from USD when requesting.
        """

        def __init__(self):
            super().__init__()
            self.value = [0, 0, 0]

    def __init__(self):
        super().__init__()

        # Current selected prim and material
        self._current_paths = []
        self.positions = []
        self._stage_listener = None
        self.populate()
        
        # Track selection changes
        self.events = self._get_context().get_stage_event_stream()
        self.stage_event_delegate = self.events.create_subscription_to_pop(
            self.on_stage_event, name="Object Info Selection Update"
        )

    def on_stage_event(self, event):
        """Called by stage_event_stream.  We only care about selection changes."""
        # NEW: if statement to only check when selection changed
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):        
            self.populate()       

    def destroy(self):
        self.events = None
        self.stage_event_delegate.unsubscribe()


    def populate(self):

        self._current_paths = []
        self.positions = []
        usd_context = self._get_context()
        stage = usd_context.get_stage()

        #Get selected prims
        usd_context = omni.usd.get_context()
        self._stage: Usd.Stage = usd_context.get_stage()
        self._selection = usd_context.get_selection()
        self._paths = self._selection.get_selected_prim_paths()

        #Selectively choose the paths
        self._paths = only_select_parent_prims(prim_paths=self._paths)

        #if len(self._current_paths) > 1: #ONLY SHOW ON MULTISELECT!
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if not prim.IsValid():
                return
            for child in prim.GetChildren():
                if child.IsA(UsdGeom.Imageable):
                    if str(path).find("Collision") == -1:
                        if str(path).find("Baked") == -1:
                            if str(path).find("/materials") == -1:
                                self._current_paths.append(child.GetPath())
                                self.positions.append(ObjectInfoModel.PositionItem())
                                # Position is changed because new selected object has a different position
                                self._item_changed(self.positions[-1])
        #elif len(self._current_paths == 0):
        #    pass

    def _get_context(self):
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def _notice_changed(self, notice: Usd.Notice, stage: Usd.Stage) -> None:
        """Called by Tf.Notice.  Used when the current selected object changes in some way."""
        for p in notice.GetChangedInfoOnlyPaths():
            for i, watched_path in enumerate(self._current_paths):
                if str(watched_path) in str(p.GetPrimPath()):
                    self._item_changed(self.positions[i])

    def get_name(self, index):
        stage = self._get_context().get_stage()
        prim = stage.GetPrimAtPath(self._current_paths[index])
        return prim.GetCustomDataByKey('res_name') 

    def get_num_prims(self):
        return len(self._current_paths)

    def get_position(self, index):
        """Returns position of currently selected object"""
        stage = self._get_context().get_stage()
        if not stage or not self._current_paths[index]:
            return [0, 0, 0]

        # Get position directly from USD
        prim = stage.GetPrimAtPath(self._current_paths[index])
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()

        # Find the top center of the bounding box and add a small offset upward.
        position = [(bboxMin[0] + bboxMax[0]) * 0.5, bboxMax[1] + TOP_OFFSET, (bboxMin[2] + bboxMax[2]) * 0.5]
        return position

    








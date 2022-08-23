# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["get_selection", "duplicate_prims", "create_prims, create_shaders"]

from re import I
from typing import List
import omni.usd
import asyncio
import omni.kit.commands
from pxr import Sdf, Gf, Usd, UsdGeom
from .prim_utils import create_plane



def get_selection() -> List[str]:
    """Get the list of currently selected prims"""
    return omni.usd.get_context().get_selection().get_selected_prim_paths()


def duplicate_prims(transforms: List = [], prim_names: List[str] = [], target_path: str = "", mode: str = "Copy"):
    """
    Returns generator with pairs containing transform matrices and ids to
    arrange multiple objects.

    ### Arguments:

        `transforms: List`
            Pairs containing transform matrices and ids to apply to new objects

        `prim_names: List[str]`
            Prims to duplicate

        `target_path: str`
            The parent for the new prims

        `mode: str`
            "Reference": Create a reference of the given prim path
            "Copy": Create a copy of the given prim path
            "PointInstancer": Create a PointInstancer

    """

    if mode == "PointInstancer":
        omni.kit.commands.execute(
            "ScatterCreatePointInstancer",
            path_to=target_path,
            transforms=transforms,
            prim_names=prim_names,
        )
        return

    usd_context = omni.usd.get_context()
    # Call commands in a single undo group. So the user will undo everything
    # with a single press of ctrl-z
    with omni.kit.undo.group():
        # Create a group
        omni.kit.commands.execute("CreatePrim", prim_path=target_path, prim_type="Scope")

        for i, matrix in enumerate(transforms):
            id = matrix[1]
            matrix = matrix[0]

            path_from = Sdf.Path(prim_names[id])
            path_to = Sdf.Path(target_path).AppendChild(f"{path_from.name}{i}")

            # Create a new prim
            if mode == "Copy":
                omni.kit.commands.execute("CopyPrims", paths_from=[path_from.pathString], paths_to=[path_to.pathString])
            elif mode == "Reference":
                omni.kit.commands.execute(
                    "CreateReference", usd_context=usd_context, prim_path=path_from, path_to=path_to, asset_path=""
                )
            else:
                continue

            # Move
            omni.kit.commands.execute("TransformPrim", path=path_to, new_transform_matrix=matrix)


def create_prims(up_axis:str, plane_size:List[float], transforms: List = [], prim_names: List[str] = [], parent_path:str = ""):
    """
    Returns generator with pairs containing transform matrices and ids to arrange multiple objects.

    ### Arguments:

        `transforms: List`
            Pairs containing transform matrices and ids to apply to new objects

        `prim_names: List[str]`
            Prims to create

        `target_paths: List[str]`
            The paths for the new prims

    """
    usd_context = omni.usd.get_context()
    stage_ref = usd_context.get_stage()  

    # Call commands in a single undo group. So the user will undo everything
    # with a single press of ctrl-z
    #with omni.kit.undo.group():
    print("Prim count: " + str(len(prim_names)))
    # Create a group
    #omni.kit.commands.execute("CreatePrim", prim_path=parent_path, prim_type="Scope")
    i=0
    for matrix in enumerate(transforms):

        if (i >= len(prim_names)): continue
        path = Sdf.Path(parent_path).AppendPath(prim_names[i]["group"])
        print(str(i) + " adding plane:" + str(path) + " " + str(plane_size[i]) +  " @ " + str(matrix[1]))

        omni.kit.commands.execute('AddGroundPlaneCommand',
        stage=stage_ref,
        planePath=str(path),
        axis=up_axis,
        size=plane_size[i],
        position=matrix[1],
        color=Gf.Vec3f(0,0,0))

        #Add a UV
        # plane_prim = omni.usd.get_context().get_stage().GetPrimAtPath(path)
        # mesh = UsdGeom.Mesh(plane_prim)
        # uv_primvar = mesh.CreatePrimvar("st",
        #     Sdf.ValueTypeNames.TexCoord2fArray,
        #     UsdGeom.Tokens.varying
        # )
        # uv_primvar.Set([(0,0), (0,1), (1,1), (1,0)])

        i=i+1


def create_shaders(base_path:str, prim_name:str ):

    prim_path = Sdf.Path(base_path)
    prim_path = prim_path.AppendPath("CollisionMesh")

    #Select the Collision Mesh
    omni.kit.commands.execute('SelectPrims',
        old_selected_paths=[''],
        new_selected_paths=[str(prim_path)],
        expand_in_stage=True)

    #print("Creating Shader: " + str(prim_path))

    #Create a Shader for the Mesh
    omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
        mdl_name='OmniPBR.mdl',
        mtl_name='OmniPBR',
        prim_name=prim_name,
        mtl_created_list=None,
        bind_selected_prims=True)

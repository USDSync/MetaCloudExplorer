
__all__ = ["create_prims"]

from typing import List
import omni.usd
import omni.kit.commands
from pxr import Sdf, Gf, Usd, UsdGeom
from .prim_utils import create_plane

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
        path = Sdf.Path(parent_path).AppendPath(prim_names[i])
        print(str(i) + " adding " + str(plane_size[i]) + " plane:" + str(path) + " " + " @ " + str(matrix[1]))

        omni.kit.commands.execute('AddGroundPlaneCommand',
        stage=stage_ref,
        planePath=str(path),
        axis=up_axis,
        size=plane_size[i],
        position=matrix[1],
        color=Gf.Vec3f(0,255,0))

        #Add a UV
        plane_prim = omni.usd.get_context().get_stage().GetPrimAtPath(path)
        mesh = UsdGeom.Mesh(plane_prim)
        uv_primvar = mesh.CreatePrimvar("st",
            Sdf.ValueTypeNames.TexCoord2fArray,
            UsdGeom.Tokens.varying
        )
        uv_primvar.Set([(0,0), (0,1), (1,1), (1,0)])



        i=i+1
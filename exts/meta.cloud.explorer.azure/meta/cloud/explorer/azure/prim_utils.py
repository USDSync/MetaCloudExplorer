__all__ = ["create_plane"]

import omni.usd
import omni.kit.commands
from pxr import Sdf
from pxr import Gf, UsdGeom, UsdLux


#Creates a plane of a certain size in a specific location
def create_plane(self,Path:str, Name :str, Size: int, Location: Gf.Vec3f):
    #if (self._groundPlaneAdded == False):
    stage_ref = omni.usd.get_context().get_stage()

    #omni.kit.undo.begin_group()

    #omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',	prim_type='Plane')

    omni.kit.commands.execute('CreatePrimWithDefaultXform',	
    prim_type='Plane', prim_path=Path )

    #plane = stage_ref.GetPrimAtPath(Path)
    #omni.kit.undo.end_group()


    # omni.kit.commands.execute('AddGroundPlaneCommand',
    # stage=stage_ref,
    # planePath=Path,
    # axis="Z",
    # size=Size,
    # position=Location,
    # color=Gf.Vec3f(0.5, 0.5, 0.5))


def cleanup_prim_path(self, Name: str):
    nme = Name.replace("-", "_")
    nme = nme.replace(" ", "_")
    nme = nme.replace("/", "_")
    nme = nme.replace(".", "_")
    nme = nme.replace(":", "_")
    nme = nme.replace(";", "_")
    return nme




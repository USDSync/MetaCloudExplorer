__all__ = ["create_plane", "get_font_size_from_length"]

import omni.usd
import omni.kit.commands
from pxr import Sdf
from pxr import Gf, UsdGeom, UsdLux


#Creates a plane of a certain size in a specific location
def create_plane(self,Path:str, Name :str, Size: int, Location: Gf.Vec3f, Color:Gf.Vec3f):
    #if (self._groundPlaneAdded == False):
    #omni.kit.undo.begin_group()
    #omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',	prim_type='Plane')
 
    #omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',	prim_type='Plane',  )

    stage_ref = omni.usd.get_context().get_stage()  
    #plane = stage_ref.GetPrimAtPath(Path)
    #Set the size
    #sizeAttr_ref = plane.CreateAttribute('size', Sdf.ValueTypeNames.Double )
    #sizeAttr_ref.Set(50)
    
    #obj = stage.GetPrimAtPath(path + "/cube") # note the extra /cube
    #sizeAttr_ref = obj.CreateAttribute('size', Sdf.ValueTypeNames.Double )

    #sizeAttr_ref.Set(50 * (i+1))
    #omni.kit.undo.end_group()

    omni.kit.commands.execute('AddGroundPlaneCommand',
    stage=stage_ref,
    planePath=Path,
    axis="Z",
    size=Size,
    position=Location,
    color=Color)


def cleanup_prim_path(self, Name: str):
    nme = Name.replace("-", "_")
    nme = nme.replace(" ", "_")
    nme = nme.replace("/", "_")
    nme = nme.replace(".", "_")
    nme = nme.replace(":", "_")
    nme = nme.replace(";", "_")
    return nme



def get_font_size_from_length(nameLength:int):
    if (nameLength < 10):
        font_size = 70
    elif (nameLength < 15):
        font_size = 50
    elif (nameLength < 20):
        font_size = 40                    
    elif (nameLength < 30):
        font_size = 30
    elif (nameLength < 50):
        font_size = 20
    elif (nameLength < 60):
        font_size = 20
    elif (nameLength < 70):
        font_size = 20
    elif (nameLength < 80):
        font_size = 10

    return font_size
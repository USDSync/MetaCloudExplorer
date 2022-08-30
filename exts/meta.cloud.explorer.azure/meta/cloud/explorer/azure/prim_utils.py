__all__ = ["create_plane", "get_font_size_from_length", "get_parent_child_prim_path", "create_and_place_prim", "log_transforms"]
import sys
from tokenize import Double
import omni.usd
import omni.kit.commands
import shutil
import carb
from pathlib import Path
from pxr import Sdf
from pxr import Gf, UsdGeom, UsdLux
from .pillow_text import draw_text_on_image_at_position

CURRENT_PATH = Path(__file__).parent
RES_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data\\resources")

async def create_and_place_prim(self,
    prim_type:str,
    prim_name:str,
    grp_name:str,
    new_prim_path:str,
    shapeToRender:str, 
    scale:float, 
    position:Gf.Vec3f
    ):
    
    carb.log_info("Creating new prim: " + prim_type + " @ "+ new_prim_path + " shape: " + shapeToRender)
    stage =  omni.usd.get_context().get_stage()

    # Create prim to add the reference to.
    prim = stage.DefinePrim(new_prim_path)
    prim.GetReferences().AddReference(shapeToRender)
    my_new_prim = stage.GetPrimAtPath(new_prim_path)

    my_new_prim.SetCustomDataByKey('res_type', prim_type) 
    my_new_prim.SetCustomDataByKey('res_name', prim_name) 
    my_new_prim.SetCustomDataByKey('res_grp', grp_name) 

    #Default rotation
    rotation = Gf.Vec3f(0,0,0)
    translate = Gf.Vec3d(position[0], position[1], position[2])

    #Are we still set to default? Change cube size and position
    if shapeToRender == "omniverse://localhost/Resources/3dIcons/scene.usd":
        scale = 3.0
        position[2] = position[2] + 30 #Buffer the cube off the z

    #CUSTOM SHAPE OVERRIDES
    if prim_name == "nvidia_chair":
        scale =0.8
        rotation = Gf.Vec3f(90,0,220)
        translate=Gf.Vec3d(position[0]+150, position[1]+150, position[2])
    if prim_name == "nvidia_jacket":
        scale =0.25
        rotation = Gf.Vec3f(90,0,0)
        translate=Gf.Vec3d(position[0]-20, position[1], position[2]-25)
    if prim_name == "nvidia_coat_rack":
        scale =0.55
        rotation = Gf.Vec3f(90,0,0)                        
        translate=Gf.Vec3d(position[0]-220, position[1]+210, position[2]+10)
    carb.log_info("Placing prim: " + shapeToRender + " | " + str(new_prim_path) + " @ " 
        + "scl:" + str(scale) + " x:" + str(position[0]) + "," + " y:" + str(position[1]) + "," + " z:" + str(position[2]))           

    api = UsdGeom.XformCommonAPI(my_new_prim)

    try:
        carb.log_info("Setting prim translate")
        api.SetTranslate(translate,1)
        print("Setting prim rotate")
        api.SetRotate(rotation,UsdGeom.XformCommonAPI.RotationOrderXYZ,1)
        print("Setting prim scale")
        api.SetScale(Gf.Vec3f(scale,scale,scale), 1)
    except:
        carb.log_error("Oops!", sys.exc_info()[0], "occurred.")
    

#log the vectors
def log_transforms(self, vectors):
    for v in vectors:
        logdata = str(vectors[v][0]) + "," + str(vectors[v][1]) + "," + str(vectors[v][2])
        print(logdata)


def draw_image(self, output_file:str, src_file:str, textToDraw:str, costToDraw:str):
            
    font = RES_PATH.joinpath("airstrike.ttf")
    font_size = get_font_size_from_length(len(textToDraw))

    draw_text_on_image_at_position(                
        input_image_path=src_file,
        output_image_path=output_file, 
        textToDraw=str(textToDraw), 
        costToDraw=str(costToDraw),
        x=180, y=1875, fillColor="Yellow", font=font,
        fontSize=font_size )

#Creates a plane of a certain size in a specific location
def create_plane(self,Path:str, Name :str, Size: int, Location: Gf.Vec3f, Color:Gf.Vec3f):

    stage_ref = omni.usd.get_context().get_stage()  

    omni.kit.commands.execute('AddGroundPlaneCommand',
    stage=stage_ref,
    planePath=Path,
    axis="Z",
    size=Size,
    position=Location,
    color=Color)


def cleanup_prim_path(self, Name: str):
    #print("cleanup: " + Name)
    nme = Name.replace("-", "_")
    nme = nme.replace(" ", "_")
    nme = nme.replace("/", "_") 
    nme = nme.replace(".", "_")
    nme = nme.replace(":", "_")
    nme = nme.replace(";", "_")
    nme = nme.replace("(", "_")
    nme = nme.replace(")", "_")
    nme = nme.replace("[", "_")
    nme = nme.replace("]", "_")

    #if it starts with a number add a _
    if nme[0].isnumeric():
        nme = "_" + nme

    #dont start with a -
    if nme[0] == "-":
        nme = nme[1:len(nme[0])-1]

    #print("cleanup res: " + nme)
    return nme

# Concats two Sdf.Paths and truncates he result to MAX_PATH_LENGTH
def get_parent_child_prim_path(self, groupPath:Sdf.Path, resName:str):

    resName = cleanup_prim_path(self, resName)  

    #prim_len = len(str(groupPath)) + len(resName)
    #if (prim_len) > 70:
    #    diff = prim_len - 70
    #    trim = len(resName) - diff 
    #    resName = resName[:trim] 
    
    try:
        shape_prim_path = Sdf.Path(groupPath.AppendPath(resName))
        return shape_prim_path
    except:
        print("Oops!", sys.exc_info()[0], "occurred.")




def get_font_size_from_length(nameLength:int):
    if (nameLength < 10):
        font_size = 160
    elif (nameLength < 15):
        font_size = 140
    elif (nameLength < 20):
        font_size = 120                   
    elif (nameLength < 30):
        font_size = 100
    elif (nameLength < 50):
        font_size = 80
    elif (nameLength < 60):
        font_size = 70
    elif (nameLength < 70):
        font_size = 60
    elif (nameLength < 80):
        font_size = 44

    return font_size
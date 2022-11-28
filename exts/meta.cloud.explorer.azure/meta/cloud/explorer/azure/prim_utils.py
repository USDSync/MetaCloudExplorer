__all__ = ["create_plane", "get_font_size_from_length", "get_parent_child_prim_path", "create_and_place_prim", "log_transforms", "only_select_parent_prims"]
import sys
from tokenize import Double
import omni.usd
import omni.kit.commands
from omni.kit.environment.core import GroundHelper
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
    sub_name:str,
    loc_name:str,
    cost:str,
    new_prim_path:str,
    shapeToRender:str, 
    scale:float, 
    position:Gf.Vec3f
    ):
    
    carb.log_info("Creating new prim: " + prim_type + " @ "+ new_prim_path + " shape: " + shapeToRender)
    stage =  omni.usd.get_context().get_stage()

    # Create prim to add the reference to.
    try:
        prim = stage.DefinePrim(new_prim_path)
        prim.GetReferences().AddReference(shapeToRender)
    except:
        carb.log_error("Invalid prim path:" + str(new_prim_path))
        return

    my_new_prim = stage.GetPrimAtPath(new_prim_path)

    my_new_prim.SetCustomDataByKey('res_type', prim_type) 
    my_new_prim.SetCustomDataByKey('res_name', prim_name) 
    my_new_prim.SetCustomDataByKey('res_sub', sub_name) 
    my_new_prim.SetCustomDataByKey('res_grp', grp_name) 
    my_new_prim.SetCustomDataByKey('res_loc', loc_name) 
    my_new_prim.SetCustomDataByKey('res_cost', cost) 

    #Default rotation
    rotation = Gf.Vec3f(0,0,0)
    translate = Gf.Vec3d(position[0], position[1], position[2])

    #Are we still set to default? Change cube size and position
    if shapeToRender == "omniverse://localhost/MCE/3dIcons/scene.usd":
        scale = 4.0
        rotation = Gf.Vec3f(90,0,0)
        position[2] = position[2] + 60 #Buffer the cube off the z

    #CUSTOM SHAPE OVERRIDES
    if prim_name.lower() == "observation_chair":
        scale =0.8
        rotation = Gf.Vec3f(90,0,220)
        translate=Gf.Vec3d(position[0]+200, position[1]+200, position[2])
    if prim_name.lower() == "leather_jacket":
        scale =0.25
        rotation = Gf.Vec3f(90,0,0)
        translate=Gf.Vec3d(position[0]-20, position[1], position[2]-25)
    if prim_name.lower() == "coat_rack":
        scale =0.55
        rotation = Gf.Vec3f(90,0,0)                        
        translate=Gf.Vec3d(position[0]-220, position[1]+210, position[2]+10)
        

    carb.log_info("Placing prim: " + shapeToRender + " | " + str(new_prim_path) + " @ " 
        + "scl:" + str(scale) + " x:" + str(position[0]) + "," + " y:" + str(position[1]) + "," + " z:" + str(position[2]))           

    api = UsdGeom.XformCommonAPI(my_new_prim)
    
    try:
        api.SetTranslate(translate)
        api.SetRotate(rotation,UsdGeom.XformCommonAPI.RotationOrderXYZ)
        api.SetScale(Gf.Vec3f(scale,scale,scale))
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
        x=180, y=1875, fillColor="White", font=font,
        fontSize=font_size )

#Creates a plane of a certain size in a specific location
def create_plane(self,Path:str, Name :str, Size: int, Location: Gf.Vec3f, Color:Gf.Vec3f):

    stage_ref = omni.usd.get_context().get_stage()  

    GroundHelper._create_default_ground(self)

    # omni.kit.commands.execute('AddGroundPlaneCommand',
    # stage=stage_ref,
    # planePath=Path,
    # axis="Z",
    # size=Size,
    # position=Location,
    # color=Color)


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
    nme = nme.replace("#", "_")

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

def only_select_parent_prims(prim_paths):
        
        paths = []

        for path in prim_paths:

            if str(path).find("Collision") != -1:
                continue #skip paths with Collision in them

            if str(path).find("Baked") != -1:
                continue #skip paths with Baked in them

            parts = path.split("/")

            if parts[2] == "Looks": continue
            if parts[1] == "Environment": continue

            #Select the root object only.
            if len(parts) == 3:
                parentPath = "/" + parts[1] + "/" + parts[2]
            if len(parts) == 4:
                parentPath = "/" + parts[1] + "/" + parts[2] + "/" + parts[3]
            if len(parts) >= 5:
                parentPath = "/" + parts[1] + "/" + parts[2] + "/" + parts[3] + "/" + parts[4]
            paths.append(parentPath)    
        
        return paths


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
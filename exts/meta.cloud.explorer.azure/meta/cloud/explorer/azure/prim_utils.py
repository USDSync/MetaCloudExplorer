__all__ = ["create_plane", "get_font_size_from_length", "get_parent_child_prim_path", "create_and_place_prim", "log_transforms"]
import sys
import omni.usd
import omni.kit.commands
import shutil
from pxr import Sdf
from pxr import Gf, UsdGeom, UsdLux
from .pillow_text import draw_text_on_image_at_position


def create_and_place_prim(self,
    new_prim_path:str,
    shapeToRender:str, 
    scale:float, 
    position:Gf.Vec3f
    ):
    
    print("Creating new prim: " + new_prim_path)
    stage =  omni.usd.get_context().get_stage()

    # Create prim to add the reference to.
    prim = stage.DefinePrim(new_prim_path)
    prim.GetReferences().AddReference(shapeToRender)
    my_new_prim = stage.GetPrimAtPath(new_prim_path)

    #Are we still set to default? Change cube size and position
    if shapeToRender == "omniverse://localhost/Resources/3dIcons/scene.usd":
        scale = 3.0
        position[2] = position[2] + 30 #Buffer the cube off the z

    print("Placing prim: " + shapeToRender + " | " + str(new_prim_path) + " @ " 
        + "scl:" + str(scale) + " x:" + str(position[0]) + "," + " y:" + str(position[1]) + "," + " z:" + str(position[2]))           

    # # Remove the tranform, rotate, scale attributes
    for name in my_new_prim.GetPropertyNames():
        if name == "xformOp:translate":
            my_new_prim.RemoveProperty("xformOp:translate")

        if name == "xformOp:rotateXYZ":
            my_new_prim.RemoveProperty("xformOp:rotateXYZ")

        if name == "xformOp:scale":
            my_new_prim.RemoveProperty("xformOp:scale")

        if name == "xformOp:orient":
            my_new_prim.RemoveProperty("xformOp:orient")

    xform = UsdGeom.Xformable(my_new_prim)
    properties = my_new_prim.GetPropertyNames()

    try:

        order = my_new_prim.GetAttribute("xformOpOrder").Get()
        if 'xformOp:scale' not in properties:
            my_new_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Asset)
            my_new_prim.GetAttribute('xformOp:scale').Set(Gf.Vec3f(scale,scale,scale))
        else:
            my_new_prim.GetAttribute('xformOp:scale').Set(Gf.Vec3f(scale,scale,scale))
    except:
        print("Oops!", sys.exc_info()[0], "occurred.")

    try:

        if 'xformOp:rotateXYZ' not in properties:
            my_new_prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Asset)
            my_new_prim.GetAttribute('xformOp:rotateXYZ').Set(Gf.Vec3f(0.0, 0.0, 0.0))
        else:
            my_new_prim.GetAttribute('xformOp:rotateXYZ').Set(Gf.Vec3f(0.0, 0.0, 0.0))

    except:
        print("Oops!", sys.exc_info()[0], "occurred.")

    try:
        if 'xformOp:translate' not in properties:
            my_new_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Asset)
            my_new_prim.GetAttribute('xformOp:translate').Set(Gf.Vec3d(position[0], position[1], position[2]))
        else: 
            my_new_prim.GetAttribute('xformOp:translate').Set(Gf.Vec3d(position[0], position[1], position[2]))    
    except:
        print("Oops!", sys.exc_info()[0], "occurred.")
        # Set your transform, rotate, scale attributes, ORDER MATTERS!!!
        # Create TRANSLATE,SCALE, ROATATE - in that order..
    try:    
        print("before: " + str(my_new_prim.GetAttribute("xformOpOrder").Get()))
        my_new_prim.GetAttribute("xformOpOrder").Set(["xformOp:translate", "xformOp:scale", "xformOp:rotateXYZ"])
        print("after: " + str(my_new_prim.GetAttribute("xformOpOrder").Get()))
    except:
        print("Oops!", sys.exc_info()[0], "occurred.")


      
    # #this might error
    # try:
    #     properties = my_new_prim.GetPropertyNames()
    #     if 'xformOp:scale' not in properties:
    #         UsdGeom.Xformable(my_new_prim).AddScaleOp()
    #     if 'xformOp:rotateXYZ' not in properties:
    #         UsdGeom.Xformable(my_new_prim).AddRotateXYZOp()
    #     if 'xformOp:translate' not in properties:
    #         UsdGeom.Xformable(my_new_prim).AddTranslateOp()
    # except:
    #     pass

    # # Set your transform, rotate, scale attributes, ORDER MATTERS!!!
    # # Create SCALE, TRANSLATE, ROATATE - in that order..
    # try:
    #     my_new_prim.GetAttribute('xformOp:translate').Set(position)
    #     my_new_prim.GetAttribute('xformOp:rotateXYZ').Set(Gf.Vec3f(0.0, 0.0, 0.0))
    #     my_new_prim.GetAttribute('xformOp:scale').Set(Gf.Vec3f(scale,scale,scale))
    
    #     #print("before: " + str(my_new_prim.GetAttribute("xformOpOrder").Get()))
    #     my_new_prim.GetAttribute("xformOpOrder").Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])
    #     #print("after: " + str(my_new_prim.GetAttribute("xformOpOrder").Get()))
    # except:
    #     pass                          
    #     #my_new_prim.GetAttribute('xformOpOrder').Set(["xformOp:translate, xformOp:rotateXYZ, xformOp:scale"])
   

#log the vectors
def log_transforms(self, vectors):
    for v in vectors:
        logdata = str(vectors[v][0]) + "," + str(vectors[v][1]) + "," + str(vectors[v][2])
        print(logdata)


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
        prim_name=g,
        mtl_created_list=None,
        bind_selected_prims=True)

def draw_image(self, output_file:str, src_file:str, textToDraw:str, costToDraw:str):
            
    font_size = get_font_size_from_length(len(textToDraw))

    draw_text_on_image_at_position(                
        input_image_path=src_file,
        output_image_path=output_file, 
        textToDraw=str(textToDraw), 
        costToDraw=str(costToDraw),
        x=180, y=1875, fillColor="Yellow", font='https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true',
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

    prim_len = len(str(groupPath)) + len(resName)
    if (prim_len) > 70:
        diff = prim_len - 70
        trim = len(resName) - diff 
        resName = resName[:trim] 
    
    shape_prim_path = Sdf.Path(groupPath.AppendPath(resName))
    return shape_prim_path
    

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
__all__ = ["create_plane", "get_font_size_from_length"]

import omni.usd
import omni.kit.commands
import shutil
from pxr import Sdf
from pxr import Gf, UsdGeom, UsdLux
from .pillow_text import draw_text_on_image_at_position



# Calculates where to put a prim on a parent plane depending on the size and index 
# stageClass = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 *2
def calcPrimPlacementOnPlane(stageClass: int, stageSize: float, position: int, scaleFactor:float, groudOffset:float, upDirection:str ): 

    if stageClass == 1: # holds one resource, put it in center..
        if upDirection == "Y":
            return Gf.Vec3f(0,0,0)

    elif stageClass == 2: #holds 4 resources
        
        pass


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
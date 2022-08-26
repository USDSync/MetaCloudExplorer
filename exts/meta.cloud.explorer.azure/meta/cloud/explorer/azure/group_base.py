from abc import ABC, abstractmethod

import omni.client
import omni.kit.app
import omni.ui as ui
import omni.usd
import omni.kit.commands

from pathlib import Path
import shutil
import os
import asyncio
import locale 

from .prim_utils import create_plane
from .prim_utils import get_font_size_from_length
from .prim_utils import draw_image
from .prim_utils import cleanup_prim_path, create_and_place_prim, get_parent_child_prim_path

from pxr import Gf, UsdGeom, UsdLux, Usd, Sdf
from .data_manager import DataManager
from .data_store import DataStore

from .math_utils import calcPlaneSizeForGroup
from .scatter_complex import distributePlanes
from .scatter_on_planes import scatterOnFixedPlane
from .omni_utils import create_prims, create_shaders
from os.path import exists


CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.joinpath("temp")

#Defines an Abstract class of an Aggregate set of resource views
#Children access specific data sets for the base
class GroupBase(ABC): 
    def __init__(self):

        self._dataManager = DataManager.instance() # Get A Singleton instance
        self._dataStore = DataStore.instance() # Get A Singleton instance

        #root prim paths
        self.root_path = Sdf.Path('/World')
               
        # limit the number of rows read
        self.max_elements = 5000
        self.base_prim_size = 50

        #limits
        self.x_threshold = 50000
        self.y_threshold = 50000
        self.z_threshold = 50000
        self.x_extent = 0
        self.y_extent = 0
        self.z_extent = 0

    #Create the stage...
    def initializeStage(self, stage_unit_per_meter:float):
        
        self._stage = omni.usd.get_context().get_stage()
        root_prim = self._stage.GetPrimAtPath(self.root_path)
        
        #  set the up axis
        UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.z)

        #  set the unit of the world
        UsdGeom.SetStageMetersPerUnit(self._stage, stage_unit_per_meter)
        self._stage.SetDefaultPrim(root_prim)

        # add a light
        light_prim_path = self.root_path.AppendPath('DomeLight')
        light_prim = UsdLux.DistantLight.Define(self._stage, str(light_prim_path))
        light_prim.CreateAngleAttr(0.53)
        light_prim.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 0.745))
        light_prim.CreateIntensityAttr(500.0)
    
    async def CreateGroups(self, basePath:Sdf.Path, upAxis:str, groups:list, transforms, sizes):
        self.CreateGroups(self, basePath, upAxis, groups, transforms, sizes)

    #Depending on the Active View, "groups" will contain different aggreagetes.
    #This function creates the GroundPlane objects on the stage for each group
    def CreateGroups(self, basePath:Sdf.Path, upAxis:str, groups:list, transforms, sizes):
        
        #b = sorted(groups)
        #print("Sorted keys",b)  

        if (len(groups)) >0 :

            #Create new prims and then transform them
            create_prims(
                transforms=transforms,
                prim_names=groups,
                parent_path=str(basePath),
                up_axis=upAxis,
                plane_size=sizes
            )

            #Create shaders for each plane
            for g in groups:
                create_shaders(base_path=basePath.AppendPath(g["group"]), prim_name=g["group"])

            #Draw shaders on the stages
            self.AddPlaneLabelShaders(groups)

    #Assign Images to the group Shaders
    def AddPlaneLabelShaders(self, groups):

        #Images have been pre-made, jsut assign them
        for g in groups:     
            clean = cleanup_prim_path(self, g["group"])   
            
            #Dont show cost
            output_file = DATA_PATH.joinpath(clean + ".png")
            file_exists = exists(output_file)                
            
            if not file_exists:
                draw_image(self, output_file=output_file, src_file=self._dataStore._bg_file_path , textToDraw=g, costToDraw="")
                
            #Get Stage
            stage = omni.usd.get_context().get_stage()

            #Find the /Looks root
            curr_prim = stage.GetPrimAtPath("/")
            looks_path = ""
            for prim in Usd.PrimRange(curr_prim):

                if prim.GetPath() == "/Looks":
                    looks_path = "/Looks"
                    break
                elif prim.GetPath() == "/World/Looks":
                    looks_path = "/World/Looks"
                    break

            #print("Looks root is: " +looks_path)
            #Get the Shader and set the image property
            if (looks_path == ""):
                looks_path = "/Looks"

            shader_path = Sdf.Path(looks_path)
            shader_path = Sdf.Path(shader_path.AppendPath(clean))
            shader_path = Sdf.Path(shader_path.AppendPath("Shader"))

            #select the shader
            selection = omni.usd.get_context().get_selection()
            selection.set_selected_prim_paths([str(shader_path)], False)         

            #Get the Shader
            shader_prim = stage.GetPrimAtPath(str(shader_path))

            # print("Shader Attributes:-----" + str(shader_path))
            # print(shader_prim.GetAttributes())

            try:
                shader_prim.CreateAttribute("inputs:diffuse_texture", Sdf.ValueTypeNames.Asset)
                                    
                omni.kit.commands.execute('ChangeProperty',
                    prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
                    value=str(output_file), prev=str(output_file))
            except:
                #Do it again!
                omni.kit.commands.execute('ChangeProperty',
                prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
                value=str(output_file),prev=str(output_file))        

    #FIGURES OUT WHERE TO PUT THE PRIMS ON A VARIABLE SIZED-PLANE
    def calculateGroupTransforms(self, scale:float, count:int, upAxis:str ):

        #ex 400.0 -> 800 - 400 plane is 800x800
        plane_size = (calcPlaneSizeForGroup(scaleFactor=scale, resourceCount=count)*1.8) #1.8 gives as a border buffer
        plane_class = ((plane_size/100)/2) +1
        
        #distance of objects depending on grid size..  
        dist = plane_size / plane_class

        #Use NVIDIAs Scatter algo to position on varying sized planes
        transforms = scatterOnFixedPlane(
            upAxis=upAxis,
            count=[int(plane_class), int(plane_class), 1], # Distribute accross the plane size
            distance=[dist,dist,dist],
            scaleFactor=scale
        )

        return transforms 
   
    #Change the Group Shaders textures to /from cost images
    def show_hide_costs(self):

        #Get Stage
        stage = omni.usd.get_context().get_stage()

        #Find the /Looks root
        curr_prim = stage.GetPrimAtPath("/")
        looks_path = ""
        for prim in Usd.PrimRange(curr_prim):

            if prim.GetPath() == "/Looks":
                looks_path = "/Looks"
                break
            elif prim.GetPath() == "/World/Looks":
                looks_path = "/World/Looks"
                break

            #print("Looks root is: " +looks_path)
            #Get the Shader and set the image property
            if (looks_path == ""):
                looks_path = "/Looks"


        #Flip the shader images on all group shader prims
        for g in self._dataStore._lcl_groups:     
            clean = cleanup_prim_path(self, g["group"])   
            
            cost_file = DATA_PATH.joinpath(clean + "-cost.png")
            file_exists = exists(cost_file)

            if not file_exists:
                draw_image(self, output_file=cost_file, src_file=self._dataStore._bg_file_path , textToDraw=g, costToDraw=self._cost)


            output_file = DATA_PATH.joinpath(clean + ".png")
            file_exists = exists(output_file)                
                
            if not file_exists:
                draw_image(self, output_file=output_file, src_file=self._dataStore._bg_file_path , textToDraw=g, costToDraw="")               

            #Get the Shaders
            shader_path = Sdf.Path(looks_path)
            shader_path = Sdf.Path(shader_path.AppendPath(clean))
            shader_path = Sdf.Path(shader_path.AppendPath("Shader"))

            #select the shader
            selection = omni.usd.get_context().get_selection()
            selection.set_selected_prim_paths([str(shader_path)], False)         

            #Get the Shader
            shader_prim = stage.GetPrimAtPath(str(shader_path))

            # print("Shader Attributes:-----" + str(shader_path))
            # print(shader_prim.GetAttributes())

            try:                           
                currentVal = shader_prim.GetAttribute("inputs:diffuse_texture").Get()
                if "-cost.png" not in str(currentVal): 
                    omni.kit.commands.execute('ChangeProperty',
                        prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
                        value=str(cost_file), prev=str(output_file))
                else:
                    omni.kit.commands.execute('ChangeProperty',
                        prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
                        value=str(output_file), prev=str(cost_file))
            except:
                pass

    async def loadGroupResources(self,group_prim_path, values):
        await self.loadGroupResources(self,group_prim_path, values)

    #Load the resources from map
    def loadGroupResources(self,group_prim_path, values):
        
        i=0 # prim count tracker
        resCount = len(values)

        for res in values:
            print("Placing prim " + str(i) + " of " + str(resCount))

            resName = res["name"]
            resShape = res["shape"]

            #Get the transform coordinates for a plane of this size with nn resources
            transforms = self.calculateGroupTransforms(scale=self._scale,upAxis=self._upAxis, count=resCount)
            prim_vector = transforms[i]
            new_prim_path = get_parent_child_prim_path(self, group_prim_path, resName)

            create_and_place_prim(self,
                new_prim_path=str(new_prim_path),
                shapeToRender=resShape,
                scale=(self._scale*self.base_prim_size),
                position=prim_vector
            )                    

            i=i+1 #increment resource id



    # Create Group Planes for the aggregates
    @abstractmethod
    def calcGroupPlaneSizes(self):      
        pass # Requires subclass implm

    # Calc Costs for the aggregates
    @abstractmethod
    def calulateCosts(self):      
        pass # Requires subclass implm

    # Load the resources for this view's groups
    @abstractmethod
    def loadResources(self):      
        pass # Requires subclass implm

    #Selcet the active group's prims
    @abstractmethod
    def selectGroupPrims(self):
        pass # Requires subclass implm
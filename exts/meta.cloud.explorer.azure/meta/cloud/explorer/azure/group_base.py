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
import carb

from .prim_utils import create_plane
from .prim_utils import get_font_size_from_length
from .prim_utils import draw_image
from .prim_utils import cleanup_prim_path, create_and_place_prim, get_parent_child_prim_path

from pxr import Gf, UsdGeom, UsdLux, Usd, Sdf
from .data_manager import DataManager
from .data_store import DataStore

from .math_utils import calculateGroupTransforms
from .scatter_complex import distributePlanes
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
    
        # add a light
        light_prim_path = self.root_path.AppendPath('DistantLight')
        light_prim = UsdLux.DistantLight.Define(self._stage, str(light_prim_path))
        light_prim.CreateAngleAttr(0.53)
        light_prim.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 0.745))
        light_prim.CreateIntensityAttr(1000.0)    


    #Depending on the Active View, "groups" will contain different aggreagetes.
    #This function creates the GroundPlane objects on the stage for each group
    async def CreateGroups(self, transforms):
        
        #b = sorted(groups)
        #carb.log_info("Sorted keys",b)  

        if (len(self._dataStore._lcl_groups)) >0 :

            #Create new prims and then transform them
            path = str(Sdf.Path(self.root_path).AppendPath(self._view_path))
            create_prims(
                transforms=transforms,
                prim_names=self._dataStore._lcl_groups,
                parent_path=path,
                up_axis="Z",
                plane_size=self._dataStore._lcl_sizes
            )

            #DEBUG
            i=0
            for grp in self._dataStore._lcl_groups:

                prim_path = Sdf.Path(self.root_path).AppendPath(str(self._view_path))
                prim_path = Sdf.Path(prim_path).AppendPath(grp["group"])
                
                #Selects prim, creates associated OMNIPBR shaders

                carb.log_info("Create shader " + grp["group"] + " of " + str(len(self._dataStore._lcl_groups)))
                await create_shaders(base_path=prim_path, prim_name=grp["group"])
                await omni.kit.app.get_app().next_update_async()

            #Set the shader images for the groups
            await self.AddShaderImages()
            await omni.kit.app.get_app().next_update_async()

    #Assign Images to the group Shaders
    async def AddShaderImages(self):

        #Images have been pre-made, jsut assign them
        for g in self._dataStore._lcl_groups:     
            clean = cleanup_prim_path(self, g["group"])   
            
            #Dont show cost
            output_file = DATA_PATH.joinpath(clean + ".png")
            file_exists = exists(output_file)                
            
            if not file_exists:
                draw_image(self, output_file=output_file, src_file=self._dataStore._bgl_file_path , textToDraw=g, costToDraw="")
                
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

            #carb.log_info("Looks root is: " +looks_path)
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

            carb.log_info("Shader Attributes:-----" + str(shader_path))
            #carb.log_info(shader_prim.GetAttributes())
            carb.log_info("Set shader image " + str(output_file))

            try:
                shader_prim.CreateAttribute("inputs:diffuse_texture", Sdf.ValueTypeNames.Asset)
                                    
                omni.kit.commands.execute('ChangeProperty',
                    prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
                    value=str(output_file), prev=str(output_file))
                await omni.kit.app.get_app().next_update_async()
            except:
                #Do it again!
                omni.kit.commands.execute('ChangeProperty',
                prop_path=Sdf.Path(shader_path).AppendPath('.inputs:diffuse_texture'),
                value=str(output_file),prev=str(output_file))        
   
    #Change the Group Shaders textures to /from cost images
    def showHideCosts(self):

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

            #carb.log_info("Looks root is: " +looks_path)
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

            # carb.log_info("Shader Attributes:-----" + str(shader_path))
            # carb.log_info(shader_prim.GetAttributes())

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

    #Load group resources async
    async def loadGroupResources(self,group_name, group_prim_path, values):
        await self.loadGroupResources(self,group_name, group_prim_path, values)

    #Load the resources from map
    def loadGroupResources(self,group_name, group_prim_path, values):
        
        i=0 # prim count tracker
        resCount = len(values)
        
        #Get the transform coordinates for a plane of this size with nn resources
        transforms = calculateGroupTransforms(self=self, scale=self._scale, count=resCount)

        for res in values:
            carb.log_info("Placing prim " + res["type"] + " " + str(i) + " of " + str(resCount))

            resName = res["name"]
            resShape = res["shape"]
            resType = res["type"]
            prim_vector = transforms[i]
            new_prim_path = get_parent_child_prim_path(self, group_prim_path, resName)

            create_and_place_prim(self,
                prim_type= resType,
                prim_name=resName,
                grp_name=group_name,
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
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

from  .prim_utils import create_plane
from  .prim_utils import cleanup_prim_path
from  .prim_utils import get_font_size_from_length
from  .prim_utils import draw_image

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

        #Calc Plane sizes based on items in group
        self._sizes = [] #Plane  sizes determined by resource counts
        self._groups = [] #Group data for creating planes

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

    
    # Create Group Planes for the aggregates
    @abstractmethod
    def calcPlaneGroupSettings(self):      
        pass # Requires subclass implm

    # Calc Costs for the aggregates
    @abstractmethod
    def calulateCosts(self):      
        pass # Requires subclass implm

    # Calc Costs for the aggregates
    @abstractmethod
    def prepResources(self):      
        pass # Requires subclass implm

    #Selcet the active group's prims
    @abstractmethod
    def selectGroupPrims(self):
        pass


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

    #Load the resources!
    def LoadResources(self, paths):
        
        if len(paths) == 0:
            pass
        else:
            pass




    #User passes in a list of selected paths 
    #TODO FIX THIS TO USE THE MAPS!!!  
    #Psuedo, using map

    #Based on view, read the resource map and load resoruces for the items in the map
    #paths can be a subset of items in the map.  ie user can select a specific group to show 

    #get the keys to load res for
    #for each group to load
        #load the resources



        # if (len(self._groups) >0):
        #     stage =  omni.usd.get_context().get_stage()

        #     #Get Group Prim to place resources on 
        #     for group in self._groups:
                
        #         #Cleanup the group name for a prim path
        #         group_prim_path = self.view_path.AppendPath(cleanup_prim_path(self, group))

        #         resource_count = self._groups[group]
        #         transforms = self.calculateGroupTransforms(self._scale, self._upAxis, resource_count)

        #         #log the transform postions
        #         self.log_transforms(transforms)

        #         i=0
        #         if (group_prim_path is not None):
                    
        #             #BAD BAD BAD!!!
        #             #Lets get the resources to place on this view
        #             for k, v in self._dataStore._resources.items():
                        


        #                 if (v["group"] == group): #is this resource in this "group"?

        #                     #Cleanup Resource Name - Max path is 84?
        #                     resName = cleanup_prim_path(self, k)

        #                     prim_len = len(str(group_prim_path)) + len(resName)
        #                     if (prim_len) > 70:
        #                         diff = prim_len - 70 # say its 89..  this gives 5 
        #                         trim = len(resName) - diff 
        #                         resName = resName[:trim] #trim off that 5

        #                     resName=cleanup_prim_path(self, resName)
        #                     print("Creating new prim: " + resName)
                            
        #                     #Place a new Prim in position X,Y,Z with A = Axis up                           
        #                     shape_prim_path = group_prim_path.AppendPath(resName)

        #                     # Create prim to add the reference to.
        #                     prim = stage.DefinePrim(shape_prim_path)

        #                     # Set a default
        #                     shape_to_render = "omniverse://localhost/Resources/3dIcons/scene.usd"

        #                     try:
        #                         typeName = cleanup_prim_path(self,  v["type"])
        #                         shape_to_render = shape_usda_name[typeName]   
        #                     except:
        #                         print("No matching prim found - " + typeName)                                  

        #                     prim.GetReferences().AddReference(shape_to_render)

        #                     my_new_prim = stage.GetPrimAtPath(shape_prim_path)

        #                     prim_vector = transforms[i]

        #                     #calculate the scale of the prim
        #                     scale = (self.scale_factor*self.base_prim_size)

        #                     #Are we still set to default? Change cube size and position
        #                     if shape_to_render == "omniverse://localhost/Resources/3dIcons/scene.usd":
        #                         scale = 3.75 * self.scale_factor
                                
        #                         if upAxis == "X":
        #                             prim_vector[0] = prim_vector[0] + 37.5
        #                         if upAxis == "Y":
        #                             prim_vector[1] = prim_vector[1] + 37.5
        #                         if upAxis == "Z":
        #                             prim_vector[2] = prim_vector[2] + 37.5


        #                     print("Placing prim: " + v["type"] + " " + shape_to_render + " | " + str(shape_prim_path) + " @ " 
        #                         + str(prim_vector[0]) + "," + str(prim_vector[1]) + "," + str(prim_vector[2]))           

        #                     # Create tranform, rotate, scale attributes
        #                     for name in my_new_prim.GetPropertyNames():
        #                         if name == "xformOp:translate":
        #                             my_new_prim.RemoveProperty("xformOp:translate")

        #                         if name == "xformOp:rotateXYZ":
        #                             my_new_prim.RemoveProperty("xformOp:rotateXYZ")

        #                         if name == "xformOp:scale":
        #                             my_new_prim.RemoveProperty("xformOp:scale")
                                
        #                     #     if name == "xformOpOrder":
        #                     #         my_new_prim.RemoveProperty("xformOp:scale")

        #                     #this might error
        #                     try:
        #                         properties = my_new_prim.GetPropertyNames()
        #                         if 'xformOp:scale' not in properties:
        #                             UsdGeom.Xformable(my_new_prim).AddScaleOp()
        #                         if 'xformOp:rotateXYZ' not in properties:
        #                             UsdGeom.Xformable(my_new_prim).AddRotateXYZOp()
        #                         if 'xformOp:translate' not in properties:
        #                             UsdGeom.Xformable(my_new_prim).AddTranslateOp()
        #                     except:
        #                         pass

        #                     # Set your transform, rotate, scale attributes, ORDER MATTERS!!!
        #                     # Create SCALE, TRANSLATE, ROATATE - in that order..
        #                     try:
        #                         my_new_prim.GetAttribute('xformOp:translate').Set(prim_vector)
        #                         my_new_prim.GetAttribute('xformOp:rotateXYZ').Set(Gf.Vec3f(0.0, 0.0, 0.0))
        #                         my_new_prim.GetAttribute('xformOp:scale').Set(Gf.Vec3f(scale,scale,scale))
                            
        #                         #print("before: " + str(my_new_prim.GetAttribute("xformOpOrder").Get()))
        #                         my_new_prim.GetAttribute("xformOpOrder").Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])
        #                         #print("after: " + str(my_new_prim.GetAttribute("xformOpOrder").Get()))
        #                     except:
        #                         pass                          
        #                     #my_new_prim.GetAttribute('xformOpOrder').Set(["xformOp:translate, xformOp:rotateXYZ, xformOp:scale"])

        #                     i=i+1 # Current shape

    #FIGURES OUT WHERE TO PUT THE PRIMS
    def calculateGroupTransforms(scale:float, count:int, upAxis:str ):

        #ex 400.0 -> 800 - 400 plane is 800x800
        plane_size = (calcPlaneSizeForGroup(scaleFactor=scale, resourceCount=count)*2) 
        plane_class = (plane_size/100)/2
        
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
        for g in self._groups:     
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

# ABSTRACT CLASSES FOR EACH VIEWTYPE
# IMPLEMENTS 

#TODO - Implement AAD
class AADGrpView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str):
        self.layer_root_path = Sdf.Path(self.root_path.AppendPath('AAD'))
        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self.view_path = viewPath
        super().__init__()

    def calcPlaneGroupSettings(self):
        pass

    def calulateCosts(self):      

        for g in self._groups:
            #Get the cost by resource group
            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
            try:
                self._cost = str(locale.currency(self._dataStore._aad_cost[g]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     


    def prepResources(self):      
        pass # Requires subclass implm

#Specific Handling for Resoruce Groups
class ResGrpView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str, symPlanes:bool):
        self._root_path = Sdf.Path(viewPath)
        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self._view_path = viewPath
        self._symPlanes = symPlanes

        super().__init__()

    def calcPlaneGroupSettings(self):
        
        if len(self._dataStore._group_count) == 0:
            self._dataManager.refresh_data()

        #check it again
        if len(self._dataStore._group_count) == 0:
            return 0
        
        #set root prim for child resources to add
        self.view_path = Sdf.Path(self.root_path.AppendPath('RGrp'))

        #temp group list to prep for planes, adds to main aggregate
        gpz = self._dataStore._group_count.copy()

        for grp in gpz:
            size = calcPlaneSizeForGroup(
                    scaleFactor=self._scale, 
                    resourceCount=self._dataStore._group_count.get(grp)
                )
            self._sizes.append(
                size
            )
            grp = cleanup_prim_path(self, grp)
            self._groups.append({ "group":grp, "size":size })

    #Abstract method to calc cost 
    def calulateCosts(self):      

        for g in self._groups:
            #Get the cost by resource group
            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
            try:
                self._cost = str(locale.currency(self._dataStore._group_cost[g["group"]]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     

    #Abstact to determine resources to show
    def prepResources(self):      
        pass # Requires subclass implm


    def selectGroupPrims(self):
        
        self.paths = []

        base = Sdf.Path("/RGrp")

        for grp in self._dataStore._map_group.keys():
            grp_path = base.AppendPath(cleanup_prim_path(self, grp))
            self.paths.append(str(grp_path))

        omni.kit.commands.execute('SelectPrimsCommand',
            old_selected_paths=[],
            new_selected_paths=self.paths,
            expand_in_stage=True)






class SubGrpView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str, symPlanes:bool):
        self._root_path = Sdf.Path(viewPath)
        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self._view_path = viewPath
        self._symPlanes = symPlanes

        super().__init__()


    def calcPlaneGroupSettings(self):
        if len(self._dataStore._subscription_count) == 0:
            self._dataManager.refresh_data()

        #check it again
        if len(self._dataStore._subscription_count) == 0:
            return 0
        
        self.view_path = Sdf.Path(self.root_path.AppendPath('Subs'))

        #temp group list to prep for planes, adds to main aggregate
        gpz = self._dataStore._subscription_count.copy()
        for grp in gpz:
            size = calcPlaneSizeForGroup(
                    scaleFactor=self._scale, 
                    resourceCount=self._dataStore._subscription_count.get(grp)
                )
            self._sizes.append(
                size
            )
            grp = cleanup_prim_path(self, grp)
            self._groups.append({ "group":grp, "size":size })

    def calulateCosts(self):      

        for g in self._groups:

            #Get the cost by resource group
            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
            try:
                self._cost = str(locale.currency(self._dataStore._subscription_cost[g]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     

    #Abstact to determine resources to show
    def prepResources(self):      
        pass # Requires subclass implm

    
    def selectGroupPrims(self):
        
        self.paths = []
        stage = omni.usd.get_context().get_stage()
        base = Sdf.Path("/World/Subs")

        curr_prim = stage.GetPrimAtPath(base)

        for prim in Usd.PrimRange(curr_prim):
            # only process shapes and meshes
            self.paths.append(str(prim.GetPath()))

        # for grp in self._dataStore._map_subscription.keys():
        #     grp_path = base.AppendPath(cleanup_prim_path(self, grp))
        #     self.paths.append(str(grp_path))

        omni.kit.commands.execute('SelectPrimsCommand',
            old_selected_paths=[],
            new_selected_paths=self.paths,
            expand_in_stage=True)


class LocGrpView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str, symPlanes:bool):
        self._root_path = Sdf.Path(viewPath)
        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self._view_path = viewPath
        self._symPlanes = symPlanes

        super().__init__()

    def calcPlaneGroupSettings(self):
        if len(self._dataStore._location_count) == 0:
            self._dataManager.refresh_data()

        #check it again
        if len(self._dataStore._location_count) == 0:
            return 0

        self.view_path = Sdf.Path(self.root_path.AppendPath('Loc'))

        gpz = self._dataStore._location_count.copy()
        for grp in gpz:
            size = calcPlaneSizeForGroup(
                    scaleFactor=self._scale, 
                    resourceCount=self._dataStore._location_count.get(grp)
                )
            self._sizes.append(
                size
            )
            grp = cleanup_prim_path(self, grp)
            self._groups.append({ "group":grp, "size":size })

    def calulateCosts(self):      

        for g in self._groups:

            #Get the cost by resource group
            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

            try:
                self._cost = str(locale.currency(self._dataStore._location_cost[g]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     

    #Abstact to determine resources to show
    def prepResources(self):      
        pass

    def selectGroupPrims(self):
        
        self.paths = []

        base = Sdf.Path("/Subs")

        for grp in self._dataStore._map_location.keys():
            grp_path = base.AppendPath(cleanup_prim_path(self, grp))
            self.paths.append(str(grp_path))

        omni.kit.commands.execute('SelectPrimsCommand',
            old_selected_paths=[],
            new_selected_paths=self.paths,
            expand_in_stage=True)

class TypeGrpView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str, symPlanes:bool):
        self._root_path = Sdf.Path(viewPath)
        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self._view_path = viewPath
        self._symPlanes = symPlanes

        super().__init__()


    def calcPlaneGroupSettings(self):
        if len(self._dataStore._type_count) == 0:
            self._dataManager.refresh_data()

        #check it again
        if len(self._dataStore._type_count) == 0:
            return 0

        self.view_path = Sdf.Path(self.root_path.AppendPath('Type'))

        #temp group list to prep for planes, adds to main aggregate
        gpz = self._dataStore._type_count.copy()
        for grp in gpz:
            size = calcPlaneSizeForGroup(
                    scaleFactor=self._scale, 
                    resourceCount=self._dataStore._type_count.get(grp)
                )
            self._sizes.append(
                size
            )
            grp = cleanup_prim_path(self, grp)
            self._groups.append({ "group":grp, "size":size })

    def calulateCosts(self):      

        for g in self._groups:

            #Get the cost by resource group
            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

            try:
                self._cost = str(locale.currency(self._dataStore._type_cost[g]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     

    #Abstact to determine resources to show
    def prepResources(self):      
        pass # Requires subclass implm

    def selectGroupPrims(self):
        
        self.paths = []

        base = Sdf.Path("/Subs")

        for grp in self._dataStore.map_group.keys():
            grp_path = base.AppendPath(cleanup_prim_path(self, grp))
            self.paths.append(str(grp_path))

        omni.kit.commands.execute('SelectPrimsCommand',
            old_selected_paths=[],
            new_selected_paths=self.paths,
            expand_in_stage=True)

class TypeTagView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str, symPlanes:bool):
        self._root_path = Sdf.Path(viewPath)
        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self._view_path = viewPath
        self._symPlanes = symPlanes

        super().__init__()


    def calcPlaneGroupSettings(self):
        if len(self._dataStore._tag_count) == 0:
            self._dataManager.refresh_data()

        #check it again
        if len(self._dataStore._tag_count) == 0:
            return 0

        self.view_path = Sdf.Path(self.root_path.AppendPath('Tag'))

        #temp group list to prep for planes, adds to main aggregate
        gpz = self._dataStore._tag_count.copy()
        for grp in gpz:
            size = calcPlaneSizeForGroup(
                    scaleFactor=self._scale, 
                    resourceCount=self._dataStore._tag_count.get(grp)
                )
            self._sizes.append(
                size
            )
            grp = cleanup_prim_path(self, grp)
            self._groups.append({ "group":grp, "size":size })

    def calulateCosts(self):      

        for g in self._groups:

            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

            try:
                self._cost = str(locale.currency(self._dataStore._tag_cost[g]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     
    
    
    #Abstact to determine resources to show
    def prepResources(self):      
        pass # Requires subclass implm

    def selectGroupPrims(self):
        
        self.paths = []

        base = Sdf.Path("/Subs")

        for grp in self._dataStore.map_tag.keys():
            grp_path = base.AppendPath(cleanup_prim_path(self, grp))
            self.paths.append(str(grp_path))

        omni.kit.commands.execute('SelectPrimsCommand',
            old_selected_paths=[],
            new_selected_paths=self.paths,
            expand_in_stage=True)
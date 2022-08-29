
from .group_base import GroupBase
from pxr import Gf, UsdGeom, UsdLux, Usd, Sdf
from .math_utils import calcPlaneSizeForGroup
from .prim_utils import cleanup_prim_path, create_and_place_prim, get_parent_child_prim_path
import locale 
import asyncio
import carb
import omni.client
import omni.kit.app
import omni.ui as ui
import omni.usd
import omni.kit.commands

class TypeGrpView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str, symPlanes:bool, binPack:bool):

        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self._view_path = viewPath
        self._symPlanes = symPlanes
        self._binPack = binPack

        super().__init__()


    def calcGroupPlaneSizes(self):

        self._dataStore._lcl_groups = []
        self._dataStore._lcl_sizes = []

        if len(self._dataStore._type_count) == 0:
            self._dataManager.refresh_data()

        #check it again
        if len(self._dataStore._type_count) == 0:
            return 0 # ---------- NO DATA
#Clone the location groups
        gpz = self._dataStore._type_count.copy()

        #How big should the groups be?
        for grp in gpz:
            size = calcPlaneSizeForGroup(
                    scaleFactor=self._scale, 
                    resourceCount=self._dataStore._type_count.get(grp)
                )
            #mixed plane sizes
            self._dataStore._lcl_sizes.append(size)
            grp = cleanup_prim_path(self, grp)
            self._dataStore._lcl_groups.append({ "group":grp, "size":size })

        #Should the groups all be the same size ?
        if self._symPlanes:
            self._dataStore._lcl_sizes.sort(reverse=True)
            maxPlaneSize = self._dataStore._lcl_sizes[0] #largest plane
            groupCount = len(self._dataStore._lcl_sizes) #count of groups

            #Reset plane sizes
            self._dataStore._lcl_sizes = []
            for count in range(0,groupCount):
                self._dataStore._lcl_sizes.append(maxPlaneSize)               

            self._dataStore._lcl_groups = []
            for grp in gpz:
                self._dataStore._lcl_groups.append({ "group":grp, "size":maxPlaneSize })

    def calulateCosts(self):      

        for g in self._dataStore._lcl_groups:

            #Get the cost by resource group
            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

            try:
                self._cost = str(locale.currency(self._dataStore._type_cost[g]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     

    def selectGroupPrims(self):
        
        self.paths = []

        base = Sdf.Path("/World/Types")

        for grp in self._dataStore.map_group.keys():
            grp_path = base.AppendPath(cleanup_prim_path(self, grp))
            self.paths.append(str(grp_path))

        omni.kit.commands.execute('SelectPrimsCommand',
            old_selected_paths=[],
            new_selected_paths=self.paths,
            expand_in_stage=True)

    #Abstact to load resources
    def loadResources(self):      

        self.view_path = Sdf.Path(self.root_path.AppendPath(self._view_path))

        if (len(self._dataStore._lcl_groups)) >0 :

            #Cycle all the loaded groups
            for grp in self._dataStore._lcl_groups:
                carb.log_info(grp["group"])

                #Cleanup the group name for a prim path
                group_prim_path = self.view_path.AppendPath(grp["group"])

                #match the group to the resource map
                for key, values in self._dataStore._map_type.items():

                    #Is this the group?
                    if key == grp["group"]:

                        self.loadGroupResources(key, group_prim_path, values)

    
    def selectGroupPrims(self):
        
        self.paths = []
        stage = omni.usd.get_context().get_stage()
        base = Sdf.Path("/World/Types")

        curr_prim = stage.GetPrimAtPath(base)

        for prim in Usd.PrimRange(curr_prim):
            # only process shapes and meshes
            tmp_path = str(prim.GetPath())

            if '/CollisionMesh' not in tmp_path:
                if '/CollisionPlane' not in tmp_path:
                    self.paths.append(tmp_path)

        # for grp in self._dataStore._map_subscription.keys():
        #     grp_path = base.AppendPath(cleanup_prim_path(self, grp))
        #     self.paths.append(str(grp_path))

        omni.kit.commands.execute('SelectPrimsCommand',
            old_selected_paths=[],
            new_selected_paths=self.paths,
            expand_in_stage=True)

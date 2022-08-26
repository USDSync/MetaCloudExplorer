
from .group_base import GroupBase
from pxr import Gf, UsdGeom, UsdLux, Usd, Sdf
from .math_utils import calcPlaneSizeForGroup
from .prim_utils import cleanup_prim_path, create_and_place_prim, get_parent_child_prim_path
import locale 

import omni.client
import omni.kit.app
import omni.ui as ui
import omni.usd
import omni.kit.commands



#--- RESOURCE BASED GROUPS
class ResGrpView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str, symPlanes:bool):
        self._root_path = Sdf.Path(viewPath)
        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self._view_path = viewPath
        self._symPlanes = symPlanes

        super().__init__()

    #Determines the sizes of the group planes to create
    def calcGroupPlaneSizes(self):
        
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
            self._dataStore._lcl_sizes.append(
                size
            )
            grp = cleanup_prim_path(self, grp)
            self._dataStore._lcl_groups.append({ "group":grp, "size":size })

    #Abstract method to calc cost 
    def calulateCosts(self):      

        for g in self._dataStore._lcl_groups:
            #Get the cost by resource group
            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
            try:
                self._cost = str(locale.currency(self._dataStore._group_cost[g["group"]]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     

    #Abstact to load resources
    def loadResources(self):      

        self.view_path = Sdf.Path(self.root_path.AppendPath('RGrp'))

        if (len(self._dataStore._lcl_groups)) >0 :

            #Cycle all the loaded groups
            for grp in self._dataStore._lcl_groups:
                print(grp)

                #Cleanup the group name for a prim path
                group_prim_path = self.view_path.AppendPath(grp["group"])

                #match the group to the resource map
                for key, values in self._dataStore._map_group.items():

                    #Is this the group?
                    if key == grp["group"]:

                        self.loadGroupResources(group_prim_path, values)




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
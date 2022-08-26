
from .group_base import GroupBase
from pxr import Gf, UsdGeom, UsdLux, Usd, Sdf
from .math_utils import calcPlaneSizeForGroup
from .prim_utils import cleanup_prim_path
import locale 

class LocGrpView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str, symPlanes:bool):
        self._root_path = Sdf.Path(viewPath)
        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self._view_path = viewPath
        self._symPlanes = symPlanes

        super().__init__()

    def calcGroupPlaneSizes(self):
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
            self._dataStore._lcl_sizes.append(
                size
            )
            grp = cleanup_prim_path(self, grp)
            self._dataStore._lcl_groups.append({ "group":grp, "size":size })

    def calulateCosts(self):      

        for g in self._dataStore._lcl_groups:

            #Get the cost by resource group
            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

            try:
                self._cost = str(locale.currency(self._dataStore._location_cost[g]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     

    #Abstact to load resources
    def loadResources(self):      

        self.view_path = Sdf.Path(self.root_path.AppendPath('Loc'))

        if (len(self._dataStore._lcl_groups)) >0 :

            #Cycle all the loaded groups
            for grp in self._dataStore._lcl_groups:
                print(grp)

                #Cleanup the group name for a prim path
                group_prim_path = self.view_path.AppendPath(grp["group"])

                #match the group to the resource map
                for key, values in self._dataStore._map_location.items():

                    #Is this the group?
                    if key == grp["group"]:

                        self.loadGroupResources(group_prim_path, values)


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


from .group_base import GroupBase
from pxr import Gf, UsdGeom, UsdLux, Usd, Sdf
import locale 

class AADGrpView(GroupBase):
    def __init__(self, viewPath:str, scale:float, upAxis:str, shapeUpAxis:str):
        self.layer_root_path = Sdf.Path(self.root_path.AppendPath('AAD'))
        self._scale = scale
        self._upAxis = upAxis
        self._shapeUpAxis = shapeUpAxis
        self.view_path = viewPath
        super().__init__()

    def calcGroupPlaneSizes(self):
        pass

    def calulateCosts(self):      

        for g in self._dataStore._lcl_groups:
            #Get the cost by resource group
            locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
            try:
                self._cost = str(locale.currency(self._dataStore._aad_cost[g]))
            except:
                self._cost = "" # blank not 0, blank means dont show it at all     

    def prepResources(self):      
        pass # Requires subclass implm

import omni.kit.pipapi

omni.kit.pipapi.install("pandas", module="pandas", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
omni.kit.pipapi.install("numpy", module="numpy", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
import numpy as np
import pandas as pd
from pathlib import Path

#CURRENT_PATH = Path(__file__).parent
#DATA_PATH = CURRENT_PATH.parent.parent.parent.joinpath("data\export")
# Default CSV Path (sample file deployed with extension)
#csv_file_path = DATA_PATH.joinpath(company + '_Groups.csv')

class DataModelFactory:
    def __init__(self, root_path, company):
         self.root_path = root_path
         self.company = company

    @classmethod
    def loaddata(self):  
        TMP_PATH = self.root_path + self.company + '_Groups.csv'
        csv_file_path = TMP_PATH
        self.df_groups = pd.read_csv(csv_file_path, index_col='Name')

    def group_count_by_location(self):
        return(self.df_groups.groupby("Location").agg(
            location_count = ("Location","count")
        ))



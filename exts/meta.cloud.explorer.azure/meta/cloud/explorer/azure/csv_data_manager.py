# Selection UI window for importing CSV files
import carb
from omni.kit.window.file_importer import get_file_importer
import os.path
import asyncio
from pathlib import Path
# external python lib
import csv
import itertools
from .data_store import DataStore
from .prim_utils import cleanup_prim_path
import omni.kit.notification_manager as nm

#This class is designed to import data from 3 input files 
#This file acts like a data provider for the data_manager

class CSVDataManager():
    def __init__(self):
        
        self._dataStore = DataStore.instance() # Get A Singleton instance, store data here
       
        # limit the number of rows read
        self.max_elements = 5000

    #specify the filesnames to load
    def loadFilesManual(self, grpFile:str, resFile:str):   

        self.load_grp_file_manual(grpFile)
        self.load_res_file_manual(resFile)

    #Load all the data from CSV files and process it
    def loadFiles(self):
        
        self.load_grp_file()
        self.load_res_file()

    #Resource Groups File Import
    #NAME,SUBSCRIPTION,LOCATION
    def load_grp_file_manual(self, fileName):
        i=1
        with open(fileName, encoding='utf-8-sig', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                name = row["NAME"]
                subs = row["SUBSCRIPTION"]
                location = row["LOCATION"]

                grp = {name:{"name":name, "subs": subs, "location":location}}
                self._dataStore._groups.update(grp)               
                i=i+1
                if i > self.max_elements: return

            self.sendNotify("MCE: Azure groups loaded: " + str(len(self._dataStore._groups)), nm.NotificationStatus.INFO)     

    #Groups File Import
    def load_grp_file(self):
        if os.path.exists(self._dataStore._rg_csv_file_path):
            self.load_grp_file_manual(self._dataStore._rg_csv_file_path)

    # Read CSV Resources file
    # Expects fields:
    # NAME,TYPE,RESOURCE GROUP,LOCATION,SUBSCRIPTION, LMCOST         
    def load_res_file_manual(self, fileName):
        i=1
        with open(fileName, encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=',')
            for row in reader:
                name = row["NAME"]
                type = row["TYPE"]
                group = row["RESOURCE GROUP"]
                location = row["LOCATION"]
                subscription = row["SUBSCRIPTION"]
                lmcost = row["LMCOST"]

                #fix spacing, control chars early
                name = cleanup_prim_path(self, Name=name)

                self._dataStore._resources[name] = {"name":name, "type": type, "group": group, "location":location, "subscription":subscription, "lmcost": lmcost}

                i=i+1
                if i > self.max_elements: return
            
        self.sendNotify("MCE: Azure resources loaded: " + str(len(self._dataStore._resources)), nm.NotificationStatus.INFO)     

    #Resources File Import
    def load_res_file(self):
         # check that CSV exists
        if os.path.exists(self._dataStore._rs_csv_file_path):
           self.load_res_file_manual(self._dataStore._rs_csv_file_path)

    # Handles the click of the Load button for file selection dialog
    def select_file(self, fileType: str):
        self.file_importer = get_file_importer()

        if fileType == "rg":
            self.file_importer.show_window(
                title="Select a CSV File",
                import_button_label="Select",
                import_handler=self._on_click_rg_open,
                file_extension_types=[(".csv", "CSV Files (*.csv)")],
                file_filter_handler=self._on_filter_item
                )

        if fileType == "res":
            self.file_importer.show_window(
                title="Select a CSV File",
                import_button_label="Select",
                import_handler=self._on_click_res_open,
                file_extension_types=[(".csv", "CSV Files (*.csv)")],
                file_filter_handler=self._on_filter_item
                )                

        if fileType == "bgl":
            self.file_importer.show_window(
                title="Select a png image file",
                import_button_label="Select",
                import_handler=self._on_click_bgl_open,
                file_extension_types=[(".png", "PNG Files (*.png)")],
                file_filter_handler=self._on_filter_item
                )                

        if fileType == "bgm":
            self.file_importer.show_window(
                title="Select a png image file",
                import_button_label="Select",
                import_handler=self._on_click_bgm_open,
                file_extension_types=[(".png", "PNG Files (*.png)")],
                file_filter_handler=self._on_filter_item
                )                

        if fileType == "bgh":
            self.file_importer.show_window(
                title="Select a png image file",
                import_button_label="Select",
                import_handler=self._on_click_bgh_open,
                file_extension_types=[(".png", "PNG Files (*.png)")],
                file_filter_handler=self._on_filter_item
                )                                

    # Handles the click of the open button within the file importer dialog
    def _on_click_rg_open(self, filename: str, dirname: str, selections):
        
        # File name should not be empty.
        filename = filename.strip()
        if not filename:
            carb.log_warn(f"Filename must be provided.")
            return

        # create the full path to csv file
        if dirname:
            fullpath = f"{dirname}/{filename}"
        else:
            fullpath = filename

        self._dataStore._rg_csv_file_path = fullpath      
        self._dataStore._rg_csv_field_model.set_value(str(fullpath))

    # Handles the click of the open button within the file importer dialog
    def _on_click_res_open(self, filename: str, dirname: str, selections):
        
        # File name should not be empty.
        filename = filename.strip()
        if not filename:
            carb.log_warn(f"Filename must be provided.")
            return

        # create the full path to csv file
        if dirname:
            fullpath = f"{dirname}/{filename}"
        else:
            fullpath = filename

        self._dataStore._rs_csv_file_path = fullpath
        self._dataStore._rs_csv_field_model.set_value(str(fullpath))

    # Handles the click of the open button within the file importer dialog
    def _on_click_bgl_open(self, filename: str, dirname: str, selections):
        
        # File name should not be empty.
        filename = filename.strip()
        if not filename:
            carb.log_warn(f"Filename must be provided.")
            return

        # create the full path to csv file
        if dirname:
            fullpath = f"{dirname}/{filename}"
        else:
            fullpath = filename

        self._dataStore._bgl_file_path = fullpath
        self._dataStore._bgl_field_model.set_value(str(fullpath))
        self._dataStore.Save_Config_Data()

    # Handles the click of the open button within the file importer dialog
    def _on_click_bgm_open(self, filename: str, dirname: str, selections):
        
        # File name should not be empty.
        filename = filename.strip()
        if not filename:
            carb.log_warn(f"Filename must be provided.")
            return

        # create the full path to csv file
        if dirname:
            fullpath = f"{dirname}/{filename}"
        else:
            fullpath = filename

        self._dataStore._bgm_file_path = fullpath
        self._dataStore._bgm_field_model.set_value(str(fullpath))
        self._dataStore.Save_Config_Data()

    # Handles the click of the open button within the file importer dialog
    def _on_click_bgh_open(self, filename: str, dirname: str, selections):
        
        # File name should not be empty.
        filename = filename.strip()
        if not filename:
            carb.log_warn(f"Filename must be provided.")
            return

        # create the full path to csv file
        if dirname:
            fullpath = f"{dirname}/{filename}"
        else:
            fullpath = filename

        self._dataStore._bgh_file_path = fullpath
        self._dataStore._bgh_field_model.set_value(str(fullpath))
        self._dataStore.Save_Config_Data()

    # Handles the filtering of files within the file importer dialog
    def _on_filter_item(self, filename: str, filter_postfix: str, filter_ext: str) -> bool:
        if not filename:
            return True
        # Show only .csv files
        _, ext = os.path.splitext(filename)
        if ext == filter_ext:
            return True
        else:
            return False


    def sendNotify(self, message:str, status:nm.NotificationStatus):
        
        # https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.kit.notification_manager/docs/index.html?highlight=omni%20kit%20notification_manager#

        import omni.kit.notification_manager as nm
        ok_button = nm.NotificationButtonInfo("OK", on_complete=self.clicked_ok)

        nm.post_notification(
            message,
            hide_after_timeout=True,
            duration=3,
            status=status,
            button_infos=[],
        )        

        
    def clicked_ok():
        carb.log_info("User clicked ok")

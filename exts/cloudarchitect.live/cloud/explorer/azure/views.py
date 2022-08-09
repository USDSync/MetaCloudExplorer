#  import from omniverse
from omni.ui.workspace_utils import TOP
#  import from other extension py
from .sub_models import SubscriptionModel
from .rg_models import ResourceGroupModel
from .rs_models import ResourceModel
from .combo_box_model import ComboBoxModel
from .style import button_styles

import sys
import webbrowser
#from turtle import width
import omni.ext
import omni.ui as ui
from omni.ui import color as cl
from omni.ui import scene as sc
import os
import omni.kit.commands
import omni.kit.pipapi
from pxr import Sdf, Usd, Gf, UsdGeom
import omni

from pxr import PhysicsSchemaTools
import random

class MainView(ui.Window):
    """The class that represents the window"""

    #___________________________________________________________________________________________________
    # UI Definitions
    #___________________________________________________________________________________________________

    def __init__(self, submodel: SubscriptionModel, rgmodel: ResourceGroupModel, rsmodel: ResourceModel, root_path):

        self._window = ui.Window("Meta Cloud Explorer (Azure)", width=800, height=600, dockPreference=ui.DockPreference.RIGHT_TOP)
        self._window.visible = True
        self._groundPlaneAdded = False
        self._company_model = ComboBoxModel("Company1", "SolidCloud")

        self._usd_context = omni.usd.get_context()
        self.root_path = root_path
        submodel.csv_field_model = None
        
        with self._window.frame:
            with ui.VStack(height=150):
                ui.Label("Meta Cloud Explorer (Azure)", style={"color": 0xFF008976, "font_size":36}, alignment=ui.Alignment.CENTER, height=0)
                ui.Line(style={"color": 0xff00b976}, height=20)

                with ui.HStack(style=button_styles):
                    ui.Button("Load Subscriptions", clicked_fn=lambda: load_subscriptions(self), name="subs", height=15)
                    ui.Button("Load Resource Groups", clicked_fn=lambda: load_resource_groups(self), name="rg", height=15)
                    ui.Button("Load All Resources", clicked_fn=lambda: load_all_resources(self), name="rs", height=15)

                with ui.HStack():
                    ui.Button("Clear Stage", clicked_fn=lambda: clear_stage(), height=15)
                    ui.Button("Add Ground", clicked_fn=lambda: create_ground_plane(), height=15)
                    ui.Button("Create Resources", clicked_fn=lambda: test(), height=15)

                ui.Line(style={"color": 0xff00b976}, height=20)
               
                with ui.HStack():
                    ui.Button("Group By Type", clicked_fn=lambda: on_group(), height=15)
                    ui.Button("Group By Region", clicked_fn=lambda: on_group(), height=15)
                    ui.Button("Group By Group", clicked_fn=lambda: on_group(), height=15)

                with ui.HStack():
                    ui.Button("Network View", clicked_fn=lambda: on_network(), height=15)
                    ui.Button("Resource View", clicked_fn=lambda: on_resource(), height=15)
                    ui.Button("Cost View", clicked_fn=lambda: on_cost(), height=15)

                ui.Line(style={"color": 0xff00b976}, height=20)

                with ui.HStack():
                    ui.Button("Docs", clicked_fn=lambda: on_docs(), height=15)
                    ui.Button("Code", clicked_fn=lambda: on_code(), height=15)
                    ui.Button("Help", clicked_fn=lambda: on_help(), height=15)

                # with ui.CollapsableFrame("Data Files", name="files"):
                #     with ui.VStack():
                #         ui.Label("Subs file path:", height=10, width=120)             
                #         with ui.HStack():
                #             self.sub_field = ui.StringField(height=10)
                #             self.sub_field.enabled = False
                #             self.sub_field.model.set_value(str(submodel.csv_file_path))
                #             submodel.csv_field_model = self.sub_field.model
                #             ui.Button("Load", width=40, clicked_fn=lambda: submodel.select_file())
                        
                #         ui.Label("RG  file path:", height=10, width=120)             
                #         with ui.HStack():
                #             self.rg_field = ui.StringField(height=10)
                #             self.rg_field.enabled = False
                #             self.rg_field.model.set_value(str(rgmodel.csv_file_path))
                #             rgmodel.csv_field_model = self.rg_field.model
                #             ui.Button("Load", width=40,clicked_fn=lambda: rgmodel.select_file())
                
                #         ui.Label("Resources file path:", height=10, width=120)             
                #         with ui.HStack():
                #             self.rs_field = ui.StringField(height=10)
                #             self.rs_field.enabled = False
                #             self.rs_field.model.set_value(str(rsmodel.csv_file_path))
                #             rsmodel.csv_field_model = self.rs_field.model
                #             ui.Button("Load", width=40,clicked_fn=lambda: rsmodel.select_file())
            
                with ui.CollapsableFrame("Connection", name="group"):
                    with ui.VStack():
                        ui.Label("Tenant Id")
                        self._tenant = ui.StringField()
                        ui.Label("Client Id")
                        self._client = ui.StringField()
                        ui.Label("Client Secret")
                        self._secret = ui.StringField()
                        ui.Button("Connect", clicked_fn=lambda: load_account_info(self))

        #___________________________________________________________________________________________________
        # Function Definitions
        #___________________________________________________________________________________________________

                def load_account_info():
                    print("HI")
                
                def on_resource():
                     stage_ref = self._usd_context.get_stage()

                def on_network():
                     stage_ref = self._usd_context.get_stage()

                def on_cost():
                     stage_ref = self._usd_context.get_stage()

                def on_group():
                     stage_ref = self._usd_context.get_stage()

                def create_ground_plane():

                    #if (self._groundPlaneAdded == False):
                    stage_ref = self._usd_context.get_stage() 
                    _create_ground_plane(stage_ref, "Z", location=Gf.Vec3f(0,0,0) )
                    self._groundPlaneAdded = True

                def test():
                    stage_ref = self._usd_context.get_stage() 
                    #draw_rect(stage_ref, "Zone 1", "0.25", position=Gf.Vec3f(0,0,0))

                def load_subscriptions(self):
                    submodel.generate()

                def load_resource_groups(self):
                    rgmodel.generate()                 

                def load_all_resources(self):
                    rsmodel.generate()                 

                #Load From Azure API
                def load_azaure_resources(self):
                    
                    #Get the stage
                    stage = self._usd_context.get_stage()
                    
                    #save the value state
                    #create_ground_plane(stage, "ground", 100, "Z", location=Gf.Vec3f(0,0,0) )

                    # Acquire a credential object
                    #credential = ClientSecretCredential(self._tenant.model.as_string, self._client.model.as_string, self._secret.model.as_string)

                    authority = 'https://login.microsoftonline.com'

                    # Retrieve subscription ID from environment variable.
                    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

                    # Obtain the management object for resources.
                    #resource_client = ResourceManagementClient(credential, subscription_id)

                    #rg_groups = resource_client.resource_groups.list()
                
                    pos=0
                    pos2=0
                    counter=0
                    path ="../Objects/"
                    #for item in rg_groups:
                    for i in range(30):

                        #print(item.name)
                        pos+=50
                        pos2-=50
                        counter+=1
                        path = "/World/rg{}".format(counter)
                        prim = stage.DefinePrim(path, 'Cube')
                        #prim.SetCustomDataByKey("location", item.location)
                        #prim.SetCustomDataByKey("rgname", item.name)
                        #prim.SetCustomDataByKey("id", item.id)
                        #prim.GetReferences().AddReference(r"omniverse://localhost/Projects/test/ControlUnit.usd")

                        # Don't forget to provide the data type on this line. Your example was missing it.
                        #prim.CreateAttribute('size', Sdf.ValueTypeNames.Double).Set(25)

                        xformable = UsdGeom.Xformable(prim)
                        for name in prim.GetPropertyNames():
                            if name == "xformOp:transform":
                                prim.RemoveProperty(name)

                        if "xformOp:translate" in prim.GetPropertyNames():
                            xform_op_tranlsate = UsdGeom.XformOp(prim.GetAttribute("xformOp:translate"))
                        else:
                            xform_op_tranlsate = xformable.AddXformOp(UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.PrecisionDouble, "")
                        xformable.SetXformOpOrder([xform_op_tranlsate])
                        
                        xform_op_tranlsate.Set(Gf.Vec3d([(2 * random.random() - 1) * 200 for _ in range(3)]))

                        # cube_prim = stage.GetPrimAtPath("/World/Cube")
                        # xform = UsdGeom.Xformable(cube_prim)
                        # transform = xform.AddTransformOp()
                        # mat = Gf.Matrix4d()
                        # mat.SetTranslateOnly(Gf.Vec3d(10.0,1.0,1.0))
                        # mat.SetRotateOnly(Gf.Rotation(Gf.Vec3d(0,1,0), 290))
                        # transform.Set(mat)
                        # stage_ref = Usd.Stage.Open(path + 'cube.usda')

                        # # Get a reference to the Xform instance as well as a generic Prim instance
                        # prim = stage_ref.GetPrimAtPath('/Cube-01')

                        # print(prim.GetName()) # Prints "sphere"
                        # print(prim.GetPrimPath()) # Prints "/sphere"

                        # path = "objects"
                        # stage = Usd.Stage.CreateNew(path + 'cube.usd')

                    rgcount = counter

                    # Print out the stage
                    print("The Layer\n\n")
                    print(stage.GetRootLayer().ExportToString())
                    print("\n\nThe result of Composition \n\n")
                    print(stage.Flatten().ExportToString())
                    print("\n\n")


                # Clear the stage
                def clear_stage():
                    stage = omni.usd.get_context().get_stage()
                    root_prim = stage.GetPrimAtPath(self.root_path)
                    if (root_prim.IsValid()):
                        stage.RemovePrim(self.root_path)                    
                    
                    ground_prim = stage.GetPrimAtPath('/GroundPlane')
                    if (ground_prim.IsValid()):
                        stage.RemovePrim('/GroundPlane')                    

                def load_aad_prim(name):
                    stage_ref = self._usd_context.get_stage() 
                    path = "/World/{}".format(name)
                    prim = stage_ref.DefinePrim(path)
                    prim.GetReferences().AddReference("omniverse://localhost/Resources/AzureAAD_1.1.usd")
                    
                    #xform_op_tranlsate = UsdGeom.XformOp(prim.GetAttribute("xformOp:translate"))
                    #xform_op_tranlsate.Set(Gf.Vec3d([(2 * random.random() - 1) * 200 for _ in range(3)]))

                def load_sql_prim(name):
                    stage_ref = self._usd_context.get_stage() 
                    path = "/World/{}".format(name)
                    prim = stage_ref.DefinePrim(path)
                    prim.GetReferences().AddReference("omniverse://localhost/Resources/SQLServer_6.0.usd")
                    
                    #xform_op_tranlsate = UsdGeom.XformOp(prim.GetAttribute("xformOp:translate"))
                    #xform_op_tranlsate.Set(Gf.Vec3d([(2 * random.random() - 1) * 200 for _ in range(3)]))

                def load_app_prim(name):
                    stage_ref = self._usd_context.get_stage() 
                    path = "/World/{}".format(name)
                    prim = stage_ref.DefinePrim(path)
                    prim.GetReferences().AddReference("omniverse://localhost/Resources/AppServices_1.2.usd")
                    

                def load_rg_prim(name):
                    stage_ref = self._usd_context.get_stage() 
                    path = "/World/{}".format(name)
                    prim = stage_ref.DefinePrim(path)
                    prim.GetReferences().AddReference("omniverse://localhost/Resources/ResourceGroups_1.2.usd")

                    #xform_op_tranlsate = UsdGeom.XformOp(prim.GetAttribute("xformOp:translate"))
                    #xform_op_tranlsate.Set(Gf.Vec3d([(2 * random.random() - 1) * 200 for _ in range(3)]))

                def load_stg_prim(name):
                    stage_ref = self._usd_context.get_stage() 
                    path = "/World/{}".format(name)
                    prim = stage_ref.DefinePrim(path)
                    prim.GetReferences().AddReference("omniverse://localhost/Resources/StorageAccounts_2.8.usd")

                def load_sub_prim(name):
                    stage_ref = self._usd_context.get_stage() 
                    path = "/World/{}".format(name)
                    prim = stage_ref.DefinePrim(path)
                    prim.GetReferences().AddReference("omniverse://localhost/Resources/Subscriptions_1.3.usd")



                #Create the Ground
                def _create_ground_plane(
                    stage,
                    up_direction="Z",
                    location=Gf.Vec3f(0,0,0),
                    unknown=Gf.Vec3f(1.0),
                    visible=True,
                ):
                    omni.kit.commands.execute('AddGroundPlaneCommand',
                    stage=stage,
                    planePath='/GroundPlane',
                    axis='Z',
                    size=2500.0,
                    position=Gf.Vec3f(0.0, 0.0, 0.0),
                    color=Gf.Vec3f(0.5, 0.5, 0.5))



    def destroy(self):
        self._window.destroy()
        self._window = None

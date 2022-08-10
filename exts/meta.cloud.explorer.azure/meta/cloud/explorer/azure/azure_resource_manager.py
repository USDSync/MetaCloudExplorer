#todo

                # #Load From Azure API
                # def load_azaure_resources(self):
                    
                #     #Get the stage
                #     stage = self._usd_context.get_stage()
                    
                #     #save the value state
                #     #create_ground_plane(stage, "ground", 100, "Z", location=Gf.Vec3f(0,0,0) )

                #     # Acquire a credential object
                #     #credential = ClientSecretCredential(self._tenant.model.as_string, self._client.model.as_string, self._secret.model.as_string)

                #     authority = 'https://login.microsoftonline.com'

                #     # Retrieve subscription ID from environment variable.
                #     subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

                #     # Obtain the management object for resources.
                #     #resource_client = ResourceManagementClient(credential, subscription_id)

                #     #rg_groups = resource_client.resource_groups.list()
                
                #     pos=0
                #     pos2=0
                #     counter=0
                #     path ="../Objects/"
                #     #for item in rg_groups:
                #     for i in range(30):

                #         #print(item.name)
                #         pos+=50
                #         pos2-=50
                #         counter+=1
                #         path = "/World/rg{}".format(counter)
                #         prim = stage.DefinePrim(path, 'Cube')
                #         #prim.SetCustomDataByKey("location", item.location)
                #         #prim.SetCustomDataByKey("rgname", item.name)
                #         #prim.SetCustomDataByKey("id", item.id)
                #         #prim.GetReferences().AddReference(r"omniverse://localhost/Projects/test/ControlUnit.usd")

                #         # Don't forget to provide the data type on this line. Your example was missing it.
                #         #prim.CreateAttribute('size', Sdf.ValueTypeNames.Double).Set(25)

                #         xformable = UsdGeom.Xformable(prim)
                #         for name in prim.GetPropertyNames():
                #             if name == "xformOp:transform":
                #                 prim.RemoveProperty(name)

                #         if "xformOp:translate" in prim.GetPropertyNames():
                #             xform_op_tranlsate = UsdGeom.XformOp(prim.GetAttribute("xformOp:translate"))
                #         else:
                #             xform_op_tranlsate = xformable.AddXformOp(UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.PrecisionDouble, "")
                #         xformable.SetXformOpOrder([xform_op_tranlsate])
                        
                #         xform_op_tranlsate.Set(Gf.Vec3d([(2 * random.random() - 1) * 200 for _ in range(3)]))

                #     #get the total count    
                #     rgcount = counter

                #     # Print out the stage
                #     print("The Layer\n\n")
                #     print(stage.GetRootLayer().ExportToString())
                #     print("\n\nThe result of Composition \n\n")
                #     print(stage.Flatten().ExportToString())
                #     print("\n\n")


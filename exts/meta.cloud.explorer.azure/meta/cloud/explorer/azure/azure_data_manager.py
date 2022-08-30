import omni.kit.pipapi
import carb
import os
import json
import sys
from datetime import datetime
import omni.kit.notification_manager as nm

omni.kit.pipapi.install("azure-identity", module="azure-identity", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
omni.kit.pipapi.install("azure-mgmt-resource", module="azure-mgmt-resource", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )

sys.path.append("D:/python37/lib/site-packages")
#print(sys.modules.keys())

from .data_store import DataStore
from .prim_utils import cleanup_prim_path
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import ClientSecretCredential
import os

# Manage resources and resource groups - create, update and delete a resource group,
# deploy a solution into a resource group, export an ARM template. Create, read, update
# and delete a resource

class AzureDataManager():
    def __init__(self):
        
        self._dataStore = DataStore.instance() # Get A Singleton instance, store data here

    def get_token(self):
         # Acquire a credential object using CLI-based authentication.
        self._dataStore._azure_tenant_id="64b3cefb-e38e-4fe8-8356-de6129c50262"
        self._dataStore._azure_client_id = "970ebf4e-232e-428a-9a33-6e42d2a70ebb"
        self._dataStore._azure_client_secret="DUU8Q~5YcqMepVdLBzvCaIKU2bqQH31AmQFMxbI3"
        self._dataStore._azure_subscription_id="9af72be6-0c53-464c-aa30-0834b42c0d94"

        self._token_credential = ClientSecretCredential(
            self._dataStore._azure_tenant_id, 
            self._dataStore._azure_client_id, 
            self._dataStore._azure_client_secret)

        # Retrieve subscription ID from environment variable.
        self._subscription_id = self._dataStore._azure_subscription_id

    #validate we can connect
    def connect(self):
        self.sendNotify("Connecting to Azure Tenant...", nm.NotificationStatus.INFO)     
        
        #Get a token
        self.get_token()

        
    def clicked_ok():
        carb.log_info("User clicked ok")

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

    #Connect to API and load adata
    def load_data(self):
        self.save_connection_data()
        self.load_groups()
        self.load_resources()


    def save_connection_data(self):
        pass
    
    def load_resources(self):    
        try:
            resCnt = 0
            for grp in self._dataStore._groups:
                resources = self.list_group_resources(grp)
                for res in resources:
                    resCnt = resCnt +1
                    name = cleanup_prim_path(self, Name=res.name)
                    self._dataStore._resources[name] = {"name":name, "type": res.type, "group": grp, "location":res.location, "subscription":self._subscription_id, "lmcost": 0}
        
                    #self._dataStore.res["name"] = {"name":res["name"], "type": type, "group": group, "location":location, "subscription":subscription, "lmcost": lmcost}
            carb.log_info("Azure API resources loaded: " + str(resCnt))                    
        except:
            error = sys.exc_info()[0]
            carb.log_error("Oops! " + str(error) + " occurred.")
            self.sendNotify("Error:" + str(error), nm.NotificationStatus.WARNING)                   


    def load_groups(self):
        try:
            grps = self.get_resource_groups()

            grpCnt = 0
            for group in grps:            
                grp = {group.name:{"name":group.name, "subs": self._subscription_id, "location":group.location}}
                self._dataStore._groups.update(grp)     
                grpCnt = grpCnt + 1
        
            carb.log_info("Azure API groups loaded: " + str(grpCnt))

        except:
            error = sys.exc_info()[0]
            carb.log_error("Oops! " + str(error) + " occurred.")
            self.sendNotify("Error:" + str(error), nm.NotificationStatus.WARNING)           


        
    
    #return a list of resource groups
    def get_resource_groups(self):

        # Obtain the management object for resources.
        try:
            resource_client = ResourceManagementClient(self._token_credential, self._subscription_id)
            rg_groups = resource_client.resource_groups.list()
            return rg_groups
        except:
            error = sys.exc_info()[0]
            carb.log_error("Oops! " + str(error) + " occurred.")
            self.sendNotify("Error:" + str(error), nm.NotificationStatus.WARNING)           

        #for item in rg_groups:
        #    print(item)


    # List Resources within the group
    def list_group_resources(self, groupName:str):
        
        # Obtain the management object for resources.
        resource_client = ResourceManagementClient(self._token_credential, self._subscription_id)

        carb.log_info("List all of the resources within the group")
        res = resource_client.resources.list_by_resource_group(groupName)
        return res


    #creates a resource group with groupName at location
    def create_resource_group(self, groupName:str, location:str):

        # Obtain the management object for resources.
        resource_client = ResourceManagementClient(self._token_credential, self._subscription_id)
        #
        # Managing resource groups
        #
        resource_group_params = {"location": location}

        # Create Resource group
        print("Create Resource Group: " + groupName + " @ " + location)
        self.print_item(
            resource_client.resource_groups.create_or_update(
                groupName, resource_group_params)
        )


    def print_item(self, group):
        """Print a ResourceGroup instance."""
        print("\tName: {}".format(group.name))
        print("\tId: {}".format(group.id))
        print("\tLocation: {}".format(group.location))
        print("\tTags: {}".format(group.tags))
        self.print_properties(group.properties)


    def print_properties(self, props):
        """Print a ResourceGroup properties instance."""
        if props and props.provisioning_state:
            print("\tProperties:")
            print("\t\tProvisioning State: {}".format(props.provisioning_state))
        print("\n\n")


    # Create a Key Vault in the Resource Group
    def create_key_vault(self, vaultName:str, location:str, groupName:str):

        # Obtain the management object for resources.
        resource_client = ResourceManagementClient(self._token_credential, self._subscription_id)

        print("Create a Key Vault via a Generic Resource Put")
        key_vault_params = {
            "location": location,
            "properties": {
                "sku": {"family": "A", "name": "standard"},
                "tenantId": self._dataStore._azure_tenant_id,
                "accessPolicies": [],
                "enabledForDeployment": True,
                "enabledForTemplateDeployment": True,
                "enabledForDiskEncryption": True
            },
        }
        resource_client.resources.begin_create_or_update(
            resource_group_name=groupName,
            resource_provider_namespace="Microsoft.KeyVault",
            parent_resource_path="",
            resource_type="vaults",
            # Suffix random string to make vault name unique
            resource_name=vaultName + datetime.utcnow().strftime("-%H%M%S"),
            api_version="2019-09-01",
            parameters=key_vault_params
        ).result()        

    # Export the Resource group template
    def export_group_template(self, groupName:str):


        # Obtain the management object for resources.
        resource_client = ResourceManagementClient(self._token_credential, self._subscription_id)
         
        print("Export Resource Group Template")
        BODY = {
        'resources': ['*']
        }
        
        result = json.dumps(
                resource_client.resource_groups.begin_export_template(
                    groupName, BODY).result().template, indent=4
            )
    
        print(result + "\n\n")
        return result


    # def run_example():
    #     """Resource Group management example."""
    #     #
    #     # Create the Resource Manager Client with an Application (service principal) token provider
    #     #
    #     subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", None) # your Azure Subscription Id

    #     credentials = DefaultAzureCredential()

    #     client = ResourceManagementClient(credentials, subscription_id)

    #     #
    #     # Managing resource groups
    #     #
    #     resource_group_params = {"location": "westus"}

    #     # List Resource Groups
    #     print("List Resource Groups")
    #     for item in client.resource_groups.list():
    #         print_item(item)

    #     # Create Resource group
    #     print("Create Resource Group")
    #     print_item(
    #         client.resource_groups.create_or_update(
    #             GROUP_NAME, resource_group_params)
    #     )

    #     # Modify the Resource group
    #     print("Modify Resource Group")
    #     resource_group_params.update(tags={"hello": "world"})
    #     print_item(
    #         client.resource_groups.update(
    #             GROUP_NAME, resource_group_params)
    #     )

    #     # Create a Key Vault in the Resource Group
    #     print("Create a Key Vault via a Generic Resource Put")
    #     key_vault_params = {
    #         "location": "westus",
    #         "properties": {
    #             "sku": {"family": "A", "name": "standard"},
    #             "tenantId": os.environ["AZURE_TENANT_ID"],
    #             "accessPolicies": [],
    #             "enabledForDeployment": True,
    #             "enabledForTemplateDeployment": True,
    #             "enabledForDiskEncryption": True
    #         },
    #     }
    #     client.resources.begin_create_or_update(
    #         resource_group_name=GROUP_NAME,
    #         resource_provider_namespace="Microsoft.KeyVault",
    #         parent_resource_path="",
    #         resource_type="vaults",
    #         # Suffix random string to make vault name unique
    #         resource_name="azureSampleVault" + datetime.utcnow().strftime("-%H%M%S"),
    #         api_version="2019-09-01",
    #         parameters=key_vault_params
    #     ).result()

    #     # List Resources within the group
    #     print("List all of the resources within the group")
    #     for item in client.resources.list_by_resource_group(GROUP_NAME):
    #         print_item(item)

    #     # Export the Resource group template
    #     print("Export Resource Group Template")
    #     BODY = {
    #     'resources': ['*']
    #     }
    #     print(
    #         json.dumps(
    #             client.resource_groups.begin_export_template(
    #                 GROUP_NAME, BODY).result().template, indent=4
    #         )
    #     )
    #     print("\n\n")

    #     # Delete Resource group and everything in it
    #     print("Delete Resource Group")
    #     delete_async_operation = client.resource_groups.begin_delete(GROUP_NAME)
    #     delete_async_operation.wait()
    #     print("\nDeleted: {}".format(GROUP_NAME))

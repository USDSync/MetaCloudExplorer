import omni.kit.pipapi
import os
import json
from datetime import datetime

omni.kit.pipapi.install("azure-identity", module="azure-identity", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )
omni.kit.pipapi.install("azure-mgmt-resource", module="azure-mgmt-resource", ignore_import_check=True, ignore_cache=True, surpress_output=False,use_online_index=True )

from azure.mgmt.resource import ResourceManagementClient
from azure.identity import AzureCliCredential
from azure.mgmt import resource, subscription

WEST_US = "westus"
GROUP_NAME = "meta-cloud-explorer-test"

# Manage resources and resource groups - create, update and delete a resource group,
# deploy a solution into a resource group, export an ARM template. Create, read, update
# and delete a resource
#
# This script expects that the following environment vars are set:
#
# AZURE_TENANT_ID: with your Azure Active Directory tenant id or domain
# AZURE_CLIENT_ID: with your Azure Active Directory Application Client ID
# AZURE_CLIENT_SECRET: with your Azure Active Directory Application Secret
# AZURE_SUBSCRIPTION_ID: with your Azure Subscription Id
#

def get_tenants(sub_client):
    tenants = sub_client.tenants
    print('api_version: ' + tenants.api_version)
    for tenant in tenants.list():
        print(tenant.__dict__.keys())


def run_example():
    """Resource Group management example."""
    #
    # Create the Resource Manager Client with an Application (service principal) token provider
    #
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", None) # your Azure Subscription Id

    credentials = DefaultAzureCredential()

    client = ResourceManagementClient(credentials, subscription_id)

    #
    # Managing resource groups
    #
    resource_group_params = {"location": "westus"}

    # List Resource Groups
    print("List Resource Groups")
    for item in client.resource_groups.list():
        print_item(item)

    # Create Resource group
    print("Create Resource Group")
    print_item(
        client.resource_groups.create_or_update(
            GROUP_NAME, resource_group_params)
    )

    # Modify the Resource group
    print("Modify Resource Group")
    resource_group_params.update(tags={"hello": "world"})
    print_item(
        client.resource_groups.update(
            GROUP_NAME, resource_group_params)
    )

    # Create a Key Vault in the Resource Group
    print("Create a Key Vault via a Generic Resource Put")
    key_vault_params = {
        "location": "westus",
        "properties": {
            "sku": {"family": "A", "name": "standard"},
            "tenantId": os.environ["AZURE_TENANT_ID"],
            "accessPolicies": [],
            "enabledForDeployment": True,
            "enabledForTemplateDeployment": True,
            "enabledForDiskEncryption": True
        },
    }
    client.resources.begin_create_or_update(
        resource_group_name=GROUP_NAME,
        resource_provider_namespace="Microsoft.KeyVault",
        parent_resource_path="",
        resource_type="vaults",
        # Suffix random string to make vault name unique
        resource_name="azureSampleVault" + datetime.utcnow().strftime("-%H%M%S"),
        api_version="2019-09-01",
        parameters=key_vault_params
    ).result()

    # List Resources within the group
    print("List all of the resources within the group")
    for item in client.resources.list_by_resource_group(GROUP_NAME):
        print_item(item)

    # Export the Resource group template
    print("Export Resource Group Template")
    BODY = {
      'resources': ['*']
    }
    print(
        json.dumps(
            client.resource_groups.begin_export_template(
                GROUP_NAME, BODY).result().template, indent=4
        )
    )
    print("\n\n")

    # Delete Resource group and everything in it
    print("Delete Resource Group")
    delete_async_operation = client.resource_groups.begin_delete(GROUP_NAME)
    delete_async_operation.wait()
    print("\nDeleted: {}".format(GROUP_NAME))


def print_item(group):
    """Print a ResourceGroup instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    print("\tLocation: {}".format(group.location))
    print("\tTags: {}".format(group.tags))
    print_properties(group.properties)


def print_properties(props):
    """Print a ResourceGroup properties instance."""
    if props and props.provisioning_state:
        print("\tProperties:")
        print("\t\tProvisioning State: {}".format(props.provisioning_state))
    print("\n\n")


if __name__ == "__main__":
    run_example()
# Cloud Explorer (Azure edition)
# NVIDIA Onmiverse Extension, A Scene Authoring Tool

CloudArchitect.live
(In Alpha Development phase)

Quickly connect to your Azure Cloud Infrastructure and visualize it in the Omniverse!
This extension generates digital models of your Azure Cloud Infrastructure that can be used to gain insights to drive better infrastructure, optimized resources, reduced costs, and breakthrough customer experiences.

# Enable the extension

Look for "cloud.explorer.azure" extension in extension manager and enable it. 

Alternatively, you can launch your app from console with this folder added to search path and your extension enabled, e.g.:

> app\omni.code.bat --ext-folder exts --enable cloud.explorer.azure

# Azure API App Link Setup

This extension lets you easily load and explore a representation of your Cloud Infrastructure as a Digital Twin in the Omniverse. This extension can connect to the Azure Resource Manager API to access your Azure Infrastructure. A read-only account can be utilized to ensure infrastructure security.  * Write-options are also avaialable, see Template View.

Steps to Connect:
1. Create an Azure AAD Application to act as a Service principal to read your Azure resources.
2. Create a Client secret for your new AAD App.
3. Give the AAD app the Global Reader Role in AAD.
4. Add the Application as a Reader Role in each of the subscriptions you want to model.
5. Enter the Tenant ID, Client Id and Client Secret into the extension connection.
6. Connect and Explore your Cloud Infrastructure in the Omniverse!

# Azure 3D Objects

The Azure 3D Icon set is a derivative work, created by several artists to help bring the needed visual context into the Meta Cloud Explorer.  The application code includes an Object Resource Map that maps Azure Objects to their corresponding 3D objects.  By default these can use Cubes or other primitive shapes.  see: cloudarchitect.live/cloud/explorer/azure/resource_map.py  

* The icon set is not yet publicly available pending permission copyright from Microsoft.


# Disconnected mode

Due to some technical issues with the Azure / Python / OmniVerse Create API integration, you can manually export data from your Azure Cloud and use these data files as the data source instead.  Detailed metadata information on resources is limited in this mode, but it has enough data to view the Subscriptions, Resource Groups and Resources.

1. Export a list of Resource Groups
2. Export a list of All Azure Resources
3. Aggregate the data into high level groupings (acdt.exe utility)
4. Select the 3 output files as input for the extension
5. Explore your Azure Infrastructure in the Omniverse!

API working in Code 2021.1.1

API NOT WORKING in Code 2021.1.2 and 2021.1.3

# Welcome to The Future of Cloud Architecture!

You can also create resources in Azure from the OmniVerse!  
This extension gives you the ability to create and model your environment and then create it in your Azure Cloud!

Review Templates, Architectures, Design Patterns and create them in your real cloud from the Onmiverse environment.  

This feature is an alpha and not ready for general use.
Load the Template view to check it out!

The roadmap is long, but full of amazing potential!


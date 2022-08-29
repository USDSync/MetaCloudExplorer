# Meta Cloud Explorer (MCE)
# NVIDIA Onmiverse Extension, a Scene Authoring Tool

CloudArchitect.live
(In Alpha Development phase)

![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/azurescaled.png)
![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/resourcegroups.png)
![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/westus.png)

Quickly connect to your Cloud Infrastructure and visualize it in the Omniverse!*

This extension generates digital models of your Cloud Infrastructure that can be used to gain insights to drive better infrastructure, optimized resources, reduced costs, and breakthrough customer experiences.

![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/aws-azure-gcp.png)

**Only works with Microsoft Azure Cloud currently*
AWS, GCP planned on roadmap.

# Enable the extension

Pull this repo to your local machine, add the path to the extension to your Extensions Search Path in Omniverse Code:  <local folder>/metacloudexplorer/exts

Look for "meta.cloud.explorer.azure" extension in extension manager and enable it. 

Alternatively, you can launch your app from console with this folder added to search path and your extension enabled, e.g.:

> app\omni.code.bat --ext-folder exts --enable cloud.explorer.azure

# Azure API App Link Setup
![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/mce_ui.png)

This extension lets you easily load and explore a representation of your Cloud Infrastructure in the Omniverse. This extension can connect to the Azure Resource Manager API to access your Azure Infrastructure. A read-only account can be utilized to ensure infrastructure security.  See the wiki page for more info on creating an account.

Steps to Connect:
1. Create an Azure AAD Application to act as a Service principal to read your Azure resources.
2. Create a Client secret for your new AAD App.
3. Give the AAD app the Global Reader Role in AAD.
4. Add the Application as a Reader Role in each of the subscriptions you want to model.
5. Enter the Tenant ID, Client Id and Client Secret into the extension connection.
6. Connect and Explore your Cloud Infrastructure in the Omniverse!

# Azure 3D Objects

The Azure 3D Icon set is a derivative work, created by several artists to help bring the needed visual context into the Meta Cloud Explorer.  The application code includes an Object Resource Map that maps Azure Objects to their corresponding 3D object assets.  By default these can use Cubes or other primitive shapes.  see: cloudarchitect.live/cloud/explorer/azure/resource_map.py

**The icon set is not yet publicly available pending copyright permission from Microsoft.*

# Disconnected mode

Due to some technical issues with the Azure / Python / OmniVerse Create API integration, you can manually export data from your Azure Cloud and use these data files as the data source instead.  Detailed metadata information on resources is limited in this mode, but it has enough data to view the Subscriptions, Resource Groups and Resources.

1. Export a list of Resource Groups
2. Export a list of All Azure Resources
3. Aggregate the data into high level groupings
4. Select the Resource Group and Resources CSV files as input for the extension
5. Explore your Azure Infrastructure in the Omniverse!

API working in Code 2021.1.1

API NOT WORKING in Code 2021.1.2 and 2021.1.3!

# Welcome to The Future!

Not quite the future yet, but this is the beginning of a new way to gain insight to your cloud infrastructure.

You can also create resources in Azure from the OmniVerse! 
This extension gives you the ability to create and model your environment in a metaverse and then create it in your Azure Cloud!

Review Templates, Architectures, Design Patterns and then create them for real in your cloud directly from the Onmiverse environment.  

This feature is an alpha and not ready for general use.
Load the Template view to check it out!

The roadmap is long, but full of amazing potential!

# Development Roadmap

Azure - In development
AWS - future
GCP - future
Others...
Terraform, bicep integration

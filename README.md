# Meta Cloud Explorer (MCE)
# NVIDIA Onmiverse Extension, a Scene Authoring Tool

MetaCloudExplorer.com
(In Alpha Development phase)

The true power of the Metaverse is to gain new insights to existing problems by experiencing things in a different way.  A simple change in perspective can sometimes work wonders!  Meta Cloud Explorer help Cloud Architects visualize thier cloud infrastructure at scale.  A Dynamic metaverse creation tool for Nvidia's Omniverse.

Quickly connect to your Cloud Infrastructure and visualize it in your private Omniverse!*
This extension generates digital models of your Cloud Infrastructure that can be used to gain insights to drive better infrastructure, optimized resources, reduced costs, and breakthrough customer experiences.

![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/azurescaled.png)
**Gain Insight by seeing your infrastructure at scale:**
![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/resourcegroups.png)
**View resources by Location, Group, Type, Subscription**
![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/westus.png)
**Optional costs data integrated to groups**
![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/costs.png)

**Can support multiple clouds!**

![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/aws-azure-gcp.png)

**Only works with Microsoft Azure Cloud currently*
AWS, GCP planned on roadmap.

# Azure 3D Objects

The Azure 3D Icon set is a derivative work, created by several artists to help bring the needed visual context into the Meta Cloud Explorer.  The application code includes an Object Resource Map that maps Azure Objects to their corresponding 3D object assets.  By default these can use Cubes or other primitive shapes.  see: exts/meta.cloud.explorer.azure/meta/cloud/explorer/azure/azure_resource_map.py

**The icon set is available here, it is pending copyright permission from Microsoft.**
https://drive.google.com/file/d/1IPVqOR5HsXn8A-dcJYMUl78mKHhnXqbQ/view?usp=sharing

Extract and upload to your local omniverse://localhost/MCE/

# Enable the extension
Pull this repo to your local machine, add the path to the extension to your Extensions Search Path in Omniverse Code:  <local folder>/metacloudexplorer/exts

Look for "meta.cloud.explorer.azure" extension in extension manager and enable it. 

# Azure API App Link Setup
![Meta Cloud Explorer](https://github.com/CloudArchitectLive/MetaCloudExplorer/blob/main/exts/meta.cloud.explorer.azure/data/resources/mce_ui.png)

This extension lets you easily load and explore a representation of your Cloud Infrastructure in the Omniverse. This extension can connect to the Azure Resource Manager API to access your Azure Infrastructure. A read-only account can be utilized to ensure infrastructure security.  See the wiki page for detailed steps on creating an application to access your Azure environment.

Steps to Connect:
1. Create an Azure AAD Application to act as a Service principal to read your Azure resources.
2. Create a Client secret for your new AAD App.
3. Give the AAD app the Global Reader Role in AAD.
4. Add the Application a Reader Role in IAM for each of the subscriptions you want to model.
5. Enter the Tenant ID, Client Id, Subscription and Client Secret into the extension connection.*
6. Connect and Explore your Cloud Infrastructure in the Omniverse!

* Your Client Secret is NOT SAVED.  You will need to re-enter your secret each time you restart Omniverse.
  
# Disconnected mode

You don't have to let MCE connect directly to your Azure Account.  Although we only use a read-only account for security, you can also export 2 data files from your Azure account and load them into MCE for modeling.  This allows you to work in "Disconnected mode"

1. Export a list of Resource Groups (CSV) Include fields: NAME,SUBSCRIPTION,LOCATION
2. Export a list of All Azure Resources (CSV) Include fields: #NAME,TYPE,RESOURCE GROUP,LOCATION,SUBSCRIPTION, LMCOST*
3. Aggregate the data into high level groupings
4. Select the Resource Group and Resources CSV files as input for the extension
5. Explore your Azure Infrastructure in the Omniverse!

*Cost values need to be added manually in the current version.

Extension working in Omniverse Code 2021.1.1!

EXTENSION NOT WORKING in Code 2021.1.2 and 2021.1.3! ;(

# Welcome to The Future of Cloud Insights!

Not quite the future yet, but this is the beginning of a new way to gain insight to your cloud infrastructure.  What insight will you gain from seeing all your resources in this context?  What are you hoping to see?  Whatever MCE generates is just that start of a stage where you can add animation, events, etc.

You can also create resources in Azure from the OmniVerse! This extension gives you the ability to create and model your environment in a metaverse and then create it in your Azure Cloud!

Review Templates, Architectures, Cloud Design Patterns and then create them for real in your cloud directly from the Onmiverse environment.  

This feature is an alpha and not ready for general use.
Load the Template view to check it out!

The roadmap is long, but full of amazing potential!

# Development Roadmap

Azure - In development
AWS - future
GCP - future
Others...
Terraform, bicep integration

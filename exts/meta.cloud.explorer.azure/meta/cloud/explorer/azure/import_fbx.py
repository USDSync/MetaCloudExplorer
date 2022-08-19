import carb
import omni
import asyncio


async def convert_asset_to_usd(input_obj: str, output_usd: str):
    import omni.kit.asset_converter

    def progress_callback(progress, total_steps):
        pass

    converter_context = omni.kit.asset_converter.AssetConverterContext()
    # setup converter and flags
    # converter_context.ignore_material = False
    # converter_context.ignore_animation = False
    # converter_context.ignore_cameras = True
    # converter_context.single_mesh = True
    # converter_context.smooth_normals = True
    # converter_context.preview_surface = False
    # converter_context.support_point_instancer = False
    # converter_context.embed_mdl_in_usd = False
    # converter_context.use_meter_as_world_unit = True
    # converter_context.create_world_as_default_root_prim = False
    instance = omni.kit.asset_converter.get_instance()
    task = instance.create_converter_task(input_obj, output_usd, progress_callback, converter_context)
    success = await task.wait_until_finished()
    if not success:
        carb.log_error(task.get_status(), task.get_detailed_error())
    print("converting done")



if __name__ == "__main__":

    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/API-management-services.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/API-management-services.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/app-service-plan.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/app-service-plan.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/application-insights.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/application-insights.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/automation-accounts.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/automation-accounts.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/azure-data-explorer-clusters.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/azure-data-explorer-cluster"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/azure-devops.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/azure-devops.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/azure-workbook.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/azure-workbook.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/container-registries.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/container-registries.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/data-factory.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/data-factory.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/data-lake-storage-gen1.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/data-lake-storage-gen1.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/event-grid-topics.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/event-grid-topics.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/events-hub.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/events-hub.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/function-apps.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/function-apps.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/image.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/image.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/kubernetess-services.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/kubernetess-services.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/load-balancer.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/load-balancer.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/logic-apps.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/logic-apps.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/network-interface.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/network-interface.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/network-security-groups.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/network-security-groups.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/network-watcher.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/network-watcher.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/public-ip-adresses.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/public-ip-adresses.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/recovery-service-vault.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/recovery-service-vault.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/search-services.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/search-services.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/service-bus.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/service-bus.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/service-fabric-clusters.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/service-fabric-clusters.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/solution.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/solution.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/sql-virtual-machine.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/sql-virtual-machine.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/traffic-manager-profiles.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/converted_fbx/traffic-manager-profiles.usd"))


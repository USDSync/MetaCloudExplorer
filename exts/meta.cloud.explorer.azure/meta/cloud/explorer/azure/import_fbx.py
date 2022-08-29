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
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/API_management_services_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/API_management_services_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/app-service-plan.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/app-service-plan.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/application-insights.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/application-insights.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/application_insights_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/application_insights_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/app_service_plan_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/app_service_plan_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/automation_accounts_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/automation_accounts_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/azure_data_explorer_clusters_fix.fbx","	C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/azure_data_explorer_clusters_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/azure_devops_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/azure_devops_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/azure_workbook_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/azure_workbook_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/container_registries_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/container_registries_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/data_factory_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/data_factory_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/data_lake_storage_gen1_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/data_lake_storage_gen1_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/events_hub_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/events_hub_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/event_grid_topics_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/event_grid_topics_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/files.txt","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/files.txt"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/function_apps_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/function_apps_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/image_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/image_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/kubernetess_services_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/kubernetess_services_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/load_balancer_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/load_balancer_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/Logic_apps_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/Logic_apps_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/network-security-groups.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/network-security-groups.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/network_interface_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/network_interface_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/network_security_group_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/network_security_group_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/network_watcher_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/network_watcher_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/public_ip_adresses_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/public_ip_adresses_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/quick_start_wireframed.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/quick_start_wireframed.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/recovery_service_vault_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/recovery_service_vault_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/search_services_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/search_services_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/service-fabric-clusters_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/service-fabric-clusters_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/service_bus_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/service_bus_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/solution.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/solution.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/sql_virtual_machine_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/sql_virtual_machine_fix.usd"))
    asyncio.ensure_future(convert_asset_to_usd("C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/FBX files/traffic_manager_profiles_fix.fbx","C:/Users/Gavin/Documents/AzureVerse/Assets/RawFromArtists/Converted/traffic_manager_profiles_fix.usd"))

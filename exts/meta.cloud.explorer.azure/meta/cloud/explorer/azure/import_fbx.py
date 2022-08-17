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


asyncio.ensure_future(
    convert_asset_to_usd(
        "</path/to/mesh.obj>",
        "</path/to/mesh.usd>",
    )
)
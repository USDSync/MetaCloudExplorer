import omni.ext
from omni.services.core import main

def ping():
    return "pong"

class SimpleMicroserviceExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("SimpleMicroserviceExtension start")
        main.register_endpoint("get", "/ping", ping, tags=["Simple Service"])
        print("Hello World")

    def on_shutdown(self):
        print("SimpleMicroserviceExtension start")
        main.deregister_endpoint("get", "/ping")
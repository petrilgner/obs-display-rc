import time
import NDIlib as ndi
from typing import Optional

ndi_find = None
scenes_callbacks = {}
default_scene_callback: Optional[callable] = None

last_switched_scene = None
auto_switch = True


def register_scene(scene: str, switch_fn: callable, default: bool = False, ndi_name: str = None):
    global scenes_callbacks, default_scene_callback
    print("Registering scene {}, NDI name {}".format(scene, ndi_name))
    if ndi_name:
        scenes_callbacks[ndi_name] = switch_fn
    if default:
        default_scene_callback = switch_fn


def init_ndi_discover():
    global ndi_find

    if not ndi.initialize():
        return False

    ndi_find = ndi.find_create_v2()
    if ndi_find:
        return False


def discover_ndi():
    while True:
        if not ndi.find_wait_for_sources(ndi_find, 5000):
            print('No change to the sources found.')

        sources = ndi.find_get_current_sources(ndi_find)
        sources_names = []
        for s in sources:
            print('[NDI-DISCOVER] Source: {}'.format(s.ndi_name))
            sources_names.append(s.ndi_name)

        if auto_switch:
            perform_auto_switch(sources_names)

        time.sleep(10)


def perform_auto_switch(found_sources: list):
    global last_switched_scene, default_scene_callback, scenes_callbacks

    for name, callback in scenes_callbacks.items():
        if name in found_sources:
            if last_switched_scene != name:
                print('[NDI] Switching to not active source {}'.format(name))
                try:
                    scenes_callbacks[name]()
                    last_switched_scene = name
                except Exception:
                    print('[NDI] Error switching to scene for source {}'.format(name))
            else:
                print('[NDI] Source {} already active'.format(name))
            return

    # no scene found
    if default_scene_callback and last_switched_scene is not None:
        print('[NDI] Switching to default scene!')
        last_switched_scene = None
        default_scene_callback()

import obsws_python as obs
import obsws_python.error as obs_error
import yaml

last_switched = None
scenes = {}
ws_config = {}


def load_config():
    global scenes, ws_config

    with open('config/scenes.yaml', 'r') as file:
        scenes = yaml.safe_load(file)

    with open('config/obs.yaml', 'r') as file:
        ws_config = yaml.safe_load(file)


def switch_scene(scene: str):

    global last_switched

    print("[OBS] Connecting to WS")
    try:
        cl = obs.ReqClient(**ws_config)
        print("[OBS] Switching scene {}".format(scene))
        last_switched = scene
        cl.set_current_program_scene(scene)

        cl.disconnect()
    except obs_error.OBSSDKError as e:
        raise ConnectionError(e)

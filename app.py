import threading

from flask import Flask, render_template, redirect, flash
from flask_bootstrap import Bootstrap5

import ndi_discover as ndi
import obs_control as obs

app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.secret_key = 'BJBNDIRc'
app.config['current_scene'] = '(auto)'


@app.route('/')
def index():
    page_scenes = {'(auto)': {'name': '(Auto)', 'style': 'bg-dark'}}
    page_scenes.update(obs.scenes)

    print(page_scenes)
    return render_template('index.html',
                           scenes=page_scenes,
                           last_switch=obs.last_switched,
                           current=app.config['current_scene'])


@app.route('/scene/<scene>')
def scene_switch(scene: str):
    if scene == '(auto)':
        ndi.auto_switch = True
        ndi.last_switched_scene = None
        app.config['current_scene'] = '(auto)'

    elif scene in obs.scenes:
        ndi.auto_switch = False
        try:
            obs.switch_scene(scene)
            app.config['current_scene'] = scene
        except ConnectionError as e:
            print("[EXCEPT] {}".format(e))
            flash("OBS Websocket error: {}".format(e), category='danger')

    return redirect('/')


if __name__ == '__main__':
    obs.load_config()
    ndi.init_ndi_discover()
    for key, scene in obs.scenes.items():
        print("Registering {}".format(key))
        ndi.register_scene(key, default=scene.get('default', False),
                           ndi_name=scene.get('ndi_name', None),
                           switch_fn=lambda k=key: obs.switch_scene(k))

    ndi_thread = threading.Thread(target=ndi.discover_ndi)
    ndi_thread.daemon = True
    ndi_thread.start()

    app.run(host="0.0.0.0", port=5050)

import os.path

import yaml
from logbook import Logger


mylog = Logger(__name__)


class Launcher:
    def __init__(self):
        with open('config.yaml', 'rt') as config_yaml:
            self.config = yaml.safe_load(config_yaml.read())

    def launch(self, params: dict) -> None:
        wads_folder = self.config['source_port']['wads_folder']

        # TODO: all of this is probably redundant now, just use the passed in params
        launch_params = {}
        if 'profile' in params.keys():
            wads = [os.path.join(wads_folder, wad) for wad in params['profile'].wads]
            launch_params['wads'] = f"-file {' '.join(wads)}"
        if 'params' in params.keys():
            launch_params['params'] = params['params']

        launch_path = f"{params['binary']} {' '.join(launch_params.values())}"
        os.system(launch_path)

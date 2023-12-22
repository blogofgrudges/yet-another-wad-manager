import os.path

import yaml
from logbook import Logger


mylog = Logger(__name__)


class Launcher:
    """
    DOOM Launcher class
    """
    def __init__(self) -> None:
        """
        Create a launcher class
        """
        with open('config.yaml', 'rt') as config_yaml:
            self.config = yaml.safe_load(config_yaml.read())

    def launch(self, params: dict) -> None:
        """
        Launch the game with passed in launch options

        :param params: launch options
        :return: None
        """
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

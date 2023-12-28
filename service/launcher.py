import os.path

from logbook import Logger

from service.models import Profile


mylog = Logger(__name__)


class Launcher:
    """
    DOOM Launcher class
    """
    def __init__(self, **kwargs) -> None:
        """
        Create a launcher class
        """
        self.config = kwargs['config']

    def launch(self, profile: Profile, binary: str, params: str = '') -> None:
        """
        Launch the game with passed in launch options

        :param profile: the profile to launch
        :param params: the launch options
        :return: None
        """
        wads_folder = self.config['source_port']['wads_folder']

        wads = [os.path.join(wads_folder, wad) for wad in profile.wads]

        launch_path = f"{binary} -file {' '.join(wads)} {profile.launch_opts} {params}"
        mylog.info(f"Launch path: {launch_path})")

        os.system(launch_path)

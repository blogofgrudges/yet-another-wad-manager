import os.path
from subprocess import Popen

import wx
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
        self.config = ''
        self.main_frame = None

        if 'config' in kwargs.keys():
            self.config = kwargs['config']
        if 'main_frame' in kwargs.keys():
            self.main_frame = kwargs['main_frame']

    def launch(self, profile: Profile, binary: str, params: str = '') -> None:
        """
        Launch the game with passed in launch options

        :param binary: the source port executable
        :param profile: the profile to launch
        :param params: the launch options
        :return: None
        """
        wads_folder = self.config['source_port']['wads_folder']

        wads = [os.path.join(wads_folder, wad) for wad in profile.wads]

        launch_path = f"{binary} -file {' '.join(wads)} {profile.launch_opts} {params}"
        mylog.info(f"Launch path: {launch_path}")

        Popen(launch_path)

        if self.config['service']['auto_close_on_launch'] and self.main_frame:
            mylog.info(f"Auto close on launch is set: {self.config['service']['auto_close_on_launch']}")
            wx.CallAfter(self.main_frame.Destroy)

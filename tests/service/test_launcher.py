from tempfile import TemporaryDirectory
import os.path

import yaml

from service.launcher import Launcher


class TestLauncher:
    """
    A test launcher class for Launcher class tests
    """
    def test_new_launcher(self):
        """
        Make a new empty launcher
        """
        launcher = Launcher()

        assert launcher.config == ''
        assert launcher.main_frame is None

    def test_new_launcher_with_kwargs(self):
        """
        Make a new empty launcher
        """
        config = {
            'source_port': {
                'wads_folder': 'my-folder'
            }
        }
        main_frame = True
        launcher = Launcher(config=config, main_frame=main_frame)

        assert launcher.config == config
        assert launcher.main_frame == main_frame

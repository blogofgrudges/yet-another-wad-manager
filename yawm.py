import sys

import yaml
from logbook import Logger, NestedSetup, StreamHandler

from gui.app import WADManagerApp
from gui.main_frame import MainFrame


mylog = Logger(__name__)


# ready for launch
if __name__ == "__main__":
    # TODO: use this as the contig source of truth from now on
    with open('config.yaml', 'rt') as config_yaml:
        config = yaml.safe_load(config_yaml.read())

    log_setup = NestedSetup([
            StreamHandler(sys.stdout, level=config['logger']['level'], bubble=False)
        ]
    )

    # bind the logs to the thread
    with log_setup:
        mylog.info("Starting application")
        app = WADManagerApp()
        main_frame = MainFrame(None, title=app.appName)
        app.MainLoop()

import os.path
import sys

import yaml
from logbook import Logger, NestedSetup, StreamHandler, TimedRotatingFileHandler

from gui.app import WADManagerApp
from gui.main_frame import MainFrame


mylog = Logger(__name__)


# ready for launch
if __name__ == "__main__":
    with open('config.yaml', 'rt') as config_yaml:
        config = yaml.safe_load(config_yaml.read())

    log_setup = NestedSetup([
            StreamHandler(sys.stdout, level=config['logger']['level'], bubble=False),
            TimedRotatingFileHandler(
                    os.path.abspath('yawm-log'),
                    level=0,
                    backup_count=3,
                    bubble=True,
                    date_format='%Y-%m-%d')
        ]
    )

    # bind the logs to the thread
    with log_setup:
        mylog.info("Starting YAWM application")
        app = WADManagerApp()

        main_frame = MainFrame(None, title=app.appName, config=config)
        app.MainLoop()

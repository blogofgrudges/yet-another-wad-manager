import argparse
import os.path

import yaml

from service.launcher import Launcher
from service.models import Profile

"""
CLI inteface, for real DOOMers
"""

argp = argparse.ArgumentParser()
argp.add_argument('-p', '--profile', type=str, required=True)
argp.add_argument('-c', '--cli_opts', type=str, nargs='?')
args = argp.parse_args()

with open('config.yaml', 'r') as config_yaml:
    config = yaml.safe_load(config_yaml.read())

launcher = Launcher(config=config, main_frame=False)
profile = Profile().from_yaml(os.path.join(config['service']['profiles_folder'], args.profile))

if args.cli_opts is None:
    args.cli_opts = ''

launch_options = {
    'binary': config['source_port']['binary'],
    'params': args.cli_opts,
    'profile': profile
}

launcher.launch(profile, config['source_port']['binary'], params=args.cli_opts)

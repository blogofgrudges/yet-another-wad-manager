"""
YAWM - Yet another (DOOM) WAD manager
python wad_manager.py -p (--profile) my-profile-0.yaml -c (--cli_opts) '-key value'
"""

import argparse
import os
import os.path

import yaml

from models import Profile


argp = argparse.ArgumentParser()
argp.add_argument('-p', '--profile', type=str)
argp.add_argument('-c', '--cli_opts', type=str, nargs='?')
args = argp.parse_args()

with open('../config.yaml', 'r') as config_yaml:
    config = yaml.safe_load(config_yaml.read())

wads_folder = config['source_port']['wads_folder']
source_port_binary = config['source_port']['binary']
profiles_folder = config['service']['profiles_folder']

profile = Profile(os.path.join(profiles_folder, args.profile))

launch_params = {}
wads = [os.path.join(wads_folder, wad) for wad in profile.wads]

if wads:
    launch_params['wads'] = f"-file {' '.join(wads)}"
if profile.launch_opts:
    launch_params['profile_opts'] = profile.launch_opts
if args.cli_opts:
    launch_params['cli_opts'] = args.cli_opts

launch_path = f"{source_port_binary} {' '.join(launch_params.values())}"
os.system(launch_path)

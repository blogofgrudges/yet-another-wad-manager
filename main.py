"""
YAWM - Yet another (DOOM) WAD manager
python main.py -p (--profile) my-profile-0.yaml
"""

import argparse
import os
import os.path

import yaml


def scuffed_path(drive: str, target: str) -> str:
    """
    Create a path from the drive to target directory.
    """
    return os.path.join(os.sep, drive + os.sep, target)


argp = argparse.ArgumentParser()
argp.add_argument('-p', '--profile', type=str)
args = argp.parse_args()

with open('config.yaml', 'r') as config_yaml:
    config = yaml.safe_load(config_yaml.read())

wads_folder = config['source_port']['wads_folder']
source_port = config['source_port']['binary']
installed_drive = config['source_port']['installed_drive']
profiles_folder = config['app']['profiles_folder']

wads_path = scuffed_path(installed_drive, wads_folder)

with open(os.path.join(profiles_folder, args.profile), 'r') as profile_yaml:
    profile = yaml.safe_load(profile_yaml.read())

wads = [scuffed_path(wads_path, wad) for wad in profile['wads']]
launch_params = f"-file {' '.join(wads)}"
launch_path = f'{scuffed_path(installed_drive, source_port)} {launch_params}'
print(launch_path)

os.system(launch_path)

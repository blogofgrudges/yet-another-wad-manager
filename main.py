import os
import os.path

import yaml


def scuffed_path(drive: str, target: str) -> str:
    return os.path.join(os.sep, drive + os.sep, target)


with open('config.yaml', 'r') as config_yaml:
    config = yaml.safe_load(config_yaml.read())

wads_folder = config['wads_folder']
source_port = config['source_port']
drv = config['drive']

wads_path = scuffed_path(drv, wads_folder)

wads = [
    'nchud-main.pk3',
    'pk_doom_sfx_20120224.wad',
    'sm4BBgorev2.pk3',
    'vsmooth.wad'
]

wads = [scuffed_path(wads_path, wad) for wad in wads]
launch_params = f"-file {' '.join(wads)}"


launch_path = f'{scuffed_path(drv, source_port)} {launch_params}'
print(launch_path)

# print(launch_params)
os.system(launch_path)

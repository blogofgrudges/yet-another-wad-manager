import os
import os.path
from typing import Self

import yaml
from logbook import Logger


mylog = Logger(__name__)


class Profile:
    def __init__(self) -> None:
        self.filename = ''
        self.name = ''
        self.launch_opts = ''
        self.profile = None
        self.wads = []

    def from_yaml(self, source_file: str) -> Self:
        with open(source_file, 'r') as profile_yaml:
            self.profile = yaml.safe_load(profile_yaml.read())
        self.filename = source_file
        self.from_dict(self.profile)
        return self

    def from_dict(self, source_dict: dict) -> Self:
        self.profile = source_dict
        if 'name' in source_dict.keys():
            self.name = source_dict['name']

        if 'launch_opts' in source_dict.keys():
            self.launch_opts = source_dict['launch_opts']

        if 'wads' in source_dict.keys():
            self.wads = source_dict['wads']
        return self

    def to_yaml(self, output_file: str) -> None:  # TODO: None?
        output = {}
        for k, v in self.asdict().items():
            if v != '':
                output[k] = v

        with open(output_file, 'w') as output_yaml:
            yaml.dump(output, output_yaml)

    def asdict(self) -> dict:
        return {'name': self.name, 'launch_opts': self.launch_opts, 'wads': self.wads}


class Profiles:
    def __init__(self, profiles_source: str) -> None:
        self.profiles_source = profiles_source
        self.profiles = []
        self.load()

    def load(self) -> Self:
        self.profiles = []
        for file in os.listdir(self.profiles_source):
            if file.endswith('.yaml') or file.endswith('.yml'):  # TODO: find a better way to do this
                p = Profile().from_yaml(os.path.join(self.profiles_source, file))
                self.profiles.append(p)
                mylog.info(f'Registered profile: {p.name}')
        mylog.info(f'Profiles registered: {len(self.profiles)}')
        return self


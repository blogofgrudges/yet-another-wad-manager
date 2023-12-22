import os
import os.path
from typing import Self

import yaml
from logbook import Logger


mylog = Logger(__name__)


class Profile:
    """
    Contains profile details
    """
    def __init__(self) -> None:
        """
        Create a profiles class
        """
        self.filename = ''
        self.name = ''
        self.launch_opts = ''
        self.profile = None
        self.wads = []

    def from_yaml(self, source_file: str) -> Self:
        """
        Populate a profile from a YAML file

        :param source_file: YAML file to load from
        :return: Self
        """
        with open(source_file, 'r') as profile_yaml:
            self.profile = yaml.safe_load(profile_yaml.read())
        self.filename = source_file
        self.from_dict(self.profile)
        return self

    def from_dict(self, source_dict: dict) -> Self:
        """
        Populate a profile from a dictionary

        :param source_dict: dictionary to load from
        :return: Self
        """
        self.profile = source_dict
        if 'name' in source_dict.keys():
            self.name = source_dict['name']

        if 'launch_opts' in source_dict.keys():
            self.launch_opts = source_dict['launch_opts']

        if 'wads' in source_dict.keys():
            self.wads = source_dict['wads']
        return self

    def to_yaml(self, output_file: str) -> None:  # TODO: None?
        """
        Create a YAML file from a profile

        :param output_file: YAML file to write to
        :return: None
        """
        output = {}
        for k, v in self.asdict().items():
            if v != '':
                output[k] = v

        with open(output_file, 'w') as output_yaml:
            yaml.dump(output, output_yaml)

    def asdict(self) -> dict:
        """
        Return the profile as a dictionary

        :return: dict
        """
        return {'name': self.name, 'launch_opts': self.launch_opts, 'wads': self.wads}


class Profiles:
    """
    Contains a list of profiles
    """
    def __init__(self, profiles_source: str) -> None:
        """
        Create a profiles class

        :param profiles_source: profiles directory path
        """
        self.profiles_source = profiles_source
        self.profiles = []

    def load(self) -> Self:
        """
        Load a list of profiles from a directory

        :return: Self
        """
        self.profiles = []
        for file in os.listdir(self.profiles_source):
            if file.endswith('.yaml') or file.endswith('.yml'):  # TODO: find a better way to do this
                p = Profile().from_yaml(os.path.join(self.profiles_source, file))
                self.profiles.append(p)
                mylog.info(f'Registered profile: {p.name}')
        mylog.info(f'Profiles registered: {len(self.profiles)}')
        return self


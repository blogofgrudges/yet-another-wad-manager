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
        Create a profile class
        """
        self.filename = ''
        self.name = ''
        self.launch_opts = ''
        self.profile = None
        self.wads = []

    def __eq__(self, another: type):
        """
        Cursed python testing magic

        :param another: the thing being compared
        :return:
        """
        return (self.filename == another.filename and
                self.name == another.name and
                self.launch_opts == another.launch_opts and
                self.profile == another.profile,
                self.wads == another.wads)

    def from_yaml(self, source_file: str) -> Self:
        """
        Populate a profile from a YAML file

        :param source_file: YAML file to load from
        :return: Self
        """
        try:
            profile_yaml = open(source_file, 'r')
        except OSError as error:
            mylog.error(error)
            return self
        else:
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

    def to_yaml(self, output_file: str) -> None:
        """
        Create a YAML file from a profile

        :param output_file: YAML file to write to
        :return: None
        """
        output = {}
        for k, v in self.asdict().items():
            if v != '':
                output[k] = v

        try:
            output_yaml = open(output_file, 'w')
        except OSError as error:
            mylog.error(error)
            return None
        else:
            yaml.dump(output, output_yaml)

    def asdict(self) -> dict:
        """
        Return the profile as a dictionary

        :return: dict
        """
        return {'filename': self.filename, 'name': self.name, 'launch_opts': self.launch_opts, 'wads': self.wads}


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
        Additively load a list of profiles from a directory

        :return: Self
        """
        for file in os.listdir(self.profiles_source):
            if not file.endswith(('.yaml', '.yml')):
                continue
            new_profile = Profile().from_yaml(os.path.join(self.profiles_source, file))

            for index, old_profile in enumerate(self.profiles):
                if new_profile.filename == old_profile.filename and new_profile.asdict() != old_profile.asdict():
                    # this is an existing, updated profile
                    self.profiles[index] = new_profile
                    mylog.info(f'Registered updated profile: {new_profile.filename}')
                    break

            if new_profile.filename not in [op.filename for op in self.profiles]:
                # this must be a new profile
                self.profiles.append(new_profile)
                mylog.info(f'Registered new profile: {new_profile.filename}')

        mylog.info(f'Profiles registered: {len(self.profiles)}')
        return self

import yaml


class Profile:
    def __init__(self, source_file: str) -> None:
        with open(source_file, 'r') as profile_yaml:
            self.profile = yaml.safe_load(profile_yaml.read())

        self.launch_opts = ''
        if 'launch_opts' in self.profile.keys():
            self.launch_opts = self.profile['launch_opts']

        self.wads = []
        if 'wads' in self.profile.keys():
            self.wads = self.profile['wads']

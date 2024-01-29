from tempfile import TemporaryDirectory
import os.path

import yaml

from service.models import Profile, Profiles


class TestProfile:
    """
    A test profile class for Profile class tests
    """
    def test_new_profile(self):
        """
        Make a new empty profile
        """
        profile = Profile()

        assert profile.filename == ''
        assert profile.name == ''
        assert profile.launch_opts == ''
        assert profile.profile is None
        assert profile.wads == []

    def test_new_profile_from_yaml(self):
        """
        Make a new profile from a YAML
        """
        with TemporaryDirectory() as test_dir:
            profile_dict = {
                'filename': 'test-profile.yaml',
                'name': 'Test Profile',
                'launch_opts': 'my-opt',
                'wads': ['my-wad-0.wad', 'my-pak-0.pk3']
            }

            profile_path = os.path.join(test_dir, 'test_profile.yaml')
            with open(profile_path, 'w') as profile_file:
                yaml.dump(profile_dict, profile_file)

            profile = Profile().from_yaml(profile_path)

            assert profile.filename == profile_path
            assert profile.name == 'Test Profile'
            assert profile.launch_opts == 'my-opt'
            assert profile.profile is not None
            assert profile.wads == ['my-wad-0.wad', 'my-pak-0.pk3']

    def test_new_profile_from_yaml_missing_file(self):
        """
        Make a new profile from a missing YAML
        """
        profile_path = ''
        profile = Profile().from_yaml(profile_path)

        assert profile.filename == ''
        assert profile.name == ''
        assert profile.launch_opts == ''
        assert profile.profile is None
        assert profile.wads == []

    def test_new_profile_from_dict(self):
        """
        Make a new profile from a dictionary
        """
        profile_dict = {
            'name': 'Test Profile',
            'launch_opts': 'my-opt',
            'wads': ['my-wad-0.wad', 'my-pak-0.pk3']
        }
        profile = Profile().from_dict(profile_dict)

        assert profile.filename == ''
        assert profile.name == 'Test Profile'
        assert profile.launch_opts == 'my-opt'
        assert profile.profile is not None
        assert profile.wads == ['my-wad-0.wad', 'my-pak-0.pk3']

    def test_profile_from_dict_empty(self):
        """
        Make a new profile from an empty dictionary
        """
        profile_dict = {}
        profile = Profile().from_dict(profile_dict)

        assert profile.filename == ''
        assert profile.name == ''
        assert profile.launch_opts == ''
        assert profile.profile == {}
        assert profile.wads == []

    def test_profile_to_yaml(self):
        """
        Write to a YAML file
        """
        with TemporaryDirectory() as test_dir:
            profile_dict = {
                'filename': 'test-profile.yaml',
                'name': 'Test Profile',
                'launch_opts': 'my-opt',
                'wads': ['my-wad-0.wad', 'my-pak-0.pk3']
            }

            profile = Profile()
            profile.filename = profile_dict['filename']
            profile.name = profile_dict['name']
            profile.launch_opts = profile_dict['launch_opts']
            profile.wads = profile_dict['wads']

            profile_path = os.path.join(test_dir, 'test_profile.yaml')
            profile.to_yaml(profile_path)

            with open(profile_path, 'r') as result_yaml:
                result = yaml.safe_load(result_yaml)

            assert profile_dict == result

    def test_profile_as_dict(self):
        """
        Return a profile as a dictionary
        """
        profile_dict = {
            'filename': 'test-profile.yaml',
            'name': 'Test Profile',
            'launch_opts': 'my-opt',
            'wads': ['my-wad-0.wad', 'my-pak-0.pk3']
        }

        profile = Profile()
        profile.filename = profile_dict['filename']
        profile.name = profile_dict['name']
        profile.launch_opts = profile_dict['launch_opts']
        profile.wads = profile_dict['wads']

        assert profile.asdict() == profile_dict


class TestProfiles:
    """
    A test profiles class for Profiles class tests
    """
    def test_new_profiles(self):
        """
        Make a new empty Profiles
        """
        with TemporaryDirectory() as test_dir:
            profiles = Profiles(test_dir)

            assert profiles.profiles_source == test_dir
            assert profiles.profiles == []

    def test_profiles_load(self):
        """
        Load YAML and YML profiles from a source directory
        """
        with TemporaryDirectory() as test_dir:
            profile_dict = {
                'name': 'Test Profile',
                'launch_opts': 'my-opt',
                'wads': ['my-wad-0.wad', 'my-pak-0.pk3']
            }

            profile_yaml = Profile().from_dict(profile_dict)
            profile_yaml.to_yaml(os.path.join(test_dir, 'test_profile.yaml'))

            profile_yml = Profile().from_dict(profile_dict)
            profile_yml.to_yaml(os.path.join(test_dir, 'test_profile.yml'))

            profiles = Profiles(test_dir).load()

            assert profiles.profiles_source == test_dir
            assert profiles.profiles == [profile_yaml, profile_yml]

    def test_profiles_load_new_profile(self):
        """
        Load a new profile after profiles have already been loaded
        """
        with TemporaryDirectory() as test_dir:
            profile_dict = {
                'name': 'Test Profile',
                'launch_opts': 'my-opt',
                'wads': ['my-wad-0.wad', 'my-pak-0.pk3']
            }

            profile_yaml = Profile().from_dict(profile_dict)
            profile_yaml.to_yaml(os.path.join(test_dir, 'test_profile.yaml'))

            profile_yml = Profile().from_dict(profile_dict)
            profile_yml.to_yaml(os.path.join(test_dir, 'test_profile.yml'))

            profiles = Profiles(test_dir).load()

            profile_another_yaml = Profile().from_dict(profile_dict)
            profile_another_yaml.to_yaml(os.path.join(test_dir, 'test_another_profile.yaml'))

            profiles.load()

            assert profiles.profiles_source == test_dir
            assert profiles.profiles == [profile_yaml, profile_yml, profile_another_yaml]

    def test_profiles_load_updated_profile(self):
        """
        Load an updated profile after profiles have already been loaded
        """
        with TemporaryDirectory() as test_dir:
            profile_dict = {
                'name': 'Test Profile',
                'launch_opts': 'my-opt',
                'wads': ['my-wad-0.wad', 'my-pak-0.pk3']
            }

            updated_profile_dict = {
                'name': 'Another Test Profile',
                'launch_opts': 'another-my-opt',
                'wads': ['my-wad-0.wad', 'my-pak-0.pk3', 'my-pak-1.pk3']
            }

            profile_yaml = Profile().from_dict(profile_dict)
            profile_yaml.to_yaml(os.path.join(test_dir, 'test_profile.yaml'))

            profile_yml = Profile().from_dict(profile_dict)
            profile_yml.to_yaml(os.path.join(test_dir, 'test_profile.yml'))

            profiles = Profiles(test_dir).load()

            updated_profile_yml = Profile().from_dict(updated_profile_dict)
            updated_profile_yml.to_yaml(os.path.join(test_dir, 'test_profile.yml'))

            profiles.load()

            assert profiles.profiles_source == test_dir
            assert profiles.profiles == [profile_yml, updated_profile_yml]

    # TODO: deal with this mess later
    # def test_profiles_deleted_profile(self):
    #     """
    #     Do not load a deleted profile after profiles have already been loaded
    #     """
    #     with TemporaryDirectory() as test_dir:
    #         profile_dict = {
    #             'name': 'Test Profile',
    #             'launch_opts': 'my-opt',
    #             'wads': ['my-wad-0.wad', 'my-pak-0.pk3']
    #         }
    #
    #         updated_profile_dict = {
    #             'name': 'Another Test Profile',
    #             'launch_opts': 'another-my-opt',
    #             'wads': ['my-wad-0.wad', 'my-pak-0.pk3', 'my-pak-1.pk3']
    #         }
    #
    #         profile_yaml = Profile().from_dict(profile_dict)
    #         profile_yaml.to_yaml(os.path.join(test_dir, 'test_profile.yaml'))
    #
    #         profile_yml = Profile().from_dict(profile_dict)
    #         profile_yml.to_yaml(os.path.join(test_dir, 'test_profile.yml'))
    #
    #         profiles = Profiles(test_dir).load()
    #
    #         os.remove(os.path.join(test_dir, 'test_profile.yml'))
    #
    #         profiles.load()
    #
    #         assert profiles.profiles_source == test_dir
    #         assert profiles.profiles == [profile_yaml, profile_yml]

import os

import wx
import yaml
from logbook import Logger

import gui.events
from service.launcher import Launcher
from service.models import Profile


mylog = Logger(__name__)


class ControlsPanel(wx.Panel):
    """
    Controls panel class (the left hand side of the window)
    """
    def __init__(self, parent) -> None:
        """
        Create a controls panel

        :param parent: MainFrame
        """
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)
        self.main_frame = parent.get_instance()

        with open('config.yaml', 'rt') as config_yaml:
            self.config = yaml.safe_load(config_yaml.read())

        # get a launcher for later
        self.launcher = Launcher()

        # sizer
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # source port controls
        self.controls_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Select source port")

        self.source_port_picker_sizer = wx.BoxSizer(wx.HORIZONTAL)
        saved_path = self.config['source_port']['binary']  # TODO: what if it's not set?
        self.source_port_picker = wx.FilePickerCtrl(self,
                                                    path=saved_path,
                                                    message="Select source port executable")
        self.source_port_picker_sizer.Add(self.source_port_picker, 1, wx.ALL, 5)

        self.additional_params_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.additional_params_control = wx.TextCtrl(self)
        self.additional_params_label = wx.StaticText(self, -1, 'Launch opts')
        self.additional_params_sizer.Add(self.additional_params_label, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 5)
        self.additional_params_sizer.Add(self.additional_params_control, 1, wx.ALL, 5)

        self.controls_sizer.Add(self.source_port_picker_sizer, 0, wx.EXPAND)
        self.controls_sizer.Add(self.additional_params_sizer, 0, wx.EXPAND)

        # profiles selector
        self.profiles_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Select launch profile")

        self.list_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.profiles_list_box = wx.ListBox(self, style=wx.LB_ALWAYS_SB)
        self.populate_profiles(gui.events.UPDATED_PROFILES)  # TODO: improve this
        self.list_box_sizer.Add(self.profiles_list_box, 1, wx.EXPAND)

        self.buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_profile_button = wx.Button(self, wx.ID_ANY, 'Add profile')
        self.refresh_profiles_button = wx.Button(self, wx.ID_ANY, 'Refresh profiles')
        self.delete_profile_button = wx.Button(self, wx.ID_ANY, 'Delete profile')

        self.buttons_sizer.Add(self.add_profile_button, 0, wx.RIGHT, 5)
        self.buttons_sizer.Add(self.refresh_profiles_button, 0, wx.LEFT | wx.RIGHT, 5)
        self.buttons_sizer.Add(self.delete_profile_button, 0, wx.LEFT, 5)

        self.profiles_sizer.Add(self.list_box_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.profiles_sizer.Add(self.buttons_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # launch control
        self.launch_button = wx.Button(self, wx.ID_ANY, 'Launch w/selected options')

        # sizer cont
        self.panel_sizer.Add(self.controls_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.panel_sizer.Add(self.profiles_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.panel_sizer.Add(self.launch_button, 0, wx.EXPAND | wx.ALL, 10)

        # bindings
        self.Bind(wx.EVT_BUTTON, self.add_profile, self.add_profile_button)
        self.Bind(wx.EVT_BUTTON, self.refresh_profiles, self.refresh_profiles_button)
        self.Bind(wx.EVT_BUTTON, self.delete_profile, self.delete_profile_button)
        self.Bind(wx.EVT_BUTTON, self.launch, self.launch_button)
        self.Bind(wx.EVT_LISTBOX, self.profiles_list_box_select, self.profiles_list_box)
        self.main_frame.Bind(gui.events.UPDATED_PROFILES, self.populate_profiles)

        # display
        self.SetSizer(self.panel_sizer)
        self.Show()

    def populate_profiles(self, event: wx.Event) -> None:
        """
        Reload the profiles list box with the current list of profiles

        :param event: not used
        :return: None
        """
        mylog.info(f"Update profiles listbox")
        self.profiles_list_box.Set([p.name for p in self.main_frame.profiles.profiles])  # doesn't work?
        self.Layout()

    def add_profile(self, event: wx.Event) -> None:
        """
        Create a new profile file, post a profiles changed event

        :param event: not used
        :return: None
        """
        mylog.info(f"Hit: on_add_profile")

        # TODO: This should be dynamic
        source = {'name': 'my-profile-2', 'wads': ['SIGIL2.WAD']}
        new_profile = Profile().from_dict(source)
        new_profile.filename = f'{new_profile.name}.yaml'
        new_profile.to_yaml(f"profiles\\{new_profile.filename}")
        mylog.info(f"Created {new_profile.name} ({new_profile.filename})")

        wx.PostEvent(self.main_frame, gui.events.ProfilesChanged())

    def refresh_profiles(self, event: wx.Event) -> None:
        """
        Trigger a profiles changed event

        :param event: not used
        :return: None
        """
        mylog.info(f"Hit: on_refresh_profiles")
        wx.PostEvent(self.main_frame, gui.events.ProfilesChanged())

    def delete_profile(self, event: wx.Event) -> None:
        """
        Delete a profile file, post a profiles changed event

        :param event: not used
        :return: None
        """
        mylog.info(f"Hit: on_delete_profile")

        profile_to_delete = self.main_frame.profiles.profiles[self.profiles_list_box.GetSelection()]
        os.remove(f"{profile_to_delete.filename}")
        mylog.info(f"Deleted {profile_to_delete.name} ({profile_to_delete.filename})")

        wx.PostEvent(self.main_frame, gui.events.ProfilesChanged())

    def launch(self, event: wx.Event) -> None:
        """
        Package all of the launch options and call the launcher to start the game

        :param event: not used
        :return: None
        """
        mylog.info(f"Hit: on_launch")

        launch_options = {
            'binary': self.source_port_picker.GetPath(),
            'params': self.additional_params_control.GetLineText(0),
            'profile': self.main_frame.profiles.profiles[self.profiles_list_box.GetSelection()]
        }
        self.launcher.launch(launch_options)

    def profiles_list_box_select(self, event: wx.Event) -> None:
        """
        New profile is selected in the list box, post a selected profile event

        :param event: not used
        :return: None
        """
        # TODO: perhaps the event data could carry the selected profile?
        new_profile = self.main_frame.profiles.profiles[self.profiles_list_box.GetSelection()]
        if self.main_frame.selected_profile != new_profile:
            self.main_frame.selected_profile = new_profile
            mylog.info(f"New profile selected: {self.main_frame.selected_profile.name} {self.main_frame.selected_profile}")
            wx.PostEvent(self.main_frame, gui.events.SelectedProfile())

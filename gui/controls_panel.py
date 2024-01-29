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
    def __init__(self, parent, **kwargs) -> None:
        """
        Create a controls panel

        :param parent: MainFrame
        """
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)
        self.main_frame = parent.get_instance()

        self.config = kwargs['config']
        kwargs['main_frame'] = self.main_frame  # TODO: This feels a bit scuffed

        # get a launcher for later
        self.launcher = Launcher(**kwargs)

        # sizer
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # source port controls
        self.controls_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Select source port")
        self.source_port_picker_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.source_port_picker = wx.FilePickerCtrl(self,
                                                    path='',
                                                    message="Select source port executable")
        if self.config['source_port']['binary']:
            self.source_port_picker.SetPath(self.config['source_port']['binary'])
            wx.CallAfter(self.source_port_picker.TextCtrl.SetInsertionPoint, 0)  # this is a bit cursed
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
        wx.PostEvent(self.main_frame, gui.events.ProfilesUpdated())  # force the listbox to populate
        self.list_box_sizer.Add(self.profiles_list_box, 1, wx.EXPAND)

        self.buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_profile_button = wx.Button(self, wx.ID_ANY, 'Add profile')
        self.refresh_profiles_button = wx.Button(self, wx.ID_ANY, 'Refresh profiles')
        self.delete_profile_button = wx.Button(self, wx.ID_ANY, 'Delete profile')

        self.buttons_sizer.Add(self.add_profile_button, 0, wx.RIGHT, 5)
        self.buttons_sizer.Add(self.refresh_profiles_button, 0, wx.LEFT | wx.RIGHT, 5)
        self.buttons_sizer.Add(self.delete_profile_button, 0, wx.LEFT, 5)

        self.profiles_sizer.Add(self.list_box_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.profiles_sizer.Add(self.buttons_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # launch control
        self.launch_control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.launch_auto_close = wx.CheckBox(self, label='Auto-close')
        self.launch_auto_close.SetValue(self.config['service']['auto_close_on_launch'])
        self.launch_button = wx.Button(self, wx.ID_ANY, 'Launch w/selected options')
        self.launch_control_sizer.Add(self.launch_auto_close, 0, wx.EXPAND | wx.RIGHT, 5)
        self.launch_control_sizer.Add(self.launch_button, 1, wx.EXPAND | wx.LEFT, 5)

        # sizer cont
        self.panel_sizer.Add(self.controls_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.panel_sizer.Add(self.profiles_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.panel_sizer.Add(self.launch_control_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # bindings
        self.Bind(wx.EVT_BUTTON, self.add_profile, self.add_profile_button)
        self.Bind(wx.EVT_BUTTON, self.refresh_profiles, self.refresh_profiles_button)
        self.Bind(wx.EVT_BUTTON, self.delete_profile, self.delete_profile_button)
        self.Bind(wx.EVT_BUTTON, self.launch, self.launch_button)
        self.Bind(wx.EVT_LISTBOX, self.profiles_list_box_select, self.profiles_list_box)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.source_port_changed, self.source_port_picker)
        self.Bind(wx.EVT_CHECKBOX, self.auto_close_changed, self.launch_auto_close)

        self.main_frame.Bind(gui.events.CONFIG_CHANGED, self.config_changed)
        self.main_frame.Bind(gui.events.PROFILES_UPDATED, self.populate_profiles)

        self.last_selected_profile_index = self.profiles_list_box.GetSelection()

        # display
        self.SetSizer(self.panel_sizer)
        self.Show()

    def populate_profiles(self, event: wx.Event) -> None:
        """
        Reload the profiles list box with the current list of profiles
        Constrain the selected profile to the profiles list range
        Post a profile selected event

        :param event: not used
        :return: None
        """
        mylog.info("Refresh profiles listbox")
        previous_selection = self.profiles_list_box.GetSelection()
        self.profiles_list_box.Set([p.name for p in self.main_frame.profiles.profiles])

        if previous_selection >= len(self.main_frame.profiles.profiles):
            # a profile has been deleted and the selection is now out of range, constrain it to range
            new_selection = len(self.main_frame.profiles.profiles) - 1
        elif previous_selection < 0 and self.main_frame.profiles.profiles:
            # nothing was selected before, but there are profiles so pick the first one
            new_selection = 0
        else:
            # the previous selection is still in the range, so keep using it
            new_selection = previous_selection

        self.profiles_list_box.SetSelection(new_selection)
        self.last_selected_profile_index = new_selection
        wx.PostEvent(self.main_frame, gui.events.SelectedProfile())
        self.Layout()

    def add_profile(self, event: wx.Event) -> None:
        """
        Create a new profile file, post a profiles changed event

        :param event: not used
        :return: None
        """
        mylog.info("Launch profile name dialog")
        profile_name_dialog = wx.TextEntryDialog(self,
                                                 message='Choose a new profile name',
                                                 caption='Add profile')

        if profile_name_dialog.ShowModal() == wx.ID_OK:  # TODO: what if the name is already being used? or empty
            # just so we dont lose any unsaved edits
            if self.last_selected_profile_index >= 0:
                active_profile = self.main_frame.selections_panel.my_profile
                last_profile = self.main_frame.profiles.profiles[self.last_selected_profile_index]
                discard_changes = self.discard_unsaved_changes(active_profile, last_profile)
                if not discard_changes:
                    return None

            new_profile = Profile().from_dict({'name': profile_name_dialog.GetValue()})
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
        # just so we dont lose any unsaved edits
        if self.last_selected_profile_index >= 0:
            active_profile = self.main_frame.selections_panel.my_profile
            last_profile = self.main_frame.profiles.profiles[self.last_selected_profile_index]
            discard_changes = self.discard_unsaved_changes(active_profile, last_profile)
            if not discard_changes:
                return None

        wx.PostEvent(self.main_frame, gui.events.ProfilesChanged())

    def delete_profile(self, event: wx.Event) -> None:
        """
        Delete a profile file, post a profiles changed event

        :param event: not used
        :return: None
        """
        # just so we dont lose any unsaved edits
        if self.last_selected_profile_index >= 0:
            active_profile = self.main_frame.selections_panel.my_profile
            last_profile = self.main_frame.profiles.profiles[self.last_selected_profile_index]
            discard_changes = self.discard_unsaved_changes(active_profile, last_profile)
            if not discard_changes:
                return None

        # TODO: make sure a profile is selected first
        profile_to_delete = self.main_frame.profiles.profiles[self.profiles_list_box.GetSelection()]
        os.remove(f"{profile_to_delete.filename}")
        self.main_frame.profiles.profiles.pop(self.profiles_list_box.GetSelection())
        mylog.info(f"Deleted {profile_to_delete.name} ({profile_to_delete.filename})")

        wx.PostEvent(self.main_frame, gui.events.ProfilesChanged())

    def launch(self, event: wx.Event) -> None:
        """
        Package all of the launch options and call the launcher to start the game

        :param event: not used
        :return: None
        """
        self.launcher.launch(self.main_frame.profiles.profiles[self.profiles_list_box.GetSelection()],
                             self.source_port_picker.GetPath(),
                             params=self.additional_params_control.GetLineText(0))

    def profiles_list_box_select(self, event: wx.Event) -> None:
        """
        New profile is selected in the list box
        Post a selected profile event if successful

        :param event: wx.EVT_LISTBOX
        :return: None
        """
        if self.last_selected_profile_index >= 0:
            active_profile = self.main_frame.selections_panel.my_profile
            last_profile = self.main_frame.profiles.profiles[self.last_selected_profile_index]
            discard_changes = self.discard_unsaved_changes(active_profile, last_profile)
            if not discard_changes:
                event.GetEventObject().SetSelection(self.last_selected_profile_index)
                return None

        # TODO: there is probably some weirdness going on in here when deleteing the last profile
        new_profile = self.main_frame.profiles.profiles[event.GetEventObject().GetSelection()]
        self.last_selected_profile_index = event.GetEventObject().GetSelection()
        mylog.info(f"New profile selected: {new_profile.name}")
        wx.PostEvent(self.main_frame, gui.events.SelectedProfile())

    def source_port_changed(self, event: wx.Event) -> None:
        """
        Record the source port path if it changed
        Post a config changed event if successful

        :param event: not used
        :return: None
        """
        if self.config['source_port']['binary'] != self.source_port_picker.GetPath():
            mylog.info(f"Source port changed to: {self.source_port_picker.GetPath()}")
            self.config['source_port']['binary'] = self.source_port_picker.GetPath()
            wx.PostEvent(self.main_frame, gui.events.ConfigChanged())

    def auto_close_changed(self, event: wx.Event) -> None:
        """
        Record the auto close on launch option if it changed
        Post a config changed event if successful

        :param event: not used
        :return: None
        """
        if self.config['service']['auto_close_on_launch'] != self.launch_auto_close.GetValue():
            mylog.info(f"Auto close on launch changed to: {self.launch_auto_close.GetValue()}")
            self.config['service']['auto_close_on_launch'] = self.launch_auto_close.GetValue()
            wx.PostEvent(self.main_frame, gui.events.ConfigChanged())

    def config_changed(self, event: wx.Event) -> None:
        """
        Record the changed config to YAML file

        :param event: not used
        :return: None
        """
        self.main_frame.config = self.config

        with open('config.yaml', 'w') as config_yaml:
            mylog.info(f"Config changed write to config.yaml")
            yaml.dump(self.config, config_yaml)

    def discard_unsaved_changes(self, active_profile: Profile, last_profile: Profile) -> bool:
        """
        Check for unsaved changes and launch a modal for discard or cancel

        :param active_profile: Current profile
        :param last_profile: Last profile
        :return: None
        """

        if active_profile.asdict() != last_profile.asdict():
            mylog.info(f"Active profile {active_profile.name} has unsaved changes!")
            discard_changes_dialog = wx.MessageDialog(self,
                                                   f'Profile "{active_profile.name}" has unsaved changes',
                                                   'Unsaved changes',
                                                   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            discard_changes_dialog.SetYesNoLabels('Discard changes', 'Cancel')
            discard_changes = discard_changes_dialog.ShowModal()

            if discard_changes == wx.ID_YES:
                # discard changes
                mylog.info(f"Discard the changes and continue")
                return True
            else:
                # cancel the action
                mylog.info(f"Cancel the action")
                return False
        else:
            mylog.info(f"Profiles match")
            return True

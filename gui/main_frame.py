import wx
import wx.grid
import yaml
from logbook import Logger

import gui.events
from gui.controls_panel import ControlsPanel
from gui.selections_panel import SelectionsPanel
from service.models import Profiles


mylog = Logger(__name__)


class MainFrame(wx.Frame):
    __instance = None

    @classmethod
    def get_instance(cls):
        return cls.__instance  # TODO: if None?

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        MainFrame.__instance = self  # cursed

        # TODO: manage config in here from now on
        with open('config.yaml', 'rt') as config_yaml:
            self.config = yaml.safe_load(config_yaml.read())

        self.profiles = Profiles('profiles').load()
        self.selected_profile = None  # TODO: what about a default profile?

        # main panel
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # controls panel
        self.controls_panel = ControlsPanel(self)

        # selections panel
        self.selections_panel = SelectionsPanel(self)

        # main panel cont.
        self.main_sizer.Add(self.controls_panel, 1, wx.EXPAND)
        self.main_sizer.Add(self.selections_panel, 1, wx.EXPAND)
        self.SetSizer(self.main_sizer)

        # bindings
        self.Bind(gui.events.CHANGED_PROFILES, self.on_profiles_changed)

        # display
        self.SetMinSize(wx.Size(self.config['gui']['size_x'], self.config['gui']['size_y']))
        self.Show()

    def on_profiles_changed(self, event: wx.Event) -> None:
        mylog.info(f"Profiles changed, reload")
        self.profiles.load()
        wx.PostEvent(self, gui.events.ProfilesUpdated())
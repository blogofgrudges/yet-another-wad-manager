import wx
import wx.grid
from logbook import Logger

import gui.events
from gui.controls_panel import ControlsPanel
from gui.selections_panel import SelectionsPanel
from service.models import Profiles


mylog = Logger(__name__)


class MainFrame(wx.Frame):
    """
    Main frame class to contain the panels
    """
    __instance = None

    @classmethod
    def get_instance(cls) -> type:
        """
        Get a sepcific instance of this class

        :return: TBC
        """
        return cls.__instance

    def __init__(self, *args, **kwargs) -> None:
        """
        Create the main frame

        :param args: TBC
        :param kwargs: title, config
        """
        wx.Frame.__init__(self, *args, title=kwargs['title'])
        MainFrame.__instance = self  # cursed
        self.title = kwargs['title']
        self.config = kwargs['config']
        self.SetIcon(wx.Icon(self.config['gui']['icon']))

        # load the profiles
        self.profiles = Profiles('profiles').load()

        # main panel
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # controls panel
        self.controls_panel = ControlsPanel(self, **kwargs)

        # selections panel
        self.selections_panel = SelectionsPanel(self, **kwargs)

        # main panel cont.
        self.main_sizer.Add(self.controls_panel, 1, wx.EXPAND)
        self.main_sizer.Add(self.selections_panel, 1, wx.EXPAND)
        self.SetSizer(self.main_sizer)

        # bindings
        self.Bind(gui.events.CHANGED_PROFILES, self.profiles_changed)

        # force the window to a fixed size specified in the config
        self.SetMinSize(wx.Size(self.config['gui']['size_x'], self.config['gui']['size_y']))
        self.SetMaxSize(wx.Size(self.config['gui']['size_x'], self.config['gui']['size_y']))

        # display
        self.Show()

    def profiles_changed(self, event: wx.Event) -> None:
        """
        Reload profiles from profiles source, posts a profile updated event

        :param event: not used
        :return: None
        """
        mylog.info(f"Profiles changed, reload")
        self.profiles.load()
        wx.PostEvent(self, gui.events.ProfilesUpdated())

import wx
from logbook import Logger

import gui.events


mylog = Logger(__name__)


class WADGridContextMenu(wx.Menu):
    """
    WAD Grid context menu class
    """
    def __init__(self, parent, row):
        """
        Create a WAD grid context menu

        :param parent: SelectionsPAnel
        :param row: Row that spawned the context menu
        """
        wx.Menu.__init__(self)
        self.selections_panel = parent
        self.selected_row = row

        self.delete_option = wx.MenuItem(self, wx.NewId(), 'Delete WAD')
        self.Append(self.delete_option)

        self.Bind(wx.EVT_MENU, self.delete_wad, self.delete_option)
        mylog.info(f"Opened WAD grid context menu for row: {self.selected_row}")

    def delete_wad(self, event: wx.Event) -> None:
        # TODO: Merge this with delete_wads in SelectionsPanel
        """
        Delete the WAD that spawned the context menu
        Post a WADs updated event if successful

        :param event: not used
        :return: None
        """
        old_wads = self.selections_panel.my_profile.wads
        deleted_wads = []
        new_wads = []
        for i, wad in enumerate(old_wads):
            if i != self.selected_row:
                new_wads.append(wad)
            else:
                deleted_wads.append(wad)

        if new_wads != old_wads:
            mylog.info(f"Deleted WAD: {deleted_wads}")
            self.selections_panel.my_profile.wads = new_wads
            wx.PostEvent(self.selections_panel.main_frame, gui.events.WADsUpdated())

import copy
import os.path

import wx
import wx.grid
from logbook import Logger

import gui.events
from gui.context_menus import WADGridContextMenu


mylog = Logger(__name__)


class SelectionsPanel(wx.Panel):
    """
    Selections panel class (the right hand side of the window)
    """
    def __init__(self, parent, **kwargs) -> None:
        """
        Create a selections panel

        :param parent: MainFrame
        """
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)
        self.main_frame = parent.get_instance()

        self.config = kwargs['config']

        # safe version of the profile to work with
        self.my_profile = copy.deepcopy(self.main_frame.selected_profile)

        # sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Launch profile")

        # profile options
        self.profile_options_sizer = wx.BoxSizer(wx.VERTICAL)
        self.profile_params_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.profile_params_control = wx.TextCtrl(self)
        self.profile_params_label = wx.StaticText(self, -1, 'Launch opts')
        self.profile_params_sizer.Add(self.profile_params_label, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 5)
        self.profile_params_sizer.Add(self.profile_params_control, 1, wx.ALL, 5)

        self.profile_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.profile_name_control = wx.TextCtrl(self)
        self.profile_name_label = wx.StaticText(self, -1, 'Profile name')
        self.profile_name_sizer.Add(self.profile_name_label, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 5)
        self.profile_name_sizer.Add(self.profile_name_control, 1, wx.ALL, 5)

        self.profile_options_sizer.Add(self.profile_params_sizer, 0, wx.EXPAND)
        self.profile_options_sizer.Add(self.profile_name_sizer, 0, wx.EXPAND)

        # WAD list
        self.wad_grid_max_displayed_rows = 9
        self.wad_grid = wx.grid.Grid(self, style=wx.VSCROLL)
        self.wad_grid.CreateGrid(1, 0)
        self.wad_grid.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.wad_grid.EnableDragRowMove(True)
        self.wad_grid.SetSelectionMode(wx.grid.Grid.GridSelectRows)
        self.wad_grid.DisableDragGridSize()
        self.wad_grid.DisableDragRowSize()

        self.column_labels = ['WAD Name']
        for i, column_label in enumerate(self.column_labels):
            self.wad_grid.AppendCols(1)
            self.wad_grid.SetColLabelValue(i, column_label)
        if self.wad_grid.GetNumberRows() < self.wad_grid_max_displayed_rows:
            self.wad_grid.AppendRows(self.wad_grid_max_displayed_rows - self.wad_grid.GetNumberRows())

        self.wad_grid_sizer = wx.BoxSizer(wx.VERTICAL)
        self.wad_grid_sizer.Add(self.wad_grid, 1, wx.EXPAND)

        # buttons
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_profile_button = wx.Button(self, wx.ID_ANY, 'Save profile')
        self.wad_picker_button = wx.Button(self, wx.ID_ANY, 'Add WADs')
        self.wad_delete_button = wx.Button(self, wx.ID_ANY, 'Delete WADs')

        self.button_sizer.Add(self.save_profile_button, 0, wx.RIGHT, 5)
        self.button_sizer.Add(self.wad_picker_button, 0, wx.LEFT | wx.RIGHT, 5)
        self.button_sizer.Add(self.wad_delete_button, 0, wx.LEFT, 5)

        self.panel_sizer.Add(self.profile_options_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.panel_sizer.Add(self.wad_grid_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.panel_sizer.Add(self.button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # bindings
        self.Bind(wx.EVT_BUTTON, self.save_profile, self.save_profile_button)
        self.Bind(wx.EVT_BUTTON, self.wad_picker, self.wad_picker_button)
        self.Bind(wx.EVT_BUTTON, self.delete_wads, self.wad_delete_button)
        self.Bind(wx.EVT_SIZE, self.size_grid)
        self.Bind(wx.grid.EVT_GRID_ROW_MOVE, self.row_moved, self.wad_grid)
        self.Bind(wx.EVT_TEXT, self.launch_opts_changed, self.profile_params_control)
        self.Bind(wx.EVT_TEXT, self.profile_name_changed, self.profile_name_control)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.wad_selected, self.wad_grid)
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.wad_selected, self.wad_grid)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.wad_right_click, self.wad_grid)

        self.main_frame.Bind(gui.events.SELECTED_PROFILE, self.new_profile_selected)
        self.main_frame.Bind(gui.events.UPDATED_WADS, self.refresh_wad_grid)

        # display
        self.main_sizer.Add(self.panel_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.main_sizer)
        self.Show()

    def wad_right_click(self, event: wx.Event) -> None:
        """
        Spawna context menu when right clicking on a cell

        :param event: EVT_GRID_CELL_RIGHT_CLICK
        :return: None
        """
        self.wad_grid.GetPopupMenuSelectionFromUser(WADGridContextMenu(self, event.GetRow()), event.GetPosition())

    def delete_wads(self, event: wx.Event) -> None:
        """
        Delete the currently selected WADs
        Post a WADs updated event if successful

        :param event: not used
        :return: None
        """
        old_wads = self.my_profile.wads
        deleted_wads = []
        new_wads = []
        for i, wad in enumerate(old_wads):
            if i not in self.wad_grid.GetSelectedRows():
                new_wads.append(wad)
            else:
                deleted_wads.append(wad)

        if new_wads != old_wads:
            mylog.info(f"Deleted WADs: {deleted_wads}")
            self.my_profile.wads = new_wads
            wx.PostEvent(self.main_frame, gui.events.WADsUpdated())

    def wad_selected(self, event: wx.Event) -> None:
        """
        Constrain the selected WADs to the size of the WADs list

        :param event: not used
        :return: None
        """
        selected_rows = self.wad_grid.GetSelectedRows()
        wads_list_size = len(self.my_profile.wads)
        for row in selected_rows:
            if row >= wads_list_size:
                self.wad_grid.DeselectRow(row)
        mylog.info(f"Selected WADs: {[self.my_profile.wads[x] for x in self.wad_grid.GetSelectedRows()]}")
        event.Skip()

    def launch_opts_changed(self, event: wx.Event) -> None:
        """
        Record the launch opts if they have changed

        :param event: not used
        :return: None
        """
        self.my_profile.launch_opts = self.profile_params_control.GetValue()

    def profile_name_changed(self, event: wx.Event) -> None:
        """
        Record the profile name if it has changed

        :param event: not used
        :return: None
        """
        self.my_profile.name = self.profile_name_control.GetValue()

    def wad_picker(self, event: wx.Event) -> None:
        """
        Launch a file picker dialog for selecting WADs to add to the profile
        Post a WADs updated event if successful

        :param event: not used
        :return: None
        """
        mylog.info("Launch WAD picker dialog")
        wad_picker = wx.FileDialog(self,
                                   style=wx.FD_OPEN | wx.FD_MULTIPLE,
                                   defaultDir=self.config['source_port']['wads_folder'],
                                   message="Select WADs",
                                   wildcard="WAD and PK3 files (*.WAD, *.PK3)|*.WAD;*.PK3| All files (*.*)|*.*")

        if wad_picker.ShowModal() == wx.ID_OK:
            """
            wx.FileDialog().GetFilenames() appears to return the file path, rather than just the filname so keep using
            wx.FileDialog().GetPaths() and left trimming the directory for now until I can figure out why
            might be an issue in wxPython
            """
            wads = [wad.split(os.path.sep)[-1] for wad in wad_picker.GetPaths()]
            self.my_profile.wads.extend(wads)
            mylog.info(f"WADs added: {wads}")

            wx.PostEvent(self.main_frame, gui.events.WADsUpdated())

    def save_profile(self, event: wx.Event) -> None:
        """
        Try to save a profile to file, posts a profiles changed event if successful

        :param event: not used
        :return: None
        """
        if self.my_profile.asdict() != self.main_frame.selected_profile.asdict():
            mylog.info(f"Profiles have diverged, write new profile to {self.main_frame.selected_profile.filename}")
            self.my_profile.to_yaml(self.main_frame.selected_profile.filename)  # TODO: what if there isnt a filename?
            wx.PostEvent(self.main_frame, gui.events.ProfilesChanged())  # force a refresh

    def new_profile_selected(self, event: wx.Event) -> None:
        """
        Change the selected profile, post a WADs updated event

        :param event: not used
        :return: None
        """
        new_profile = self.main_frame.selected_profile
        self.my_profile = copy.deepcopy(new_profile)

        mylog.info(f"Reloading WADS and opts from new profile {new_profile.name}")

        self.profile_params_control.SetValue(self.my_profile.launch_opts)
        self.profile_name_control.SetValue(self.my_profile.name)

        wx.PostEvent(self.main_frame, gui.events.WADsUpdated())

    def size_grid(self, event: wx.Event) -> None:
        """
        Size the WAD grid to fit the window correctly
        The YAWM window is fixed size now so this should only ever get called at launch now

        :param event: wx.EVT_SIZE
        :return: None
        """
        row_label_size = 40  # this fits labels up to 999 WADs, that ought to be enough for anyone
        row_size = 20
        col_label_size = 30
        min_column_size = 100
        scroll_rate = 20  # must be equal to row size to stop rows being cut off
        panel_size = self.GetSize()

        column_size = panel_size.GetWidth() - row_label_size - wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
        if column_size < min_column_size:
            column_size = min_column_size  # just in case of weirdness

        self.wad_grid.SetColLabelSize(col_label_size)
        self.wad_grid.SetDefaultRowSize(row_size, row_size)
        self.wad_grid.SetScrollRate(scroll_rate, scroll_rate)
        max_height = self.wad_grid.GetColLabelSize() + self.wad_grid.GetRowSize(0) * self.wad_grid_max_displayed_rows

        self.wad_grid.SetRowLabelSize(row_label_size)
        self.wad_grid.SetColSize(0, column_size)
        self.wad_grid.SetMinSize(wx.Size(-1, max_height))
        self.wad_grid.SetMaxSize(wx.Size(-1, max_height))
        event.Skip()

    def row_moved(self, event: wx.Event) -> None:
        """
        Row in the WAD grid has been moved, post a call after event

        :param event: wx.grid.EVT_GRID_ROW_MOVE
        :return: None
        """
        event.Skip()
        index_moved_row = event.Col  # spooky wxpython bug ??
        wx.CallAfter(self.get_row_pos, index_moved_row)

    def get_row_pos(self, row) -> None:
        """
        Determine where a row in the grid has been moved to and update the WADs list with the new position
        WAD indicies are constrained to the size of the wads list
        Post a WADs updated event

        :param row: previous position of WAD in the WADs list
        :return: None
        """
        from_index = row
        to_index = self.wad_grid.GetRowPos(row)
        wads_list_size = len(self.my_profile.wads)
        if from_index < wads_list_size:  # make sure a filler row is not selected
            if to_index >= wads_list_size:  # in case target position is a filler row
                to_index = wads_list_size - 1  # constrain target position to wads list

            self.my_profile.wads.insert(to_index, self.my_profile.wads.pop(from_index))
            mylog.info(f"Moved WAD: {self.my_profile.wads[to_index]} from position: {from_index} "
                       f"to position: {self.wad_grid.GetRowPos(row)} new WAD list: {self.my_profile.wads}")

        wx.PostEvent(self.main_frame, gui.events.WADsUpdated())

    def refresh_wad_grid(self, event: wx.Event) -> None:
        """
        Refresh the WADs grid

        :param event: not used
        :return: None
        """
        mylog.info("Refresh the WAD grid")
        self.wad_grid.ClearGrid()
        self.wad_grid.DeleteRows(0, self.wad_grid.GetNumberRows())
        for row, wad in enumerate(self.my_profile.wads):
            self.wad_grid.AppendRows(1)
            self.wad_grid.SetCellValue(row, 0, wad)
        filler = self.wad_grid_max_displayed_rows - self.wad_grid.GetNumberRows()
        if filler > 0:
            self.wad_grid.AppendRows(filler)
        for row in range(0, self.wad_grid.GetNumberRows()):
            self.wad_grid.SetReadOnly(row, 0)

        mylog.info(f"WADs: {len(self.my_profile.wads)} Filler: {filler}")
        self.Layout()  # refresh

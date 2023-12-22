import copy
import wx
import wx.grid
import yaml

from logbook import Logger

import gui.events


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
        self.wad_grid.SetSelectionMode(wx.grid.Grid.GridSelectNone)
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

        self.button_sizer.Add(self.save_profile_button, 0, wx.RIGHT, 5)
        self.button_sizer.Add(self.wad_picker_button, 0, wx.LEFT, 5)

        self.panel_sizer.Add(self.profile_options_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.panel_sizer.Add(self.wad_grid_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.panel_sizer.Add(self.button_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # bindings
        self.Bind(wx.EVT_BUTTON, self.save_profile, self.save_profile_button)
        self.Bind(wx.EVT_BUTTON, self.wad_picker, self.wad_picker_button)
        self.Bind(wx.EVT_SIZE, self.size_grid)
        self.Bind(wx.grid.EVT_GRID_ROW_MOVE, self.row_moved, self.wad_grid)
        self.Bind(wx.EVT_TEXT, self.launch_opts_changed, self.profile_params_control)
        self.Bind(wx.EVT_TEXT, self.profile_name_changed, self.profile_name_control)

        self.main_frame.Bind(gui.events.SELECTED_PROFILE, self.new_profile_selected)
        self.main_frame.Bind(gui.events.UPDATED_WADS, self.refresh_wad_grid)

        # display
        self.main_sizer.Add(self.panel_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.main_sizer)
        self.Show()

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
        Launch a file picker dialog for selecting WADs to add to the profile, post a WADs updated event

        :param event: not used
        :return: None
        """
        mylog.info("Launch WAD picker dialog")
        wad_picker = wx.FileDialog(self,  # TODO: default file types?
                                   style=wx.FD_OPEN | wx.FD_MULTIPLE,
                                   defaultDir=self.config['source_port']['wads_folder'],
                                   message="Select WADs")
        if wad_picker.ShowModal() == wx.ID_OK:
            wad_paths = wad_picker.GetPaths()
            mylog.info(f"WADs picked: {wad_paths}")
            for wad in reversed(wad_paths):
                # TODO: this is causing me physical discomfort
                if wad.startswith(self.config['source_port']['wads_folder']):
                    chars = len(self.config['source_port']['wads_folder'])
                    self.my_profile.wads.append(wad[chars+1:])

        wx.PostEvent(self.main_frame, gui.events.WADsUpdated())

    def save_profile(self, event: wx.Event) -> None:
        """
        Try to save a profile to file, posts a profiles changed event if successful

        :param event: not used
        :return: None
        """
        should_save = False
        if self.my_profile.name != self.main_frame.selected_profile.name:
            should_save = True
        if self.my_profile.wads != self.main_frame.selected_profile.wads:
            should_save = True
        if self.my_profile.launch_opts != self.main_frame.selected_profile.launch_opts:
            should_save = True

        if should_save is True:
            mylog.info(f"Name/WADs/launch opts diff, write new profile to {self.main_frame.selected_profile.filename}")
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

        :param event: wx.EVT_SIZE
        :return: None
        """
        r_label_size = 40  # TODO: what if its a really big number?
        panel_size = self.GetSize()
        # TODO: wtf is 19 ??
        column_size = panel_size.GetWidth() - r_label_size - wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
        if column_size < 100:
            column_size = 100  # just in case of weirdness

        self.wad_grid.SetColLabelSize(30)
        self.wad_grid.SetDefaultRowSize(20, 20)
        self.wad_grid.SetScrollRate(20, 20)
        max_height = self.wad_grid.GetColLabelSize() + self.wad_grid.GetRowSize(0) * self.wad_grid_max_displayed_rows

        self.wad_grid.SetRowLabelSize(r_label_size)
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
        Post a WADs updated event

        :param row: previous position of WAD in the WADs list
        :return: None
        """
        from_index = row
        if from_index >= len(self.my_profile.wads):  # in case a filler row is moved
            wx.PostEvent(self.main_frame, gui.events.WADsUpdated())  # refresh the grid
            return None  # TODO: don't like the look of this
        to_index = self.wad_grid.GetRowPos(row)
        if to_index >= len(self.my_profile.wads):  # in case moved to a filler row
            to_index = len(self.my_profile.wads) - 1  # just in case

        self.my_profile.wads.insert(to_index, self.my_profile.wads.pop(from_index))
        mylog.info(f"Moved WAD: {self.my_profile.wads[to_index]} from position: {from_index} to position: {self.wad_grid.GetRowPos(row)} new WAD list: {self.my_profile.wads}")

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
            self.wad_grid.SetReadOnly(row, 0)
        filler = self.wad_grid_max_displayed_rows - self.wad_grid.GetNumberRows()
        if filler > 0:
            self.wad_grid.AppendRows(filler)

        mylog.info(f"WADs: {len(self.my_profile.wads)} Filler: {filler}")
        self.Layout()  # refresh

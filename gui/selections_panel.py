import copy
import wx
import wx.grid
import yaml

from logbook import Logger

import gui.events
from service.models import Profile, Profiles


mylog = Logger(__name__)


class SelectionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)
        self.main_frame = parent.get_instance()

        with open('config.yaml', 'rt') as config_yaml:
            self.config = yaml.safe_load(config_yaml.read())

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
        self.Bind(wx.EVT_BUTTON, self.on_save_profile, self.save_profile_button)
        self.Bind(wx.EVT_BUTTON, self.on_wad_picker, self.wad_picker_button)
        self.main_frame.Bind(gui.events.SELECTED_PROFILE, self.on_new_profile_selected)
        self.Bind(wx.EVT_SIZE, self.size_grid)
        self.Bind(wx.grid.EVT_GRID_ROW_MOVE, self.on_row_moved, self.wad_grid)

        # display
        self.main_sizer.Add(self.panel_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.main_sizer)
        self.Show()

    def on_wad_picker(self, event: wx.Event) -> None:
        wad_picker = wx.FileDialog(self,  # TODO: default file types?
                                   style=wx.FD_OPEN | wx.FD_MULTIPLE,
                                   defaultDir=self.config['source_port']['wads_folder'],
                                   message="Select WADs")
        if wad_picker.ShowModal() == wx.ID_OK:
            wad_paths = wad_picker.GetPaths()
            for wad in reversed(wad_paths):
                # TODO: this is causing me physical discomfort
                if wad.startswith(self.config['source_port']['wads_folder']):
                    chars = len(self.config['source_port']['wads_folder'])
                    self.my_profile.wads.append(wad[chars+1:])

        self.wad_grid.ClearGrid()
        self.wad_grid.DeleteRows(0, self.wad_grid.GetNumberRows() - 1)
        for row, wad in enumerate(self.my_profile.wads):
            self.wad_grid.AppendRows(1)
            self.wad_grid.SetCellValue(row, 0, wad)
            self.wad_grid.SetReadOnly(row, 0)
        if self.wad_grid.GetNumberRows() < self.wad_grid_max_displayed_rows:
            self.wad_grid.AppendRows(self.wad_grid_max_displayed_rows - self.wad_grid.GetNumberRows())
        self.Layout()  # refresh

    def on_save_profile(self, event: wx.Event) -> None:
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

    def on_new_profile_selected(self, event: wx.Event) -> None:
        mylog.info(f"Reload WADS and opts from new profile")
        new_profile = self.main_frame.selected_profile
        self.my_profile = copy.deepcopy(new_profile)

        self.profile_params_control.SetValue(self.my_profile.launch_opts)
        self.profile_name_control.SetValue(self.my_profile.name)

        self.wad_grid.ClearGrid()
        self.wad_grid.DeleteRows(0, self.wad_grid.GetNumberRows() - 1)
        for row, wad in enumerate(new_profile.wads):
            self.wad_grid.AppendRows(1)
            self.wad_grid.SetCellValue(row, 0, wad)
            self.wad_grid.SetReadOnly(row, 0)
        if self.wad_grid.GetNumberRows() < self.wad_grid_max_displayed_rows:
            self.wad_grid.AppendRows(self.wad_grid_max_displayed_rows - self.wad_grid.GetNumberRows())
        self.Layout()  # refresh

    def size_grid(self, event: wx.Event) -> None:
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

    def on_row_moved(self, event: wx.Event) -> None:
        event.Skip()
        index_moved_row = event.Col  # spooky wxpython bug ??
        wx.CallAfter(self.get_row_pos, index_moved_row)

    def get_row_pos(self, row) -> None:
        from_index = row
        to_index = self.wad_grid.GetRowPos(row)
        if to_index > len(self.my_profile.wads):
            to_index = len(self.my_profile.wads)  # just in case

        self.my_profile.wads.insert(to_index, self.my_profile.wads.pop(from_index))
        mylog.info(f"Moved WAD: {self.my_profile.wads[row]} to position {self.wad_grid.GetRowPos(row)} new WADS={self.my_profile.wads}")

        # TODO: This should really be an event
        self.wad_grid.ClearGrid()
        self.wad_grid.DeleteRows(0, self.wad_grid.GetNumberRows() - 1)
        for row, wad in enumerate(self.my_profile.wads):
            self.wad_grid.AppendRows(1)
            self.wad_grid.SetCellValue(row, 0, wad)
            self.wad_grid.SetReadOnly(row, 0)
        if self.wad_grid.GetNumberRows() < self.wad_grid_max_displayed_rows:
            self.wad_grid.AppendRows(self.wad_grid_max_displayed_rows - self.wad_grid.GetNumberRows())
        self.Layout()  # refresh

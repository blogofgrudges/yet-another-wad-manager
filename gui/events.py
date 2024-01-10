import wx.lib.newevent


SelectedProfile, SELECTED_PROFILE = wx.lib.newevent.NewEvent()
ProfilesChanged, CHANGED_PROFILES = wx.lib.newevent.NewEvent()
ProfilesUpdated, UPDATED_PROFILES = wx.lib.newevent.NewEvent()
WADsUpdated, UPDATED_WADS = wx.lib.newevent.NewEvent()
ConfigChanged, CHANGED_CONFIG = wx.lib.newevent.NewEvent()

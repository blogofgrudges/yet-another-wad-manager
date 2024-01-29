import wx.lib.newevent


SelectedProfile, SELECTED_PROFILE = wx.lib.newevent.NewEvent()
ProfilesChanged, PROFILES_CHANGED = wx.lib.newevent.NewEvent()
ProfilesUpdated, PROFILES_UPDATED = wx.lib.newevent.NewEvent()
WADsUpdated, WADS_UPDATED = wx.lib.newevent.NewEvent()
ConfigChanged, CONFIG_CHANGED = wx.lib.newevent.NewEvent()

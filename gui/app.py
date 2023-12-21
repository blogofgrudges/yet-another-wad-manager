import wx


class WADManagerApp(wx.App):
    def __init__(self):
        super(WADManagerApp, self).__init__()
        self.appName = "Yet Another WAD Manager (YAWM)"

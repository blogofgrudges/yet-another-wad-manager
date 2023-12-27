import wx


class WADManagerApp(wx.App):
    """
    WAD Manager App Class
    """
    def __init__(self) -> None:
        """
        Create the WAD manager app
        """
        super(WADManagerApp, self).__init__()
        self.appName = "Yet Another WAD Manager (YAWM)"

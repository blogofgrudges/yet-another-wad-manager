# YAWM - Yet another (DOOM) WAD manager

Another manager, organizer and launcher for DOOM WADs.

![This is what it looks like!](https://github.com/blogofgrudges/yet-another-wad-manager/blob/main/github_splash.png?raw=true)

## Profiles

A profile is just a collection of WADs. WADs, pk3s, Paks, etc are loaded in the order specified in the profile. Additional launch options can be specified as `launch_opts` and will be passed directly to the binary.
```yaml
name: My WAD pack
launch_opts: -skill 4
wads:
  - my-wad.pk3
  - another-wad.wad
  - ...
```
The profile name is only used to display in the profiles list panel. A profile can contain as many WADs as you want. Put profiles into the `profiles` folder in the project root directory.

## Launch options

Launch options are usually passed into the binary like:

```commandline
gzdoom.exe -skill 4 -warp 7
```

YAWM supports two kinds of launch options: profile options and runtime options.

* Profile options are saved in the profile and will be passed into the executable whenever the profile is selected
* Runtime options are also passed into the executable but they are not saved to a profile and will be lost when the application is closed

If you like to always play a WAD on UV difficulty then you should set `-skill 4` in the profile options. If you want to play starting at map 07 this time, but not always, then set `-warp 7` in the runtime options.

Runtime options are passed into the executable last, so if the same option is specified in both profile and runtime options then the runtime value will take priority.

## Configuration

In `config.yaml` specify the locations of the source port executable and the directory containing the downloaded WADs. The `wads_folder` value will be prepended to the name of selected WADs before being passed into the executable, if the WAD is not present in this directory it will fail to load.

```yaml
source_port:
  binary: F:\GZDoom\gzdoom.exe
  wads_folder: F:\GZDoom\WADs
```

The source port path can be changed at any time through the appliation window.

## Dependencies

* PyYAML==6.0.1
* Logbook==1.7.0.post0
* wxPython==4.2.1

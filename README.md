# YAWM - Yet another (DOOM) WAD manager

Another manager, organizer and launcher for DOOM WADs. 

## Profiles

A profile is just a collection of WADs. WADs, pk3s, Paks, etc are loaded in the order specified in the profile. Additional launch options can be specified as `launch_opts` and will be passed directly to the binary.
```yaml
launch_opts: '-skill 4'
wads:
  - my-wad.pk3
  - another-wad.wad
  - ...
```
Put profiles into the `profiles` folder in the project root directory.

## Launching the application

In `config.yaml` specify the locations of the source port executable and the directory containing the downloaded WADs.

```yaml
app:
  profiles_folder: 'profiles'

source_port:
  installed_drive: 'F:'
  binary: 'GZDoom\gzdoom.exe'
  wads_folder: 'GZDoom\WADs'
```

To run in a terminal:
```commandline
python main.py -p my-profile-0.yaml
```

Additional launch options can be specified as `-c [OPTIONS]` like:
```commandline
python main.py -p my-profile-0.yaml -c '-warp 7'
```

## Dependencies

* PyYAML==6.0.1

import io
import json
import sys
import os
from ruamel.yaml import YAML  # use ruamel.yaml to preserve comments in config


def get_conf_path():
    # Determine system
    # When we are in some Java world do extra checks
    if sys.platform.startswith('java'):
        import platform
        os_name = platform.java_ver()[3][0]
        system = 'win32' if os_name.startswith('Windows') else 'linux2'
    else:
        system = sys.platform

    if system == 'win32':
        # In windows alacritty config can only exist in one place
        alacritty_path = os.path.expandvars(r'%APPDATA%\alacritty\alacritty.yml')
        if os.path.exists(alacritty_path):
            return alacritty_path
    else:
        # If it is not win32 it can exists in only a few other places
        xdg_config_home = os.getenv('XDG_CONFIG_HOME')
        if xdg_config_home is not None and os.path.exists(
            f'{xdg_config_home}/alacritty/alacritty.yml'
        ):
            return f"{xdg_config_home}/alacritty/alacritty.yml"
        if xdg_config_home is not None and os.path.exists(
            f"{xdg_config_home}/alacritty.yml"
        ):
            return f"{xdg_config_home}/alacritty.yml"

        home = os.getenv('HOME')
        if home is not None and os.path.exists(
            f'{home}/.config/alacritty/alacritty.yml'
        ):
            return f"{home}/.config/alacritty/alacritty.yml"
        if home is not None and os.path.exists(
            f'{home}/.config/alacritty.yml'
        ):
            return f"{home}/.config/alacritty.yml"
        if home is not None and os.path.exists(f'{home}alacritty.yml'):
            return f"{home}/alacritty.yml"

    print("Could not find alacritty config file\nPlease make sure you have a file in one of the paths specified on\nhttps://github.com/alacritty/alacritty#configuration")
    sys.exit(1)
# end


conf_path = get_conf_path()
yaml = YAML()

# Read & parse alacritty config
with open(conf_path, 'r') as stream:
    data_loaded = yaml.load(stream)

# parse new colors
js = json.loads(sys.argv[1])

# Update yaml file
try:
    # Use update to not remove existing comments
    data_loaded['colors']['primary'].update(js['colors']['primary'])
    data_loaded['colors']['normal'].update(js['colors']['normal'])
    data_loaded['colors']['bright'].update(js['colors']['bright'])
except KeyError:
    print("Could not find existing 'colors' settings in your alacritty.yml file\nplease make sure to uncomment\n'colors', as well as 'primary', 'normal' and 'bright'")
    print("Check the example config at\nhttps://github.com/alacritty/alacritty/blob/master/alacritty.yml for more information")
    sys.exit(1)

# make sure the user is okay with having their config changed
answer = input("This script will update your alacritty config at: \n" +
               conf_path + "\nIt is reccomended to make a copy of this file before proceeding.\nAre you sure you want to continue? (Y/N)\n")
if answer.lower() not in ['y', 'yes']:
    print("Aborted")
    sys.exit(1)

# Write alacritty config
with io.open(conf_path, 'w', encoding='utf8') as outfile:
    yaml.dump(data_loaded, outfile)

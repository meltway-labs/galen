import os

import appdirs
import toml

CONFIG_FOLDER_NAME = "galen"
CONFIG_FILE_NAME = "config.toml"


def warning(msg):
    click.secho(msg, fg="yellow", err=True)


def error(msg):
    click.secho(msg, fg="red", err=True)


def handler(signum, frame):
    sys.exit(0)


def create_empty_config():
    config_dir = appdirs.user_config_dir(CONFIG_FOLDER_NAME)
    # create empty config dir
    os.makedirs(config_dir)

    default_config = {"default_profile": "", "profiles": {}}

    # create empty config file
    with open(os.path.join(config_dir, CONFIG_FILE_NAME), "w") as f:
        toml.dump(default_config, f)
        pass


def read_config():
    config_dir = appdirs.user_config_dir(CONFIG_FOLDER_NAME)
    # read toml config from file
    with open(os.path.join(config_dir, CONFIG_FILE_NAME), "r") as f:
        config = toml.loads(f.read())

    return config


def write_config(config):
    config_dir = appdirs.user_config_dir(CONFIG_FOLDER_NAME)
    # create empty config file
    with open(os.path.join(config_dir, CONFIG_FILE_NAME), "w") as f:
        toml.dump(config, f)


def get_config():
    config_dir = appdirs.user_config_dir(CONFIG_FOLDER_NAME)
    if not os.path.exists(config_dir):
        create_empty_config()

    return read_config()

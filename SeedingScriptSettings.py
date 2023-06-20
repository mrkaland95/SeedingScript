import configparser
import enum
import json
import logging
import os
import shutil
from enum import StrEnum, auto
from collections import OrderedDict
from pathlib import Path

VALUE_KEY = 'value'
DESCRIPTION_KEY = 'description'

# Path globals
__VERSION__ = "3.0.4"
LOCAL_APPDATA = os.environ.get('LOCALAPPDATA')
SCRIPT_CONFIG_SETTINGS_FOLDER = Path(LOCAL_APPDATA) / 'SeedingScript'
SCRIPT_CONFIG_SETTINGS_FILE = Path(SCRIPT_CONFIG_SETTINGS_FOLDER) / 'seedingconfig.json'
GAME_CONFIG_PATH = Path(LOCAL_APPDATA) / 'SquadGame/Saved/Config/WindowsNoEditor'
ICONS_FOLDER_NAME = 'icons'
ICONS_PATH_PERMANENT = Path(SCRIPT_CONFIG_SETTINGS_FOLDER) / ICONS_FOLDER_NAME
ICONS_PATH_LOCAL = Path(os.path.dirname(os.path.realpath(__file__))) / ICONS_FOLDER_NAME

programfiles_32 = os.environ.get("ProgramFiles(x86)")
programfiles_64 = os.environ.get('ProgramW6432')
game_config_path = os.path.abspath(f"{LOCAL_APPDATA}/SquadGame/Saved/Config/WindowsNoEditor")
game_launcher_path_32 = f'{programfiles_32}/Steam/steamapps/common/Squad/squad_launcher.exe'
game_launcher_path_64 = f'{programfiles_64}/Steam/steamapps/common/Squad/squad_launcher.exe'
game_launcher_path = game_launcher_path_32 if os.path.exists(game_launcher_path_32) else game_launcher_path_64


class ConfigKeys(StrEnum):
    PLAYER_NAME = auto()
    PLAYER_THRESHOLD = auto()
    ATTEMPT_RECONNECTION_TO_SERVER = auto()
    SERVER_IP = auto()
    SERVER_QUERY_PORT = auto()
    SLEEP_INTERVAL_SECONDS = auto()
    RANDOM_PLAYER_THRESHOLD_ENABLED = auto()
    RANDOM_PLAYER_THRESHOLD_UPPER = auto()
    RANDOM_PLAYER_THRESHOLD_LOWER = auto()
    LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED = auto()
    JOIN_SERVER_AUTOMATICALLY_ENABLED = auto()
    GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS = auto()
    SERVER_HANDLE_TO_AUTOJOIN = auto()
    CLOSE_SCRIPT_IF_GAME_HAS_CLOSED = auto()
    ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME = auto()
    ATTEMPTS_TO_AUTOJOIN_SERVER = auto()
    GAME_EXECUTABLE_NAME = auto()
    SQUAD_INSTALL_PATH = auto()
    SQUAD_CONFIG_FILES_PATH = auto()
    SQUAD_STEAM_URL_HANDLE = auto()
    DEFAULT_USER_ACTION = auto()
    LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED = auto()


class ScriptConfigFile:
    def __init__(self, config_path: str | Path):
        self.config_path: str = config_path
        self.config: dict = load_json_config(config_path)
        self.settings = self._load_settings()

    def _get_config_value(self, key):
        return self.config[key.value][VALUE_KEY]

    def _load_settings(self):
        return {key: self._get_config_value(key) for key in ConfigKeys}

    def save_settings(self):
        for key, value in self.settings.items():
            self.config[key.value][VALUE_KEY] = value
        self.save_json_config()

    def __getattr__(self, name):
        if name in ConfigKeys.__members__:
            return self.settings[ConfigKeys[name]]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in ConfigKeys.__members__:
            self.settings[ConfigKeys[name]] = value
        else:
            super().__setattr__(name, value)

    def save_json_config(self) -> None:
        """
        Saves a python dictonary to a json file.
        """
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
        return

    def generate_initial_config(self):
        """
        Function responsible for initiating the JSON file

        :param config_file:
        :return:
        """

        seedingscript_config: dict = \
            {
                'version': __VERSION__,

                ConfigKeys.PLAYER_NAME:
                    {
                        VALUE_KEY: "",
                        DESCRIPTION_KEY: "The user's in-game player name, tags not included. Used to see if the player is connected to the server"
                    },
                ConfigKeys.PLAYER_THRESHOLD:
                    {
                        VALUE_KEY: 60,
                        DESCRIPTION_KEY: 'The threshold that the desired user action will be taken. Overriden by the "Seeding Random" parameter, if enabled'
                    },
                ConfigKeys.ATTEMPT_RECONNECTION_TO_SERVER:
                    {
                        VALUE_KEY: False,
                        DESCRIPTION_KEY: 'Whether the script will attempt to reconnect if the user is no longer in the server'
                    },

                ConfigKeys.SERVER_IP:
                    {
                        VALUE_KEY: '',
                        DESCRIPTION_KEY: 'The IP/Domain of the server, that the script will query for player numbers.'
                    },
                ConfigKeys.SERVER_QUERY_PORT:
                    {
                        VALUE_KEY: 27165,
                        DESCRIPTION_KEY: 'The port the script will use to query the server for player numbers'
                    },
                ConfigKeys.SLEEP_INTERVAL_SECONDS:
                    {
                        VALUE_KEY: 60,
                        DESCRIPTION_KEY: 'How often the script'
                    },
                ConfigKeys.RANDOM_PLAYER_THRESHOLD_ENABLED:
                    {
                        VALUE_KEY: True,
                        DESCRIPTION_KEY: 'Whether script will utilise a random seeding threshold between the specified upper and lower bounds. On by default'
                    },
                ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER:
                    {
                        VALUE_KEY: 60,
                        DESCRIPTION_KEY: 'The lower bound of the random seeding threshold'
                    },
                ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER: {
                    VALUE_KEY: 98,
                    DESCRIPTION_KEY: 'The upper bound of the random seeding threshold'
                },
                ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED: {
                    VALUE_KEY: True,
                    DESCRIPTION_KEY: 'Whether lightweight seeding settings should be enabled.'

                },
                ConfigKeys.JOIN_SERVER_AUTOMATICALLY_ENABLED: {
                    VALUE_KEY: True,
                    DESCRIPTION_KEY: 'Whether the script should attempt to automatically join the server'
                },
                ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS: {
                    VALUE_KEY: 20,
                    DESCRIPTION_KEY: ''
                },
                ConfigKeys.SERVER_HANDLE_TO_AUTOJOIN: {
                    VALUE_KEY: 'triggernometry',
                    DESCRIPTION_KEY: 'The server handle the script will use to attempt to autojoin'
                },
                ConfigKeys.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED: {
                    VALUE_KEY: True,
                    DESCRIPTION_KEY: 'If the script should automatically close if the game stops running for whatever reason'
                },
                ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME: {
                    VALUE_KEY: True,
                    DESCRIPTION_KEY: 'If the script will try to autojoin the server, even if you were already ingame when it started'
                },
                ConfigKeys.ATTEMPTS_TO_AUTOJOIN_SERVER: {
                    VALUE_KEY: 3,
                    DESCRIPTION_KEY: 'The number of attempts the script will make to autojoin the server before giving up'
                },
                ConfigKeys.GAME_EXECUTABLE_NAME: {
                    VALUE_KEY: 'SquadGame.exe',
                    DESCRIPTION_KEY: 'The name of the games executable'
                },
                ConfigKeys.SQUAD_INSTALL_PATH: {
                    VALUE_KEY: f'{game_launcher_path}',
                    DESCRIPTION_KEY: 'The path to the games launcher. No longer really necessary, but used as a backup'
                },
                ConfigKeys.SQUAD_CONFIG_FILES_PATH: {
                    VALUE_KEY: f'{game_config_path}',
                    DESCRIPTION_KEY: "The path to squad's config files."
                },
                ConfigKeys.SQUAD_STEAM_URL_HANDLE: {
                    VALUE_KEY: "steam://rungameid/393380",
                    DESCRIPTION_KEY: 'The steam URL to start up the game'
                },
                ConfigKeys.DEFAULT_USER_ACTION: {
                    VALUE_KEY: None,
                    DESCRIPTION_KEY: 'if the user desires to not have to choose an input from the GUI, they can instead save one in the settings.'
                },
                ConfigKeys.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED: {
                    VALUE_KEY: False,
                    DESCRIPTION_KEY: 'This is here to have a consistent variable to see if a user has had their settings restored'
                }
            }

        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as f:
                json.dump(seedingscript_config, f, indent=4)
        return


def initialize_folder(folder_path: str | os.PathLike):
    """
    Initializes a folder if it does not exist.
    """
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)


def save_json_config(config: dict, config_file_path: str | os.PathLike) -> None:
    """
    Saves a python dictonary to a json file.
    """
    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4)
    return


def load_json_config(config_file_path: str | os.PathLike) -> dict:
    """
    Loads the settings from the config files.
    :return: Python dictionary with all the settings from the config file
    """
    with open(config_file_path, 'r') as f:
        config_file_json = json.load(f)
    return config_file_json


class IconsPaths:
    def __init__(self, base_path: str | os.PathLike):
        pass


class MultiOrderedDict(OrderedDict):
    """
    Required class to so it's possible to have multiple values per key in the game's config file,
    Since python otherwise does not support such functionality.
    """

    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super().__setitem__(key, value)


# class ScriptConfigFile:
#     def __init__(self, config_path: str | Path):
#
#         self.config_path: str = config_path
#         self.config: dict = load_json_config(config_path)
#         self.settings = self.load_settings()
#
#     def _get_config_value(self, key):
#         return self.config[key][VALUE_KEY]
#
#     def load_settings(self):
#         """
#         Loads settings from the config files into memory.
#         """
#         return {key: self._get_config_value(key) for key in ConfigKeys}
#
#     def save_settings(self):
#         """
#         Saves settings from memory into the config file.
#         """
#         for key in ConfigKeys:
#             self.config[key][VALUE_KEY] = self.settings[key]
#         save_json_config(self.config, self.config_path)


def init_JSON_config(config_file: os.PathLike):
    """
    Function responsible for initiating the JSON file

    :param config_file:
    :return:
    """

    seedingscript_config = \
        {
            'version': __VERSION__,

            ConfigKeys.PLAYER_NAME:
                {
                    VALUE_KEY: "",
                    DESCRIPTION_KEY: "The user's in-game player name, tags not included. Used to see if the player is connected to the server"
                },
            ConfigKeys.PLAYER_THRESHOLD:
                {
                    VALUE_KEY: 60,
                    DESCRIPTION_KEY: 'The threshold that the desired user action will be taken. Overriden by the "Seeding Random" parameter, if enabled'
                },
            ConfigKeys.ATTEMPT_RECONNECTION_TO_SERVER:
                {
                    VALUE_KEY: False,
                    DESCRIPTION_KEY: 'Whether the script will attempt to reconnect if the user is no longer in the server'
                },

            ConfigKeys.SERVER_IP:
                {
                    VALUE_KEY: '',
                    DESCRIPTION_KEY: 'The IP/Domain of the server, that the script will query for player numbers.'
                },
            ConfigKeys.SERVER_QUERY_PORT:
                {
                    VALUE_KEY: 27165,
                    DESCRIPTION_KEY: 'The port the script will use to query the server for player numbers'
                },
            ConfigKeys.SLEEP_INTERVAL_SECONDS:
                {
                    VALUE_KEY: 60,
                    DESCRIPTION_KEY: 'How often the script'
                },
            ConfigKeys.RANDOM_PLAYER_THRESHOLD_ENABLED:
                {
                    VALUE_KEY: True,
                    DESCRIPTION_KEY: 'Whether script will utilise a random seeding threshold between the specified upper and lower bounds. On by default'
                },
            ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER:
                {
                    VALUE_KEY: 60,
                    DESCRIPTION_KEY: 'The lower bound of the random seeding threshold'
                },
            ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER: {
                VALUE_KEY: 98,
                DESCRIPTION_KEY: 'The upper bound of the random seeding threshold'
            },
            ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED: {
                VALUE_KEY: True,
                DESCRIPTION_KEY: 'Whether lightweight seeding settings should be enabled.'

            },
            ConfigKeys.JOIN_SERVER_AUTOMATICALLY_ENABLED: {
                VALUE_KEY: True,
                DESCRIPTION_KEY: 'Whether the script should attempt to automatically join the server'
            },
            ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS: {
                VALUE_KEY: 20,
                DESCRIPTION_KEY: ''
            },
            ConfigKeys.SERVER_HANDLE_TO_AUTOJOIN: {
                VALUE_KEY: 'triggernometry',
                DESCRIPTION_KEY: 'The server handle the script will use to attempt to autojoin'
            },
            ConfigKeys.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED: {
                VALUE_KEY: True,
                DESCRIPTION_KEY: 'If the script should automatically close if the game stops running for whatever reason'
            },
            ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME: {
                VALUE_KEY: True,
                DESCRIPTION_KEY: 'If the script will try to autojoin the server, even if you were already ingame when it started'
            },
            ConfigKeys.ATTEMPTS_TO_AUTOJOIN_SERVER: {
                VALUE_KEY: 3,
                DESCRIPTION_KEY: 'The number of attempts the script will make to autojoin the server before giving up'
            },
            ConfigKeys.GAME_EXECUTABLE_NAME: {
                VALUE_KEY: 'SquadGame.exe',
                DESCRIPTION_KEY: 'The name of the games executable'
            },
            ConfigKeys.SQUAD_INSTALL_PATH: {
                VALUE_KEY: f'{game_launcher_path}',
                DESCRIPTION_KEY: 'The path to the games launcher. No longer really necessary, but used as a backup'
            },
            ConfigKeys.SQUAD_CONFIG_FILES_PATH: {
                VALUE_KEY: f'{game_config_path}',
                DESCRIPTION_KEY: "The path to squad's config files."
            },
            ConfigKeys.SQUAD_STEAM_URL_HANDLE: {
                VALUE_KEY: "steam://rungameid/393380",
                DESCRIPTION_KEY: 'The steam URL to start up the game'
            },
            ConfigKeys.DEFAULT_USER_ACTION: {
                VALUE_KEY: None,
                DESCRIPTION_KEY: 'if the user desires to not have to choose an input from the GUI, they can instead save one in the settings.'
            },
            ConfigKeys.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED: {
                VALUE_KEY: False,
                DESCRIPTION_KEY: 'This is here to have a consistent variable to see if a user has had their settings restored'
            }
        }

    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(seedingscript_config, f, indent=4)
    return


def config_check_integrity(config: dict):
    """
    Checks the integrity of the config file for integrity purposes.
    :param config:
    :return:
    """
    join_server_automatically = config['join_server_automatically']['value']
    attempt_autojoin_if_ingame = config['attempt_autojoin_if_ingame']['value']
    server_ip = config['server_address']['value']
    query_port = config['query_port']['value']
    player_threshold = config['player_threshold']['value']
    close_script_if_game_closed = config["close_script_if_closed_game"]['value']
    game_executable = config['game_executable']['value']
    lightweight_seeding_settings_on = config["lightweight_seeding_settings_on"]['value']
    sleep_interval = config['sleep_interval']['value']
    random_seeding_thresh_upper = config["random_seeding_thresh_upper"]['value']
    random_seeding_thresh_lower = config["random_seeding_thresh_lower"]['value']
    random_player_thresh = config["random_player_thresh"]['value']
    player_name = config["player_name"]['value']
    # attempt_reconnect = config['attempt_reconnect']['value']

    assert isinstance(join_server_automatically, bool)
    assert isinstance(attempt_autojoin_if_ingame, bool)
    assert isinstance(query_port, int)
    assert isinstance(player_threshold, int)
    assert isinstance(close_script_if_game_closed, bool)
    assert isinstance(lightweight_seeding_settings_on, bool)
    assert isinstance(sleep_interval, int)
    assert isinstance(random_seeding_thresh_upper, int)
    assert isinstance(random_seeding_thresh_lower, int)
    assert isinstance(random_player_thresh, bool)


def init_games_seeding_config(config: ScriptConfigFile):
    """
    Initializes the in game config file for setting applying seeding settings, if applicable.

    :param:
    :return:
    """

    # lightweight_seeding_settings = config.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED
    # if not lightweight_seeding_settings:
    #     return


    game_original_config_path = Path(game_config_path)
    backup_path = game_original_config_path / 'Backup'
    original_config_file = Path(game_original_config_path) / 'GameUserSettings.ini'
    on_startup_file = Path(backup_path) / 'GameUserSettingsLastUsed.ini'
    seeding_settings_swap_file = Path(backup_path) / 'GameUserSettingsSwapFile.ini'
    backup_config_file = Path(backup_path) / 'GameUserSettingsBackupOfOriginal.ini'

    if not os.path.exists(backup_path):
        try:
            backup_path.mkdir()
            logging.info(f"Backup directory successfully initialized")
        except FileExistsError:
            logging.debug(f'The backup directory already exists.')
            return

        logging.debug(f'Copying file')

        shutil.copyfile(original_config_file, seeding_settings_swap_file)

    if not os.path.exists(on_startup_file):
        try:
            shutil.copyfile(original_config_file, on_startup_file)
        except FileExistsError:
            return

    # To allow keys to still have multiple values. Otherwise the game's config file will break and not work.
    seedingparser = configparser.ConfigParser(dict_type=MultiOrderedDict, strict=False)
    seedingparser.optionxform = str
    seedingparser.read(seeding_settings_swap_file)
    mainsection = seedingparser['/Script/Squad.SQGameUserSettings']
    # Initiates the basic settings for the game's config file.
    # All 4 sections below are required to change resolution before the game starts.
    mainsection['ResolutionSizeX'] = "1280"
    mainsection['ResolutionSizeY'] = "720"
    mainsection['LastUserConfirmedResolutionSizeX'] = "1280"
    mainsection['LastUserConfirmedResolutionSizeY'] = "720"
    mainsection['LastUserConfirmedDesiredScreenWidth'] = '1280'
    mainsection['LastUserConfirmedDesiredScreenHeight'] = '720'
    mainsection['FullscreenMode'] = "2"  # Windowed mode
    mainsection['LastConfirmedFullscreenMode'] = "2"  # Windowed mode
    mainsection['MenuFrameRateLimit'] = '50.000000'
    mainsection['FrameRateLimit'] = "20.000000"
    mainsection['MasterVolume'] = "0.00000"
    mainsection['ScreenPercentage'] = "75"  # The screen resolution scaling in percent.
    with open(seeding_settings_swap_file, "w") as writefile:
        seedingparser.write(writefile)

    if not os.path.exists(on_startup_file):
        shutil.copyfile(original_config_file, on_startup_file)
    if not os.path.exists(backup_config_file):
        shutil.copyfile(original_config_file, backup_config_file)
    return


def main():
    pass


if __name__ == '__main__':
    main()

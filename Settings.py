import configparser
import json
import logging
import os
from collections import OrderedDict
from enum import Enum, StrEnum, auto
from pathlib import Path
from shutil import copyfile

VALUE_KEY = 'value'
DESCRIPTION_KEY = 'description'

# Path globals
__VERSION__ = "3.1.0"
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
    def __init__(self, config_path: Path):
        self.config_path: Path = config_path
        self._config: dict = self.load_settings()

    def __eq__(self, other):
        if isinstance(other, ScriptConfigFile):
            return self._config == other._config
        return False

    def get(self, key: ConfigKeys):
        return self._config.get(key.value, {}).get(VALUE_KEY, None)

    def set(self, key: ConfigKeys, value):
        if key.value in self._config:
            self._config[key.value][VALUE_KEY] = value
        else:
            self._config[key.value] = {VALUE_KEY: value}

    def save_settings(self):
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=4)
        return

    def load_settings(self):
        with open(self.config_path, 'r') as f:
            config_file_json = json.load(f)
        return config_file_json

    def reset_to_defaults(self):
        self._config = initial_config()
        self.save_settings()

class UserActions(StrEnum):
    CLOSE = auto()
    SHUTDOWN = auto()
    HIBERNATE = auto()


def generate_initial_config(path: Path):
    """
    Careful, this not *not* check if the file already exists, and will overwrite.
    """
    with open(path, 'w') as f:
        json.dump(initial_config(), f, indent=4)


def initial_config():
    """
    Function responsible for initiating the JSON file
    :return:
    """
    seedingscript_config: dict = {
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
            DESCRIPTION_KEY: 'The IP/Domain of the server, which will be queried.'
        },
        ConfigKeys.SERVER_QUERY_PORT:
        {
            VALUE_KEY: 27165,
            DESCRIPTION_KEY: 'The port the script will use to query the server'
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
            VALUE_KEY: 'tactrig',
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

    return seedingscript_config


def init_games_seeding_config():
    """
    Initializes the in game config file for setting applying seeding settings, if applicable.

    :param:
    :return:
    """

    game_original_config_path = Path(game_config_path)
    backup_path = game_original_config_path / 'Backup'
    original_config_file = game_original_config_path / 'GameUserSettings.ini'
    on_startup_file = backup_path / 'GameUserSettingsLastUsed.ini'
    seeding_settings_swap_file = backup_path / 'GameUserSettingsSwapFile.ini'
    backup_config_file = backup_path / 'GameUserSettingsBackupOfOriginal.ini'

    if not os.path.exists(backup_path):
        try:
            backup_path.mkdir()
            logging.info(f"Backup directory successfully initialized")
        except FileExistsError:
            logging.debug(f'The backup directory already exists.')
            return

        logging.debug(f'Copying file')
        copyfile(original_config_file, seeding_settings_swap_file)

    if not os.path.exists(on_startup_file):
        try:
            copyfile(original_config_file, on_startup_file)
        except FileExistsError:
            return

    # To allow keys to still have multiple values. Otherwise, the game's config file will break and not work.
    seedingparser = configparser.ConfigParser(dict_type=MultiOrderedDict, strict=False)
    seedingparser.optionxform = str
    seedingparser.read(seeding_settings_swap_file)
    # Initiates the basic settings for the game's config file.
    # All 4 sections below are required to change resolution before the game starts.
    mainsection = seedingparser['/Script/Squad.SQGameUserSettings']
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
        copyfile(original_config_file, on_startup_file)
    if not os.path.exists(backup_config_file):
        copyfile(original_config_file, backup_config_file)

    return True


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


def main():
    # Ensure that all the keys of the configkeys are in the config file





    pass


if __name__ == '__main__':
    main()

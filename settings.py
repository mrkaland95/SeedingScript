import logging
import multiprocessing
import shutil
import pyautogui
from configparser import ConfigParser
from json import load, dump
from os import path, environ
from collections import OrderedDict
from enum import StrEnum, auto
from pathlib import Path
from utils import log

# used to store the "keys" in the JSON config file.
VALUE_KEY = 'value'
DESCRIPTION_KEY = 'description'

# Path globals
__VERSION__ = "3.0.0b1"
# TESTING_MODE = True
TESTING_MODE = False
LOCAL_APPDATA = Path(environ.get('LOCALAPPDATA'))
SCRIPT_CONFIG_SETTINGS_FOLDER = Path(LOCAL_APPDATA) / 'SeedingScript'


if TESTING_MODE:
    SCRIPT_CONFIG_SETTINGS_FILE = Path(SCRIPT_CONFIG_SETTINGS_FOLDER) / 'seedingconfig_testing.json'
else:
    SCRIPT_CONFIG_SETTINGS_FILE = Path(SCRIPT_CONFIG_SETTINGS_FOLDER) / 'seedingconfig.json'

GAME_CONFIG_PATH = Path(LOCAL_APPDATA) / 'SquadGame/Saved/Config/WindowsNoEditor'

programfiles_32 = Path(environ.get("ProgramFiles(x86)"))
programfiles_64 = Path(environ.get('ProgramW6432'))
# game_config_path = os.path.abspath(f"{LOCAL_APPDATA}/SquadGame/Saved/Config/WindowsNoEditor")
game_config_path = LOCAL_APPDATA / "SquadGame/Saved/Config/WindowsNoEditor"

game_launcher_path_32 = programfiles_32 / 'Steam/steamapps/common/Squad/squad_launcher.exe'
game_launcher_path_64 = programfiles_64 / 'Steam/steamapps/common/Squad/squad_launcher.exe'
game_launcher_path = game_launcher_path_32 if game_launcher_path_32.exists() else game_launcher_path_64

ORIGINAL_PATH = Path(game_config_path)
BACKUP_FOLDER_PATH = Path(f'{ORIGINAL_PATH}\\Backup')
LAST_USED_SETTINGS_IN_SCRIPT_FOLDER_PATH = Path(f'{SCRIPT_CONFIG_SETTINGS_FOLDER}\\GameUserSettingsLastUsed.ini')
LAST_USED_BACKUP_PATH = Path(f'{BACKUP_FOLDER_PATH}\\GameUserSettingsLastUsed.ini')
ACTIVE_CONFIG_FILE_PATH = Path(f'{ORIGINAL_PATH}\\GameUserSettings.ini')
LIGHTWEIGHT_SWAP_FILE_PATH = Path(f'{BACKUP_FOLDER_PATH}\\GameUserSettingsSwapFile.ini')



LOGGING_LEVEL = logging.DEBUG
# LOGGING_LEVEL = logging.INFO
# logging.basicConfig(level=LOGGING_LEVEL)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(level=LOGGING_LEVEL)

close_game_key = '-CLOSE_GAME-'
hibernate_pc_key = '-HIBERNATE-'
shutdown_pc_key = '-SHUTDOWN-'

user_actions = {
    close_game_key: 'close',
    hibernate_pc_key: 'hibernate',
    shutdown_pc_key: 'shutdown'
}


GUI_WINDOW_THEME = 'DarkGrey14'
GUI_FONT = ('helvetica', 15)

SAMPLES = 100
SAMPLE_MAX = 100
CANVAS_SIZE = (400, 800)
LABEL_SIZE = (400, 20)

SEEDING_PROCESS = None
PLAYER_COUNT_ON_SERVER = None
pyautogui.FAILSAFE = False
PROGRAM_SHUTDOWN = False
CURRENT_STATE = None
EXIT_SEEDING_LOOP = False

QUEUE = multiprocessing.Queue()

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
    PREVIOUSLY_LAUNCHED_SEEDINGSCRIPT = auto()


class ScriptConfigFile:
    def __init__(self, config_file_path: Path):
        """
        Class meant to represent and store the various values that will be used by the seeding script.
        Loads and saves these settings to a JSON file.
        @param config_file_path: The path to the JSON file.
        """
        self.config_path: Path = config_file_path
        self._config: dict = self.load_settings()

    def __eq__(self, other):
        """

        @param other:
        @return:
        """
        if isinstance(other, ScriptConfigFile):
            return self._config == other._config
        return False

    def get(self, key: ConfigKeys):
        if not isinstance(key, ConfigKeys):
            raise AttributeError(f'The given key is not a valid entry in the config file\n'
                                 f'key: {key}')
        try:
            return self._config.get(key.value, {}).get(VALUE_KEY, None)
        except AttributeError:
            raise AttributeError(f"The attribute of {key} doesen't exist in the config file. This is likely because flax is a dumbass and "
                                 f"forgot to add it.")

    def set(self, key: ConfigKeys, value):
        if key.value in self._config:
            self._config[key.value][VALUE_KEY] = value
        else:
            self._config[key.value] = {VALUE_KEY: value}

    def get_server_address(self) -> tuple[str, int]:
        return self.get(ConfigKeys.SERVER_IP), int(self.get(ConfigKeys.SERVER_QUERY_PORT))

    def save_settings(self):
        log('Settings have been saved')

        with open(self.config_path, 'w') as f:
            dump(self._config, f, indent=4)
        return

    def load_settings(self):
        with open(self.config_path, 'r') as f:
            config_file_json = load(f)
        return config_file_json

    def reset_to_defaults(self):
        self._config = initial_config()
        self.save_settings()


class UserActions(StrEnum):
    CLOSE = auto()
    SHUTDOWN = auto()
    HIBERNATE = auto()


def generate_initial_config(file_path: Path):
    """
    Careful, this will *not* check if the file already exists, and will overwrite.
    """
    with open(file_path, 'w') as f:
        dump(initial_config(), f, indent=4)


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
            DESCRIPTION_KEY: 'The threshold that the desired user action will be taken. Overriden by the "Seeding Random" parameter, '
                             'if enabled'
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
            VALUE_KEY: 0,
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
            DESCRIPTION_KEY: 'Whether script will utilise a random seeding threshold between the specified upper and lower bounds. On by '
                             'default'
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
            VALUE_KEY: False,
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
        },
        ConfigKeys.PREVIOUSLY_LAUNCHED_SEEDINGSCRIPT: {
            VALUE_KEY: False,
            DESCRIPTION_KEY: 'This is here to have a consistent variable to see if a user has had their settings restored'
        }
    }

    return seedingscript_config


def testing_config():
    """
    Function responsible for initiating the JSON file
    :return:
    """
    seedingscript_config: dict = {
        'version': __VERSION__,

        ConfigKeys.PLAYER_NAME:
        {
            VALUE_KEY: "derpman",
            DESCRIPTION_KEY: "The user's in-game player name, tags not included. Used to see if the player is connected to the server"
        },
        ConfigKeys.PLAYER_THRESHOLD:
        {
            VALUE_KEY: 60,
            DESCRIPTION_KEY: 'The threshold that the desired user action will be taken. Overriden by the "Seeding Random" parameter, '
                             'if enabled'
        },
        ConfigKeys.ATTEMPT_RECONNECTION_TO_SERVER:
        {
            VALUE_KEY: False,
            DESCRIPTION_KEY: 'Whether the script will attempt to reconnect if the user is no longer in the server'
        },
        ConfigKeys.SERVER_IP:
        {
            VALUE_KEY: '147.135.30.85',
            DESCRIPTION_KEY: 'The IP/Domain of the server, which will be queried.'
        },
        ConfigKeys.SERVER_QUERY_PORT:
        {
            VALUE_KEY: 0,
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
            DESCRIPTION_KEY: 'Whether script will utilise a random seeding threshold between the specified upper and lower bounds. On by '
                             'default'
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
    last_used_file = backup_path / 'GameUserSettingsLastUsed.ini'
    seeding_settings_swap_file = backup_path / 'GameUserSettingsSwapFile.ini'
    backup_of_original_config_file = backup_path / 'GameUserSettingsBackupOfOriginal.ini'
    backup_config_file_secondary = SCRIPT_CONFIG_SETTINGS_FOLDER / 'GameUserSettingsBackupOfOriginal.ini'

    if not path.exists(backup_path):
        try:
            backup_path.mkdir()
            log(f"Backup directory successfully initialized")
        except FileExistsError:
            log(f'The backup directory already exists.')

        shutil.copyfile(original_config_file, seeding_settings_swap_file)

    if not path.exists(last_used_file):
        try:
            shutil.copyfile(original_config_file, last_used_file)
        except FileExistsError:
            return False

    initialise_swap_file(seeding_settings_swap_file)

    if not path.exists(last_used_file):
        shutil.copyfile(original_config_file, last_used_file)
    if not path.exists(backup_of_original_config_file):
        shutil.copyfile(original_config_file, backup_of_original_config_file)
    if not path.exists(backup_config_file_secondary):
        shutil.copyfile(original_config_file, backup_config_file_secondary)

    return True


def initialise_swap_file(swap_file_path: Path):
    """
    Method to define and initialise the lightweight seeding swap file.
    @param swap_file_path:
    @return:
    """
    # To allow keys to still have multiple values. Otherwise, the game's config file will break and not work.
    parser = ConfigParser(dict_type=MultiOrderedDict, strict=False)
    parser.optionxform = str
    parser.read(swap_file_path)

    # Initiates the basic settings for the game's config file.
    # All 4 sections below are required to change resolution before the game starts.
    mainsection = parser['/Script/Squad.SQGameUserSettings']
    mainsection['ResolutionSizeX'] = "1280"
    mainsection['ResolutionSizeY'] = "720"
    mainsection['LastUserConfirmedResolutionSizeX'] = "1280"
    mainsection['LastUserConfirmedResolutionSizeY'] = "720"
    mainsection['LastUserConfirmedDesiredScreenWidth'] = '1280'
    mainsection['LastUserConfirmedDesiredScreenHeight'] = '720'
    mainsection['FullscreenMode'] = "2"  # Windowed mode
    mainsection['LastConfirmedFullscreenMode'] = "2"  # Windowed mode
    mainsection['MenuFrameRateLimit'] = '30.000000'
    mainsection['FrameRateLimit'] = "20.000000"
    mainsection['MasterVolume'] = "0.00000"
    mainsection['ScreenPercentage'] = "(Value=50)"  # The screen resolution scaling in percent.
    mainsection['PostFX_Brightness'] = "0.900000"
    mainsection['FilterMaxPing'] = "500"
    with open(swap_file_path, "w") as writefile:
        parser.write(writefile)
    return


class MultiOrderedDict(OrderedDict):
    """
    Required class to, so it's possible to have multiple values per key in the game's config file,
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

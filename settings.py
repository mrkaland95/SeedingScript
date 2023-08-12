import shutil
import pyautogui
from configparser import ConfigParser
from json import load, dump
from os import path
from collections import OrderedDict
from enum import StrEnum, auto
from pathlib import Path
from utils import log
from constants import __VERSION__, SCRIPT_CONFIG_SETTINGS_FOLDER, GAME_LAUNCHER_PATH, GAME_CONFIG_PATH, LOGGING_LEVEL, LOGGER

# used to store the "keys" in the JSON config file.
VALUE_KEY = 'value'
DESCRIPTION_KEY = 'description'

LOGGER.setLevel(level=LOGGING_LEVEL)

pyautogui.FAILSAFE = False


# QUEUE = multiprocessing.Queue()

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
    DONT_START_GAME_IF_SERVER_ABOVE_THRESHOLD = auto()
    SCRIPT_AUTO_START_THRESHOLD = auto()
    SCRIPT_AUTO_START_UPPER_TIME = auto()
    SCRIPT_AUTO_START_LOWER_TIME = auto()


class ScriptConfigFile:
    def __init__(self, config_file_path: Path):
        """
        Class meant to represent and store the various values that will be used by the seeding script.
        Loads and saves these settings to a JSON file.
        @param config_file_path: The path to the JSON file.
        """
        self.config_path: Path = config_file_path

        # TODO add initialisation of the config file here.
        # if not config_file_path.exists():
        #     with open(config_file_path, 'w') as f:
        #         f.write("")


        settings = self._load_settings()
        self._config: dict = self._update_missing_fields(settings, template_config())
        self.save_settings()

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
        """
        Retrieves the IP/Domain and the query port
        @return:
        """
        return self.get(ConfigKeys.SERVER_IP), int(self.get(ConfigKeys.SERVER_QUERY_PORT))

    def save_settings(self):
        log('Settings have been saved')

        with open(self.config_path, 'w') as f:
            dump(self._config, f, indent=4)
        return self

    def _load_settings(self):
        with open(self.config_path, 'r') as f:
            config_file_json = load(f)
        config_file_json = self._update_missing_fields(config_file_json, template_config())
        return config_file_json

    @staticmethod
    def _update_missing_fields(existing_dict, template_dict):
        new_dict = {}
        for key in template_dict:
            new_dict[key] = existing_dict.get(key, template_dict[key])

        return new_dict

    def reload_settings(self):
        self._config: dict = self._load_settings()

    def reset_to_defaults(self):
        self._config = template_config()
        self.save_settings()


class UserActions(StrEnum):
    CLOSE = auto()
    SHUTDOWN = auto()
    HIBERNATE = auto()


def template_config():
    """
    Function responsible for storing the initial and default values of the script' config file
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
            DESCRIPTION_KEY: 'The interval of how often the script will query the server for player numbers.'
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
            VALUE_KEY: f'{GAME_LAUNCHER_PATH}',
            DESCRIPTION_KEY: 'The path to the games launcher. No longer really necessary, but used as a backup'
        },
        ConfigKeys.SQUAD_CONFIG_FILES_PATH: {
            VALUE_KEY: f'{GAME_CONFIG_PATH}',
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
        },
        ConfigKeys.DONT_START_GAME_IF_SERVER_ABOVE_THRESHOLD: {
            VALUE_KEY: True,
            DESCRIPTION_KEY: "Setting to specify if the script should still launch the game if the server is already above the player threshold."
        },
        ConfigKeys.SCRIPT_AUTO_START_THRESHOLD: {
            VALUE_KEY: 20,
            DESCRIPTION_KEY: 'The lower bound of players of where the automatic "watcher" thread will launch the part of the script that autojoins and performs the desired user action.'
        },
        ConfigKeys.SCRIPT_AUTO_START_LOWER_TIME: {
            VALUE_KEY: "11:00",
            DESCRIPTION_KEY: 'The lower bound of players of where the automatic "watcher" thread will launch the part of the script that autojoins and performs the desired user action.'
        },
        ConfigKeys.SCRIPT_AUTO_START_UPPER_TIME: {
            VALUE_KEY: "12:00",
            DESCRIPTION_KEY: 'The lower bound of players of where the automatic "watcher" thread will launch the part of the script that autojoins and performs the desired user action.'
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
            VALUE_KEY: f'{GAME_LAUNCHER_PATH}',
            DESCRIPTION_KEY: 'The path to the games launcher. No longer really necessary, but used as a backup'
        },
        ConfigKeys.SQUAD_CONFIG_FILES_PATH: {
            VALUE_KEY: f'{GAME_CONFIG_PATH}',
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
    }

    return seedingscript_config


def init_games_seeding_config():
    """
    Initializes the in game config file for setting applying seeding settings, if applicable.

    :param:
    :return:
    """
    game_original_config_path = GAME_CONFIG_PATH
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

    if not path.exists(last_used_file):
        shutil.copyfile(original_config_file, last_used_file)

    if not path.exists(backup_of_original_config_file):
        shutil.copyfile(original_config_file, backup_of_original_config_file)

    if not path.exists(backup_config_file_secondary):
        shutil.copyfile(original_config_file, backup_config_file_secondary)

    initialise_swap_file(seeding_settings_swap_file)

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


def compare_lightweight_to_active_config_file(active_config_file: Path, lightweight_config_file: Path) -> bool:
    lightweight_settings_active = False
    parser_active = ConfigParser(dict_type=MultiOrderedDict, strict=False)
    parser_active.optionxform = str
    parser_active.read(active_config_file)

    parser_lightweight = ConfigParser(dict_type=MultiOrderedDict, strict=False)
    parser_lightweight.optionxform = str
    parser_lightweight.read(lightweight_config_file)

    # Checks how many of the settings are the same, if it's above the threshold,
    similarity_counter = 0
    similarity_threshold = 5

    settings_section = '/Script/Squad.SQGameUserSettings'
    resolution_x = 'ResolutionSizeX'
    resolution_y = 'ResolutionSizeY'
    last_confirmed_resolution_x = 'LastUserConfirmedResolutionSizeX'
    last_confirmed_resolution_y = 'LastUserConfirmedResolutionSizeY'
    last_confirmed_desired_y = 'LastUserConfirmedDesiredScreenWidth'
    last_confirmed_desired_x = 'LastUserConfirmedDesiredScreenHeight'
    fullscreen_mode = 'FullscreenMode'
    last_confirmed_fullscreen_mode = 'LastConfirmedFullscreenMode'
    menu_frame_limit = 'MenuFrameRateLimit'
    master_volume = 'MasterVolume'
    resolution_scaling = 'ScreenPercentage'
    postfx_brightness = 'PostFX_Brightness'
    max_ping = 'FilterMaxPing'

    distinct_settings = [menu_frame_limit, menu_frame_limit, master_volume, resolution_scaling, postfx_brightness, max_ping]

    mainsection_active = parser_active[settings_section]
    mainsection_light = parser_lightweight[settings_section]

    if (mainsection_active[resolution_x] == mainsection_light[resolution_x] and
        mainsection_active[resolution_y] == mainsection_light[resolution_y]):

        similarity_counter += 1

    if (mainsection_active[last_confirmed_resolution_x] == mainsection_light[last_confirmed_resolution_x] and
        mainsection_active[last_confirmed_resolution_y] == mainsection_light[last_confirmed_resolution_y]):

        similarity_counter += 1

    if (mainsection_active[last_confirmed_desired_x] == mainsection_light[last_confirmed_desired_x] and
        mainsection_active[last_confirmed_desired_y] == mainsection_light[last_confirmed_desired_y]):

        similarity_counter += 1

    # if (mainsection_active[fullscreen_mode] == mainsection_light[fullscreen_mode] and
    #     mainsection_active[last_confirmed_fullscreen_mode] == mainsection_light[last_confirmed_fullscreen_mode]):
    #
    #     similarity_counter += 1

    for setting in distinct_settings:
        if mainsection_active[setting] == mainsection_light[setting]:
            similarity_counter += 1

    if similarity_counter >= similarity_threshold:
        lightweight_settings_active = True

    return lightweight_settings_active



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

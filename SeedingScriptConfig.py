import configparser
import enum
import json
import logging
import os
import shutil
import SeedingScriptMain as app
from enum import StrEnum, auto
from collections import OrderedDict
from pathlib import Path


VALUE_KEY = 'value'
DESCRIPTION_KEY = 'description'

#########################################################################
PLAYER_NAME_KEY = 'player_name'
PLAYER_THRESHOLD_KEY = 'player_threshold'
ATTEMPT_RECONNECTION_KEY = 'attempt_reconnect'
SERVER_IP_KEY = 'server_address'
QUERY_PORT_KEY = 'query_port'
SLEEP_INTERVAL_SECONDS_KEY = 'sleep_interval'
RANDOM_PLAYER_THRESHOLD_ENABLED_KEY = 'random_player_thresh'
RANDOM_PLAYER_THRESHOLD_LOWER_KEY = 'random_seeding_thresh_lower'
RANDOM_PLAYER_THRESHOLD_UPPER_KEY = 'random_seeding_thresh_upper'
LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED_KEY = 'lightweight_seeding_settings_on'
JOIN_SERVER_AUTOMATICALLY_ENABLED_KEY = 'join_server_automatically'
GAME_LAUNCH_TO_AUTOJOIN_DELAY_KEY = 'game_start_to_autojoin_delay'
SERVER_HANDLE_TO_AUTOJOIN_KEY = 'server_handle_to_autojoin'
CLOSE_SCRIPT_IF_GAME_HAS_CLOSED_KEY = 'close_script_if_closed_game'
ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME_KEY = 'attempt_autojoin_if_ingame'
ATTEMPTS_TO_AUTOJOIN_SERVER_KEY = 'attempts_to_auto_join_server'
GAME_EXECUTABLE_KEY = 'game_executable'
SQUAD_INSTALL_PATH_KEY = 'squad_install'
SQUAD_CONFIG_FILES_PATH_KEY = 'game_config_path'
SQUAD_STEAM_URL_HANDLE_KEY = 'game_url'
DEFAULT_USERACTION_KEY = 'desired_useraction'
LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED_KEY = 'lightweight_settings_applied'




class ConfigKeys(enum.StrEnum):
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
    DEFAULT_USER_ACTION_KEY = auto()
    LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED_KEY = auto()




# class ConfigKeys:
#     player_name_key = 'player_name'
#     attempt_reconnection_key = 'attempt_reconnect'
#     player_threshold_key = 'player_threshold'
#     server_ip_key = 'server_address'
#     query_port_key = 'query_port'
#     sleep_interval_seconds_key = 'sleep_interval'
#     random_player_threshold_enabled_key = 'random_player_thresh'
#     random_player_threshold_lower_key = 'random_seeding_thresh_lower'
#     random_player_threshold_upper_key = 'random_seeding_thresh_upper'
#     lightweight_seeding_settings_enabled_key = 'lightweight_seeding_settings_on'
#     join_server_automatically_enabled_key = 'join_server_automatically'
#     game_launch_to_autojoin_delay_key = 'game_start_to_autojoin_delay'
#     server_handle_to_autojoin_key = 'server_handle_to_autojoin'
#     close_script_if_game_has_closed_key = 'close_script_if_closed_game'
#     attempt_autojoin_if_already_ingame_key = 'attempt_autojoin_if_ingame'
#     attempts_to_autojoin_server_key = 'attempts_to_auto_join_server'
#     game_executable_key = 'game_executable'
#     squad_install_path_key = 'squad_install'
#     squad_config_files_path_key = 'game_config_path'
#     squad_steam_url_handle_key = 'game_url'
#     default_useraction_key = 'desired_useraction'
#     lightweight_settings_applied_key = 'lightweight_settings_applied'


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


class ScriptConfigFile:
    SETTINGS_KEYS = [
        app.PLAYER_NAME_KEY,
        app.PLAYER_THRESHOLD_KEY,
        app.ATTEMPT_RECONNECTION_KEY,
        app.SERVER_IP_KEY,
        app.QUERY_PORT_KEY,
        app.SLEEP_INTERVAL_SECONDS_KEY,
        app.RANDOM_PLAYER_THRESHOLD_ENABLED_KEY,
        app.RANDOM_PLAYER_THRESHOLD_UPPER_KEY,
        app.RANDOM_PLAYER_THRESHOLD_LOWER_KEY,
        app.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED_KEY,
        app.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED_KEY,
        app.JOIN_SERVER_AUTOMATICALLY_ENABLED_KEY,
        app.GAME_LAUNCH_TO_AUTOJOIN_DELAY_KEY,
        app.SERVER_HANDLE_TO_AUTOJOIN_KEY,
        app.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED_KEY,
        app.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME_KEY,
        app.GAME_EXECUTABLE_KEY,
        app.SQUAD_INSTALL_PATH_KEY,
        app.SQUAD_CONFIG_FILES_PATH_KEY,
        app.SQUAD_STEAM_URL_HANDLE_KEY,
        app.DEFAULT_USERACTION_KEY,
        app.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED_KEY
    ]

    def __init__(self, config_path: str | Path):

        self.config_path: str = config_path
        self.config: dict = load_json_config(config_path)
        self.settings = self._load_settings()

        #
        # self.config_path: str = config_path
        # self.config: dict = load_json_config(config_path)
        #
        # self.player_name = self.config[app.PLAYER_NAME_KEY][VALUE_KEY]
        # self.player_threshold = self.config[app.PLAYER_THRESHOLD_KEY][VALUE_KEY]
        # self.attempt_reconnection = self.config[app.ATTEMPT_RECONNECTION_KEY][VALUE_KEY]
        # self.server_ip = self.config[app.SERVER_IP_KEY][VALUE_KEY]
        # self.query_port = self.config[app.QUERY_PORT_KEY][VALUE_KEY]
        # self.sleep_interval_seconds = self.config[app.SLEEP_INTERVAL_SECONDS_KEY][VALUE_KEY]
        # self.random_player_threshold_enabled = self.config[app.RANDOM_PLAYER_THRESHOLD_ENABLED_KEY][VALUE_KEY]
        # self.random_player_threshold_lower = self.config[app.RANDOM_PLAYER_THRESHOLD_LOWER_KEY][VALUE_KEY]
        # self.random_player_threshold_upper = self.config[app.RANDOM_PLAYER_THRESHOLD_UPPER_KEY][VALUE_KEY]
        # self.lightweight_seeding_settings_enabled = self.config[app.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED_KEY][VALUE_KEY]
        # self.join_server_automatically_enabled = self.config[app.JOIN_SERVER_AUTOMATICALLY_ENABLED_KEY][VALUE_KEY]
        # self.game_launch_to_autojoin_delay_seconds = self.config[app.GAME_LAUNCH_TO_AUTOJOIN_DELAY_KEY][VALUE_KEY]
        # self.server_handle_to_autojoin = self.config[app.SERVER_HANDLE_TO_AUTOJOIN_KEY][VALUE_KEY]
        # self.close_script_if_game_has_closed = self.config[app.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED_KEY][VALUE_KEY]
        # self.attempt_autojoin_if_already_ingame = self.config[app.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME_KEY][VALUE_KEY]
        # self.attempts_to_autojoin_max = self.config[app.ATTEMPTS_TO_AUTOJOIN_SERVER_KEY][VALUE_KEY]
        # self.game_executable = self.config[app.GAME_EXECUTABLE_KEY][VALUE_KEY]
        # self.squad_install_path = self.config[app.SQUAD_INSTALL_PATH_KEY][VALUE_KEY]
        # self.squad_game_config_path = self.config[app.SQUAD_CONFIG_FILES_PATH_KEY][VALUE_KEY]
        # self.steam_url_handle = self.config[app.SQUAD_STEAM_URL_HANDLE_KEY][VALUE_KEY]
        # self.default_user_action = self.config[app.DEFAULT_USERACTION_KEY][VALUE_KEY]
        # self.lightweight_seeding_settings_applied = self.config[app.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED_KEY][VALUE_KEY]


    # def save_settings(self):
    #     """
    #     Takes all the settings stored internally in the object, puts them in the config dictionary,
    #     which is then saved as a JSON file.
    #     """
    #     self.config[app.PLAYER_NAME_KEY][VALUE_KEY] = self.player_name
    #     self.config[app.PLAYER_THRESHOLD_KEY][VALUE_KEY] = self.player_threshold
    #     self.config[app.ATTEMPT_RECONNECTION_KEY][VALUE_KEY] = self.attempt_reconnection
    #     self.config[app.SERVER_IP_KEY][VALUE_KEY] = self.server_ip
    #     self.config[app.QUERY_PORT_KEY][VALUE_KEY] = self.query_port
    #     self.config[app.SLEEP_INTERVAL_SECONDS_KEY][VALUE_KEY] = self.sleep_interval_seconds
    #     self.config[app.RANDOM_PLAYER_THRESHOLD_ENABLED_KEY][VALUE_KEY] = self.random_player_threshold_enabled
    #     self.config[app.RANDOM_PLAYER_THRESHOLD_LOWER_KEY][VALUE_KEY] = self.random_player_threshold_lower
    #     self.config[app.RANDOM_PLAYER_THRESHOLD_UPPER_KEY][VALUE_KEY] = self.random_player_threshold_upper
    #     self.config[app.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED_KEY][VALUE_KEY] = self.lightweight_seeding_settings_enabled
    #     self.config[app.JOIN_SERVER_AUTOMATICALLY_ENABLED_KEY][VALUE_KEY] = self.join_server_automatically_enabled
    #     self.config[app.GAME_LAUNCH_TO_AUTOJOIN_DELAY_KEY][VALUE_KEY] = self.game_launch_to_autojoin_delay_seconds
    #     self.config[app.SERVER_HANDLE_TO_AUTOJOIN_KEY][VALUE_KEY] = self.server_handle_to_autojoin
    #     self.config[app.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED_KEY][VALUE_KEY] = self.close_script_if_game_has_closed
    #     self.config[app.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME_KEY][VALUE_KEY] = self.attempt_autojoin_if_already_ingame
    #     self.config[app.ATTEMPTS_TO_AUTOJOIN_SERVER_KEY][VALUE_KEY] = self.attempts_to_autojoin_max
    #     self.config[app.GAME_EXECUTABLE_KEY][VALUE_KEY] = self.game_executable
    #     self.config[app.SQUAD_INSTALL_PATH_KEY][VALUE_KEY] = self.squad_install_path
    #     self.config[app.SQUAD_CONFIG_FILES_PATH_KEY][VALUE_KEY] = self.squad_game_config_path
    #     self.config[app.SQUAD_STEAM_URL_HANDLE_KEY][VALUE_KEY] = self.steam_url_handle
    #     self.config[app.DEFAULT_USERACTION_KEY][VALUE_KEY] = self.default_user_action
    #     self.config[app.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED_KEY][VALUE_KEY] = self.lightweight_seeding_settings_applied
    #     save_json_config(self.config, self.config_path)


    def _get_config_value(self, key):
        return self.config[key][VALUE_KEY]

    def _load_settings(self):
        return {key: self._get_config_value(key) for key in self.SETTINGS_KEYS}

    def save_settings(self):
        for key in self.SETTINGS_KEYS:
            self.config[key][VALUE_KEY] = self.settings[key]
        save_json_config(self.config, self.config_path)



def init_JSON_config(config_file: str | os.PathLike):
    """
    Function responsible for initiating the JSON file

    :param config_file:
    :return:
    """

    seedingscript_config = \
        {
            'version': app.__VERSION__,

            app.PLAYER_NAME_KEY:
            {
                VALUE_KEY: "",
                DESCRIPTION_KEY: "The user's in-game player name, tags not included. Used to see if the player is connected to the server"
            },
            app.PLAYER_THRESHOLD_KEY:
            {
                VALUE_KEY: 60,
                DESCRIPTION_KEY: 'The threshold that the desired user action will be taken. Overriden by the "Seeding Random" parameter, if enabled'
            },
            app.ATTEMPT_RECONNECTION_KEY:
            {
                VALUE_KEY: False,
                DESCRIPTION_KEY: 'Whether the script will attempt to reconnect if the user is no longer in the server'
            },

            app.SERVER_IP_KEY:
            {
                VALUE_KEY: '185.38.151.52',
                DESCRIPTION_KEY: 'The IP/Domain of the server, that the script will query for player numbers.'
            },
            app.QUERY_PORT_KEY:
            {
                VALUE_KEY: 27165,
                DESCRIPTION_KEY: 'The port the script will use to query the server for player numbers'
            },
            app.SLEEP_INTERVAL_SECONDS_KEY:
            {
                VALUE_KEY: 60,
                DESCRIPTION_KEY: 'How often the script'
            },
            app.RANDOM_PLAYER_THRESHOLD_ENABLED_KEY:
            {
                VALUE_KEY: True,
                DESCRIPTION_KEY: 'Whether script will utilise a random seeding threshold between the specified upper and lower bounds. On by default'
            },
            app.RANDOM_PLAYER_THRESHOLD_LOWER_KEY:
            {
                VALUE_KEY: 60,
                DESCRIPTION_KEY: 'The lower bound of the random seeding threshold'
            },
            app.RANDOM_PLAYER_THRESHOLD_UPPER_KEY: {
                VALUE_KEY: 98,
                DESCRIPTION_KEY: 'The upper bound of the random seeding threshold'
            },
            app.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED_KEY: {
                VALUE_KEY: True,
                DESCRIPTION_KEY: 'Whether lightweight seeding settings should be enabled.'

            },
            app.JOIN_SERVER_AUTOMATICALLY_ENABLED_KEY: {
                VALUE_KEY: True,
                DESCRIPTION_KEY: 'Whether the script should attempt to automatically join the server'
            },
            app.GAME_LAUNCH_TO_AUTOJOIN_DELAY_KEY: {
                VALUE_KEY: 20,
                DESCRIPTION_KEY: ''
            },
            app.SERVER_HANDLE_TO_AUTOJOIN_KEY: {
                VALUE_KEY: 'triggernometry',
                DESCRIPTION_KEY: 'The server handle the script will use to attempt to autojoin'
            },
            app.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED_KEY: {
                VALUE_KEY: True,
                DESCRIPTION_KEY: 'If the script should automatically close if the game stops running for whatever reason'
            },
            app.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME_KEY: {
                VALUE_KEY: True,
                DESCRIPTION_KEY: 'If the script will try to autojoin the server, even if you were already ingame when it started'
            },
            app.ATTEMPTS_TO_AUTOJOIN_SERVER_KEY: {
                VALUE_KEY: 3,
                DESCRIPTION_KEY: 'The number of attempts the script will make to autojoin the server before giving up'
            },
            app.GAME_EXECUTABLE_KEY: {
                VALUE_KEY: 'SquadGame.exe',
                DESCRIPTION_KEY: 'The name of the games executable'
            },
            app.SQUAD_INSTALL_PATH_KEY: {
                VALUE_KEY: f'{app.game_launcher_path}',
                DESCRIPTION_KEY: 'The path to the games launcher. No longer really necessary, but used as a backup'
            },
            app.SQUAD_CONFIG_FILES_PATH_KEY: {
                VALUE_KEY: f'{app.game_config_path}',
                DESCRIPTION_KEY: "The path to squad's config files."
            },
            app.SQUAD_STEAM_URL_HANDLE_KEY: {
                VALUE_KEY: "steam://rungameid/393380",
                DESCRIPTION_KEY: 'The steam URL to start up the game'
            },
            app.DEFAULT_USERACTION_KEY: {
                VALUE_KEY: None,
                DESCRIPTION_KEY: 'if the user desires to not have to choose an input from the GUI, they can instead save one in the settings.'
            },
            app.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED_KEY: {
                VALUE_KEY: False,
                DESCRIPTION_KEY: 'This is here to have a consistent variable to see if a user has had their settings restored'
            }
        }

    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(seedingscript_config, f, indent=4)
    return


# def check_current_seeding_settings(config_settings_file: BasicConfigFile):
#     config = load_config_JSON(config_settings_file)
#     game_config_path = config["game_config_path"]['value']
#     game_config_file = f'{game_config_path}\\GameUserSettings.ini'
#     return

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

    lightweight_seeding_settings = config.lightweight_seeding_settings_enabled
    if not lightweight_seeding_settings:
        return
    game_original_config_path = Path(config.squad_game_config_path)
    backup_path = game_original_config_path / 'Backup'
    original_config_file = Path(game_original_config_path) / 'GameUserSettings.ini'
    on_startup_file = Path(backup_path) / 'GameUserSettingsLastUsed.ini'
    seeding_settings_swap_file = Path(backup_path) / 'GameUserSettingsSwapFile.ini'
    backup_config_file = Path(backup_path) / 'GameUserSettingsBackupOfOriginal.ini'

    if not os.path.exists(backup_path):
        try:
            backup_path.mkdir()
            # os.mkdir(backup_path)
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

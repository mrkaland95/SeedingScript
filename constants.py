import logging
from datetime import datetime
from os import environ
from pathlib import Path

__VERSION__ = "3.0.0b3"
GUI_WINDOW_THEME = 'DarkGrey14'
GUI_FONT = ('helvetica', 15)

SAMPLES = 100
SAMPLE_MAX = 50
PLAYER_COUNT_ON_SERVER = None
PROGRAM_SHUTDOWN = False
CURRENT_STATE = None
EXIT_SEEDING_LOOP = False
TESTING_MODE = False
# TESTING_MODE = True

LOCAL_APPDATA = Path(environ.get('LOCALAPPDATA'))
SCRIPT_CONFIG_SETTINGS_FOLDER = Path(LOCAL_APPDATA) / 'SeedingScript'

programfiles_32 = Path(environ.get("ProgramFiles(x86)"))
programfiles_64 = Path(environ.get('ProgramW6432'))
game_launcher_path_32 = programfiles_32 / 'Steam/steamapps/common/Squad/squad_launcher.exe'
game_launcher_path_64 = programfiles_64 / 'Steam/steamapps/common/Squad/squad_launcher.exe'
GAME_LAUNCHER_PATH = game_launcher_path_32 if game_launcher_path_32.exists() else game_launcher_path_64

GAME_CONFIG_PATH = Path(LOCAL_APPDATA) / 'SquadGame/Saved/Config/WindowsNoEditor'
LAST_USED_SETTINGS_IN_SCRIPT_FOLDER_PATH = SCRIPT_CONFIG_SETTINGS_FOLDER / 'GameUserSettingsLastUsed.ini'

BACKUP_FOLDER_PATH = GAME_CONFIG_PATH / 'Backup'
LAST_USED_BACKUP_PATH = BACKUP_FOLDER_PATH / 'GameUserSettingsLastUsed.ini'
ACTIVE_CONFIG_FILE_PATH = GAME_CONFIG_PATH / 'GameUserSettings.ini'
LIGHTWEIGHT_SWAP_FILE_PATH = BACKUP_FOLDER_PATH / 'GameUserSettingsSwapFile.ini'
GAME_SETTINGS_BACKUP_FOLDER = SCRIPT_CONFIG_SETTINGS_FOLDER / 'GameSettingsBackup'

LOGGING_LEVEL = logging.DEBUG
LOGGER = logging.getLogger(__name__)

close_game_key = '-CLOSE_GAME-'
hibernate_pc_key = '-HIBERNATE-'
shutdown_pc_key = '-SHUTDOWN-'
none_key = 'none'

user_actions = {
    # none_key: None,
    close_game_key: 'close',
    hibernate_pc_key: 'hibernate',
    shutdown_pc_key: 'shutdown'
}

SCRIPT_START_TIME = datetime.utcnow()
LOG_FOLDER: Path = SCRIPT_CONFIG_SETTINGS_FOLDER / 'log'
LOGFILE: Path = LOG_FOLDER / f'SeedingScript_{SCRIPT_START_TIME.strftime("%Y.%m.%d_%H.%M.%S")}.log'
MAX_LOGFILES = 10

if not TESTING_MODE:
    SCRIPT_CONFIG_SETTINGS_FILE = Path(SCRIPT_CONFIG_SETTINGS_FOLDER) / 'seedingconfig.json'
else:
    SCRIPT_CONFIG_SETTINGS_FILE = Path(SCRIPT_CONFIG_SETTINGS_FOLDER) / 'seedingconfig_testing_2.json'
SEEDING_PROCESS = None
STOP_SEEDINGSCRIPT = False
GAME_STARTED_BY_SCRIPT = False
PT_TIME_STAMP = []
PT_PLAYER_NUMBERS = []
DATA_UPDATED = False


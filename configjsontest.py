import json
import os
import sys


def initConfig(config_folder: str, game_path: str, game_config_path):

    seedingscript_config = \
            {
            'version': 3.0,

            'settings':
                {
                    'seeding_threshold':
                    {
                        'value': 60,
                        'description': 'The threshold that the desired user action will be taken. Overriden by the "Seeding Random" parameter, if enabled'
                    },
                    'server_address':
                    {
                        'value': '72.9.150.223',
                        'description': 'The IP/Domain of the server, that the script will query for player numbers.'
                    },
                    'query_port':
                    {
                        'value': 27165,
                        'description': ''
                    },
                    'sleep_interval':
                    {
                        'value': 60,
                        'description': ''
                    },
                    'random_seeding_thresh':
                    {
                        'value': True,
                        'description': 'Whether script will utilise a random seeding threshold between the specified upper and lower bounds. On by default'
                    },
                    'random_seeding_thresh_lower': {
                        'value': 60,
                        'description': 'The lower bound of the random seeding threshold'
                    },
                    'random_seeding_thresh_upper': {
                        'value': 98,
                        'description': 'The upper bound of the random seeding threshold'
                    },
                    'lightweight_seeding_settings': {
                        'value': True,
                        'description': 'Whether lightweight seeding settings should be enabled.'

                    },
                    'join_server_automatically_enabled': {
                        'value': True,
                        'description': 'Whether the script should attempt to automatically join the server'
                    },
                    'game_start_to_autojoin_delay': {
                        'value': 60,
                        'description': ''

                    },
                    'server_handle_to_autojoin': {
                        'value': 'triggernometry',
                        'description': 'The server handle the script will use to attempt to autojoin'
                    },
                    'close_script_if_closed_running': {
                        'value': True,
                        'description': 'If the script should automatically close if the game stops running for whatever reason'
                    },
                    'attempt_autojoin_if_ingame': {
                        'value': False,
                        'description': 'If the script will try to autojoin the server, even if you were already ingame when it started'
                    },
                    'attempts_to_auto_join_server': {
                        'value': 3,
                        'description': 'How many attempts the script will make to autojoin the server before giving up'
                    }
                },

            'other':

                {
                    'paths':
                        {
                            'game_executable': {
                                'value': 'SquadGame.exe',
                                'description': 'The name of the games executable'
                            },
                            'squad_install': {
                                'value': f'{game_path}',
                                'description': 'The path to the games launcher. No longer really necessary, but used as a backup'
                            },
                            'game_config_path': {
                                'value': f'{game_config_path}',
                                'description': ''
                            },
                            'game_url': {
                                'value': "steam://rungameid/393380",
                                'description': 'The steam URL to start up the game'

                            }
                        }
                },
            'desired_useraction': None
        }

    if not os.path.isdir(config_folder):
        os.makedirs(name=config_folder)


    path = f'{config_folder}\\seedingconfig.json'
    with open(path, 'w') as f:
        json.dump(seedingscript_config, f, indent=4)
    return



def readConfig(config_folder: str):
    config_path = f'{config_folder}\\seedingconfig.json'
    with open(config_path, 'r') as f:
        try:
            config_file_json = json.load(f)
        except Exception as err:
            print(err)
            sys.exit()
    seed_thresh = config_file_json['settings']['seeding_threshold']['value']
    server_address = config_file_json['settings']['server_address']['value']
    query_port = config_file_json['settings']['query_port']['value']
    sleep_interval = config_file_json['settings']['sleep_interval']['value']
    random_seeding_thresh = config_file_json['settings']['random_seeding_thresh']['value']
    random_thresh_lower = config_file_json['settings']['random_seeding_thresh_lower']['value']
    random_thresh_upper = config_file_json['settings']['random_seeding_thresh_upper']['value']
    lightweight_seeding_settings = config_file_json['settings']['lightweight_seeding_settings']['value']
    join_server_automatically = config_file_json['settings']['join_server_automatically_enabled']['value']
    game_start_to_autojoin_delay = config_file_json['settings']['game_start_to_autojoin_delay']['value']
    server_handle_to_autojoin = config_file_json['settings']['server_handle_to_autojoin']['value']
    close_script_if_game_closed = config_file_json['settings']['close_script_if_closed_running']['value']
    attempt_autojoin_if_ingame = config_file_json['settings']['attempt_autojoin_if_ingame']['value']
    attempts_to_autojoin = config_file_json['settings']['attempts_to_auto_join_server']['value']
    game_executable = config_file_json['other']['paths']['game_executable']['value']
    squad_install = config_file_json['other']['paths']['squad_install']['value']
    game_config_path = config_file_json['other']['paths']['game_config_path']['value']
    game_url_handle = config_file_json['other']['paths']['game_url']['value']

    return seed_thresh,\
    (server_address, query_port), \
    sleep_interval, \
    random_seeding_thresh, \
    random_thresh_lower, \
    random_thresh_upper, \
    lightweight_seeding_settings, \
    join_server_automatically, \
    game_start_to_autojoin_delay, \
    server_handle_to_autojoin, \
    close_script_if_game_closed, \
    attempt_autojoin_if_ingame,\
    attempts_to_autojoin, \
    game_executable, \
    squad_install, \
    game_config_path, \
    game_url_handle




def saveConfig(seed_thresh,
    server_address, query_port,
    sleep_interval,
    random_seeding_thresh,
    random_thresh_lower,
    random_thresh_upper,
    lightweight_seeding_settings,
    join_server_automatically,
    game_start_to_autojoin_delay,
    server_handle_to_autojoin,
    close_script_if_game_closed,
    attempt_autojoin_if_ingame,
    attempts_to_autojoin,
    game_executable,
    squad_install,
    game_config_path,
    game_url_handle):
















if __name__ == '__main__':
    game_launcher_path = ""

    local_appdata = os.environ['LOCALAPPDATA']
    config_settings_path = f'{local_appdata}/SeedingScript'
    programfiles_32 = os.environ["ProgramFiles(x86)"]
    game_launcher_path_32 = f'{programfiles_32}/Steam/steamapps/common/Squad/squad_launcher.exe'
    programfiles_64 = os.environ['ProgramW6432']
    game_launcher_path_64 = f'{programfiles_64}/Steam/steamapps/common/Squad/squad_launcher.exe'



    if os.path.exists(game_launcher_path_32):
        game_launcher_path = game_launcher_path_32
    elif os.path.exists(game_launcher_path_64):
        game_launcher_path = game_launcher_path_64

    config_parameters = []

    #print(game_launcher_path)
    #initConfigJSON(config_folder=config_settings_folder, game_path=game_launcher_path, game_config_path="")
    #config_parameters.append(readConfigJSON(config_settings_folder))
    #print(config_parameters)

    seeding_threshold,\
    seeding_address,\
    sleep_interval,\
    random_seeding_threshold,\
    random_thresh_lower,\
    random_thresh_upper, \
    lightweight_seeding_settings, \
    join_server_automatically, \
    game_start_to_autojoin_delay,\
    server_handle_to_autojoin, \
    close_script_if_game_closed, \
    attempt_autojoin_if_ingame,\
    attempts_to_autojoin, \
    game_executable, \
    squad_install, \
    game_config_path, \
    game_url_handle= readConfig(config_settings_path)











    #print(seeding_config_json)





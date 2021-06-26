import json



path = ''






seedingscript_config = {
    'Settings':
        {
            'seeding_threshold': 60,
            'server_address': '72.9.150.223',
            'query_port': 27180,
            'sleep_interval': 60,
            'random_seeding_thresh': True,
            'random_seeding_thresh_lower': 60,
            'random_seeding_thresh_upper': 98,
            'lightweight_seeding_settings': True,
            'join_server_automatically_enabled': True,
            'game_start_to_autojoin_delay': 60,
            'server_handle_to_autojoin': 'triggernometry',
            'close_script_if_game_not_running': True,
            'autojoin_if_already_ingame': False,
            'attempts_to_auto_join_server': 3
        },

    'Other':
        {
            'desired_action': None,
            'paths':
                {
                    'game_executable': 'SquadGame.exe',
                    'squad_install': 'C:\Program Files (x86)\Steam\steamapps\common\Squad\Squad_launcher.exe',
                    'game_config_path': f"{path}"
                }
            }
        }



seeding_config_json = json.dumps(seedingscript_config, indent = 4)

print(seeding_config_json)





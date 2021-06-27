import json
import os
import threading
import time


import PySimpleGUI as sgui


def main_window():
    sgui.theme('DarkGrey14')
    menu_def = [['Settings', ['Open']],]
    layout = [ [sgui.Menu(menu_def, tearoff=True)],
               [sgui.Text('SeedingScript Output', font=('Helvetica', 16))],
               [sgui.MLine(size=(40, 40), key='-ML-', text_color='WHITE',
                tooltip='The output console of the seedingscript',
                autoscroll=True, reroute_stdout=True,
                reroute_stderr=True, write_only=True)],
             ],

    window = sgui.Window('SeedingScript', layout, font=('Helvetica', 16), resizable=True, size = (1000, 700), finalize=True)
    threading.Thread(target=simulate_gameloop, daemon=True).start()
    while True:
        event, values = window.read(timeout=100)
        if event == 'Exit' or event == sgui.WIN_CLOSED:
            break
        if event == 'Open':
            settings_window()
    window.close()






def simulate_gameloop():
    while True:
        print('test')
        time.sleep(5)






def load_config_settings(settings_file: str):
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except Exception as err:
        sgui.popup_quick_message(f'exception{err}', 'likely beacuse no settings file were found.')













def settings_window(random_seeding_thresh: bool = True, random_seeding_thresh_lower: int = 60,
                    random_seeding_thresh_upper: int = 98, lightweight_seeding_settings: bool = True, join_server_automatically_enabled: bool = True,
                    close_script_if_game_not_running: bool = True, sleep_interval: int = 60, game_start_to_autojoin_delay: int = 60,
                    autojoin_if_already_ingame: bool = True):




    sgui.theme('DarkGrey14')
    sgui.SystemTray(tooltip='SeedingScript')





    server_ip = '72.9.150.223'
    server_port = 27180
    random_seeding_thresh_lower = ""
    game_start_to_autojoin_delay = ""
    server_handle_to_autojoin = ""
    attempts_to_auto_join_server = ""
    #random_seeding_updated =




    # [sgui.Frame('Options')]


    layout = [[sgui.Text('Settings', font=('Helvetica', 16), justification='center')],
            [sgui.Text('Server IP/Domain', font=('Helvetica', 12))],
            [sgui.InputText(size=(35, 20), key='server_ip', default_text=server_ip)],
            [sgui.Text('Server Query Port', font=('Helvetica', 12))],
            [sgui.InputText(size=(35, 20), key='query_port', default_text=server_port)],
            [sgui.Frame('On/Off settings', layout=[
            [sgui.Checkbox('Random Seeding Threshold', default=random_seeding_thresh, key='randomSeedingThresh')],
            [sgui.Checkbox('Lightweight Seeding Settings', default=lightweight_seeding_settings, key='lightweightSeeding')],
            [sgui.Checkbox('Attempt to join automatically', default=join_server_automatically_enabled, key='joinServerAutomatically')],
            [sgui.Checkbox('Close program if game is closed', default=close_script_if_game_not_running, key='closeifrunning')],
            [sgui.Checkbox('Attempt to autojoin if already ingame', default=autojoin_if_already_ingame, key='autojoinIfIngame')]])],
            [sgui.Button('Save', key='Save')]
            [sgui.Slider()]

    ]



    window = sgui.Window('SeedingScript Settings', layout, font=('Helvetica', 16), resizable=True, size=(1000, 600))

    while True:
        event, values = window.read(timeout=100)
        """
        try:
            server_ip = values['server_ip']
            query_port = values['query_port']
            sleep_interval = values['sleep_interval']
            random_seeding_thresh_lower = values['random_seeding_thresh_lower']
            random_seeding_thresh_upper = values['random_seeding_thresh_upper']
            lightweight_seeding_settings = values['lightweight_seeding_settings']
            join_server_automatically_enabled = values['join_server_automatically_enabled']
            game_start_to_autojoin_delay = values['game_start_to_autojoin_delay']
            server_handle_to_autojoin = values['server_handle_to_autojoin']
            close_script_if_game_not_running = values['close_script_if_game_not_running']
            autojoin_if_already_ingame = values['autojoin_if_already_ingame']
            attempts_to_auto_join_server = values['attempts_to_auto_join_server']
        except TypeError or KeyError:
            pass
        """
        #if server_ip != None:
            #print(server_ip)
            #print(server_port)

        if event == 'Exit' or event == sgui.WIN_CLOSED:
            break
    window.close()








if __name__ == '__main__':
    local_appdata = os.environ['LOCALAPPDATA']
    config_settings_path = f'{local_appdata}\\SeedingScript'
    settings_window()
    #main_window()
    #threading.Thread(target=main_window, daemon=True).start()








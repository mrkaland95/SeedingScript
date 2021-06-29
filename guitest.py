import json
import os
import threading
import time


import PySimpleGUI as sgui



def simulate_gameloop():
    while True:
        print('test')
        time.sleep(5)





def initializeConfigFile(destination: str):
    destination = destination



def load_config_settings(settings_file: str):
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except Exception as err:
        sgui.popup_quick_message(f'exception{err}', 'likely beacuse no settings file were found.')




def settings_window(server_ip: str = '104.128.58.250', server_port: int = 27165, random_seeding_thresh: bool = True, random_seeding_thresh_lower: int = 60,
                    random_seeding_thresh_upper: int = 98, lightweight_seeding_settings: bool = True, join_server_automatically_enabled: bool = True,
                    close_script_if_game_not_running: bool = True, sleep_interval: int = 60, game_start_to_autojoin_delay: int = 60,
                    autojoin_if_already_ingame: bool = True, game_executeable: str = 'SquadGame', desired_useraction = None, game_url: str = 'steam://rungameid/393380'):





    sgui.theme('DarkGrey14')
    sgui.SystemTray(tooltip='SeedingScript')





    #server_ip = '72.9.150.223'
    #server_port = 27180
    game_start_to_autojoin_delay = ""
    server_handle_to_autojoin = ""
    attempts_to_auto_join_server = ""
    #random_seeding_updated =
    squad_install = ""




    # [sgui.Frame('Options')]


    layout = [[sgui.Text('Settings', font=('Helvetica', 24), justification='left'), sgui.Text('Other:', pad=(350, 0), font=('Helvetica', 24), justification='center')],
            [sgui.Text('Server IP/Domain', font=('Helvetica', 14)), sgui.Text('Game Executable', pad=(315, 0), font=('Helvetica', 14))],
            [sgui.InputText(size=(35, 20), key='server_ip', default_text=server_ip), sgui.InputText(size=(35, 20), key='-executable-', default_text=game_executeable, pad=(45, 0))],
            [sgui.Text('Server Query Port', font=('Helvetica', 14)), sgui.Text('Game Executable', pad=(313, 0), font=('Helvetica', 14))],
            [sgui.InputText(size=(35, 20), key='query_port', default_text=server_port)],
            [sgui.Frame('On/Off settings', layout=[
            [sgui.Checkbox('Random Seeding Threshold', default=random_seeding_thresh, key='randomSeedingThresh')],
            [sgui.Checkbox('Lightweight Seeding Settings', default=lightweight_seeding_settings, key='lightweightSeeding')],
            [sgui.Checkbox('Attempt to join automatically', default=join_server_automatically_enabled, key='joinServerAutomatically')],
            [sgui.Checkbox('Close program if game is closed', default=close_script_if_game_not_running, key='closeifrunning')],
            [sgui.Checkbox('Attempt to autojoin if already ingame', default=autojoin_if_already_ingame, key='autojoinIfIngame')]])],
            [sgui.Frame('Setting Threshold Settings',[
            [sgui.Text('Upper and lower seeding threshold')],
            [sgui.Slider(range=(1, 100), orientation='v', size=(5, 20), default_value=random_seeding_thresh_lower, key='-LowerThresh-'),
             sgui.Slider(range=(random_seeding_thresh_lower, 100), orientation='v', size=(5, 20),
                         default_value=random_seeding_thresh_upper, key='-UpperThresh')]])],








            #[sgui.Slider(range=(random_seeding_thresh_lower, random_seeding_thresh_upper))]






              [sgui.Button('Save', key='Save')],


    ]



    window = sgui.Window('SeedingScript Settings', layout, font=('Helvetica', 16), resizable=True, finalize=True)

    while True:
        event, values = window.read(timeout=100)
        if event == "-LowerThresh-":
            random_seeding_thresh_lower = values['-LowerThresh-']

        #if event == ''
        #if server_ip != None:
            #print(server_ip)
            #print(server_port)

        if event == 'Exit' or event == sgui.WIN_CLOSED:
            break
    window.close()



def main_window():
    sgui.theme('DarkGrey14')
    menu_def = [['Settings', ['Open']],]
    layout = [[sgui.Menu(menu_def, tearoff=True)],
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
            settings_window(server_ip='test', server_port=12414)
    window.close()


if __name__ == '__main__':




    local_appdata = os.environ['LOCALAPPDATA']
    config_settings_path = f'{local_appdata}\\SeedingScript'
    settings_window()
    #main_window()
    #threading.Thread(target=main_window, daemon=True).start()








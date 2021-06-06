# SeedingScript

Script for shutting down the game/PC when the server population is high enough, and automatically launch the game when the chosen action is taken(close or shutdown)
***
To download, go in to the "releases tab", choose the most recent release and then download the "seedingscript.zip" file under the assets dropdown.
***
On startup, a config file will be initialized, where the script will pull most of it's parameters from.
This config file will be created in the same folder as the script was launched from, and if the script is moved,
the config file should be moved with it, otherwise a new config file will be initialized.



Some examples:
````
is_seeding_random_enabled = true
seeding_random_upper_limit = 98
seeding_random_lower_limit = 60
````
In this example, parameters that decide whether your chosen action should be executed at a random player number between the lower and upper limit. By defualt set to on.
````
join_server_automatically_enabled = false
````
The parameter that determines whether the script will try to autojoin the desired server.
Opt in by default, so this must be enabled after the config file has been initialized.
````
autojoin_if_already_ingame = false
````
Lets you chose whether the script should attempt to autojoin the server, if the game was already running when the script started.


***


The script also has the capability of applying lightweight "seeding" settings upon the game
being started(If the game is launched by the program only,
it won't try to apply these settings if you are already running the game).
This setting however, is disabled by default in the config file.
To enable it, change the "lightweight_seeding_settings" variable to "true" and save.
Then, when the script is started up for the first time,
it will create a folder named "backup" in your game config folder,
and initialize some game config files, as well as take a backup of your game config file.
Use this file to restore your config file doesen't get restored properly.
The script will restore your last used config file,
but can't do this if the script is forcefully closed,
or if the player threshold is not triggered.
Included in the GUI is a button that will restore your last used settings if the script were to be forcefully closed.
This is highly recommended to be used in those instances of the script being close imporperly.
***
In addition to normal GUI use, there is added capability to adjust or enable certain settings from the command line.
These are as following:
````
-help or -h
-close
-shutdown
-restorelast
-thresh-<<integer here>>
-autoseed
````
The 'help' argument explains the use of these.
"close" and "shutdown" are exclusive paramters, only one or the other can be used, or the program will shut down.

***
Finally, if any issues pop up, you can PM Flax on discord, or report issues here.
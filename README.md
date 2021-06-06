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
In this example, these are the parameters that decide whether your chosen action would be executed, at a random number of players between the lower and upper limit.

This setting is by defualt set to on.
````
join_server_automatically_enabled = false
````
The parameter that determines whether the script will try to autojoin the desired server.
This setting is *OPT-IN* by default, so this must be enabled after the config file has been initialized.
````
autojoin_if_already_ingame = false
````
This lets you chose if the script should attempt to autojoin the server, if the game was already running when the script started.


***


The script also has the capability of applying lightweight "seeding" settings upon game start.
This will however only work if the game was not already running.

Since the setting still has some flaws, it will be set to *false* by default in the config file, and must be set to *true* should you wish to use it

To enable it, change the "lightweight_seeding_settings" variable to "true" and save.

At that point, when the script starts up for the first time,
the script will create a folder named "backup" in your game config folder,
and initialize some game config files, as well as create an "original" backup of your game config file.
This is done so your settings are saved in the rare event your proper settings are not restored properly.

Be aware that this can basically only happen if the script was forcefully closed from the taskmanager or the terminal it's running in was closed.

While there are some safeguards built in, in the event of the script being forcefully closed, and your proper settings have not been restored yet, you can use the "restore last" button in the GUI or the "-restorelast" command from the commandline.
***
In addition to normal GUI use, there is added capability to adjust or enable certain settings from the command line.
These are as following:

| Command | Description |
|------------|-----------------|
| `-help` or `-h` | Let's you see the available commands while in the terminal. Stops execution of the script. |
| `-close` | Sets your input to close and skips the GUI startup. Mutually exclusive with -shutdown|
| `-shutdown` | Sets your input to shutdown and skips the GUI startup. Mutually exclusive with -close |
| `-restorelast` | Restores the last saved game config file before launching the script. Can for example be used if the script was closed before regular settings were restored|
| `-thresh-`{desired integer here}| Allows you to set the seeding threshold from the command line. Overrides the 'seeding-random' parameter from the config file. Remove the curly braces when inputting the desired threshold|
| `-autoseed` | Overrides the 'autoseeding_enabled' option from the config file and sets to it to 'True'

Example of use in the commandline would for example be:

````
Seedingscript.exe -close -thresh-80
````
or using the source code file:
````
python seedingscript.py -close -thresh-80
````

In this instance, you would set the desired action to close, and the action threshold to 80 players.
The script would then close the game down once the player number reaches 80.



***
Finally, if any issues pop up, you can PM Flax on discord, or report issues here.
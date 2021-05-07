# SeedingScript v2.0

Script for shutting down the game/PC when the server population is high enough, and automatically launch the game when the chosen action is taken(close or shutdown)

Source code is in the "SeedingScript.py" file.
To run, simply download and run the file called "SeedingScript v2.0.exe".

On startup, a config file will be initialized, where the script will pull some adjustable options. This config file will be created in the same folder as the script was launched from, and if the script is moved, the config file should be moved with it, otherwise a new config file will be initialized.
The config file contains some adjustable parameters, like what player count your chosen action will activate at. By default this is set to 60. Other options include the interval at which the server will be queried. Generally don't touch this, but the option is there.

For the script to be able to launch the game, the correct path to the game need to be stored in the config file. By default this is set to your C drive, so if the game is installed on any other drive, you will need to adjust the path to the Squad_launcher.exe in there.

The script also has the capability of applying lightweight "seeding" settings upon the game being started(If the game is launched by the program only, it won't try to apply these settings if you are already running the game). This setting however, is disabled by default in the config file. To enable it, change the "lightweight_seeding_settings" variable to "true" and save. Then, when the script is started up for the first time, it will create a folder named "backup" in your game config folder, and initialize some game config files, as well as take a backup of your game config file. Use this file to restore your config file doesen't get restored properly. The script will restore your last used config file, but can't do this if the script is forcefully closed, or if the player threshold is not triggered. Included in the GUI is a button that will restore your last used settings if the script were to be forcefully closed. This is highly recommended to be used in those instance of the script being closes imporperly.

Also program should be able to find the game's config file for most people, but in the instance it won't, you can yet again manually adjust the path to your config file folder.

Lastly, if any issues pop up, you can PM Flax on discord.

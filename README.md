# Purpose
### This is a GUI application, written in Python, intended to ease the burden of getting the population of a Squad game server going, AKA seeding.

## Functionality

- Ability to fully automatically join a server, by launching the game, navigating the menus and clicking on the server
- This is done using OCR(Optical Character Recognition).
- TEMPORARILY NOT WORKING: After hitting a configurable player number 1. close down the game 2. ) Send computer into sleep mode 3. ) Power down computer
- This player number can be configured to either randomly be picked between a specified upper and lower bound, or to a specific number.
- The program will periodically check whether the specified server is above the given total player threshold, and then execute the stored user action.
- Automatically apply low resource usage settings before launching the game. This for example includes a 

## Drawbacks

Due to the program using OCR, it uses a lot more resources than it would otherwise need, since it needs to take screenshots, process them for text, and then click the various buttons in the menus. This means it's not always completely reliable, but this will ideally be improved over time. 

## To run:

Download an executable package from releases, or download the source code, install the dependencies from the <code>requirements.txt</code> file and run the <code>main.py</code> file.

Once running, you'll need to configure the settings before the program will work properly.

At a minimum the following settings need to be set for the script to work:

1. Server IP/Query Port need to be set. These can be found at [battlemetrics](https://www.battlemetrics.com/servers/squad) and finding the information to the server you want to join.
2. Either a.) Player threshold, or b. ) Upper and lower bound of player threshold in addition to the <code>Use Random Player Threshold </code> setting being enabled.
3. Your player name. This needs to ideally be a distinct portion of your in game name, ideally without spaces.

[//]: # (3. Your player name. This needs to ideally be a distinct portion of your name, ideally without spaces.)


At this point, the program can perform the basic functionality of closing down the game once it hits the player threshold.

If you want to use the autojoin feature, you need to additionally set the following settings:

1. Enable the <code>Automatic Server Joining</code> setting
2. Server Handle - A distinct, recognizable portion of the name that can be seen in the server browser. Ideally this should be without spaces.

Once these settings are enabled, the program can now automatically start the game, join the specified server, and then exit once done.

[//]: # (<code></code>)


# Ogame-Bot 

Intelligent BOT playing in Ogame

## Features

* building buildings
* transporting resources
* SMS notifications about incoming attack(s) (relies on a Polish SMS API, so that's not really working right now)
* sending messages to attacker
* fleet save
* farming (hell yeah!)
* sending expeditions (NOT TESTED)
* and many more!

## Usage

Adjust your credentials and other settings in `config.ini` file.

    pip install -r requirements.txt
    python bot.py
    
If there are still some dependencies problems, these commands might help:

    pip install --upgrade beautifulsoup4
    pip install --upgrade html5lib

Thanks to r4fek whom i started editing the code from

Inside the `config.ini` file, multiple settings can be tweaked:

###### Credentials
 - uni: The universe in which you're playing (eg. https://s128-it.ogame.gameforge.com is universe 128)
 - server : The server you're currently playing in (eg. https://s128-it.ogame.gameforge.com is 'it' without commas)
 - username : Your account email
 - password : Your account password

###### General
 - seed : Needed togheter with `check_intervals` to define the sleeping time between various logins
 - check_interval : Needed togheter with `seed` to define the sleeping time between various logins
 - timeout : General socket timeout

###### Building
 - max_fusion_plant_level : Self-explanatory
 - levels_diff : Used to regulate mines level

###### Station
 - enabled : Enables automatic staion upgrades
 - priority : Station to give priority to, possible structures are : 
   - roboticsFactory
   - shipyard
   - researchLab
   - allianceDepot
   - missileSilo
   - naniteFactory
   - terraformer
   - spaceDock
 - levels_diff : Maximum level difference between the `priority` station and the others

###### Research
 - enabled : Enables automatic research upgrade
 - high_prior : Researches to prioritize the most, possible researches are:    
   - energyTech
   - laserTech 
   - ionTech
   - hyperspaceTech
   - plasmaTech
   - combustionDrive
   - impulseDrive
   - hyperspaceDrive
   - espionageTech
   - computerTech
   - astrophysics
   - intergalacticRes
   - gravitonTech
   - weaponTech
   - shieldingTech
   - armourTech
 - medium_prior : Researches to prioritize less
 - low_prior : 'meh' researches

###### Attack
 - max_ships : Max ships to keep in the attacked planet
 - messages : Message to send to the attacker
 - message_topic : Message topic

###### Farming
 - farms : List of inactive planets to farm, without ANY pity (eg. x:y:z x1:y1:z1 ecc..)
 - ships_kind : Ships to send to farm the planet
 - ships_number : Number of `ships_kind` to send to the farmed planet

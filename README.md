# Ladybug-Randomizer
A randomizer for Touhou Luna Nights and Deedlit in Wonder Labyrinth, the two metroidvania games made by Team Ladybug

![Screenshot (754)](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/f0bd7e80-4215-47c9-93d3-5b70f0f7ea52)

![Screenshot (711)](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/7c681014-ad59-4c08-8ead-eaf25f60d4e4)

![Screenshot (757)](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/d0f4459f-1c98-4723-88e0-e4a6a8bd37ae)

## Item Randomization

Randomize item pickups using logic that will guarantee that the game will always be completable. You can customize the complexity level of the placement and select which item types should be included or excluded from the random item pool. Excluded item types will only be shuffled within themselves.

![vlcsnap-2024-01-12-21h04m54s474](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/517dc839-3970-4d7c-8541-da5db9a7562a)

![vlcsnap-2024-01-15-12h25m21s920](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/a2bba2c0-2c42-45bb-b093-52ebca95486f)

## Enemy Randomization

Randomize enemy types, this is similar to the concept of enemizers minus the facts that enemy stats or positions cannot be edited. This creates a simple, systemic enemy shuffle where you can customize the possible tier difference of enemies that appear.

![vlcsnap-2024-01-12-21h09m49s346](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/11b1f995-ba95-4d03-8940-3448c0702f39)

![vlcsnap-2024-01-30-08h28m45s953](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/63077f4e-3c5e-4458-a271-01e64dc2f2db)

## Music Randomization

Randomize which bgm tracks play for levels, bosses and events. This only shuffles them by type, meaning that you will not hear boss music play in a regular level.

## Color Randomization

Randomize the hue of many types of in-game sprites. This edits the texture assets directly to provide as much color variety as possible while still retaining balanced-looking visuals.

![vlcsnap-2024-01-30-08h24m48s551](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/45749517-b3ea-4b82-9fee-fc4f291a3a43)

![vlcsnap-2024-01-30-08h25m51s366](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/8d4978b6-4561-47ac-8c7a-949cd65355a0)

## Dialogue Randomization

Randomize the conversation lines that characters can say during events and cutscenes. This can also restructure sentences at random similarily to the dialogue rando implemented in DSVrando.

![vlcsnap-2024-01-23-17h03m02s579](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/13a146ee-401a-4580-93e8-51eaf6b1b343)

![vlcsnap-2024-01-23-17h05m16s558](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/446f54a7-d7a8-4b70-a2f0-93cb1b5f1da3)

## Reverse Rando

Start the game from the top of the map and make your way down to find the items required to reach the end. Using the item tracker's warp to start feature may be required to beat the game in that mode.

![vlcsnap-2024-01-23-10h22m28s726](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/e40f638b-3d85-4cd3-afd5-eb5198286974)

![vlcsnap-2024-01-23-10h23m34s030](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/4a5cc568-e664-4f14-9f5e-bcf1932508ef)

## Require All Keys

Block off the final boss with all colored doors/gates, forcing you to collect all colored keys/switches to finish the rando.

![vlcsnap-2024-01-30-08h23m32s954](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/ee465606-bc56-4b0a-b1a2-bd6e25fac840)

![vlcsnap-2024-01-30-08h25m06s782](https://github.com/Lakifume/Ladybug-Randomizer/assets/56451477/07f73eab-8c4a-4390-a437-3e889d6ca6ed)

## Stage 6 Unlocked

Unlock Luna Night's extra stage from the start of the game without having to reach Flandre beforehand, also affecting the logic.

## Skip Boss Rush

Remove the endgame boss rush in Wonder Labyrinth's last stage, simplifying relatively quick seeds.

## Speedrun Logic

Toggle a more advanced item logic that may require in-depth knowledge of the game's tricks as well as taking more risks to reach an item.

# Setup

Run the executable and start by specifying the path to where your game is installed. From there simply pick your options and press Randomize.
If you are unusure what an option does hover over its widget to see a tooltip.
You also have the option to automatically restore your game directory to its original state afterwards.
And if you get stuck at any point and need to look at the solution use the Load Spoiler option and select the corresponding spoiler log.

# Things to note

- Progression abilities in both games were programmed to work in a skill tree fashion rather than each giving a unique ability, so pickup up any of them will only progress you to the next ability.
- The only exception to the skill tree rule is Wonder Labyrinth's high jump which straight up gives you every ability at once.
- The 2nd, 3rd and 4th randomization options determine whether these item types will be included in the random item pool. If unselected each type will simply be shuffled within itself.
- The less item randomization options that you select alongside Key Items the more likely a seed is to fail generating due to the restricted amount of options for the next key to be placed without making the game unbeatable.
- Due to limitations the Ice Magatama and first Eternal Clock items will not be randomized if the only options selected alongside Key Items is Gem Towers
- Tilesets were edited in a few spots to avoid softlocks or conflicts.
- The 50x jump platform in stage 1 of Wonder Labyrinth was replaced by a soul gate. The soul crusher check will now require all soul keys to get to.
- Due to having to edit large assets the mod will take longer to generate if music or color randomization is selected.
- The item tracker has an option to warp you back to your initial spawn location which may be required to complete reverse rando seeds.

# Troubleshooting

- If the program fails to open when double clicking the exe open it via command prompt instead to be able to read the error.
- If you get an error get the zip file again, right click on it, go to Properties, check Unblock and extract again.
- If problems still persist open an issue on Github and try to be as specific as possible.

# Changelog

1.1.0:
- Added an option for starting the game from the top of the map
- Added an option to unlock Luna Nights's extra stage from the start
- Added an option to require all colored keys to beat the game
- Implemented save file editing to remove problematic cutscenes
- Implemented a semi-automatic item and boss tracker
- Added an option to warp to the start in the item tracker
- Moved the built-in extra game modes to the rando interface
- Included basic downthrow/downslash hovers in the default logic
- Included minor damage boosts in the default Wonder Labyrinth logic
- Replaced speedrun logic in Wonder Labyrinth by hitless logic when OHKO mode is on
- Fixed some of the major volume differences in music rando

1.0.0:
- Added an option to randomize background music
- Added options to randomize the color of sprites
- Added an option to randomize dialogues
- Added an option for speedrun logic (experimental)
- Added an option to skip Wonder Labyrinth's boss rush
- Included Nitori's first stopwatch in the randomization
- Included Wonder Labyrinth's first bow in the randomization

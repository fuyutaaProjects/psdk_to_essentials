# psdk_to_essentials
 Convert PSDK Pokedex made in PKM Studio to PKM Essentials Pokedex.

## What is this ?
It's a tool made to speed up your fangame developpement process!
When creating your new pokedex for your fangame, you might be adding new fakemons, and using already existing pokemons.
You then have two options: you either:
- use PSDK's starterkit fresh and clean pokedex editor app (PKM Studio)
- or use Pokémon Essentials starterkit and edit an old and ugly txt file. 

**But with this script, you can use PSDK's Pokémon Studio to make your pokedex and then import your pokedex onto Pokémon Essentials!**

## Why? Like wtf PSDK is supposed to be the new and better starterkit!
Yeee, but PSDK doesn't have tutorials. Essentials have a long and perfect documentation, and so I prefer working on Essentials than PSDK, but still want to use their Pokémon Studio app to make my pokedex.
So I made a converter PSDKDEX > EssentialsDEX.

## How does it work?
so basically what this script does is that it will get the name of each of your fakemons through the frontsprites pngs placed in ./FRONTSPRITES_HERE
it will get the name of each file placed in that folder, and parse the files names to get only the fakemon names (file is in format "fs_[fakemonname.png]" all lowercase).
then with that list of names, it will begin searching for the matching .JSON file. 

After finding all the corresponding JSONS for each fakemon, it will begin writing a new pokemon.txt file (the one used by PBS in Pokémn Essentials).
Longgg editing but you'll get your pokedex converted after that.

##Why does it need to search? 
Because the fakemon json file name doesn't correspond the new pokemon's the name, but the original pokemon name.

See manual.md to see how you can use this script.

genderless pokemon not supported
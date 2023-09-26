## How To Use

Before usage:

### ⚠️⚠️MAKE SURE YOUR FAKEMONS SPRITES FILES ARE NAMED ONLY BY THE FAKEMON NAME!⚠️⚠️
>works: chlorofyte.png
>does not work: chlorofyte_shiny

Right now you should have a Pokedex made in Pokémon Studio where you imported your fakemons over already existing pokemons.
You have imported the stats, the fakemon uses the previous pokémon's moveset and you imported the sprites.

1. Put all you fakemons sprites in the 'fs' folder.

2. Convert your fakemons sprites to PNGs with the following name format: fs_[name].png
To automatically rename your fakemons, run fs_renamer.py. It will reformat every file's name in the 'fs' folder.
fs_renamer.py will lowercase and add fs_ before your fakemon's name.

3. Copy the 'pokemon' folder from PSDK located at [PROJECT NAME]\Data\Studio\ to the root of this folder (the same level as main.py)

4. Copy pokemon.txt from Essentials 

5. Copy the dex folder from PSDK to root of this repertory
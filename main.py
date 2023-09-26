import os
import json

# gets fakemons names from the PNGs located in the 'fs' folder
def get_fakemons_names(): 
    l_files = os.listdir('fs/')
    l_fakemons_names= [s[s.find('fs_')+len('fs_'):s.rfind('.png')] for s in l_files]
    return l_fakemons_names

# Function to recursively search for fakemon name in JSON files
def search_match(directory, searched_fakemon_name):
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if data['forms'][0]['resources']['icon'].lower() == searched_fakemon_name:
                        return file_path
    return None  # No match found in any JSON file

# Note: the problem with this function is that it cannot search for the fakemon's name, as the dbSymbol is still the original pokemon name.
# We will have to use a translator that can translate from OG name to fakemon.
def get_pokedex_order(): 
    l_pokedex_order = []
    with open('./dex/national.json', 'r') as national_dex_file: # only supported dex is national. remove regional.
        data_national_dex = json.load(national_dex_file)
        for creature_dict in data_national_dex['creatures']:
            l_pokedex_order.append(creature_dict['dbSymbol'])
    return l_pokedex_order


def ability_and_move_name_formatter(txt):
    if '_' in txt:
        return txt.replace('_', '').upper()
    else:
        return txt.upper()
    
def main():
    try:
        os.remove("new_pokemon.txt")
        print('Deleted previously exported file "new_pokemon.txt".')
    except FileNotFoundError:
        print("new_pokemon.txt not found so not deleted.\n(it's the exported file by this script: the one made by the previous execution of that script gets deleted each time you start the script.)")
    
    # Get corresponding JSONs paths:
    # Replace 'your_directory_path' with the path to your directory if not 'pokemon'
    directory_path = './pokemon/'
    l_fakemons_names = get_fakemons_names()
    corresponding_path_dict = {}

     # example when filled by script: ogname_to_newname_dict['bulbasaur'] returns 'chlorofyte' (the mon i wrote over bulbasaur)
     # when retrieving pokedex order, we retrieve a list containing the JSONs files names, so not the actual mons names
     # Because the JSON and national.json cannot change names, and the new pokemon's name is contained in dbSymbol.
     # (I overwrote bulbasaur's name in Pokémon Studio as Chlorofyte.)
     # So when we'll have the dict of JSONs paths (example: corresponding_path_dict['chlorofyte'] returns path to bulbasaur.json)
     # we will translate bulbasaur to chlorofyte using this dict.
     # this dict is used for the pokedex order.
    ogname_to_newname_dict = {} 
     # sorry if it's complicated to understand and explained poorly, i'm trying to gain time here, 
     # and not make a perfectly explained tool ^^'

    for fakemon_name in l_fakemons_names:
        result =  search_match(directory_path, fakemon_name)
        if result:
            print(f"Found {fakemon_name} in file: {result}")
            corresponding_path_dict[fakemon_name] = result
            ogname_to_newname_dict[result[10:result.rfind('.json')]] = fakemon_name # if the directory is not .pokemon/ IT WILL CRASH. But it should be, i said it in the manual.
            #print(f'ogname to newname dict new entry added: {result[10:result.rfind(".json")]} = {fakemon_name}')
        else:
            print("No match found in any JSON file for " + fakemon_name + ".")
    
    # Get pokedex order
    l_pokedex_by_order = get_pokedex_order()
    
    # Data Writer
    with open('new_pokemon.txt', 'w') as new_pokemon_txt:
        for entry_as_og_mon_name in l_pokedex_by_order:
            try:
                if corresponding_path_dict[ogname_to_newname_dict[entry_as_og_mon_name]]:
                    print(f'{ogname_to_newname_dict[entry_as_og_mon_name]} named as {entry_as_og_mon_name} in nationaldex json found in pokedex order and in fakemon paths. Writing data...')

                    # Writing block of data
                    with open(corresponding_path_dict[ogname_to_newname_dict[entry_as_og_mon_name]], 'r') as mon_json:
                        new_pokemon_txt.write('\n#-------------------------------')
                        new_pokemon_txt.write(f'\n[{ogname_to_newname_dict[entry_as_og_mon_name].upper()}]')
                        new_pokemon_txt.write('\nName = ' + ogname_to_newname_dict[entry_as_og_mon_name].capitalize())
                        json_data = json.load(mon_json)
                        if json_data['forms'][0]['type2'] == '__undef__':
                            new_pokemon_txt.write(f'\nTypes = {json_data["forms"][0]["type1"].upper()}')
                        else:
                            new_pokemon_txt.write(f'\nTypes = {json_data["forms"][0]["type1"].upper()}, {json_data["forms"][0]["type2"].upper()}')
                            #print(ogname_to_newname_dict[entry_as_og_mon_name] + {mon_json["forms"]["type1"].upper()} + {mon_json["forms"]["type2"].upper()})
                        new_pokemon_txt.write(f'\nBaseStats = {json_data["forms"][0]["baseHp"]},{json_data["forms"][0]["baseAtk"]},{json_data["forms"][0]["baseDfe"]},{json_data["forms"][0]["baseSpd"]},{json_data["forms"][0]["baseAts"]},{json_data["forms"][0]["baseDfs"]}')
                        
                        female_rate_numberical_val = min([-1, 0, 12.5, 25, 50, 75, 87.5, 100], key=lambda x:abs(x-json_data["forms"][0]["femaleRate"]))
                        translated_female_rate_vals = {
                            "-1": "Genderless",
                            "0": "AlwaysMale",
                            "12.5": "FemaleOneEighth",
                            "25": "Female25Percent",
                            "50": "Female50Percent",
                            "75": "Female75Percent",
                            "87.5": "FemaleSevenEights",
                            "100": "AlwaysFemale"
                        }
                        new_pokemon_txt.write(f'\nGenderRatio = {translated_female_rate_vals[str(female_rate_numberical_val)]}') # genderless not supported
                        
                        growthrate_psdk_to_essentials = {
                            0: "Fast", # Rapide
                            1: "Medium", # Normal
                            2: "Slow", # Lent
                            3: "Parabolic", # Parabolique
                            4: "Erratic", # Erratique
                            5: "Fluctuating" # Fluctuante
                        }


                        # GrowthRate
                        new_pokemon_txt.write(f'\nGrowthRate = {growthrate_psdk_to_essentials[json_data["forms"][0]["experienceType"]]}')


                        # BaseExp
                        new_pokemon_txt.write(f'\nBaseExp = {json_data["forms"][0]["baseExperience"]}')


                        # EVs
                        already_wrote_a_ev_stat = False # we need ',' punctation if there's two EV stats
                        new_pokemon_txt.write(f'\nEVs = ')
                        if json_data["forms"][0]["evHp"] != 0:
                            if already_wrote_a_ev_stat:
                                new_pokemon_txt.write(',')
                            new_pokemon_txt.write(f'HP,{json_data["forms"][0]["evHp"]}')
                            already_wrote_a_ev_stat = True

                        if json_data["forms"][0]["evAtk"] != 0:
                            if already_wrote_a_ev_stat:
                                new_pokemon_txt.write(',')
                            new_pokemon_txt.write(f'ATTACK,{json_data["forms"][0]["evAtk"]}')
                            already_wrote_a_ev_stat = True

                        if json_data["forms"][0]["evDfe"] != 0:
                            if already_wrote_a_ev_stat:
                                new_pokemon_txt.write(',')
                            new_pokemon_txt.write(f'DEFENSE,{json_data["forms"][0]["evDfe"]}')
                            already_wrote_a_ev_stat = True

                        if json_data["forms"][0]["evSpd"] != 0:
                            if already_wrote_a_ev_stat:
                                new_pokemon_txt.write(',')
                            new_pokemon_txt.write(f'SPEED,{json_data["forms"][0]["evSpd"]}')
                            already_wrote_a_ev_stat = True

                        if json_data["forms"][0]["evAts"] != 0:
                            if already_wrote_a_ev_stat:
                                new_pokemon_txt.write(',')
                            new_pokemon_txt.write(f'SPECIAL_ATTACK,{json_data["forms"][0]["evAts"]}')
                            already_wrote_a_ev_stat = True

                        if json_data["forms"][0]["evDfs"] != 0:
                            if already_wrote_a_ev_stat:
                                new_pokemon_txt.write(',')
                            new_pokemon_txt.write(f'SPECIAL_DEFENSE,{json_data["forms"][0]["evDfs"]}')
                            already_wrote_a_ev_stat = True


                        # CatchRate
                        new_pokemon_txt.write(f'\nCatchRate = {json_data["forms"][0]["catchRate"]}')


                        # Hapiness
                        new_pokemon_txt.write(f'\nHappiness = {json_data["forms"][0]["baseLoyalty"]}')


                        # Abilities
                        if '_' in json_data["forms"][0]["abilities"][0]:
                            abilities_str_result = (json_data["forms"][0]["abilities"][0].replace('_', '')).upper()
                        else:
                            abilities_str_result = json_data["forms"][0]["abilities"][0].upper()

                        if json_data["forms"][0]["abilities"][0] != json_data["forms"][0]["abilities"][1]:
                            if '_' in json_data["forms"][0]["abilities"][1]:
                                abilities_str_result = abilities_str_result + ',' + json_data["forms"][0]["abilities"][1].replace('_', '').upper()
                            else:
                                abilities_str_result = abilities_str_result + ',' + json_data["forms"][0]["abilities"][1].upper()
                        
                        #print(f'appending abilities str result: {abilities_str_result}')
                        new_pokemon_txt.write(f'\nAbilities = {abilities_str_result}')

                        
                        # Hidden Ability
                        hidden_ability_str_result = ''
                        if json_data["forms"][0]["abilities"][1] != json_data["forms"][0]["abilities"][2] and json_data["forms"][0]["abilities"][0] != json_data["forms"][0]["abilities"][2]: # hidden 
                            if '_' in json_data["forms"][0]["abilities"][2]:
                                hidden_ability_str_result = json_data["forms"][0]["abilities"][2].replace('_', '').upper()
                            else:
                                hidden_ability_str_result = json_data["forms"][0]["abilities"][2].upper()
                        
                        if hidden_ability_str_result != '':
                            new_pokemon_txt.write(f'\nHiddenAbilities = {hidden_ability_str_result}')


                        # Moves
                        print('reached #moves')
                        moveset_str_result = ''
                        for move_dict in json_data["forms"][0]["moveSet"]:
                            if moveset_str_result != '':
                                moveset_str_result += ','
                            moveset_str_result += f'{move_dict["level"]},{ability_and_move_name_formatter(move_dict["move"])}'
                            print(moveset_str_result)
                        
                        print('reached writing moves')
                        new_pokemon_txt.write(f'\nMoves = {moveset_str_result}')
                        new_pokemon_txt.write(f'\nTutorMoves = ')
                        new_pokemon_txt.write(f'\nEggMoves = ')
                        new_pokemon_txt.write(f'\nEggGroups = ')
                        new_pokemon_txt.write(f'\nHatchSteps = ')
                        new_pokemon_txt.write(f'\nHeight = ')
                        new_pokemon_txt.write(f'\nWeight = ')
                        new_pokemon_txt.write(f'\nColor = ')
                        new_pokemon_txt.write(f'\nShape = ')
                        new_pokemon_txt.write(f'\nHabitat = ')
                        new_pokemon_txt.write(f'\nCategory = ')
                        new_pokemon_txt.write(f'\nPokedex = ')
                        new_pokemon_txt.write(f'\nGeneration = ')
                        new_pokemon_txt.write(f'\nEvolutions = ')
            except:
                print(f'{entry_as_og_mon_name} was found in national.json but not in the fakemon JSONs paths list. Cannot be processed.')

main()

"""
#-------------------------------
[BULBASAUR]
Name = Bulbasaur
Types = GRASS,POISON
BaseStats = 45,49,49,45,65,65
GenderRatio = FemaleOneEighth
GrowthRate = Parabolic
BaseExp = 64
EVs = SPECIAL_ATTACK,1
CatchRate = 45
Happiness = 50
Abilities = OVERGROW
HiddenAbilities = CHLOROPHYLL
Moves = 1,TACKLE,1,GROWL,3,VINEWHIP,6,GROWTH,9,LEECHSEED,12,RAZORLEAF,15,POISONPOWDER,15,SLEEPPOWDER,18,SEEDBOMB,21,TAKEDOWN,24,SWEETSCENT,27,SYNTHESIS,30,WORRYSEED,33,DOUBLEEDGE,36,SOLARBEAM
TutorMoves = AMNESIA,ATTRACT,BIND,BODYSLAM,BULLETSEED,CAPTIVATE,CHARM,CONFIDE,CUT,DEFENSECURL,DOUBLEEDGE,DOUBLETEAM,ECHOEDVOICE,ENDURE,ENERGYBALL,FACADE,FALSESWIPE,FLASH,FRUSTRATION,FURYCUTTER,GIGADRAIN,GRASSKNOT,GRASSPLEDGE,GRASSYGLIDE,GRASSYTERRAIN,HEADBUTT,HELPINGHAND,HIDDENPOWER,KNOCKOFF,LEAFSTORM,LIGHTSCREEN,MAGICALLEAF,MIMIC,MUDSLAP,NATURALGIFT,NATUREPOWER,POWERWHIP,PROTECT,REST,RETURN,ROCKSMASH,ROUND,SAFEGUARD,SECRETPOWER,SEEDBOMB,SLEEPTALK,SLUDGEBOMB,SNORE,SOLARBEAM,STRENGTH,STRINGSHOT,SUBSTITUTE,SUNNYDAY,SWAGGER,SWORDSDANCE,SYNTHESIS,TOXIC,VENOSHOCK,WEATHERBALL,WORKUP,WORRYSEED
EggMoves = AMNESIA,CHARM,CURSE,GRASSYTERRAIN,INGRAIN,LEAFSTORM,MAGICALLEAF,NATUREPOWER,PETALDANCE,POWERWHIP,SKULLBASH,SLUDGE,TOXIC
EggGroups = Monster,Grass
HatchSteps = 5120
Height = 0.7
Weight = 6.9
Color = Green
Shape = Quadruped
Habitat = Grassland
Category = Seed
Pokedex = Bulbasaur can be seen napping in bright sunlight. There is a seed on its back. By soaking up the sun's rays, the seed grows progressively larger.
Generation = 1
Evolutions = IVYSAUR,Level,16
"""
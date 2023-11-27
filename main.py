import os, json, math, csv, sys
from numpy import sqrt 

#------------------------------------------------------------------------#
# script is not optimized, but it doesn't matter as it runs only one time.
# i don't have munch time left for my game, i did this really quick and it
# looks ugly. don't expect clean code, it's not made to be 
# edited by someone else.
#------------------------------------------------------------------------#


# used for the field 'Color' in the pokemon's entries in Essentials PBS.
# pip install colorthief
from colorthief import ColorThief 


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

# Function to calculate Euclidean distance between two RGB colors
def calculate_distance(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def closest_color(rgb, COLORS):
    r, g, b = rgb
    color_diffs = []
    for color in COLORS:
        cr, cg, cb = color
        color_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]

def read_species_csv():
    with open('100001.csv', 'r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = list(csv_reader)
        return rows
    
def read_pokedex_descriptions_csv():
    with open('100002.csv', 'r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = list(csv_reader)
        return rows

pokedex_descriptions_reader = read_pokedex_descriptions_csv()

species_csv_reader = read_species_csv()
# print(species_csv_reader[2][1]) returns species 'fr' row (returns 'Pokémonn Feuille' from my sample file)

def create_ogname_to_newname_dict(): # returns the og pokemon name to the new one that you gave it.
    ogname_to_newname_dict = {}
    for root, _, files in os.walk('./pokemon/'):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    ogname_to_newname_dict[filename.split('.')[0]] = data['forms'][0]['resources']['icon'].lower() # will crash if the fakemon has a composed name
    return ogname_to_newname_dict

ogname_to_newname_dict = create_ogname_to_newname_dict()
def get_pokedex_in_order():
    pokedex_in_order = []
    with open('./dex/national.json', 'r') as nationaldexjson:
        json_data = json.load(nationaldexjson)
        for pokemon in json_data['creatures']:
            pokedex_in_order.append(ogname_to_newname_dict[pokemon['dbSymbol']])
    return pokedex_in_order

pokedex_in_order = get_pokedex_in_order()

# returns pokémon specie, but it's called 'category' for some reason.
def get_category(pokemon_name):
    return species_csv_reader[pokedex_in_order.index(pokemon_name)][1]

def get_pokedex_description(pokemon_name):
    return pokedex_descriptions_reader[pokedex_in_order.index(pokemon_name)][1]

"""
maps # if player is on a map: id can be a list of maps, separated by commas. NON SUPPORTED
gender # en fonction du genre NON SUPPORTED
0 # unknown
1 # male
2 # female
func # selon une fonction, value field contains function name. # NON SUPPORTE
"""

time_psdk_to_essentials = {
    0: 'Night',
    1: 'Evening',
    2: 'Morning',
    3: 'Day',
    4: 'Afternoon'
}

# there's a lot of dirty stuff here. also the max and min versions are wierd, i don't care i just apply same variable to both cases. minloyalty or maxloyalty, weird concept.

# If it could not process the evolution condition, it sends an error message in the console and replace the 
# returned_str by ERROR_EVOL_CONDITION so that you can search it in the txt file.
def generate_evolution_str(og_pokemon_name):
    pokemon_name = ogname_to_newname_dict[og_pokemon_name]
    returned_str = ''
    with open(f'./pokemon/{og_pokemon_name}.json', 'r') as json_file:
        json_data = json.load(json_file)
        n_of_evol_dicts = len(json_data["forms"][0]["evolutions"])

        if n_of_evol_dicts == 0:
            return 'NO_EVOLUTIONS'
        
        processed_next_dict = False
        for i in range(n_of_evol_dicts):
            #print(f'i: {i}, str: {returned_str}, n_evols_dicts: {n_of_evol_dicts}')
            if processed_next_dict != True:
                try:
                    c_dict = json_data["forms"][0]["evolutions"][i] # getting evolution dict
                    e_type = c_dict["conditions"][0]["type"]
                    evolution_name_fc = ogname_to_newname_dict[c_dict["dbSymbol"]].upper()

                    if e_type == 'dayNight':
                        time = time_psdk_to_essentials[c_dict["conditions"][0]["value"]]
                        try: # probably breaks
                            if i < n_of_evol_dicts:
                                next_dict = json_data["forms"][0]["evolutions"][i+1] # getting second evolution dict
                                e_type_next_dict = next_dict["conditions"][0]["type"]
                                if e_type_next_dict == 'Level' or e_type_next_dict == 'minLevel' or e_type_next_dict == 'maxLevel':
                                    returned_str += f'{evolution_name_fc},Level{time},{str(next_dict["conditions"][0]["value"])}'
                                if e_type_next_dict == 'minLoyalty' or e_type_next_dict == 'maxLoyalty':
                                    returned_str += f'{evolution_name_fc},Hapiness{time},{str(next_dict["conditions"][0]["value"])}'
                                processed_next_dict = True
                            else:
                                print(f'Got time parameter for {pokemon_name}, but no additional one. Cannot process.')
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print('Exception in e_type dayNight:', ogname_to_newname_dict[pokemon_name], exc_type, fname, exc_tb.tb_lineno, e)

                    elif e_type in ['minLevel', 'maxLevel', 'Level']:
                        print(f'{pokemon_name}: e_level is Level related')
                        if i+2 <= n_of_evol_dicts:
                            print('i = ', i)
                            next_dict = json_data["forms"][0]["evolutions"][i+1] # getting second evolution dict
                            e_type_next_dict = next_dict["conditions"][0]["type"]

                            print(f'{pokemon_name} || next_dict: {next_dict}, e_type_n_dict: {e_type_next_dict}')
                            if e_type_next_dict == 'weather':
                                print('detected weather field in 2nd dict')
                                weather = next_dict["conditions"][0]["value"]
                                if weather == 'rain' or weather == 'hardrain':
                                    if returned_str != '': returned_str += ','
                                    returned_str += f'{evolution_name_fc},LevelRain,{str(c_dict["conditions"][0]["value"])}'
                                    processed_next_dict = True
                                if weather == 'sunny' or weather == 'hardsun':
                                    processed_next_dict = True
                                    if returned_str != '': returned_str += ','
                                    returned_str += f'{evolution_name_fc},LevelSun,{str(c_dict["conditions"][0]["value"])}'
                                    processed_next_dict = True
                                if weather == 'sandstorm':
                                    if returned_str != '': returned_str += ','
                                    returned_str += f'{evolution_name_fc},LevelSandstorm,{str(c_dict["conditions"][0]["value"])}'
                                    processed_next_dict = True
                                if weather == 'hail':
                                    if returned_str != '': returned_str += ','
                                    returned_str += f'{evolution_name_fc},LevelSnow,{str(c_dict["conditions"][0]["value"])}'
                                    processed_next_dict = True
                                if weather == 'fog': # unsupported by essentials, so i just change it to LevelDarkness
                                    if returned_str != '': returned_str += ','
                                    returned_str += f'{evolution_name_fc},LevelDarkness,{str(c_dict["conditions"][0]["value"])}'
                                    processed_next_dict = True
                            else:
                                print('This pokemon has an evolution requirement that asks a specific level and another condition that this script does not support. The second condition will be skipped, and the evolution condition will be written as only requiring a minimal level of the level found in the json file.')
                                if returned_str != '': returned_str += ','
                                returned_str += f'{evolution_name_fc},Level,{str(c_dict["conditions"][0]["value"])}'

                        else:
                            print('in minlevel else for: ', pokemon_name)
                            if returned_str != '': returned_str += ','
                            returned_str += f'{evolution_name_fc},Level,{str(c_dict["conditions"][0]["value"])}'

                    

                    elif e_type == 'trade':
                        returned_str += f'{evolution_name_fc},Trade,'

                    elif e_type == 'tradeWith':
                        print('e type is tradewith')
                        returned_str += f'{evolution_name_fc},Level,{str(ogname_to_newname_dict[c_dict["conditions"][0]["value"]]).upper()}'
                    
                    elif e_type == 'itemHold':
                        print('e type is itemHold')
                        returned_str += f'{evolution_name_fc},HoldItem,{c_dict["conditions"][0]["value"].upper().replace("_", "")}'

                    elif e_type == 'maxLoyalty' or e_type == 'minLoyalty':
                        print('e type is max/minloyalty')
                        returned_str += f'{evolution_name_fc},MaxHapiness,{str(c_dict["conditions"][0]["value"])}'
                        -1
                        
                    elif e_type == 'skill1':
                        print('e type is skill1')
                        returned_str += f'{evolution_name_fc},HasMove,{c_dict["conditions"][0]["value"].upper().replace("_", "")}'

                    elif e_type == 'env':
                        print('e type is env')
                        returned_str += f'{evolution_name_fc},Location,{str(c_dict["conditions"][0]["value"])}'

                    elif e_type == 'stone':
                        print('e type is stone')
                        if returned_str != '': returned_str += ','
                        returned_str += f'{evolution_name_fc},Item,{c_dict["conditions"][0]["value"].upper().replace("_", "")}'
                    
                    else:
                        print('e_type non supported')
                        returned_str += f'ERROR_EVOL_CONDITION'


                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print('ERROR evol function', ogname_to_newname_dict[pokemon_name], exc_type, fname, exc_tb.tb_lineno, e)
                n_of_evol_dicts -= 1
            else:
                processed_next_dict = False

        return returned_str


colors = [
    (0, 0, 0), #Black
    (127, 127, 127), #Gray
    (136, 0, 21), #Bordeaux
    (237, 28, 36), #Red
    (255, 127, 39), #Orange
    (255, 242, 0), #Yellow
    (34, 177, 76), #Green
    (203, 228, 253), #Blue
    (0, 162, 232), #Dark Blue
    (63, 72, 204), #Purple
    (255, 255, 255), #White
    (195, 195, 195), #Light Gray
    (185, 122, 87), #Light Brown
    (255, 174, 201), #Light Pink
    (255, 201, 14), #Dark Yellow
    (239, 228, 176), #Light Yellow
    (181, 230, 29), #Light Green
    (153, 217, 234), #Light Blue
    (112, 146, 190), #Dark Blue
    (200, 191, 231), #Light Purple
    (128, 0, 0), #Maroon
    (128, 128, 0), #Olive
    (0, 128, 0), #Green
    (128, 0, 128), #Purple
    (0, 128, 128), #Teal
    (0, 0, 128), #Navy
    (128, 64, 0), #Brown
    (255, 128, 0), #Hot Pink
    (128, 0, 128), #Dark Purple
    (128, 128, 128), #Medium Gray
    (192, 192, 192), #Silver
    (255, 0, 0), #Bright Red
    (255, 255, 0), #Bright Yellow
    (0, 255, 0), #Bright Green
    (0, 255, 255), #Bright Cyan
    (0, 0, 255), #Bright Blue
    (255, 0, 255), #Bright Magenta
    (139, 69, 19), #Saddle Brown
    (218, 112, 214), #Orchid
    (210, 105, 30), #Chocolate
    (165, 42, 42), #Brown
    (220, 20, 60), #Crimson
    (255, 182, 193), #Light Pink
    (255, 160, 122), #Light Salmon
    (255, 228, 181), #Moccasin
    (255, 165, 0), #Orange
    (255, 69, 0), #Red-Orange
    (255, 140, 0), #Dark Orange
    (255, 255, 224), #Light Yellow
    (255, 255, 0), #Yellow
    (0, 255, 127), #Spring Green
    (124, 252, 0), #Lawn Green
    (0, 128, 0), #Green
    (0, 250, 154), #Medium Spring Green
    (173, 216, 230), #Light Blue
    (0, 0, 128), #Navy
    (65, 105, 225), #Royal Blue
    (70, 130, 180), #Steel Blue
    (0, 0, 139), #Dark Blue
    (106, 90, 205), #Slate Blue
    (138, 43, 226), #Blue Violet
    (148, 0, 211), #Dark Violet
    (139, 0, 139), #Dark Magenta
    (128, 0, 128), #Purple
    (218, 112, 214), #Orchid
    (255, 105, 180), #Hot Pink
    (255, 20, 147), #Deep Pink
    (255, 182, 193), #Light Pink
    (255, 0, 255), #Fuchsia
    (139, 69, 19), #Saddle Brown
    (244, 164, 96), #Sandy Brown
    (255, 69, 0), #Red-Orange
    (255, 140, 0), #Dark Orange
    (255, 215, 0), #Gold
    (238, 232, 170), #Pale Goldenrod
    (255, 239, 0), #Yellow
    (154, 205, 50), #Yellow-Green
    (0, 128, 0), #Green
    (34, 139, 34), #Forest Green
    (0, 100, 0), #Dark Green
    (0, 255, 127), #Spring Green
    (124, 252, 0), #Lawn Green
    (173, 255, 47), #Green Yellow
    (0, 255, 0), #Lime
    (50, 205, 50), #Lime Green
    (240, 255, 240), #Honeydew
    (144, 238, 144), #Light Green
    (152, 251, 152), #Pale Green
    (0, 250, 154), #Medium Spring Green
    (127, 255, 0), #Chartreuse
    (173, 216, 230), #Light Blue
    (135, 206, 250), #Light Sky Blue
    (0, 191, 255), #Deep Sky Blue
    (70, 130, 180), #Steel Blue
    (30, 144, 255), #Dodger Blue
    (0, 0, 205), #Medium Blue
    (65, 105, 225), #Royal Blue
    (106, 90, 205), #Slate Blue
    (75, 0, 130), #Indigo
    (139, 0, 139) #Dark Magenta
]

basic_colors = {
    'Black': [
        (0, 0, 0), # Black
    ],
    'Blue': [
        (203, 228, 253), #Blue
        (0, 0, 128), # Navy
        (0, 0, 255), # Bright Blue
        (0, 162, 232), # Dark Blue
        (112, 146, 190), # Dark Blue
        (153, 217, 234), # Light Blue
        (112, 146, 190), # Dark Blue
        (0, 0, 128), # Navy
        (65, 105, 225), # Royal Blue
        (70, 130, 180), # Steel Blue
        (0, 0, 139), # Dark Blue
        (106, 90, 205), # Slate Blue
        (138, 43, 226), # Blue Violet
        (148, 0, 211), # Dark Violet
        (139, 0, 139), # Dark Magenta
        (136, 0, 21), # Bordeaux (Added)
        (0, 128, 128), #Teal
        (135, 206, 250), #Light Sky Blue (fnf reference??!?)
        (75, 0, 130), #Indigo
    ],
    'Brown': [
        (128, 64, 0), # Brown
        (165, 42, 42), # Brown
        (139, 69, 19), # Saddle Brown
        (139, 69, 19), # Saddle Brown
        (244, 164, 96), # Sandy Brown
        (185, 122, 87), # Light Brown (Added)
        (210, 105, 30), #Chocolate
    ],
    'Gray': [
        (127, 127, 127), # Gray
        (128, 128, 128), # Medium Gray
        (192, 192, 192), # Silver
        (195, 195, 195), # Light Gray
    ],
    'Green': [
        (0, 128, 0), # Green
        (0, 250, 154), # Medium Spring Green
        (34, 177, 76), # Green
        (181, 230, 29), # Light Green
        (0, 128, 0), # Green
        (34, 139, 34), # Forest Green
        (0, 100, 0), # Dark Green
        (0, 255, 127), # Spring Green
        (124, 252, 0), # Lawn Green
        (0, 128, 0), # Green
        (0, 250, 154), # Medium Spring Green
        (173, 216, 230), # Light Blue
        (0, 0, 128), # Navy
    ],
    'Pink': [
        (255, 174, 201), # Light Pink
        (255, 182, 193), # Light Pink
        (255, 255, 224), # Light Yellow
        (255, 255, 224), # Light Yellow
        (255, 255, 224), # Light Yellow
        (255, 128, 0), # Hot Pink
        (255, 20, 147), # Deep Pink
        (255, 182, 193), # Light Pink
        (255, 0, 255), # Fuchsia
        (255, 105, 180), # Hot Pink
        (255, 165, 0), # Orange (Added)
        (255, 69, 0), # Red-Orange (Added)
        (255, 140, 0), # Dark Orange (Added)
    ],
    'Purple': [
        (63, 72, 204), # Purple
        (128, 0, 128), # Dark Purple
        (128, 0, 128), # Purple
        (139, 0, 139), # Dark Magenta
        (136, 0, 21), # Bordeaux
        (148, 0, 211), # Dark Violet
        (200, 191, 231), # Light Purple
        (218, 112, 214), # Orchid
    ],
    'Red': [
        (128, 0, 0), # Maroon
        (237, 28, 36), # Red
        (255, 0, 0), # Bright Red
        (255, 69, 0), # Red-Orange
        (255, 140, 0), # Dark Orange
        (255, 255, 39), # Yellow (Added)
        (255, 165, 0), # Orange (Added)
        (255, 127, 39), #Orange
    ],
    'White': [
        (255, 255, 255), # White
    ],
    'Yellow': [
        (128, 128, 0), # Olive
        (239, 228, 176), # Light Yellow
        (255, 201, 14), # Dark Yellow
        (255, 242, 0), # Yellow
        (255, 255, 0), # Bright Yellow
        (255, 255, 224), # Light Yellow
        (255, 255, 0), # Yellow
        (255, 239, 0), # Yellow
        (154, 205, 50), # Yellow-Green
        (238, 232, 170), #Pale Goldenrod
        (255, 228, 181), #Moccasin
    ]
}



# Function to find the basic color for a given RGB tuple
def find_basic_color(rgb):
    for basic_color, rgb_list in basic_colors.items():
        if rgb in rgb_list:
            return basic_color
    return None



def main():
    try:
        os.remove("new_pokemon.txt")
        print('Deleted previously exported file "new_pokemon.txt".')
    except FileNotFoundError:
        print("new_pokemon.txt not found so not deleted.\n(it's the exported file by this script: the one made by the previous execution of that script gets deleted each time you start the script.)")

    # Get corresponding JSONs paths:
    directory_path = './pokemon/'
    l_fakemons_names = get_fakemons_names()
    corresponding_path_dict = {}
    ogname_to_newname_dict = {}

    for fakemon_name in l_fakemons_names:
        result = search_match(directory_path, fakemon_name)
        if result:
            print(f"Found {fakemon_name} in file: {result}")
            corresponding_path_dict[fakemon_name] = result
            ogname_to_newname_dict[result[10:result.rfind('.json')]] = fakemon_name
        else:
            print("No match found in any JSON file for " + fakemon_name + ".")

    # Get pokedex order
    l_pokedex_by_order = get_pokedex_order()

    # Data Writer
    with open('new_pokemon.txt', 'w', encoding='utf-8') as new_pokemon_txt:
        for entry_as_og_mon_name in l_pokedex_by_order:
            try:
                if corresponding_path_dict[ogname_to_newname_dict[entry_as_og_mon_name]]:
                    #print(f'{ogname_to_newname_dict[entry_as_og_mon_name]} named as {entry_as_og_mon_name} in nationaldex json found in pokedex order and in fakemon paths. Writing data...')

                    # Writing block of data
                    with open(corresponding_path_dict[ogname_to_newname_dict[entry_as_og_mon_name]], 'r') as mon_json:
                        pokemon_name = ogname_to_newname_dict[entry_as_og_mon_name]
                        
                        new_pokemon_txt.write('\n#-------------------------------')
                        new_pokemon_txt.write(f'\n[{pokemon_name.upper()}]')
                        new_pokemon_txt.write('\nName = ' + pokemon_name.capitalize())
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
                        moveset_str_result = ''
                        teachable_moves_str = ''  # Initialize teachable_moves_str
                        for move_dict in json_data["forms"][0]["moveSet"]:
                            if "level" in move_dict:
                                if moveset_str_result != '':
                                    moveset_str_result += ','
                                moveset_str_result += f'{move_dict["level"]},{ability_and_move_name_formatter(move_dict["move"])}'
                            else:
                                if teachable_moves_str != '':
                                    teachable_moves_str += ','
                                teachable_moves_str += ability_and_move_name_formatter(move_dict["move"])

                        # ... (continue writing other data)

                        new_pokemon_txt.write(f'\nMoves = {moveset_str_result}')
                        new_pokemon_txt.write(f'\nTutorMoves = {teachable_moves_str}')


                        # Egg groups
                        egg_groups_psdk_to_essentials = {
                            4: "Flying", # Aérien
                            11: "Amorphous", # Amorphe
                            2: "Water1", # Aquatique 1
                            12: "Water2", # Aquatique 2
                            9: "Water3", # Aquatique 3
                            14: "Dragon", # Draconique
                            6: "Fairy", # Féerique
                            8: "Humanlike", # Humanoide
                            15: "Undiscovered", # Inconnu
                            3: "Bug", # Insecte
                            13: "Ditto", # Métamorph
                            10: "Mineral", # Minéral
                            1: "Monster", # Monstre
                            0: "Undiscovered", # Non défini
                            5: "Field", # Terrestre
                            7: "Grass", # Végétal
                        }
                        if len(json_data["forms"][0]["breedGroups"]) > 1 and json_data["forms"][0]["breedGroups"][0] != json_data["forms"][0]["breedGroups"][1]:
                            new_pokemon_txt.write(f'\nEggGroups = {egg_groups_psdk_to_essentials[json_data["forms"][0]["breedGroups"][0]]}, {egg_groups_psdk_to_essentials[json_data["forms"][0]["breedGroups"][1]]}')
                        else:
                            new_pokemon_txt.write(f'\nEggGroups = {egg_groups_psdk_to_essentials[json_data["forms"][0]["breedGroups"][0]]}')

                        # HatchSteps
                        new_pokemon_txt.write(f'\nHatchSteps = {json_data["forms"][0]["hatchSteps"]}')


                        # Height
                        new_pokemon_txt.write(f'\nHeight = {json_data["forms"][0]["height"]}')


                        # Weight
                        new_pokemon_txt.write(f'\nWeight = {json_data["forms"][0]["weight"]}')

                        # Color: THIS FIELD DOES NOT EXIST IN PSDK !
                        # We're scanning the img to see what is the dominant color
                        try:
                            color_thief = ColorThief('./fs/fs_' + pokemon_name + '.png')
                            dominant_color = color_thief.get_color(quality=1)
                        except Exception as e:
                            print("Error in colorthief: " + str(e))

                        
                        closest_dominant = closest_color(dominant_color, colors)
                        # Example usage
                        basic_color = find_basic_color(closest_dominant)
                        rgb_color = closest_dominant
                        """
                        if basic_color:
                            print(f"{pokemon_name}: dominant is {dominant_color}, closest dominant is {closest_dominant} The basic color for ({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}) is {basic_color}")
                        else:
                            print(f"{pokemon_name}: dominant is {dominant_color}, closest dominant is {closest_dominant} but No basic color found for the given RGB.")
                        new_pokemon_txt.write(f'\nColor = {basic_color}')
                        """
                        new_pokemon_txt.write(f'\nColor = {basic_color}')


                        new_pokemon_txt.write(f'\nShape = MultiBody')


                        new_pokemon_txt.write(f'\nHabitat = Rare')


                        try: # because it's code that can break easily after modifications
                            new_pokemon_txt.write(f'\nCategory = {get_category(pokemon_name)}')
                        except Exception as e:
                            print(f'Error when writing "Category" field: {e}')
                        try:
                            new_pokemon_txt.write(f'\nPokedex = {get_pokedex_description(pokemon_name)}')
                        except Exception as e:
                            print(f'Error when writing "Pokedex" field: {e}')
                        
                        
                        # Generation
                        new_pokemon_txt.write(f'\nGeneration = 0')


                        # Evolutions
                        try:
                            evolutions_str = generate_evolution_str(entry_as_og_mon_name)
                            if evolutions_str == 'ERROR_EVOL_CONDITION':
                                print(f"{pokemon_name} : evolution method is not handled. Add it yourself.")
                            
                            elif evolutions_str == 'NO_EVOLUTIONS':
                                print(f"{pokemon_name} : has no evolutions.")

                            elif evolutions_str != '':
                                print(f"{pokemon_name} evolution str: {evolutions_str}")
                                new_pokemon_txt.write(f'\nEvolutions = {evolutions_str}')
                            
                            else:
                                print('got else somehow')

                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print('(evolutions at main) ERROR: ', ogname_to_newname_dict[entry_as_og_mon_name], exc_type, fname, exc_tb.tb_lineno, e)


            except Exception as e:
                continue
                #print(f'{entry_as_og_mon_name} was found in national.json but not in the fakemon JSONs paths list. Cannot be processed.')
                #print(f'Error: {e}')

main()
import os
with open('./pokemon/bulbasaur.json', 'r') as mon_json:
    print(mon_json['forms'][0]['resources']['icon'])
    print(mon_json['forms'][0]['type2'])
import json

finalPlayers = {}

with open('input/players.json', encoding="utf8") as json_file:
    players = json.load(json_file)
 
for idx, player in enumerate(players):
    finalPlayers[player['ID_Cyclist']] = {
        'ID_Cyclist': player['ID_Cyclist'],
        'Lastname': player['Lastname'],
        'Firstname': player['Firstname'],
        'FavRaces': player['FavRaces']
    }

with open('output/players_final.json', 'w', encoding="utf-8") as outfile:
    json.dump(finalPlayers, outfile, ensure_ascii=False)
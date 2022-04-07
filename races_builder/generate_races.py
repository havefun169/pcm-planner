import json
from datetime import datetime

helpBuilder = {}
WTRaces = {}
NTDays = {}
NTRaces = {}
otherRaces = {}
finalRaces = {}
biggestRow = -1

def getRaceRule(rid):
    for r_rule in races_rules:
        if r_rule['ID_Race'] == rid:
            return r_rule

    return None

def getStage(sid):
    for stage in stages:
        if stage['ID_Stage'] == sid:
            return stage

def getStageDayOfYear(day):
    datetimeObj = datetime.strptime(str(day), '%Y%m%d')
    return datetimeObj.timetuple().tm_yday

def getBestRow(r, fd, ld, sid):
    bestRow = r
    r = str(r)
    if 'row_' + r not in helpBuilder:
        helpBuilder['row_' + r] = {}

        for v in range(fd, ld+1):
            helpBuilder['row_' + r]['col_' + str(v)] = sid

        return bestRow

    for v in range(fd, ld+1):
        if 'col_' + str(v) in helpBuilder['row_' + r]:
            return getBestRow(bestRow + 1, fd, ld, sid)

    for v in range(fd, ld+1):
        helpBuilder['row_' + r]['col_' + str(v)] = sid

    return bestRow


with open('input/stages.json', encoding="utf8") as json_file:
    stages = json.load(json_file)

with open('input/races.json', encoding="utf8") as json_file:
    races = json.load(json_file)

with open('input/races_rules.json', encoding="utf8") as json_file:
    races_rules = json.load(json_file)
 
for idx, race in enumerate(races):
    firstStage = getStage(race['First_Stage'])
    lastStage = getStage(race['Last_Stage'])

    firstDay = getStageDayOfYear(firstStage['Date'])
    lastDay = getStageDayOfYear(lastStage['Date'])

    if race['UCI_Clas'] <= 8 or race['UCI_Clas'] in [20,21,33,34]:
        WTRaces[race['ID_Race']] = {
            'ID_Race': race['ID_Race'],
            'Name': race['Name'],
            'NameTitle': race['Name'],
            'Number_Stages': race['Number_Stages'],
            'UCI_Clas': race['UCI_Clas'],
            'FirstStageDay': firstDay,
            'LastStageDay': lastDay,
            'TotalDaysWithBreaks': (lastDay - firstDay) + 1,
        }
    elif race['UCI_Clas'] in [22,23]:

        if 'ITT' in race['Name']:
            raceName = race['Name'].split(" - ")[1] + "I"
        else:
            raceName = race['Name'].split(" - ")[1] + "R"

        if firstDay not in NTDays.keys():
            NTRaces[race['ID_Race']] = {
                'ID_Race': race['ID_Race'],
                'Name': race['Name'],
                'NameTitle': raceName,
                'Number_Stages': race['Number_Stages'],
                'UCI_Clas': race['UCI_Clas'],
                'FirstStageDay': firstDay,
                'LastStageDay': lastDay,
                'TotalDaysWithBreaks': (lastDay - firstDay) + 1,
            }
            NTDays[firstDay] = race['ID_Race']
        else:
            NTRaces[NTDays[firstDay]]["NameTitle"] += ", " + raceName
    else:
        otherRaces[race['ID_Race']] = {
            'ID_Race': race['ID_Race'],
            'Name': race['Name'],
            'NameTitle': race['Name'],
            'Number_Stages': race['Number_Stages'],
            'UCI_Clas': race['UCI_Clas'],
            'FirstStageDay': firstDay,
            'LastStageDay': lastDay,
            'TotalDaysWithBreaks': (lastDay - firstDay) + 1,
        }

    finalRaces = {**WTRaces, **NTRaces, **otherRaces}

for race in finalRaces:
    race = finalRaces[race]
    bestRow = getBestRow(1, race['FirstStageDay'], race['LastStageDay'], race['ID_Race'])
    race['BestRow'] = bestRow

    rr = getRaceRule(race['ID_Race'])
    if race['UCI_Clas'] in [20,21,33,34,22,23]:
        minRiders = 1
        maxRiders = 30
    elif race['UCI_Clas'] in [1,2]:
        minRiders = 8
        maxRiders = 8
    elif rr is None:
        minRiders = 7
        maxRiders = 7
    else:
        minRiders = rr['Min_Riders']
        maxRiders = rr['Max_Riders']
    race['Min_Riders'] = minRiders
    race['Max_Riders'] = maxRiders

    if bestRow > biggestRow:
        biggestRow = bestRow
    print(f'Race: {race["Name"]} - {bestRow}')

print(f'Biggest Row: {biggestRow}')
with open('output/races_final.json', 'w', encoding="utf-8") as outfile:
    json.dump(finalRaces, outfile, ensure_ascii=False)
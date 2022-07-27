import sys, getopt
import subprocess
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import OrderedDict

InputFile = '1.cdb'
OutputFolder = '2022'
TeamId = '1'
IgnoreDB = False

HelpBuilder = {}
BiggestRow = -1

Stages = {}
RaceRules = {}
Races = {}

WTRaces = {}
NTDays = {}
NTRaces = {}
OtherRaces = {}
FinalRaces = {}

def ConvertFavRaces(FavRaces):
    FavRaces = FavRaces.translate(str.maketrans({'(': '', ')': ''})).split(',')

    for Idx in range(len(FavRaces)):
        FavRaces[Idx] = Races[str(FavRaces[Idx])]['gene_sz_race_name']

    return '|'.join(FavRaces)

def GetStageDayOfYear(day):
    datetimeObj = datetime.strptime(str(day), '%Y%m%d')
    return datetimeObj.timetuple().tm_yday

def GetBestRow(r, fd, ld, sid):
    BestRow = r
    r = str(r)
    if 'row_' + r not in HelpBuilder:
        HelpBuilder['row_' + r] = {}

        for v in range(fd, ld+1):
            HelpBuilder['row_' + r]['col_' + str(v)] = sid

        return BestRow

    for v in range(fd, ld+1):
        if 'col_' + str(v) in HelpBuilder['row_' + r]:
            return GetBestRow(BestRow + 1, fd, ld, sid)

    for v in range(fd, ld+1):
        HelpBuilder['row_' + r]['col_' + str(v)] = sid

    return BestRow

def ConvertDBToXml():
    print('Extracting database to xml...')
    process = subprocess.Popen(f'ExcelExporter.exe Extract "{InputFile}" {OutputFolder}', stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b""):
        print('\t' + line.decode("utf-8"))
    print()

def ConvertRaces():
    print('Converting races...')

    global Races

    XmlRaces = ET.parse(f'Data/{OutputFolder}/STA_race.xml').getroot()

    for RC in XmlRaces.findall('STA_race'):
        RaceId = RC.find('IDrace').text
        Races[str(RaceId)] = {
            "IDrace": RC.find('IDrace').text,
            "gene_sz_race_name": RC.find('gene_sz_race_name').text,
            "fkIDfirst_stage": RC.find('fkIDfirst_stage').text,
            "fkIDlast_stage": RC.find('fkIDlast_stage').text,
            "fkIDUCI_class": int(RC.find('fkIDUCI_class').text),
            "gene_i_number_stages": RC.find('gene_i_number_stages').text
        }

    Races = OrderedDict(sorted(Races.items(), key=lambda v: v[1]['fkIDUCI_class'], reverse=False))
    print('\tDone.\n')

def ConvertStages():
    print('Converting stages...')
    XmlStages = ET.parse('Data/2022/STA_stage.xml').getroot()

    for ST in XmlStages.findall('STA_stage'):
        StageId = ST.find('IDstage').text
        Stages[str(StageId)] = {
            "IDstage": ST.find('IDstage').text,
            "fkIDrace": ST.find('fkIDrace').text,
            "gene_i_day": ST.find('gene_i_day').text,
            "gene_i_month": ST.find('gene_i_month').text,
            "gene_i_computed_date": ST.find('gene_i_computed_date').text,
            "gene_i_stage_number": ST.find('gene_i_stage_number').text,
            "gene_b_selected": ST.find('gene_b_selected').text
        }
    print('\tDone.\n')

def ConvertRaceRules():
    print('Converting race rules...')
    XmlRaceRules = ET.parse('Data/2022/STA_race_rules.xml').getroot()

    for RR in XmlRaceRules.findall('STA_race_rules'):
        RaceId = RR.find('fkIDrace').text
        RaceRules[str(RaceId)] = {
            "IDrace_rule": RR.find('IDrace_rule').text,
            "fkIDrace": RR.find('fkIDrace').text,
            "gene_i_max_team": RR.find('gene_i_max_team').text,
            "gene_i_min_riders": RR.find('gene_i_min_riders').text,
            "gene_i_max_riders": RR.find('gene_i_max_riders').text
        }
    print('\tDone.\n')

def GenerateCyclists():
    print('Generating cyclists...')
    Cyclists = {}
    XmlCyclists = ET.parse(f'Data/{OutputFolder}/DYN_cyclist.xml').getroot()

    for CY in XmlCyclists.findall('DYN_cyclist'):
        CTeamId = CY.find('fkIDteam').text

        if CTeamId == TeamId:
            CyclistId = CY.find('IDcyclist').text
            Cyclists[str(CyclistId)] = {
                "ID_Cyclist": CyclistId,
                "Lastname": CY.find('gene_sz_lastname').text,
                "Firstname": CY.find('gene_sz_firstname').text,
                "FavRaces": ConvertFavRaces(CY.find('gene_ilist_fkIDfavorite_races').text)
            }

    PathOutput = f'Output/{OutputFolder}/players_final.json'
    os.makedirs(os.path.dirname(PathOutput), exist_ok=True)
    with open(PathOutput, 'w', encoding="utf-8") as outfile:
        json.dump(Cyclists, outfile, ensure_ascii=False)

    print('\tDone.\n')

def GenerateRaces():
    print('Generating races...')

    global BiggestRow

    for Idx in Races:
        Race = Races[Idx]
        RaceId = Race['IDrace']
        RaceName = Race['gene_sz_race_name']
        RaceFirstStage = Race['fkIDfirst_stage']
        RaceLastStage = Race['fkIDlast_stage']
        RaceNumberOfStages = int(Race['gene_i_number_stages'])
        RaceUCIClass = int(Race['fkIDUCI_class'])

        FirstDay = GetStageDayOfYear(Stages[RaceFirstStage]['gene_i_computed_date'])
        LastDay = GetStageDayOfYear(Stages[RaceLastStage]['gene_i_computed_date'])

        if RaceUCIClass <= 8 or RaceUCIClass in [20,21,33,34]:
            WTRaces[str(RaceId)] = {
                'ID_Race': RaceId,
                'Name': RaceName,
                'NameTitle': RaceName,
                'Number_Stages': RaceNumberOfStages,
                'UCI_Clas': RaceUCIClass,
                'FirstStageDay': FirstDay,
                'LastStageDay': LastDay,
                'TotalDaysWithBreaks': (LastDay - FirstDay) + 1,
            }
        elif RaceUCIClass in [22,23]:
            NewRaceName = RaceName.split(" - ")
            if 'ITT' in RaceName:
                NewRaceNameTitle = NewRaceName[0] + "T"
            else:
                NewRaceNameTitle = NewRaceName[0] + "R"

            if FirstDay not in NTDays.keys():
                NTRaces[str(RaceId)] = {
                    'ID_Race': RaceId,
                    'Name': f'{NewRaceName[1]} - {NewRaceName [0]}',
                    'NameTitle': NewRaceNameTitle,
                    'Number_Stages': RaceNumberOfStages,
                    'UCI_Clas': RaceUCIClass,
                    'FirstStageDay': FirstDay,
                    'LastStageDay': LastDay,
                    'TotalDaysWithBreaks': (LastDay - FirstDay) + 1,
                }
                NTDays[FirstDay] = RaceId
            else:
                NTRaces[NTDays[FirstDay]]["NameTitle"] += ", " + NewRaceNameTitle
        else:
            OtherRaces[str(RaceId)] = {
                'ID_Race':RaceId,
                'Name': RaceName,
                'NameTitle': RaceName,
                'Number_Stages': RaceNumberOfStages,
                'UCI_Clas': RaceUCIClass,
                'FirstStageDay': FirstDay,
                'LastStageDay': LastDay,
                'TotalDaysWithBreaks': (LastDay - FirstDay) + 1,
            }

        FinalRaces = {**WTRaces, **NTRaces, **OtherRaces}

    for Race in FinalRaces:
        Race = FinalRaces[Race]
        BestRow = GetBestRow(1, Race['FirstStageDay'], Race['LastStageDay'], Race['ID_Race'])
        Race['BestRow'] = BestRow

        RR = RaceRules.get(Race['ID_Race'])
        if Race['UCI_Clas'] in [20,21,33,34,22,23]:
            MinRiders = 1
            MaxRiders = 30
        elif Race['UCI_Clas'] in [1,2]:
            MinRiders = 8
            MaxRiders = 8
        elif RR is None:
            MinRiders = 7
            MaxRiders = 7
        else:
            MinRiders = RR['gene_i_min_riders']
            MaxRiders = RR['gene_i_max_riders']
        Race['Min_Riders'] = MinRiders
        Race['Max_Riders'] = MaxRiders

        if BestRow > BiggestRow:
            BiggestRow = BestRow
        print(f'\t\tRace: {Race["Name"]} - {BestRow}')

    print(f'\n\tBiggest Row: {BiggestRow}\n')

    PathOutput = f'Output/{OutputFolder}/races_final.json'
    os.makedirs(os.path.dirname(PathOutput), exist_ok=True)
    with open(PathOutput, 'w', encoding="utf-8") as outfile:
        json.dump(FinalRaces, outfile, ensure_ascii=False)

    print('\tDone.\n')

def main(argv):
    if len(sys.argv) < 2:
        print("builder.py -i <inputfile> -o <outputfolder> -t <team_id> -d")
        sys.exit(2)

    try:
        Opts, Args = getopt.getopt(argv, "hi:o:t:d", ["ifile=", "ofolder=", "teamid=", "ignoredb="])
    except getopt.GetoptError:
        print("builder.py -i <inputfile> -o <outputfolder> -t <team_id> -d")
        sys.exit(2)

    global InputFile, OutputFolder, TeamId, IgnoreDB

    for Opt, Arg in Opts:
        if Opt == '-h':
            print("builder.py -i <inputfile> -o <outputfolder> -t <team_id> -d")
            sys.exit()
        elif Opt in ("-i", "--ifile"):
            InputFile = Arg
        elif Opt in ("-o", "--ofolder"):
            OutputFolder = Arg
        elif Opt in ("-t", "--teamid"):
            TeamId = Arg
        elif Opt in ("-d", "--ignoredb"):
            IgnoreDB = True

    print('Starting build...')
    print(f'\tInput File: {InputFile}')
    print(f'\tOutput folder: {OutputFolder}\n')

    if not IgnoreDB:
        ConvertDBToXml()
    ConvertRaces()
    ConvertStages()
    ConvertRaceRules()
    GenerateCyclists()
    GenerateRaces()

if __name__ == "__main__":
    main(sys.argv[1:])
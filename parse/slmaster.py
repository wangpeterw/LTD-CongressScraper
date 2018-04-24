import pandas as pd
import re
import numpy as np
from datascience import *
import urllib
from selenium import webdriver
from time import sleep
import requests
from bs4 import BeautifulSoup as Soup
import os

#Speech Table
speeches = Table().with_columns("speech_id", make_array(), 
                                "speaker_id", make_array(), 
                                "proceeding_id", make_array(), 
                                "topic_id", make_array(), 
                                "word_count", make_array(), 
                                "speech_text", make_array(),
                                'file_name', make_array())

#Speaker Table
speakers = Table().with_columns("speaker_id", make_array(), 
                                "first_name", make_array(), 
                                "last_name", make_array(), 
                                "type" , make_array(),
                                "party", make_array(), 
                                "state", make_array(), 
                                "district", make_array(),
                                "bio_guide_id", make_array(),
                                "congress_id", make_array())

topics = Table().with_columns("topic_id", make_array(), 
                                "topic_name", make_array())

#Proceedings Table
proceedings = Table().with_columns("proceeding_id", make_array(), 
                              "date", make_array(),
                              "title", make_array())

def remove_space(regex):
    return regex.group().replace(' ', '')

def sep_speech(string, folder_str):
    parse_file = ''
    with open("/Users/halliday/Desktop/parsing/runparse/" + folder_str + "/" + string) as file:
        for line in file:
            parse_file += line
    parse_file = parse_file.replace('\n', '')
#     parse_file = parse_file.replace('Mr. President', 'MrPresident')
#     parse_file = parse_file.replace('Mr. Short', 'Mr.Short')
    parse_file = re.sub('Mr. [A-Z][a-z]', remove_space, parse_file)
    
    split = re.split(r'Mr. |Ms. |Mrs. ', parse_file)
    split.pop(0)
    name_and_speech = make_array()
    for i in np.arange(len(split)):
        try:
            lastname = re.match('[A-Z]*\. ', split[i]).group(0)[:-2]
            name_and_speech = np.append(name_and_speech, lastname)
            value = re.sub('[A-Z]\w*\. ', '', split[i])
            name_and_speech = np.append(name_and_speech, value)
        except:
            abcabcabc = 1
    return name_and_speech

def sep_date_from_file(file):
    abcdef = re.findall('[0-9]{4}-[0-9]{2}-[0-9]{2}', file)
    return re.split('-', abcdef[0])

def find_title(folder_str, file_name):
    parse_file = ''
    with open("/Users/halliday/Desktop/parsing/runparse/" + folder_str + "/" + file_name) as file:
        for line in file:
            parse_file += line
    parse_file = parse_file.replace('Mr. President', 'MrPresident')
    title = re.findall('[A-Z \'-]+[A-Z0-9-,\. ]*[Continued]*\\n', parse_file)
    return title[0].strip()

def getAllExtensions(file):
    handler = open(file).read()
    soup = Soup(handler, "lxml")
    return soup.find_all('extension')

master_extensions = getAllExtensions("mastermods.xml")

def getCongMemberExtension(extensions, last_name):
    for extension in extensions:
        ext = str(extension)
        if last_name in ext:
            return extension

def getCongMemberExtensionFromFile(folder_str, last_name, filename):
    handler = open("/Users/halliday/Desktop/parsing/runparse/" + folder_str + "/" + filename).read()
    soup = Soup(handler, "lxml")
    extensions = soup.find_all('extension')
    for extension in extensions:
        ext = str(extension)
        if last_name in ext:
            return extension

def getCongMemberTag(last_name, congMemberExtension):
    contents = congMemberExtension.contents
    for tag in contents:
        tag_str = str(tag)
        if 'congmember' in tag_str:
            if last_name in tag_str:
                return tag

def getParty(congMemberTag):
    return congMemberTag.attrs['party']
def getType(congMemberTag):
    return congMemberTag.attrs['type']
def getAuthorityId(congMemberTag):
    return congMemberTag.attrs['authorityid']
def getBioGuideId(congMemberTag):
    return congMemberTag.attrs['bioguideid']
def getState(congMemberTag):
    return congMemberTag.attrs['state']
def getCongressId(congMemberTag):
    return congMemberTag.attrs['congress']

def getDistrictTag(congMemberExtension):
    contents = congMemberExtension.contents
    for tag in contents:
        tag_str = str(tag)
        if 'district' in tag_str:
            return tag

def getFirstName(congMemberTag):
    contents = congMemberTag.contents
    name_tags = []
    for tag in contents:
        tag_str = str(tag)
        if 'name' in tag_str:
            name_tags += [tag]
    try:
        first_name = name_tags[1].string.split()[0]
    except:
        first_name = None
    return first_name

def getCongMemberInfoFromMaster(last_name, mods_filename):
    info = make_array()
    if last_name == 'BORDALLO' or last_name == 'CAPITO':
        return getCongMemberInfoFromLocal(last_name, mods_filename)
    try:
        extension = getCongMemberExtension(master_extensions, last_name)
        if extension is None:
            return getCongMemberInfoFromLocal(last_name, mods_filename)
        congMemberTag = getCongMemberTag(last_name, extension)
        if congMemberTag == None:
            return getCongMemberInfoFromLocal(last_name, mods_filename)
    except:
        return getCongMemberInfoFromLocal(last_name, mods_filename)
    
    
    
    congMemType = getType(congMemberTag)
    district = 'N/A'
    if congMemType == 'DELEGATE':
        try:
            info = getcongMemberInfoFromLocal(last_name, mods_filename)
        except:
            info = [99999999999999, 'First Name unavailable', last_name, congMemType, 'Party Info Unavailable','state info unavailable', district, 'BioGuideID unavailable', 'CongressID unavailable']
    else:
        if congMemType == 'REPRESENTATIVE':
            try:
                district_tag = getDistrictTag(extension)
                district = district_tag.string
            except:
                district = 'N/A'
    try:
        bioGuideID = getBioGuideId(congMemberTag)
    except:
        bioGuideID = 99999999999999999
    info = [getAuthorityId(congMemberTag), getFirstName(congMemberTag), last_name, congMemType, getParty(congMemberTag), getState(congMemberTag), district, bioGuideID, getCongressId(congMemberTag) ]
        
    return info

def getChamber(congMemberTag):
    return congMemberTag.attrs['chamber']

def getCongMemberInfoFromLocal(last_name, mods_filename):
    # print('checking local file')
    try:
        extension = getCongMemberExtensionFromFile(folder, last_name, mods_filename)
        if extension is None:
            info = [99999999999999, 'First Name unavailable', last_name, 'Type Unavailable', 'Party Info Unavailable','state info unavailable', 'District Unavailable', 'BioGuideID unavailable', 'CongressID unavailable']
            return info
    except:
        info = [99999999999999, 'First Name unavailable', last_name, 'Type Unavailable', 'Party Info Unavailable','state info unavailable', 'District Unavailable', 'BioGuideID unavailable', 'CongressID unavailable']
        return info
    info = make_array()
    congMemberTag = getCongMemberTag(last_name, extension)
    
    if congMemberTag is None:
        return [99999999999999, 'First Name unavailable', last_name, 'Type Unavailable', 'Party Info Unavailable','state info unavailable', 'District Unavailable', 'BioGuideID unavailable', 'CongressID unavailable']

    congMemChamber = getChamber(congMemberTag)
    congMemType = 'N/A'
    if congMemChamber == 'H':
        congMemType = 'REPRESENTATIVE'
    elif congMemChamber == 'S':
        congMemType = "SENATOR"
    
    district = 'N/A'
    if congMemType == 'REPRESENTATIVE':
        try:
            district_tag = getDistrictTag(extension)
            district = district_tag.string
        except:
            district = 'N/A'
            
#     info = np.append(info, getAuthorityId(congMemberTag))
#     info = np.append(info, getFirstName(congMemberTag))
#     info = np.append(info, last_name)
#     info = np.append(info, congMemType)
#     info = np.append(info, getParty(congMemberTag))
#     info = np.append(info, getState(congMemberTag))
#     info = np.append(info, district)
#     info = np.append(info, getBioGuideId(congMemberTag))
#     info = np.append(info, getCongressId(congMemberTag))
    try:
        authID = getAuthorityId(congMemberTag)
    except:
        authID = 99999999999999
    try:
        party = getParty(congMemberTag)
    except:
        party = 'Party information Unavailable'
    try:
        state = getState(congMemberTag)
    except:
        state = 'State Info Unavailable'
    try:
        bioID = getBioGuideId(congMemberTag)
    except:
        bioID = 9999999999999999
    info = [authID, getFirstName(congMemberTag), last_name, congMemType, party, state, district, bioID, getCongressId(congMemberTag) ]
    return info

#Populate the Speech Table
speech_count = 0
count = 0
list_of_dirs = os.listdir("/Users/halliday/Desktop/parsing/runparse")
list_of_dirs.remove('.DS_Store')
print(list_of_dirs)
y = 0
for folder in list_of_dirs:
    print("         " + folder + "          ")
    list_of_files = os.listdir("/Users/halliday/Desktop/parsing/runparse/" + folder)
    for file in list_of_files:
        if file.endswith(".txt"):
            # if count > 1100:
            print(file)
            if file == 'CREC-2018-03-22-pt1-PgH1769-2.txt':
                continue
            if file == 'CREC-2017-09-06-pt1-PgH6695.txt':
                continue
            separated = sep_speech(file, folder)
            i = 0
            while i < len(separated):
                row = make_array()
                text = separated[i+1]
                text = text.replace('MrPresident', 'Mr. President')
                if len(text) > 30:
                    row = [speech_count, separated[i], 'proceeding_id', 'topic-id', len(text.split()), text, file] 
                    speech_count += 1
                    speeches = speeches.with_row(row)     
                i +=2
            speech_count+= 1
            print('finished with file ', speech_count)

    #create dictionairy of unique last names to files
    distinct_lastname_table = speeches.group('speaker_id')
    lastname_file_table = speeches.join('speaker_id', distinct_lastname_table, 'speaker_id')

    if lastname_file_table is None:

        print("               " + "DONE" + " with " + folder)
        print("resetting")

        speeches = Table().with_columns("speech_id", make_array(), 
                                        "speaker_id", make_array(), 
                                        "proceeding_id", make_array(), 
                                        "topic_id", make_array(), 
                                        "word_count", make_array(), 
                                        "speech_text", make_array(),
                                        'file_name', make_array())

        #Speaker Table
        speakers = Table().with_columns("speaker_id", make_array(), 
                                        "first_name", make_array(), 
                                        "last_name", make_array(), 
                                        "type" , make_array(),
                                        "party", make_array(), 
                                        "state", make_array(), 
                                        "district", make_array(),
                                        "bio_guide_id", make_array(),
                                        "congress_id", make_array())

        topics = Table().with_columns("topic_id", make_array(), 
                                        "topic_name", make_array())

        #Proceedings Table
        proceedings = Table().with_columns("proceeding_id", make_array(), 
                                      "date", make_array(),
                                      "title", make_array())
        continue

    lastname_file_table = lastname_file_table.drop('count').drop('speech_id').drop('proceeding_id').drop('topic_id').drop('word_count').drop('speech_text')
    name_to_xml = {}
    lastnames = lastname_file_table.column(0)
    files = lastname_file_table.column(1)
    count = 0
    while count < len(lastnames):
        name_to_xml[lastnames[count]] = files[count].replace('.txt', '.xml')
        count += 1


    #Populate Speaker Table

    for name in list(name_to_xml.keys()):
        # print(name)
        row = getCongMemberInfoFromMaster(name, name_to_xml[name])
        speakers = speakers.with_row(row)

    names = speakers.column('last_name')
    ids = speakers.column('speaker_id')
    name_to_id = dict(zip(names, ids))
    name_to_id['CAPITO'] = 1676

    newcol = make_array()
    for name in speeches.sort('speaker_id').column('speaker_id'):
        if name == 'SOUZZI':
            name = 'SUOZZI'
            name_to_id['SUOZZI'] = name_to_id['SOUZZI']
        if name == 'VANHOLLEN':
            name = 'VAN HOLLEN'
            name_to_id['VAN HOLLEN'] = name_to_id['VANHOLLEN']
            print("Dict change happened")
        if name == 'FISHCER':
            name = 'FISCHER'
            name_to_id['FISCHER'] = name_to_id['FISHCER']
        newcol = np.append(name_to_id[name], newcol)
    speeches = speeches.sort('speaker_id')
    speeches = speeches.relabel('speaker_id', 'last_name_id')
    speeches = speeches.with_column('speaker_id', np.flip(newcol, 0))

    title_column = make_array()
    year_column = make_array()
    month_column = make_array()
    day_column = make_array()

    for file_name in speeches.column('file_name'):
        title_column = np.append(find_title(folder, file_name), title_column)
        year, month, day = sep_date_from_file(file_name)
        year_column = np.append(int(year), year_column)
        month_column = np.append(int(month), month_column)
        day_column = np.append(int(day), day_column)

    title_column = np.flip(title_column, 0)
    year_column = np.flip(year_column, 0)
    month_column = np.flip(month_column, 0)
    day_column = np.flip(day_column, 0)

    speeches = speeches.drop('proceeding_id')
    speeches = speeches.with_columns('session_title', title_column, 'year', year_column, 'month', month_column, 'day', day_column)

    month_int_name = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 
                     10: 'October', 11: 'November', 12: 'December'}
    new_month = make_array()
    for month in speeches.column('month'):
        new_month = np.append(month_int_name[month], new_month)
    new_month = np.flip(new_month, 0)
    new_month
    speeches = speeches.drop('month').with_column('month', new_month)

    speech_string = 'speeches' + folder + '.csv'
    speakers_string = 'speakers' + folder + '.csv'

    speeches.to_csv(speech_string)
    speakers.to_csv(speakers_string)

    print("               " + "DONE" + " with " + folder)
    print("resetting")

    speeches = Table().with_columns("speech_id", make_array(), 
                                    "speaker_id", make_array(), 
                                    "proceeding_id", make_array(), 
                                    "topic_id", make_array(), 
                                    "word_count", make_array(), 
                                    "speech_text", make_array(),
                                    'file_name', make_array())

    #Speaker Table
    speakers = Table().with_columns("speaker_id", make_array(), 
                                    "first_name", make_array(), 
                                    "last_name", make_array(), 
                                    "type" , make_array(),
                                    "party", make_array(), 
                                    "state", make_array(), 
                                    "district", make_array(),
                                    "bio_guide_id", make_array(),
                                    "congress_id", make_array())

    topics = Table().with_columns("topic_id", make_array(), 
                                    "topic_name", make_array())

    #Proceedings Table
    proceedings = Table().with_columns("proceeding_id", make_array(), 
                                  "date", make_array(),
                                  "title", make_array())

# print("DONE")
# print("Don't forget to change speaker and speech strings")
# print("Dirs to Remove:")
# print("         " + speech_string)
# print("         " + speakers_string)
# print("         " + curr_folders)
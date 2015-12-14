import json
from urllib2 import urlopen

# url strings
apiBase = "https://api.guildwars2.com/v2/"
itemsSubsect = "items?"
charactersSubsect = "characters?"
commercePricesSubsect = "commerce/prices?"
accountBankSubsect = "account/bank?"
idsReq = "ids="
authPref = 'access_token='
authSuff = '&'

# folder and file strings
baseFolder = '../'
databaseFolder = 'dbFiles/'
outputFolder = 'outputFiles/'
itemListFolder = baseFolder + databaseFolder + 'itemLists/'
searchFolderName = baseFolder + databaseFolder + 'sigilrune_files/'
rsPricesFolderName = baseFolder + outputFolder + 'rsPrices/'
charactersFolderName = baseFolder + outputFolder
masterItemFilename = 'masterItemList.json'
newItemsFilename = 'newItems.txt'
newNamesFilename = 'newNames.txt'
runeAndSigilsFilename = 'runesAndSigils.json'


# functions
def getMIL():
    # function to easily return the master item list json
    with open(itemListFolder+masterItemFilename) as masterItemFile:
        theList = json.load(masterItemFile)
    return theList

def getAllCharacterData(auth):
    # gets all character names, then gets all character data and returns it (as a json)
    # includes 2 api calls
    url = apiBase + charactersSubsect + authPref + auth + authSuff
    charIDs = json.load(urlopen(url))
    reqIDs = ','.join(['%20'.join(x.split()) for x in charIDs])
    chars = json.load(urlopen(url+idsReq+reqIDs))
    return chars

def getBankData(auth):
    url = apiBase + accountBankSubsect + authPref + auth + authSuff
    bank = json.load(urlopen(url))
    return bank

def makeReqUrlList(idsList,url=apiBase+itemsSubsect+idsReq):
    # creates a list of ready to use url requests, and filename ranges to go with them (may be unnecessary)
    reqList = []
    filenameRanges = []
    for index in range(0, len(idsList), 200):
        textIDs = ','.join(str(x) for x in idsList[index:index+200])
        reqList.append(url + textIDs)
        filenameRanges.append([idsList[index],idsList[min(index+200,len(idsList)-1)]])
    return [reqList, filenameRanges]

def compareByID(x,y):
    # used to sort masterItemList and similar jsons by id
    return cmp(x['id'],y['id'])

def rarityComp(rarity):
    rarityDict = { 'Legendary': 0, 'Ascended': 1, 'Exotic': 2, 'Rare': 3, 'Masterwork': 4, 'Fine': 5, 'Basic': 6, 'Junk': 7 }
    return rarityDict[rarity]

def getRuneSigilObjs(masterItemList):
    # get a list of all superior rune and sigil ids
    # masterItemList needs to be the big ol' json list
    rsObjs = []
    for x in masterItemList:
        if 'AccountBound' in x['flags']:
            continue
        if 'details' in x.keys():
            if 'type' in x['details'].keys():
                if (x['details']['type'] == 'Sigil' or x['details']['type'] == 'Rune') and x['rarity'] == 'Exotic':
                    if len(x['name']) > 1:
                        rsObjs.append(x)
    return rsObjs

def getContainerLists(masterItemList,rsID):
    # get a list of all items that have x rune/sigil in them
    # NOTE: may have to also look at 'secondary_suffix_item_id'
    rsItemList = []
    for x in masterItemList:
        if 'details' in x.keys():
            if 'suffix_item_id' in x['details'].keys():
                if x['details']['suffix_item_id'] == rsID:
                    rsItemList.append(x)
    return rsItemList

def findByID(id,list):
    # find an item object by its id
    for x in list:
        if x['id'] == id:
            return x

def findByX(val,criteria,list):
    # find all item objects by any criteria
    rList = []
    for item in list:
        if criteria in item.keys():
            if item[criteria] == val:
                rList.append(item)
    return rList

def formatCoins(coins, denom=''):
    # formats coins based on value
    # denom argument can be used to set the format
    if denom == 'copper':
        number = coins
    elif denom == 'silver':
        number = coins/100.
    elif denom == 'gold':
        number =coins/10000.
    else:
        if coins < 100:
            number = coins
            denom = 'copper'
        elif coins < 10000:
            number = coins/100.
            denom = 'silver'
        else:
            number = coins/10000.
            denom = 'gold'
    return [number, denom, str(number) + ' ' + denom]



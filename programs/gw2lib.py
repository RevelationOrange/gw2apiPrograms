import json
from urllib2 import urlopen
import os


'''
This file contains various functions useful across many (well, at least more than one [usually]) gw2 api programs:
getMIL, getAllCharacterData, getBankData, makeReqUrlList, compareByID, rarityComp, getRuneSigilObjs, getContainerLists,
findByID, findByX, formatCoins
and more!
'''

# url strings, pretty self explanatory (I think?)
apiBase = "https://api.guildwars2.com/v2/"
itemsSubsect = "items?"
charactersSubsect = "characters?"
commercePricesSubsect = "commerce/prices?"
accountBankSubsect = "account/bank?"
recipesSubsect = "recipes?"
recipeSearch = "recipes/search?"
searchByInput = "input="
searchByOutput = "output="
idsReq = "ids="
authPref = 'access_token='
authSuff = '&'

# folder and file strings
sep = os.sep
baseFolder = '..' + sep
databaseFolder = 'dbFiles' + sep
outputFolder = 'outputFiles' + sep
itemListFolder = baseFolder + databaseFolder + 'itemLists' + sep
recipeListFolder = baseFolder + databaseFolder + 'recipeLists' + sep
searchFolderName = baseFolder + databaseFolder + 'sigilrune_files' + sep
rsPricesFolderName = baseFolder + outputFolder + 'rsPrices' + sep
charactersFolderName = baseFolder + outputFolder
masterItemFilename = 'masterItemList.json'
masterRecipeFilename = 'masterRecipeList.json'
newItemsFilename = 'newItems.txt'
newNamesFilename = 'newNames.txt'
runeAndSigilsFilename = 'runesAndSigils.json'


# functions
def getMIL():
    # function to easily get the master item list json
    # simply loads the master item file and returns it as a json object
    with open(itemListFolder+masterItemFilename) as masterItemFile:
        theList = json.load(masterItemFile)
    return theList

def getMRL():
    # function to easily get the master recipe list json
    # just like getMIL()
    with open(recipeListFolder+masterRecipeFilename) as masterRecipeFile:
        theList = json.load(masterRecipeFile)
    return theList

def getRecipe(itemID, searchBy=searchByOutput):
    url = apiBase + recipeSearch + searchBy + str(itemID)
    recipeIDs = json.load(urlopen(url))
    return recipeIDs

def getAllCharacterData(auth):
    # gets all character names for the given api key, then gets all character data and returns it (as a json)
    # includes 2 api calls
    url = apiBase + charactersSubsect + authPref + auth + authSuff
    charIDs = json.load(urlopen(url))
    # charIDs is a list of each character name, spaces included
    # reqIDs needs to be each character name separated by commas, with %20 instead of spaces
    # so for each thing in charIDs, split (on spaces by default) and join on %20, then for that list, join it on commas
    reqIDs = ','.join(['%20'.join(x.split()) for x in charIDs])
    # now the url will look like api/chars?auth=key&ids=name,name,name,etc.
    chars = json.load(urlopen(url+idsReq+reqIDs))
    # and chars will contain json objects for each character, as documented in the gw2 api
    return chars

def getBankData(auth):
    # gets the bank data for the given api key and returns the json object
    url = apiBase + accountBankSubsect + authPref + auth + authSuff
    bank = json.load(urlopen(url))
    return bank

def makeReqUrlList(idsList,url=apiBase+itemsSubsect+idsReq, incr=200):
    # creates a list of ready to use url requests, and filename ranges to go with them (may be unnecessary)
    # originally intended for item id requests, but can be used for other requests
    # each item in the list is a full url for the api
    reqList = []
    filenameRanges = []
    # for loop goes from 0 to the total number of ids, in increments of 200
    for index in range(0, len(idsList), incr):
        # join on commas: each item (as a string) in the id list, from the current index to current+200
        textIDs = ','.join(str(x) for x in idsList[index:index+incr])
        # add to the list of request urls: the given url (or default) with the id string (that was just created) appended
        reqList.append(url + textIDs)
        '''
        filename ranges is just intended for the first run of buildItemListV2, when it stores the json data for each
        call of 200 ids in a file, so it can pick up where it left off in case there's a connection error
        however, seeing as the code doesn't actually check for that, and since the total run time is only around 12
        minutes anyway, this part hardly seems useful, but eh
        '''
        filenameRanges.append([index, index+incr])
    return [reqList, filenameRanges]

def compareByID(x, y):
    # used to sort masterItemList and similar jsons by id
    return cmp(x['id'],y['id'])

def rarityComp(rarity):
    # returns a number based on rarity text, useful when sorting things by rarity
    rarityDict = { 'Legendary': 0, 'Ascended': 1, 'Exotic': 2, 'Rare': 3, 'Masterwork': 4, 'Fine': 5, 'Basic': 6, 'Junk': 7 }
    return rarityDict[rarity]

def getRuneSigilObjs(masterItemList):
    # get a list of all superior rune and sigil objects
    # masterItemList needs to be the big ol' json list
    # intended for use when finding rune and sigil prices on trade
    # I mean, I guess if you wanted all the runes and sigils from a reduced list, this would work too
    rsObjs = []
    for x in masterItemList:
        if 'AccountBound' in x['flags']:
            # anything account bound won't be on trade anyway
            continue
        # if the object has a 'details' key, a 'type' key in the details dict, the rarity is exotic, and the type is
        # sigil or rune, then add it to the list of rune/sigil objects, to be returned
        if 'details' in x.keys():
            if 'type' in x['details'].keys():
                if (x['details']['type'] == 'Sigil' or x['details']['type'] == 'Rune') and x['rarity'] == 'Exotic':
                    if len(x['name']) > 1:
                        rsObjs.append(x)
    return rsObjs

def getContainerLists(masterItemList,rsID):
    # get a list of all item objects that have x rune/sigil in them
    # NOTE: may have to also look at 'secondary_suffix_item_id'
    rsItemList = []
    for x in masterItemList:
        # if the object has a 'details' key, a 'suffix_item_id' in the details dict, and that suffix_item_id matches
        # the given id of the rune/sigil (rsID), then add it to the list of item objects, to be returned
        if 'details' in x.keys():
            if 'suffix_item_id' in x['details'].keys():
                if x['details']['suffix_item_id'] == rsID:
                    rsItemList.append(x)
    return rsItemList

def findByID(id,list):
    '''
    find an item object by its id
    simply loops through the given list (usually the master item list) and returns the object when its id is found.
    notably, some items exist in game and will return ids in the characters or account/bank endpoints that do not
    exist in the items endpoint
    why. why anet, why.
    no checking for such cases is provided, usually causing an error when the return value of [] is used in the
    program calling findByID, which is intentional; this kind of error should never occur in the first place, so it's
    best to know when it happens so more information about the item in question can be obtained
    '''
    for x in list:
        if x['id'] == id:
            return x
    else:
        return None

def findByX(val,criteria,dict):
    # find all item objects by any criteria
    # criteria is a dictionary key, like 'name' or 'id', and val is the value of that key, like 'Salvage Kit' or 47
    # this will only work for keys in the main dictionary; for example it can't search by the key 'type' found in the
    # 'details' object of an object in the given dict
    rList = []
    # in the for loop, each item in dict is checked and if criteria is in the keys and it matches val, it's added
    # to the return list
    for item in dict:
        if criteria in item.keys():
            if item[criteria] == val:
                rList.append(item)
    return rList

def formatCoins(coins, denom=''):
    '''
    formats coins based on value
    denom argument can be used to set the format
    coins by default is simply the number of copper (with 1 silver -> 100 copper,
    and 1 gold -> 100 silver -> 10000 copper)
    with no denom argument, this function makes sure the number of coins is expressed as a decimal number not less
    than 1 or greater than 100, except if denom is set to 'gold'
    the function returns a list of the number of coins (an integer if denom is copper, likely a float otherwise),
    the denomination, and a nice string of the number followed by the denomination, such as '4.2 gold' (42000 copper)
    '''
    if denom == 'copper':
        number = coins
    elif denom == 'silver':
        number = coins/100.
    elif denom == 'gold':
        number = coins/10000.
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

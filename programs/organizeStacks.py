import gw2lib
import sys
import copy

'''
organizeStacks checks all inventories for combinable stacks of items
that is, it reports when more than one of a stack of an item is found that is not at max
it reports its location and amount
'''

def findPartialStacks(bag, locationsDict, curChar, mil):
    # checks a whole bag object or bank for every item (by id) that can stack and isn't a full stack, modifies a dict
    # given as an argument, returns a list of 'weird items'
    # some item types never stack and can be excluded, but some items are apparently exceptions, such as Baelfire's
    # Weapons Box, a container type item that doesn't stack. unfortunately, unless a rule is found that determines
    # which items like these do and don't stack, a restriction list must be used to ignore them.
    restrictedTypes = 'Gathering, Tool, Weapon, Armor, Back, Trinket, Bag'
    restrictedNames = 'Baelfire\'s Weapons Box'

    # by default a full stack is 250 items. this can change by buying a thing in the gem store, so this isn't actually
    # a general case. I haven't been able to find a way to retun the max stack size for an account (yet?), so this
    # will have to be manually changed if the user has a different max stack size
    fullStack = 250

    # a 'weird item' is one that doesn't find a valid id from the master item list. how can there be an actual item
    # found in an actual inventory space in game that doesn't have a valid id in the item api endpoint? GOOD QUESTION.
    # but they do exist. so far I just know of one, 'Druid's Shoulderguards', id 69991 (I think, I'll check again
    # later), which really baffles me since a very similar item 'Dragonhunter's Gauntlet', id 72045, appears in my
    # inventory and is perfectly valid in the api.
    # ANYWAY
    weirdItems = []

    # i is just a counter for finding where any weird items occur in inventories
    i = 0
    for item in bag:
        i += 1
        if item is not None:
            # for every existing item in the given bag:
            # if it's not a full stack
            if item['count'] != fullStack:
                # and it's not bound (account or soul)
                if 'bound_to' not in item.keys():
                    # get the item object from the master list
                    itemData = gw2lib.findByID(item['id'], mil)
                    if itemData is None:
                        # as above, if it's not found in the master list, it's weird
                        weirdItems.append([item, curChar, i])
                        continue
                    # if it's type and name are not in the respective restricted lists
                    if itemData['type'] not in restrictedTypes and itemData['name'] not in restrictedNames:
                        # add it to or update it in the dictionary of locations
                        # use its id as the key, in that dict have a 'name' key and have a subdict of 'locations' that
                        # stores the number of items and which character they're on
                        if item['id'] in locationsDict.keys():
                            locationsDict[item['id']]['locations'].append([item['count'], curChar])
                        else:
                            locationsDict[item['id']] = {'locations': [[item['count'], curChar]], 'name': itemData['name']}
    return weirdItems

stacksByItemFilename = 'extraStacksByItem.txt'
stacksByCharacterFilename = 'extraStacksByCharacter.txt'

# grab the api key from the command line
apiKey = sys.argv[1]

# grab character and bank data, and get the MIL
chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)
masterItemList = gw2lib.getMIL()

stackLocations = {}

# get the partial stacks from the bank
weirdBankItems = findPartialStacks(bank, stackLocations, 'bank', masterItemList)
# if there are any, print the weird items
if len(weirdBankItems) > 0:
    print weirdBankItems

# for each character, go through their bags and add any partial stacks to the list
for char in chars:
    for bag in char['bags']:
        if bag is not None:
            # give the 'inventory' of the bag object to findPartialStacks, as well as the locations list, the character
            # being checked, and the MIL, and then print out any weird items
            weirdCharItems = findPartialStacks(bag['inventory'], stackLocations, char['name'], masterItemList)
            if len(weirdCharItems) > 0:
                print weirdCharItems

# fill out the names for the items in stackLocations, since the data from characters and banks only includes ids
for id in stackLocations.keys():
    itemName = gw2lib.findByID(id, masterItemList)['name']
    stackLocations[id]['name'] = itemName

reducedStacks = {}

# get a reduced list- one that only saves ids of items found in more than one location (ex, 25 bloodstone dust in a
# bank tab, 50 bloodstone dust on a character)
# this is simply done by checking how many 'locations' were recorded for each item id. however this doesn't check for
# (though easily could) split stacks on the same character. this is much less likely, since the compact command in the
# inventory window combines stacks when possible, but still is good information to return, just so the user is aware
for x in stackLocations:
    if len(stackLocations[x]['locations']) > 1:
        reducedStacks[x] = stackLocations[x]

# now, output the items in reducedStacks to a file, with lines like:
# itemName- found in: charName (#), charName (#)
# charName will sometimes be 'bank'
with open(gw2lib.charactersFolderName+stacksByItemFilename, 'w') as stacksBIfile:
    for x in reducedStacks:
        stacksBIfile.write(reducedStacks[x]['name'] + '- found in: '
                         + ', '.join([ y[1] + ' (' + str(y[0]) + ')' for y in reducedStacks[x]['locations'] ]) + '\n')

stacksByCharacter = {}

# now to organize the items in reducedStacks by character rather than item id
for itemID in reducedStacks:
    # for each item id in the dict, grab the name
    itemName = reducedStacks[itemID]['name']
    # then go through the locations dict
    for loc in reducedStacks[itemID]['locations']:
        # get the name and count, for ease of use
        charName = loc[1]
        itemCount = loc[0]
        # if the character name is in the by character dict, and the item id is in the character's dict, append the
        # current location list to the character's 'locations' dict
        # both usually won't happen, which is why I had it print a thing; I think it only occurs when multiple
        # locations are found and it's the same character
        # if the character name is already in the dict but but the item id isn't in the character's dict, set the item
        # id key of the character to A COPY (and a deep copy; this is important for later) of the item id dict from
        # reducedStacks, which includes a locations dict and the name of the item
        # if neither case is true, make a new key in stacksByCharacter and set its 'itemID' key to a deep copy of the
        # item id dict from reduced stacks
        if charName in stacksByCharacter.keys():
            if itemID in stacksByCharacter[charName].keys():
                stacksByCharacter[charName][itemID]['locations'].append(loc)
                print 'did the thing', loc, charName, itemName, itemID
            else:
                stacksByCharacter[charName][itemID] = copy.deepcopy(reducedStacks[itemID])
        else:
            stacksByCharacter[charName] = { itemID: copy.deepcopy(reducedStacks[itemID]) }

# this is where deep copy became a big deal
# this for loop eliminates references to the location of an item on a character in that character's key in
# stacksByCharacter. it's mostly pretty simple.
# for each character in the dict:
for charName in stacksByCharacter:
    # and for each item id in the character's dict
    for itemID in stacksByCharacter[charName]:
        # and for each location in the 'locations' key of the character's dict
        for loc in stacksByCharacter[charName][itemID]['locations']:
            # if the character name of the location is the same as the character being checked, give the item id of
            # the character a new key, 'count', which is the count the item on that character, and remove that location
            # from the 'locations' list
            if loc[1] == charName:
                stacksByCharacter[charName][itemID]['count'] = loc[0]
                stacksByCharacter[charName][itemID]['locations'].remove(loc)
# some notes:
# removing references to the same character in the locations simply makes it a nicer list to read, since you don't have
# stuff like 'on revel orange: bloodstone dust: revel orange (32), bank (128)'
# regarding deepcopy(): when simply assigning the entry in stacksByCharacter to the appropriate reducedStacks object,
# using remove() in this way would result in completely empty lists for stacksByCharacter. I learned this was due to
# python's obsession with assignment by reference, and when calling remove() it was changing the object that multiple
# things in stacksByCharacter were pointing to, and since each character was going to call a remove on an item, the
# list was always going to end up empty. even just copy() didn't work, since the thing being passed wasn't the thing
# being directly edited, so references to the original 'locations' object were still intact. deep copy solved this
# issue.

# finally, time to write the stacksByCharacter file
# again mostly straightforward, each character gets a section:
# charName
# itemName (#): charName (#), charName (#)
#
# including the bank, which usually happens to be at the end. there's probly a reason for this, but eh.
with open(gw2lib.charactersFolderName+stacksByCharacterFilename, 'w') as stacksBCfile:
    for charName in stacksByCharacter:
        stacksBCfile.write(charName + '\n')
        for itemID in stacksByCharacter[charName]:
            stacksBCfile.write(stacksByCharacter[charName][itemID]['name'] + ' (' \
                  + str(stacksByCharacter[charName][itemID]['count']) + '): ' \
                  + ', '.join([ y[1] + ' (' + str(y[0]) + ')' for y in stacksByCharacter[charName][itemID]['locations'] ]) + '\n')
        stacksBCfile.write('\n')

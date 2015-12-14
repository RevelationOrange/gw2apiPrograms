import gw2lib
import sys
import copy


def findPartialStacks(bag, locationsDict, curChar, mil):
    restrictedTypes = 'Gathering, Tool, Weapon, Armor, Back, Trinket, Bag'
    restrictedNames = 'Baelfire\'s Weapons Box'
    weirdItems = []
    i = 0
    for item in bag:
        i += 1
        if item is not None:
            if item['count'] != 250:
                if 'bound_to' not in item.keys():
                    itemData = gw2lib.findByID(item['id'], mil)
                    if itemData is None:
                        weirdItems.append([item, curChar, i])
                        continue
                    if itemData['type'] not in restrictedTypes and itemData['name'] not in restrictedNames:
                        if item['id'] in locationsDict.keys():
                            locationsDict[item['id']]['locations'].append([item['count'], curChar])
                        else:
                            locationsDict[item['id']] = {'locations': [[item['count'], curChar]], 'name': itemData['name']}
    return weirdItems

stacksByItemFilename = 'extraStacksByItem.txt'
stacksByCharacterFilename = 'extraStacksByCharacter.txt'

apiKey = sys.argv[1]

chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)
masterItemList = gw2lib.getMIL()

stackLocations = {}

weirdBankItems = findPartialStacks(bank, stackLocations, 'bank', masterItemList)
if len(weirdBankItems) > 0:
    print weirdBankItems

for char in chars:
    for bag in char['bags']:
        if bag is not None:
            weirdCharItems = findPartialStacks(bag['inventory'], stackLocations, char['name'], masterItemList)
            if len(weirdCharItems) > 0:
                print weirdCharItems

for id in stackLocations.keys():
    itemName = gw2lib.findByID(id, masterItemList)['name']
    stackLocations[id]['name'] = itemName

reducedStacks = {}

for x in stackLocations:
    if len(stackLocations[x]['locations']) > 1:
        reducedStacks[x] = stackLocations[x]

with open(gw2lib.charactersFolderName+stacksByItemFilename, 'w') as stacksBIfile:
    for x in reducedStacks:
        stacksBIfile.write(reducedStacks[x]['name'] + '- found in: '
                         + ', '.join([ y[1] + ' (' + str(y[0]) + ')' for y in reducedStacks[x]['locations'] ]) + '\n')

stacksByCharacter = {}

for itemID in reducedStacks:
    itemName = reducedStacks[itemID]['name']
    for loc in reducedStacks[itemID]['locations']:
        charName = loc[1]
        itemCount = loc[0]
        if charName in stacksByCharacter.keys():
            if itemID in stacksByCharacter[charName].keys():
                stacksByCharacter[charName][itemID]['locations'].append(loc)
                print 'did the thing', loc, charName, itemName, itemID
            else:
                stacksByCharacter[charName][itemID] = copy.deepcopy(reducedStacks[itemID])
        else:
            stacksByCharacter[charName] = { itemID: copy.deepcopy(reducedStacks[itemID]) }

for charName in stacksByCharacter:
    for itemID in stacksByCharacter[charName]:
        for loc in stacksByCharacter[charName][itemID]['locations']:
            if loc[1] == charName:
                stacksByCharacter[charName][itemID]['count'] = loc[0]
                stacksByCharacter[charName][itemID]['locations'].remove(loc)

with open(gw2lib.charactersFolderName+stacksByCharacterFilename, 'w') as stacksBCfile:
    for charName in stacksByCharacter:
        stacksBCfile.write(charName + '\n')
        for itemID in stacksByCharacter[charName]:
            stacksBCfile.write(stacksByCharacter[charName][itemID]['name'] + ' (' \
                  + str(stacksByCharacter[charName][itemID]['count']) + '): ' \
                  + ', '.join([ y[1] + ' (' + str(y[0]) + ')' for y in stacksByCharacter[charName][itemID]['locations'] ]) + '\n')
        stacksBCfile.write('\n')

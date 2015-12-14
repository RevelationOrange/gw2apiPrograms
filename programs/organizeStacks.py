import gw2lib
import sys


def findPartialStacks(bag, locationsDict, curChar, mil):
    restrictedTypes = 'Gathering, Tool, Weapon, Armor, Back, Trinket, Bag'
    restrictedNames = 'Baelfire\'s Weapons Box'
    for item in bag:
        if item is not None:
            if item['count'] != 250:
                if 'bound_to' not in item.keys():
                    itemData = gw2lib.findByID(item['id'], mil)
                    if itemData['type'] not in restrictedTypes and itemData['name'] not in restrictedNames:
                        if item['id'] in locationsDict.keys():
                            locationsDict[item['id']]['locations'].append([item['count'], curChar])
                        else:
                            locationsDict[item['id']] = {'locations': [[item['count'], curChar]], 'name': itemData['name']}

stacksFilename = 'stacks.txt'

apiKey = sys.argv[1]

chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)
masterItemList = gw2lib.getMIL()

stackLocations = {}

findPartialStacks(bank, stackLocations, 'bank', masterItemList)

for char in chars:
    for bag in char['bags']:
        if bag is not None:
            findPartialStacks(bag['inventory'], stackLocations, char['name'], masterItemList)

for id in stackLocations.keys():
    itemName = gw2lib.findByID(id, masterItemList)['name']
    stackLocations[id]['name'] = itemName

reducedStacks = {}

for x in stackLocations:
    if len(stackLocations[x]['locations']) > 1:
        reducedStacks[x] = stackLocations[x]

with open(gw2lib.charactersFolderName+stacksFilename, 'w') as stacksFile:
    for x in reducedStacks:
        stacksFile.write(reducedStacks[x]['name'] + '- found in: ' + ', '.join([ y[1] + ' (' + str(y[0]) + ')' for y in reducedStacks[x]['locations'] ]) + '\n')

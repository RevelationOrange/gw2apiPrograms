import gw2lib
import sys
from copy import deepcopy

def isArmor(type):
    if type in ['Shoulders', 'Coat', 'Boots', 'HelmAquatic', 'Gloves', 'Helm', 'Leggings']:
        return True
    else:
        return False

def findEquips(equipSet, char=None, makeBase=True):
    for piece in equipSet:
        if piece['slot'] != 'Sickle' and piece['slot'] != 'Axe' and piece['slot'] != 'Pick':
            slot = piece['slot']
            while slot[-1] in '12AB':
                slot = slot[:-1]
            itemObj = gw2lib.findByID(piece['id'], masterItemList)
            rarity = itemObj['rarity']
            if isArmor(slot):
                slot += itemObj['details']['weight_class']
            if makeBase:
                if slot in baselines.keys():
                    if (gw2lib.rarityComp(rarity) > gw2lib.rarityComp(baselines[slot])):
                        baselines[slot] = rarity
                else:
                    baselines[slot] = rarity
                    itemsBySlot[slot] = []
            else:
                if slot in bestOfInvy.keys():
                    if gw2lib.rarityComp(rarity) >= gw2lib.rarityComp(bestOfInvy[slot]):
                        equipsByCharBySlot[char][slot].append([ itemObj['name'], rarity ])
    return

def makeInvyDict(bag, loc=None, makeBase=True):
    for item in bag:
        if item is not None:
            if 'binding' in item.keys() and item['binding'] == 'Character':
                pass
            else:
                iType = None
                itemObj = gw2lib.findByID(item['id'], masterItemList)
                if itemObj['type'] == 'Back':
                    iType = 'Backpack'
                elif itemObj['type'] == 'Weapon':
                    if itemObj['details']['type'] in ['Harpoon', 'Speargun', 'Trident']:
                        iType = 'WeaponAquatic'
                    else:
                        iType = itemObj['type']
                elif itemObj['type'] == 'Armor':
                    iType = itemObj['details']['type'] + itemObj['details']['weight_class']
                elif itemObj['type'] == 'Trinket':
                    iType = itemObj['details']['type']
                else:
                    pass
                if iType is not None:
                    if makeBase:
                        if iType in bestOfInvy.keys():
                            if (gw2lib.rarityComp(itemObj['rarity']) < gw2lib.rarityComp(bestOfInvy[iType])):
                                bestOfInvy[iType] = itemObj['rarity']
                        else:
                            bestOfInvy[iType] = itemObj['rarity']
                            slotsFromInvy[iType] = []
                    else:
                        if gw2lib.rarityComp(itemObj['rarity']) <= gw2lib.rarityComp(baselines[iType]):
                            itemsBySlot[iType].append([ itemObj['name'], itemObj['rarity'], loc ])
    return

# grab the api key from the command line
apiKey = sys.argv[1]

# grab character and bank data, and get the MIL
chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)
masterItemList = gw2lib.getMIL()

baselines = {}
bestOfInvy = {}
itemsBySlot = {}
equipsByCharBySlot = {}
slotsFromInvy = {}
#itemTypes = ['Armor', 'Back', 'Weapon']

for char in chars:
    if char['level'] == 80:
        equipsByCharBySlot[char['name']] = {}
        findEquips(char['equipment'])
        for bag in char['bags']:
            if bag is not None:
                makeInvyDict(bag['inventory'])

makeInvyDict(bank)

for char in chars:
    if char['level'] == 80:
        equipsByCharBySlot[char['name']] = deepcopy(slotsFromInvy)
        findEquips(char['equipment'], char['name'], False)
        for bag in char['bags']:
            if bag is not None:
                makeInvyDict(bag['inventory'], char['name'], False)

makeInvyDict(bank, 'bank', False)

print baselines
print bestOfInvy
print itemsBySlot
print equipsByCharBySlot

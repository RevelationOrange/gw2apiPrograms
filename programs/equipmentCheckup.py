import gw2lib
import sys
from copy import deepcopy
import codecs


'''
equipmentCheckup looks through current equips and inventory and shows you items in your inventory that would upgrade
equipped items
'''

def isArmor(type):
    # for boolean tests; returns true if the equip type is armor that comes in different weight classes, else false
    if type in ['Shoulders', 'Coat', 'Boots', 'HelmAquatic', 'Gloves', 'Helm', 'Leggings']:
        return True
    else:
        return False

def findEquips(equipSet, char=None, makeBase=True):
    # searches for equipment on characters, and either records baseline rarities and creates slots for itemsBySlot, or
    # records equips in equipsByCharBySlot
    # equipSet must be the char['equipment'] array, char is the character name, makeBase decides if it's recording
    # baseline rarities

    # go through each piece of equipment
    for piece in equipSet:
        # if the equip isn't for gathering (sickle axe or pick)
        if piece['slot'] != 'Sickle' and piece['slot'] != 'Axe' and piece['slot'] != 'Pick':
            slot = piece['slot']
            # get the slot text and remove the necessary characters
            # this is to avoid recording stuff like weaponA1 and weaponA2 separately
            # same for rings and accessories
            while slot[-1] in '12AB':
                slot = slot[:-1]
            # grab the item object
            itemObj = masterItemList[str(piece['id'])] #gw2lib.findByID(piece['id'], masterItemList)
            # use it to get the rarity
            rarity = itemObj['rarity']
            # if the slot has an associated weight class, append that text to it
            if isArmor(slot):
                slot += itemObj['details']['weight_class']
            # if we're recording baselines:
            if makeBase:
                # if something has already been recorded in that slot:
                if slot in baselines.keys():
                    # check the rarity, if it's lower (less rare, that is it returns a higher number), record it as
                    # the new baseline rarity for that slot
                    if (gw2lib.rarityComp(rarity) > gw2lib.rarityComp(baselines[slot])):
                        baselines[slot] = rarity
                # if it hasn't been recorded yet, no need for rarityComp, just record it
                # and set the slot to and empty list in itemsBySlot
                # this is so accessing it later doesn't cause errors
                else:
                    baselines[slot] = rarity
                    itemsBySlot[slot] = []
            # if not recording baselines:
            else:
                # check if the slot has been recorded in bestOfInvy
                # this check is needed because not necessarily every slot will be recorded in the inventory check
                # i.e. there might not be a light helm found in inventory, so we don't want to list that equip on chars
                if slot in bestOfInvy.keys():
                    # if the equip rarity is below the best item found, record it- append to that char's slot the equip
                    # name and rarity
                    # that is, if the best item found in inventory has a higher (or equal) rarity to this piece of
                    # equipment, it's a candidate for replacement, so record it
                    # this will lead to multiple listings for weapons and rings and such, but shouldn't for helms, etc.
                    if gw2lib.rarityComp(rarity) >= gw2lib.rarityComp(bestOfInvy[slot]):
                        equipsByCharBySlot[char][slot].append([ itemObj['name'], rarity ])
    return

def makeInvyDict(bag, loc=None, makeBase=True):
    # searches through inventories (character or bank) and either records highest rarity found by slot (in bestOfInvy),
    # or records items by slot, noting name, rarity, and location
    # bag must be a bag['inventory'] array of items, loc is a character name or 'bank', and makeBase decides if it's
    # recording baseline rarities (which is this case is highest rarities found)

    # for each item
    for item in bag:
        # if it exists
        if item is not None:
            # and it's not character bound
            if 'binding' in item.keys() and item['binding'] == 'Character':
                pass
            else:
                # reset the type (this is used to exclude irrelevant item types, as iType is only set when a relevant
                # type is found), and get the item object
                iType = None
                itemObj = masterItemList[str(item['id'])] #gw2lib.findByID(item['id'], masterItemList)
                # and now a separate case for each slot type, because screw uniformity, right?
                if itemObj['type'] == 'Back':
                    # 'Back' type items should be 'Backpack'
                    iType = 'Backpack'
                elif itemObj['type'] == 'Weapon':
                    # 'Weapon' type items will either stay 'Weapon' or have 'Aquatic' appended if they're one of the
                    # harpoon, speargun, or trident subtypes
                    if itemObj['details']['type'] in ['Harpoon', 'Speargun', 'Trident']:
                        iType = 'WeaponAquatic'
                    else:
                        iType = itemObj['type']
                elif itemObj['type'] == 'Armor':
                    # 'Armor' type items need their weight class appended
                    iType = itemObj['details']['type'] + itemObj['details']['weight_class']
                elif itemObj['type'] == 'Trinket':
                    # 'Trinket' type items use their subtype (found in ['details']['type']), Accessory, Amulet, or Ring
                    iType = itemObj['details']['type']
                else:
                    # this case simply leaves iType as None, so the following code is not run
                    pass
                if iType is not None:
                    # if we're recording best of:
                    if makeBase:
                        # if something has already been recorded in that slot:
                        if iType in bestOfInvy.keys():
                            # check the rarity, if it's higher (more rare, that is returns a lower number), then record
                            # it as the best rarity for that slot
                            if (gw2lib.rarityComp(itemObj['rarity']) < gw2lib.rarityComp(bestOfInvy[iType])):
                                bestOfInvy[iType] = itemObj['rarity']
                        # if it's a new slot, no comparison needed, just record the rarity, and set the slot to an
                        # empty list in slotsFromInvy
                        # this dict will be used later, to be copied into the equipsByCharBySlot dict, again to avoid
                        # errors when accessing slots
                        else:
                            bestOfInvy[iType] = itemObj['rarity']
                            slotsFromInvy[iType] = []
                    # if not recording best of:
                    else:
                        # check rarity of the item, if it's rarer than the current baseline, record it in itemsBySlot-
                        # append a list of its name, rarity, and location
                        # that is, if the item found is above the lowest equipment (on an actual character) then it is
                        # a candidate to replace equipment for that slot
                        if gw2lib.rarityComp(itemObj['rarity']) <= gw2lib.rarityComp(baselines[iType]):
                            itemsBySlot[iType].append([ itemObj['name'], itemObj['rarity'], loc ])
    return

charFileName = 'characterEquips.txt'
invyFileName = 'inventoryEquips.txt'

# grab the api key from the command line, or exit if one isn't provided
if len(sys.argv) < 2:
    print "No api key provided. Please provide your api key as the first argument. If you need to create one, you can "\
          "do so at https://account.arena.net/applications"
    print "Be sure to include the 'character' and 'inventories' permissions for this program to work."
    sys.exit()
apiKey = sys.argv[1]

# grab character and bank data, and get the MIL
chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)
masterItemList = gw2lib.getMILv2()

# baselines is a dictionary of the lowest rarity found on any character for a particular item slot
# equipment found in inventory must be equal to or rarer than this for it to be a candidate to replace an equip
baselines = {}

# bestOfInvy is a dict of the highest rarity found in any inventory for a particular item slot
# equipment on a character must be equal to or less rare than this to be a candidate for replacement
bestOfInvy = {}

# itemsBySlot is a dict of items found in inventories that meet the baseline rarity, listing their names, rarities, and
# location found
itemsBySlot = {}

# equipsByCharBySlot is a dict of dicts, listing for each character their equipment, by slot, that is below or equal to
# the best rarity found from inventories
equipsByCharBySlot = {}

# slotsFromInvy is a dict to hold empty lists for each item slot actually found in inventories
# this will be copied into each character in equipsByCharBySlot, so as not to check slots for items that weren't
# actually found
slotsFromInvy = {}

# go through each character
for char in chars:
    # if they're an 80
    if char['level'] == 80:
        # add a placeholder for their equips by slot
        equipsByCharBySlot[char['name']] = {}
        # search their equipment to find minimum rarities to check for in inventories
        findEquips(char['equipment'])
        # then go through their bags
        for bag in char['bags']:
            # and if it's an actual bag
            if bag is not None:
                # search the items to find best rarities to check against current equips
                makeInvyDict(bag['inventory'])

# check the bank to make best rarities list
makeInvyDict(bank)

# go through each character again
for char in chars:
    # if they're an 80
    if char['level'] == 80:
        # this time, make a deep copy of the found slots (in inventory)
        equipsByCharBySlot[char['name']] = deepcopy(slotsFromInvy)
        # and record their current equips if they're at or below that slot rarity
        findEquips(char['equipment'], char['name'], False)
        # then go through their bags again
        for bag in char['bags']:
            # and if it's an actual bag
            if bag is not None:
                # make lists, by slots, of items found that meet the baseline rarity
                makeInvyDict(bag['inventory'], char['name'], False)

# add stuff found in the bank to the lists by slots
makeInvyDict(bank, 'bank', False)

# output the info of the characters' equips according to the format:
# charName
# slot: name, rarity
#       name, rarity
#       ...
# ...
# charName
# ...
with codecs.open(gw2lib.charactersFolderName+charFileName, 'w', 'utf-8') as charFile:
    for charName in equipsByCharBySlot:
        charFile.write(charName + '\n')
        for slot in equipsByCharBySlot[charName]:
            if len(equipsByCharBySlot[charName][slot]) > 0:
                if slot == 'Ring' or slot == 'Coat':
                    nTabs = '\t\t'
                else:
                    nTabs = '\t'
                charFile.write(slot + ': ' + nTabs + ', '.join([ x for x in equipsByCharBySlot[charName][slot][0] ]) + '\n')
                if len(equipsByCharBySlot[charName][slot]) > 1:
                    for equipInfo in equipsByCharBySlot[charName][slot][1:]:
                        charFile.write('\t\t' + ', '.join([ x for x in equipInfo ]) + '\n')
        charFile.write('\n')

# output the inventory items according to te format:
# slot:
#  name, rarity, locations
#  ...
# slot:
# ...
with codecs.open(gw2lib.charactersFolderName+invyFileName, 'w', 'utf-8') as invyFile:
    for slot in itemsBySlot:
        if len(itemsBySlot[slot]) > 0:
            invyFile.write(slot + ':\n')
            for info in itemsBySlot[slot]:
                invyFile.write('  ' + ', '.join([ x for x in info ]) + '\n')
            invyFile.write('\n')
print 'equipment info written to {} and {}'.format(gw2lib.charactersFolderName+charFileName,
                                                   gw2lib.charactersFolderName+invyFileName)

import gw2lib
import sys
from copy import deepcopy


'''
this may someday be a tool that accurately sums up and displays the stat totals for a character
but if back (or other) items give bonuses whose numerical values are stored in a goddamn string with newline separators
and the numbers in freakin' non-standard locations on that line, I don't know when that day will be
'''

def makeStats(stats, level):
    # makeStats will calculate proper base stat numbers (for power, precision, toughness, and vitality) for a character
    # given their level
    # the 4 base stats start at 37 at level 1
    num = 37

    # loop through each level and add the appropriate number to stats
    for x in range(2,level+1):
    # uggghh god look at this mostrosity
    # at levels 2-10, you get +7 each level
    # after that you only get stats every even level, and the number changes every 10-4-2-4 levels, except at the end
    # basically it's a bunch of non-standard bs and I practically had to had code every goddamn level uggghhhh
        if x < 11:
            num += 7
        elif x%2 == 0:
            if x < 21:
                num += 10
            elif x < 25:
                num += 14
            elif x < 27:
                num += 15
            elif x < 31:
                num += 16
            elif x < 41:
                num += 20
            elif x < 45:
                num += 24
            elif x < 47:
                num += 25
            elif x < 51:
                num += 26
            elif x < 61:
                num += 30
            elif x < 65:
                num += 34
            elif x < 67:
                num += 35
            elif x < 71:
                num += 36
            elif x < 75:
                num += 44
            elif x < 77:
                num += 45
            elif x < 81:
                num += 46
            else:
                print "uh, this shouldn't happen"
    stats['Power'] = num
    stats['Precision'] = num
    stats['Toughness'] = num
    stats['Vitality'] = num
    return stats

# grab the api key from the command line
apiKey = sys.argv[1]

# grab character and bank data, and get the MIL
chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)
masterItemList = gw2lib.getMIL()

# base stats dictionary, all values zero and an empty equips list
statsDict = {"Defense":0, "Power":0, "Toughness":0, "Vitality":0, "Precision":0, "CritDamage":0, "ConditionDamage":0,
             "Healing":0, "ConditionDuration":0, "Concentration":0, "Agony Resistance":0, "BoonDuration":0, "equips":[]}

# empty character dict, and a list of slots whose stats won't be summed up
charDict = {}
noCountSlots = ['HelmAquatic', 'WeaponAquaticA', 'WeaponAquaticB', 'WeaponB1', 'WeaponB2']

# for each character
for char in chars:
    # add their name to the dict keys and set it to the stats dict from makeStats, using a copy of statsDict so as not
    # to anger the almighty python and its WONDERFUL devotion the way of the fuckin' argument by reference
    charDict[char['name']] = makeStats(deepcopy(statsDict), char['level'])
    # for each piece of equipment (that isn't None and isn't in noCountSlots)
    for piece in char['equipment']:
        if piece is not None:
            if piece['slot'] not in noCountSlots:
                # get the item object
                itemObj = gw2lib.findByID(piece['id'], masterItemList)
                # the back piece check was just to see what the hell was going on with backpack stats
                # A BUNCH OF GODDAMN NONSENSE, THAT'S WHAT
                if piece['slot'] == 'Backpack':
                    print char['name'], piece, itemObj
                # if it's armor or a weapon that's a shield,
                if itemObj['type'] == 'Armor' or (itemObj['type'] == 'Weapon' and itemObj['details']['type'] == 'Shield'):
                    # it has a defense stat that should be counted
                    charDict[char['name']]['Defense'] += itemObj['details']['defense']
                # if it has 'infix_upgrade', it has stats that should be counted
                # because 'infix_upgrade' indicates that, right?
                if "infix_upgrade" in itemObj['details'].keys():
                    # for each attribute item, count up the appropriate modifier and add to the equips list:
                    # the name of the item it came from, the attribute, and modifier
                    for attrs in itemObj['details']['infix_upgrade']['attributes']:
                        charDict[char['name']][attrs['attribute']] += attrs['modifier']
                        charDict[char['name']]['equips'].append([itemObj['name'], attrs['attribute'], attrs['modifier']])

# output info
# in this case, the power stat of revelation orange and all the equipment that contributed to that number
# which APPARENTLY ISN'T THE DAMN BACKPACK
# or at least not the jewel part of it
# because hell with standardized stat locations, apparently
chkSt = 'Power'
chkCh = 'Revelation Orange'
print chkCh + ' ' + chkSt
for ch in charDict:
    if ch == chkCh:
        print charDict[ch][chkSt]
        for x in charDict[ch]['equips']:
            if x[1] == chkSt:
                print x

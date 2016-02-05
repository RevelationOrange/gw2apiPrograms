import gw2lib
import sys
from copy import deepcopy


def makeStats(stats, level):
    num = 37
    for x in range(2,level+1):
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

statsDict = {"Defense":0, "Power":0, "Toughness":0, "Vitality":0, "Precision":0, "CritDamage":0, "ConditionDamage":0,
             "Healing":0, "ConditionDuration":0, "Concentration":0, "Agony Resistance":0, "BoonDuration":0, "equips":[]}

charDict = {}
noCountSlots = ['HelmAquatic', 'WeaponAquaticA', 'WeaponAquaticB', 'WeaponB1', 'WeaponB2']

for char in chars:
    charDict[char['name']] = makeStats(deepcopy(statsDict), char['level'])
    for piece in char['equipment']:
        if piece is not None:
            if piece['slot'] not in noCountSlots:
                itemObj = gw2lib.findByID(piece['id'], masterItemList)
                if piece['slot'] == 'Backpack':
                    print char['name'], piece, itemObj
                if itemObj['type'] == 'Armor' or (itemObj['type'] == 'Weapon' and itemObj['details']['type'] == 'Shield'):
                    charDict[char['name']]['Defense'] += itemObj['details']['defense']
                if "infix_upgrade" in itemObj['details'].keys():
                    for attrs in itemObj['details']['infix_upgrade']['attributes']:
                        charDict[char['name']][attrs['attribute']] += attrs['modifier']
                        charDict[char['name']]['equips'].append([itemObj['name'], attrs['attribute'], attrs['modifier']])

chkSt = 'Power'
chkCh = 'Revelation Orange'
print chkCh + ' ' + chkSt
for ch in charDict:
    if ch == chkCh:
        print charDict[ch][chkSt]
        for x in charDict[ch]['equips']:
            if x[1] == chkSt:
                print x

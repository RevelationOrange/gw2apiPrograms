import gw2lib
import sys


def sumUpItems(bagObj, cIDs, bbr, bpls, nPB):
    for item in bagObj:
        if item is not None:
            for id in cIDs:
                if item['id'] == id[0]:
                    bbr[id[1]] += item['count']
                    if id[1] != 'Basic':
                        nPB += item['count']
                    if id[2] in bpls.keys():
                        bpls[id[2]][1] += item['count']
                    else:
                        bpls[id[2]] = [id[1], item['count']]
    return nPB


apiKey = sys.argv[1]
chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)

nProfitBags = 0
bagsByRarity = {'Junk': 0, 'Basic': 0, 'Fine': 0, 'Masterwork': 0, 'Rare': 0, 'Exotic': 0}

masterItemList = gw2lib.getMIL()

containerIDs = []

for x in masterItemList:
    if x['type'] == 'Container':
        if 'Mists' not in x['name'] and 'Black Lion Chest' not in x['name'] \
                and 'Transcendent Chest' is not x['name'] and 'Exotic Equipment' not in x['name']\
                and 'Weapons Box' not in x['name'] and 'Armor Box' not in x['name']:
            containerIDs.append([x['id'], x['rarity'], x['name']])

bagPrintLines = {}

res0 = sumUpItems(bank, containerIDs, bagsByRarity, bagPrintLines, nProfitBags)
nProfitBags = res0

for char in chars:
    for bag in char['bags']:
        if bag is not None:
            res = sumUpItems(bag['inventory'], containerIDs, bagsByRarity, bagPrintLines, nProfitBags)
            nProfitBags = res

for x in bagPrintLines.keys():
    print x + ' (' + bagPrintLines[x][0] + '), ' + str(bagPrintLines[x][1])

for x in bagsByRarity.keys():
    print x + 's: ' + str(bagsByRarity[x])
print 'total (non basic):', nProfitBags

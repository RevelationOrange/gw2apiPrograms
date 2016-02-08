import gw2lib
import sys


'''
countProfitBags counts up the total containers that drop random gear, across all characters and your bank
ex: not black lion chests or daily chests, but including 'bag of gear' and the like
prints summed results by name (excessive) and by rarity (more useful); basic rarity items not included in total count
'''

def sumUpItems(bagObj, cIDs, bbr, bpls, nPB):
    # counts up containers by rarity, not counting basic in the total count
    # must be given the dictionary to modify, and returns the total number of bags
    for item in bagObj:
        if item is not None:
            for id in cIDs:
                if item['id'] == id[0]:
                    # for each item in the given bag object, if it's in the list of container ids, increment the
                    # respective rarity counter and the total counter (if it isn't basic)
                    # then, if it's already been added to the names dict, increment the count, otherwise add it to
                    # the names dict as [rarity, count]
                    bbr[id[1]] += item['count']
                    if id[1] != 'Basic':
                        nPB += item['count']
                    if id[2] in bpls.keys():
                        bpls[id[2]][1] += item['count']
                    else:
                        bpls[id[2]] = [id[1], item['count']]
    return nPB

# gets the api key to use from the command line arguments, or exit if one isn't provided
if len(sys.argv) < 2:
    print "No api key provided. Please provide your api key as the first argument. If you need to create one, you can "\
          "do so at https://account.arena.net/applications"
    print "Be sure to include the 'character' and 'inventories' permissions for this program to work."
    sys.exit()
apiKey = sys.argv[1]
# grabs all the character data and bank info
chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)

# start all counts at 0 of course, using a dictionary to organize bags by rarity
nProfitBags = 0
bagsByRarity = {'Junk': 0, 'Basic': 0, 'Fine': 0, 'Masterwork': 0, 'Rare': 0, 'Exotic': 0}

# get master item list
masterItemList = gw2lib.getMIL()

containerIDs = []

# here, create a list of container info [id, rarity, name]
# unfortunately, it must use a specific list of exceptions, until rules can be found that determine whether or not
# a bag drops random gear (as opposed to special stuff like the black lion chest, or fixed rewards like armor box)
# simply go through every item in the master list and if it's a container and not one of the restricted names,
# add its id, rarity, and name to the list
for x in masterItemList:
    if x['type'] == 'Container':
        if 'Mists' not in x['name'] and 'Black Lion Chest' not in x['name'] \
                and 'Transcendent Chest' is not x['name'] and 'Exotic Equipment' not in x['name']\
                and 'Weapons Box' not in x['name'] and 'Armor Box' not in x['name']:
            containerIDs.append([x['id'], x['rarity'], x['name']])

bagPrintLines = {}

# res0 (result0 [super informative, I know]) is the total count from stuff in the bank
res0 = sumUpItems(bank, containerIDs, bagsByRarity, bagPrintLines, nProfitBags)
nProfitBags = res0

# for each character, go through each bag that exists and sumUpItems
# because of the way it uses nProfitBags, it can simply be set to the return value, as long as nProfitBags is used
# in the function call
for char in chars:
    for bag in char['bags']:
        if bag is not None:
            res = sumUpItems(bag['inventory'], containerIDs, bagsByRarity, bagPrintLines, nProfitBags)
            nProfitBags = res

# for each item name found (... should have done that by id, derp), output: name (rarity), count)
# this is probly excessive for printing, would be more useful written to a text file or something
for x in bagPrintLines.keys():
    print x + ' (' + bagPrintLines[x][0] + '), ' + str(bagPrintLines[x][1])

# output rarity info; ex: Rares: 420 (blaze it)
for x in bagsByRarity.keys():
    if bagsByRarity[x] == 420:
        derp = ' (blaze it)'
    else:
        derp = ''
    print x + 's: ' + str(bagsByRarity[x]) + derp
print 'total (non basic):', nProfitBags

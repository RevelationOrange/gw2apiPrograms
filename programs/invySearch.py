import gw2lib
import sys
import string


# grab the api key from the command line
apiKey = sys.argv[1]

# grab character and bank data, and get the MIL
chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)
masterItemList = gw2lib.getMIL()

findList = []

with open("finditems.txt", 'r') as listFile:
    for line in listFile:
        findList.append(line[:-1])

print findList
foundList = []

allInvys = []

for char in chars:
    for bag in char['bags']:
        if bag is not None:
            allInvys.append([char['name'], bag['inventory']])
            #for item in bag['inventory']:

allInvys.append(['bank', bank])

for bag in allInvys:
    for item in bag[1]:
        if item is not None:
            iName = gw2lib.findByID(item['id'], masterItemList)['name']
            if string.lower(iName) in [string.lower(x) for x in findList]:
                foundList.append([bag[0], iName])

for x in foundList:
    print x[1] + " - found on " + x[0]

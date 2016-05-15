import gw2lib
import sys
import string

'''
invySearch provides a quick way to find items across all characters + bank
uses a text file, finditems.txt, to easily enter a bunch of items to search for
'''

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

findList = []

# open finditems.txt and read it into findList, or just set the list to the item(s) you want after this part, if it's
# only a few you want to check
with open("finditems.txt", 'r') as listFile:
    for line in listFile:
        findList.append(line[:-1])

# make sure there's at least something in the findList; if not, remind the user of the text file location and exit
if len(findList) == 0:
    print 'no item names found in programs/finditems.txt\nto search for items, put each item you\'re looking for ' \
          'there, each on it\'s own line (capitalization doesn\'t matter, but spelling and punctuation do)'
    sys.exit()
foundList = []

allInvys = []

# loop through every inventory and just add every item that exists (plus location) to a master list
# this avoids needing a function to call for every bag on every character
for char in chars:
    for bag in char['bags']:
        if bag is not None:
            allInvys.append([char['name'], bag['inventory']])
            #for item in bag['inventory']:

allInvys.append(['bank', bank])

# go through every item and if the name matches, add it to foundList
for bag in allInvys:
    for item in bag[1]:
        if item is not None:
            iName = masterItemList[str(item['id'])]['name'] #gw2lib.findByID(item['id'], masterItemList)['name']
            if string.lower(iName) in [string.lower(x) for x in findList]:
                foundList.append([bag[0], iName])

# print what you found
if len(foundList) > 0:
    for x in foundList:
        print x[1] + " - found on " + x[0]
else: print 'none of the listed items found anywhere'

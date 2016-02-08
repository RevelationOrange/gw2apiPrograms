import json
import gw2lib
import time


'''
buildRSref just builds the reference files of runes and sigils, to be used with getRSprices in order to find
cheap alternatives to buying a rune or sigil on trade
the files it makes are lists of every item each rune/sigil is found in (including the rune/sigil itself)
'''

startTime = time.time()

# here I just wanted to time how long it takes to load the master item list; not necessary, obvs
mifStart = time.time()
# get the master item list v2
masterItemList = gw2lib.getMILv2()
mifEnd = time.time()
print 'mif make time:', mifEnd-mifStart, 'seconds'

# this returns a list of all superior runes and sigils
runeSigilObjs = gw2lib.getRuneSigilObjs(masterItemList)

# write all the names to a file; this is mainly just a sanity check
with open(gw2lib.searchFolderName+'allRuneSigilNames.txt', 'w') as namesFile:
    for x in runeSigilObjs:
        namesFile.write(x['name'] + '\n')

# save the objects to a file
with open(gw2lib.searchFolderName+'runesAndSigils.json', 'w') as allRSobjs:
    json.dump(runeSigilObjs, allRSobjs)

# for each rune/sigil object, get a list of items that contain it, and save that list to a file
for x in runeSigilObjs:
    # get the id real quick
    rsID = x['id']
    containers = []

    # the rune/sigil itself will of course be on the list
    containers.append(x)

    # getContainerLists() returns a list with every item that contains the given rune/sigil (by id#)
    # add this to the current containers list
    containers += gw2lib.getContainerLists(masterItemList, rsID)

    # save the json list to a file, named after the rune/sigil id
    with open(gw2lib.searchFolderName+str(rsID)+'.json', 'w') as containersFile:
        json.dump(containers, containersFile)

endTime = time.time()

print endTime-startTime,'seconds'

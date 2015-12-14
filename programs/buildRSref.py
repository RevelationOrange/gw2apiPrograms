import json
import gw2lib
import time


startTime = time.time()

mifStart = time.time()
with open(gw2lib.itemListFolder+gw2lib.masterItemFilename, 'r') as masterItemFile:
    masterItemList = json.load(masterItemFile)
mifEnd = time.time()
print 'mif make time:', mifEnd-mifStart, 'seconds'

runeSigilObjs = gw2lib.getRuneSigilObjs(masterItemList)

with open(gw2lib.searchFolderName+'allRuneSigilNames.txt', 'w') as namesFile:
    for x in runeSigilObjs:
        namesFile.write(x['name'] + '\n')

with open(gw2lib.searchFolderName+'runesAndSigils.json', 'w') as allRSobjs:
    json.dump(runeSigilObjs, allRSobjs)

for x in runeSigilObjs:
    rsID = x['id']
    containers = []
    containers.append(x)
    containers += gw2lib.getContainerLists(masterItemList, rsID)
    with open(gw2lib.searchFolderName+str(rsID)+'.json', 'w') as containersFile:
        json.dump(containers, containersFile)

endTime = time.time()

print endTime-startTime,'seconds'

'''
with codecs.open(searchFolderName+sigilName+'.csv', 'w', 'utf-8') as csvFile:
    csvFile.write("item name,item id\n")
    for x in sigilItems:
        print x['name'], x['id']
        csvFile.write(x['name'] + "," + str(x['id']))
        csvFile.write("\n")

print 'yay'
'''
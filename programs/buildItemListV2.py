from urllib2 import urlopen
import json
import gw2lib
import time


timeStart = time.time()

masterItemList = []
incr = 200
update = True

url = gw2lib.apiBase + gw2lib.itemsSubsect
itemIDlist = json.load(urlopen(url))

lastListIndex = len(itemIDlist)
lastItemID = itemIDlist[-1]
print 'final item ID:', lastItemID, ', final list index:', lastListIndex

if update:
    print 'updating'
    masterItemList = gw2lib.getMIL()
    currentIDs = sorted([x['id'] for x in masterItemList ])
    newIDs = list(set(itemIDlist)^set(currentIDs))
    if len(newIDs) > 0:
        print newIDs,'\n',len(newIDs)
        [urlReqList, filenameRanges] = gw2lib.makeReqUrlList(newIDs)
        newItemList = []
        for x in urlReqList:
            print x
        for urlReq in urlReqList:
            newItemList += json.load(urlopen(urlReq))
        masterItemList += newItemList
        masterItemList = sorted(masterItemList, cmp=gw2lib.compareByID)
        with open(gw2lib.itemListFolder+gw2lib.newItemsFilename, 'a') as newItemsFile:
            newItemsFile.write( ','.join(str(x) for x in newIDs) + '\t' + time.strftime("%c") + '\n' )
        with open(gw2lib.itemListFolder+gw2lib.newNamesFilename, 'a') as newNamesFile:
            newNamesFile.write( ','.join( x['name'] for x in newItemList ) + '\t' + time.strftime("%c") + '\n' )
        with open(gw2lib.itemListFolder+gw2lib.masterItemFilename, 'w') as masterItemFile:
            json.dump(masterItemList, masterItemFile)
    else:
        print 'oop, no need'

    print 'finished'
else:

    # requestURLs = []

    [requestURLs, filenamesStartEnd] = gw2lib.makeReqUrlList(itemIDlist)

    # filenamesStartEnd = []
    i = 0
    for req in requestURLs:
        itemList = json.load(urlopen(req))
        masterItemList += itemList
        # print len(masterItemList)
        filenameString = gw2lib.itemListFolder+'ids'+str(filenamesStartEnd[i][0])+'_'+str(filenamesStartEnd[i][1])+'.json'
        with open(filenameString, 'w') as itemFile:
            json.dump(itemList, itemFile)
        print filenameString,'written\n'
        i += 1
    with open(gw2lib.itemListFolder+gw2lib.masterItemFilename, 'w') as masterItemFile:
        json.dump(masterItemList, masterItemFile)
    print len(masterItemList),'ids saved to master item list'

timeEnd = time.time()
runTime = timeEnd-timeStart
if runTime > 3600:
    print str(runTime/3600.) + " hours"
elif runTime > 60:
    print str(runTime/60.) + " minutes"
else:
    print str(runTime) + " seconds"


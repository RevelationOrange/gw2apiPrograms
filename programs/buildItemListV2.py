from urllib2 import urlopen
import json
import gw2lib
import time
import sys
import codecs


'''
buildItemListV2 is used to create the file masterItemList.json, which contains the json objects for every item id
in the guild wars 2 item api endpoint.
to build the list the first time, update should be set to False. after it's built, set update to True, and it will
only call the api on ids that are new.
or just leave update alone and use the command line options --new, new, or -n to make a new master list
'''

timeStart = time.time()

masterItemList = []
# incr is the most number of ids that the api will allow you to request. this likely won't ever change.
incr = 200
update = True

# this allows command line arguments to be used to create the list the first time, instead of editing the file
# the options --new, new, or -n will cause this program to run the first-time code
if len(sys.argv) > 1:
    if sys.argv[1] == '--new' or sys.argv[1] == 'new' or sys.argv[1] == '-n':
        update = False

# this url (https://api.guildwars2.com/v2/items?) returns a list of every existing item id (well, it's supposed to.
# see gw2lib.findByID() for more info.)
url = gw2lib.apiBase + gw2lib.itemsSubsect
itemIDlist = json.load(urlopen(url))

# the last ID isn't really important, just nice to know. lastListIndex is needed to build the list of url requests
lastListIndex = len(itemIDlist)
lastItemID = itemIDlist[-1]
print 'final item ID:', lastItemID, ', final list index:', lastListIndex

if update:
    # this is the code that will usually be run.
    print 'updating'
    masterItemList = gw2lib.getMIL()

    # get a list of the ids from the current masterItemList.json, and sort them
    currentIDs = sorted([x['id'] for x in masterItemList ])

    # compare using sets and get a list of the ids that exist in the list from the api but not in the list from
    # masterItemList.json
    newIDs = list(set(itemIDlist)^set(currentIDs))

    # if there are any new ids:
    if len(newIDs) > 0:
        # not necessary, but nice to see the new ids
        print newIDs,'\n',len(newIDs)

        # use makeReqUrlList to get a list containing strings, each of which is a url to request up to 200 item ids
        # from the api. filename ranges isn't really necessary here.
        [urlReqList, filenameRanges] = gw2lib.makeReqUrlList(newIDs)
        newItemList = []

        # again, not necessary, but nice to see all the request urls. plus, you can just click then and check out
        # some of the new items.
        for x in urlReqList:
            print x

        # for each request url, make a call to the api and add the resulting json data to newItemList
        for urlReq in urlReqList:
            newItemList += json.load(urlopen(urlReq))

        # add newItemList to the master list. I guess I could have just added it to the master list directly,
        # newItemList seems like an extra step.
        masterItemList += newItemList

        # sort the master item list by id using gw2lib.compareByID()
        masterItemList = sorted(masterItemList, cmp=gw2lib.compareByID)

        # write statements: newItemsFile gets a list of the new ids, comma separated with a tab and the full current
        # time at the end. newNamesFile gets the same but with names instead of ids. finally, the new master item list
        # is saved over the old one.
        with open(gw2lib.itemListFolder+gw2lib.newItemsFilename, 'a') as newItemsFile:
            newItemsFile.write( ','.join(str(x) for x in newIDs) + '\t' + time.strftime("%c") + '\n' )
        with codecs.open(gw2lib.itemListFolder+gw2lib.newNamesFilename, 'a', 'utf-8') as newNamesFile:
            newNamesFile.write( ','.join( x['name'] for x in newItemList ) + '\t' + time.strftime("%c") + '\n' )
        with open(gw2lib.itemListFolder+gw2lib.masterItemFilename, 'w') as masterItemFile:
            json.dump(masterItemList, masterItemFile)
    else:
        # no new ids? no need to update
        print 'oop, no need'

    print 'finished'
else:
    # same as in the update section, get a list of all the request urls, only this time it's every single item id
    # returned by the api, in sets of 200
    [requestURLs, filenamesStartEnd] = gw2lib.makeReqUrlList(itemIDlist)

    # i keeps track of the index associated with each set of 200 ids stored in requestURLs
    i = 0
    for req in requestURLs:
        # for each request, get the json data for those 200 items
        itemList = json.load(urlopen(req))

        # add them to the master item list
        masterItemList += itemList

        # create a string to name the file where those 200 items will be stored
        # this will be 'ids####_####.json', where the start and end ids are stored in filenamesStartEnd
        # i keeps filenamesStartEnd in track with requestURLs
        filenameString = gw2lib.itemListFolder+'ids'+str(filenamesStartEnd[i][0])+'_'+str(filenamesStartEnd[i][1])+'.json'

        # open the file and save the 200 items using json.dump()
        with open(filenameString, 'w') as itemFile:
            json.dump(itemList, itemFile)
        print filenameString,'written\n'
        i += 1
    # once all the urls are used and masterItemList has everything, save it to masterItemList.json
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

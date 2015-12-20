from urllib2 import urlopen
import gw2lib
import json
import codecs
import time
import sys
from operator import itemgetter


'''
getRSprices makes a list of the highest buy and lowest sell offers for all items containing a particular rune/sigil
includes a top 5 buy and sell for each rune/sigil; full list is saved to a csv, top 5 lists also printed out
by leaving rsNames empty and using no command line arguments, every rune and sigil will be checked
arguments provided on the command line are assumed to be case sensitive rune/sigil names; can provide any number, all
will be checked
'''

startTime = time.time()

def makeCsvList(prices, containers):
    # creates a list of lines to print to a csv file, looks like:
    # item name     buy price       sell price      item id
    csvList = []
    for x in prices:
        id = x['id']
        # get the item object from the containers list provided
        item = gw2lib.findByID(id, containers)
        # use formatCoins from gw2lib to get the buy and sell price in gold for each entry in prices
        buyCoins = gw2lib.formatCoins(x['buys']['unit_price'],'gold')[0]
        sellCoins = gw2lib.formatCoins(x['sells']['unit_price'],'gold')[0]
        # put it all in a list, and append that list to the csvList (of lists)
        csvLine = [ item['name'], buyCoins, sellCoins, id ]
        csvList.append(csvLine)
    return csvList

# the runes/sigils to check can be set here, but any provided on the command line will take priority
rsNames = ['Superior Sigil of Energy']
# rsNames = []
if len(sys.argv) > 1:
    rsNames = sys.argv[1:]

# if rsNames is empty, read in all rune/sigil names from file
if len(rsNames) < 1:
    with open(gw2lib.searchFolderName+'allRuneSigilNames.txt') as nameFile:
        rsNames = [x[:-1] for x in nameFile]

# grab all the rune and sigil objects from file
with open(gw2lib.searchFolderName+gw2lib.runeAndSigilsFilename) as rsRefFile:
        runeSigilObjs = json.load(rsRefFile)

# for each rune/sigil name:
for rsName in rsNames:
    # get the object by name
    rsID0 = gw2lib.findByX(rsName, 'name', runeSigilObjs)
    ''' NOTE: here, may need to fix, or replace getID() function '''
    # if more than 1 object is returned, that's wrong, exit (this should probly be handled better)
    if len(rsID0) > 1:
        sys.exit()

    # get the id number
    rsID = rsID0[0]['id']

    # using the id, get the containers list for that rune/sigil from its file id#.json
    with open(gw2lib.searchFolderName+str(rsID)+'.json', 'r') as ctList:
        containersList = json.load(ctList)

    pricesList = []
    idsCsvList = []
    start = 0
    end = start
    # here, use the container ids list to make comma separated strings of 200 ids, to use to make the api requests
    while end < len(containersList):
        end += 200
        # this if statement was a single exception to avoid making a url request of all bad ids
        # it might not be necerssary any more, I'll have to check
        if (rsID == 24561 and end > 200):
            continue

        # join on commas: the 'id' of each thing ins containersList from the current start to end index
        # this is a range of 200, and in the last iteration of the loop, end will be past the actual end of
        # containersList, but thanks to python being super nice, start:end will simply go to the end of the list
        idsCsvList.append([','.join([ str(x['id']) for x in containersList[start:end] ])])
        start += 200

    # once the id strings are made, go through them and append them to 'api/commerce/prices?ids=', call the api, and
    # add the result to the prices list
    for x in idsCsvList:
        fullReqURL = gw2lib.apiBase + gw2lib.commercePricesSubsect + gw2lib.idsReq + x[0]
        pricesList += json.load(urlopen(fullReqURL))

    # now use makeCsvList() to make the output list, which is a list of lists, each of which contains the item name,
    # buy price in gold, sell price in gold, and item id
    outputList = makeCsvList(pricesList,containersList)
    # if the outputList doesn't contain anything, skip this item
    if len(outputList) < 1:
        continue
    # now make lists of the cheapest 5 buy and sell orders
    # each entry in the lowest 5 list is is the respective buy or sell price, and the item name
    # to start with, just use the first item from each list 5 times, since the highest price will be replaced and the
    # list sorted each time. in the case of runes/sigils with less than 5 associated items, this will mean repeated
    # lowest 5 lists, but eh
    lowBuy = [ outputList[0][1], outputList[0][0] ]
    lowBuy5 = [lowBuy]*5
    lowSell = [ outputList[0][2], outputList[0][0] ]
    lowSell5 = [lowSell]*5

    for x in outputList:
        # go through each item in the output list, if the buy price is lower than the buy price of the last item on the
        # lowBuy5 list, replace it and sort the list; same with the sell price (of x) and the lowSell5 list
        if x[1] < lowBuy5[-1][0]:
            lowBuy5[-1] = [ x[1], x[0] ]
            lowBuy5 = sorted(lowBuy5, key=itemgetter(0))
        if x[2] < lowSell5[-1][0]:
            lowSell5[-1] = [ x[2], x[0] ]
            lowSell5 = sorted(lowSell5, key=itemgetter(0))

    # use the codecs library to open the csv file for writing, since some item names exist (ex; mjollnir) that have
    # weird characters and can't be written normally
    # each csv file name will be the name of the rune/sigil followed by .csv
    with codecs.open(gw2lib.rsPricesFolderName+rsName+'.csv', 'w', 'utf-8') as csvFile:
        # header line
        csvFile.write('name,highest buy (gold),lowest sell (gold), id\n')

        # for each line (which is a list) in the output list, join it on commas and write it (with a new line) to the
        # csv file
        for x in outputList:
            # this stupid statement exists because str() can't be called on those weird characters, so it has to be
            # called on the 2nd-4th items in x individually while leaving x[0] alone
            writeline = ','.join([ x[0], str(x[1]), str(x[2]), str(x[3])])
            csvFile.write(writeline + '\n')

        # now write header lines for lowest 5 buy and sell lists, and the lists themselves; aligned to the first header
        # in the file, so one extra space in each line for the sell list. ex:
        # name  buy price
        # name              sell price
        csvFile.write('\nLowest 5 buy orders\n')
        for x in lowBuy5:
            csvFile.write(x[1] + ',' + str(x[0]) + '\n')
        csvFile.write('\nLowest 5 sell offers\n')
        for x in lowSell5:
            csvFile.write(x[1] + ', ,' + str(x[0]) + '\n')

    # here, print a (somewhat) nicely formatted version of the lowest 5 buy and sell lists, so you don't have to
    # open the csv file if you're just after the lowest prices
    # there are a few items with very long names where this formatting still doesn't quite work, but eh
    print '{:<40}{:<6}\t{:<40}{:<6}'.format('Five Lowest Buys', 'price', 'Five Lowest Sells', 'price')
    for i in range(0,len(lowBuy5)):
        print '{:<40}{:<6}\t{:<40}{:<6}'.format(lowBuy5[i][1], lowBuy5[i][0], lowSell5[i][1], lowSell5[i][0])
    print '\n'

endTime = time.time()

print 'runtime =',endTime-startTime,'seconds'

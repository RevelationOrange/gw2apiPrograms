from urllib2 import urlopen
import gw2lib
import json
import codecs
import time
import sys
from operator import itemgetter


startTime = time.time()

def makeCsvList(prices, containers):
    csvList = []
    for x in prices:
        id = x['id']
        item = gw2lib.findByID(id, containers)
        buyCoins = gw2lib.formatCoins(x['buys']['unit_price'],'gold')[0]
        sellCoins = gw2lib.formatCoins(x['sells']['unit_price'],'gold')[0]
        csvLine = [ item['name'], buyCoins, sellCoins, id ]
        # print csvLine
        csvList.append(csvLine)
    return csvList


rsNames = ['Superior Sigil of Energy']
# rsNames = []

if len(rsNames) < 1:
    with open(gw2lib.searchFolderName+'allRuneSigilNames.txt') as nameFile:
        rsNames = [x[:-1] for x in nameFile]

with open(gw2lib.searchFolderName+gw2lib.runeAndSigilsFilename) as rsRefFile:
        runeSigilObjs = json.load(rsRefFile)

for rsName in rsNames:
    rsID0 = gw2lib.findByX(rsName, 'name', runeSigilObjs)
    ''' NOTE: here, may need to fix, or replace getID() function '''
    if len(rsID0) > 1:
        sys.exit()

    rsID = rsID0[0]['id']

    with open(gw2lib.searchFolderName+str(rsID)+'.json', 'r') as ctList:
        containersList = json.load(ctList)

    pricesList = []
    idsCsvList = []
    start = 0
    end = start
    while end < len(containersList):
        end += 200
        if (rsID == 24561 and end > 200):
            continue
        idsCsvList.append([','.join([ str(x['id']) for x in containersList[start:end] ])])
        start += 200
    for x in idsCsvList:
        fullReqURL = gw2lib.apiBase + gw2lib.commercePricesSubsect + gw2lib.idsReq + x[0]
        pricesList += json.load(urlopen(fullReqURL))

    outputList = makeCsvList(pricesList,containersList)
    if len(outputList) < 1:
        continue
    lowBuy = [ outputList[0][1], outputList[0][0] ]
    lowBuy5 = [lowBuy]*5
    lowSell = [ outputList[0][2], outputList[0][0] ]
    lowSell5 = [lowSell]*5

    for x in outputList:
        if x[1] < lowBuy5[-1][0]:
            lowBuy5[-1] = [ x[1], x[0] ]
            lowBuy5 = sorted(lowBuy5, key=itemgetter(0))
        if x[2] < lowSell5[-1][0]:
            lowSell5[-1] = [ x[2], x[0] ]
            lowSell5 = sorted(lowSell5, key=itemgetter(0))

    with codecs.open(gw2lib.rsPricesFolderName+rsName+'.csv', 'w', 'utf-8') as csvFile:
        csvFile.write('name,highest buy (gold),lowest sell (gold), id\n')
        for x in outputList:
            writeline = ','.join([ x[0], str(x[1]), str(x[2]), str(x[3])])
            csvFile.write(writeline + '\n')
        csvFile.write('\nLowest 5 buy orders\n')
        for x in lowBuy5:
            csvFile.write(x[1] + ',' + str(x[0]) + '\n')
        csvFile.write('\nLowest 5 sell offers\n')
        for x in lowSell5:
            csvFile.write(x[1] + ', ,' + str(x[0]) + '\n')


    print '{:<40}{:<6}\t{:<40}{:<6}'.format('Five Lowest Buys', 'price', 'Five Lowest Sells', 'price')
    for i in range(0,len(lowBuy5)):
        print '{:<40}{:<6}\t{:<40}{:<6}'.format(lowBuy5[i][1], lowBuy5[i][0], lowSell5[i][1], lowSell5[i][0])
    print '\n'



endTime = time.time()

print 'runtime =',endTime-startTime,'seconds'


'''
with codecs.open(searchFolderName+sigilName+'.csv', 'w', 'utf-8') as csvFile:
    csvFile.write("item name,item id\n")
    for x in sigilItems:
        print x['name'], x['id']
        csvFile.write(x['name'] + "," + str(x['id']))
        csvFile.write("\n")
'''
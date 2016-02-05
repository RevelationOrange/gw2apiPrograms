import gw2lib
import sys
from copy import deepcopy
import time


'''
craftingProfit will go through one/all your characters' known recipes and calculate the difference between the cost (on
trade) off all the ingredients and the sell price (minus fees) of the resulting item, and show you the most profitable
recipes you know
'''

def chkRec(itemID, count):
    # get recipe that produces itemID via: searching masterRecipeList
    recObjs = gw2lib.findByX(itemID, 'output_item_id', masterRecipeList)
    if len(recObjs) == 1:
        recObj = recObjs[0]
        trChk = deepcopy( recObj['ingredients'] )
        for ingr in trChk:
            ingr['buyPrice'] = 2
            ingr['count'] *= count
            ingr['name'] = gw2lib.findByID(ingr['item_id'], masterItemList)['name']
            ingr['ingredients'] = chkRec(ingr['item_id'], ingr['count'])
        return trChk
    elif len(recObjs) < 1:
        return None
    else:
        print ">1 recipes found"
        return None

def printRecTrail(ingrs, nTabs=1):
    for ingr in ingrs:
        print '\t'*nTabs + 'item id: ' + str(ingr['item_id']) + ', name: ' + ingr['name'] + ', COUNT: ' +\
              str(ingr['count']) + ', buy price: ' + str(ingr['buyPrice'])
        if ingr['ingredients'] is not None:
            printRecTrail(ingr['ingredients'], nTabs+1)

# grab the api key from the command line
apiKey = sys.argv[1]

# grab character and bank data, and get the MIL
chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)
masterItemList = gw2lib.getMIL()
masterRecipeList = gw2lib.getMRL()

recipeList = []
for char in chars:
    if char['name'] == 'Revelation Orange':
        recipeList = char['recipes']
        #print char['recipes']

#print recipeList
#recipeList = [11725]
tradeChecks = []
#print len(recipeList)

# timing
timeStart = time.time()

for recID in recipeList[:]:
    trChk = {} #chkRec(recID)
    recObj = gw2lib.findByID(recID, masterRecipeList)
    trChk['sourceID'] = recObj['output_item_id']
    trChk['buyPrice'] = 2
    trChk['name'] = gw2lib.findByID(trChk['sourceID'], masterItemList)['name']
    trChk['ingredients'] = deepcopy( recObj['ingredients'] )
    for ingr in trChk['ingredients']:
        ingr['buyPrice'] = 2
        ingr['name'] = gw2lib.findByID(ingr['item_id'], masterItemList)['name']
        ingr['ingredients'] = chkRec(ingr['item_id'], ingr['count'])
    tradeChecks.append(trChk)

timeEnd = time.time()

a = {'item_id':46742, 'buyPrice':2, 'ingredients':[{'item_id':19721, 'count':1, 'buyPrice':2, 'ingredients':[]},
                                                   {'item_id':46747, 'count':10, 'buyPrice':2, 'ingredients':[]},
                                                   {'item_id':19684, 'count':50, 'buyPrice':2, 'ingredients':[{'source_output':19700, 'count':2, 'buyPrice':2, 'ingredients':[]}]
                                                    }
                                                   ]}
'''
for x in tradeChecks:
    print 'source id: ' + str(x['sourceID']) + ', name: ' + x['name'] + ', buy price: ' + str(x['buyPrice'])
    printRecTrail(x['ingredients'])
    print ''
'''

print timeEnd-timeStart, 's'

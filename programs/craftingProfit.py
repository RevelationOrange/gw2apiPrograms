import gw2lib
import sys
from copy import deepcopy
import time


'''
craftingProfit will go through one/all your characters' known recipes and calculate the difference between the cost (on
trade) off all the ingredients and the sell price (minus fees) of the resulting item, and show you the most profitable
recipes you know
'''

'''
currently: gets a full recipe path with correct counts for each ingredient, adds placeholder buy prices for each item,
and makes a list of all item ids involved in the recipe

todo: make that id list into a dict that determines what to do with each id (check trade, get the vendor price, etc.)
get the price of each item on trade, which involves coming up with a way to group ids together in a single request and
put them back in the right place after
doing an api call for each id would take a horrendous amount of time
'''

def chkRec(itemID, count, idsList):
    # recursive function that adds the ingredients list of the recipe that produces the current item to that item's
    # ingredients dict

    # get the recipe object by searching the master recipe list for the given item id
    recObjs = gw2lib.findByX(itemID, 'output_item_id', masterRecipeList)
    # if there's exactly 1 resulting recipe:
    if len(recObjs) == 1:
        recObj = recObjs[0]
        # deepcopy the ingredients list (oh python, you crazy reference obsessed fool)
        trChk = deepcopy( recObj['ingredients'] )
        # go through each ingredient:
        for ingr in trChk:
            # set the buy price to 2 (will change later to actually get the buy price)
            ingr['buyPrice'] = None
            # update the count- multiply the count of the ingredient by the count of the recipe 'above' it
            # this ensures nested recipes have the correct total counts for the ingredients at the bottom
            ingr['count'] *= count
            # add the id to the ids list, which for now just tracks every item id involved in the top level recipe
            idsList.append(ingr['item_id'])
            # add the item name
            ingr['name'] = gw2lib.findByID(ingr['item_id'], masterItemList)['name']
            # get the ingredients list (if it exists) for the recipe 'below'
            ingr['ingredients'] = chkRec(ingr['item_id'], ingr['count'], idsList)
        # return the updated ingredients list
        return trChk
    # if there are no recipes that produce itemID, return None
    elif len(recObjs) < 1:
        return None
    # if there are multiple recipes that produce an item, output a message about it; I'll figure out what to do about
    # it later
    else:
        print ">1 recipes found"
        return None

def printRecTrail(ingrs, nTabs=1):
    # this recursively prints the ingredients for a recipe
    # go through each ingredient
    for ingr in ingrs:
        # add tabs to visually show what 'level' these ingredients are on, print the item id, name, count, and buy price
        print '\t'*nTabs + 'item id: ' + str(ingr['item_id']) + ', name: ' + ingr['name'] + ', COUNT: ' +\
              str(ingr['count']) + ', buy price: ' + str(ingr['buyPrice'])
        # if there are any further ingredients, call printRecTrail again to print them
        if ingr['ingredients'] is not None:
            printRecTrail(ingr['ingredients'], nTabs+1)

# grab the api key from the command line, or exit if one isn't provided
if len(sys.argv) < 2:
    print "No api key provided. Please provide your api key as the first argument. If you need to create one, you can "\
          "do so at https://account.arena.net/applications"
    print "Be sure to include the 'character' and 'inventories' permissions for this program to work."
    sys.exit()
apiKey = sys.argv[1]

# grab character and bank data, and get the MIL and MRL
chars = gw2lib.getAllCharacterData(apiKey)
bank = gw2lib.getBankData(apiKey)
masterItemList = gw2lib.getMIL()
masterRecipeList = gw2lib.getMRL()

# recipe list will be every recipe to check
recipeList = []
# for now just check recipes on one character
chkChar = 'Revelation Orange'
# go through the characters and get the recipe ids list of the character you want
for char in chars:
    if char['name'] == chkChar:
        recipeList = char['recipes']
        #print char['recipes']

#recipeList = [11725]
# hold trChk objects here, which will keep track of ids, counts, and buy prices
tradeChecks = []
#print len(recipeList)

# this part was timed to check if using api/recipes/search?output= was faster than looping through the master recipe
# list; the api was MUCH slower
timeStart = time.time()

# for the recipe ids you want to chcek (limited list for now, just to make sure things work):
for recID in recipeList[-100:]:
    # trChk will be the dict added to the tradeChecks list
    trChk = {}
    # get the recipe object for the given id
    recObj = gw2lib.findByID(recID, masterRecipeList)
    # add the item id to the dict and the ids list
    trChk['sourceID'] = recObj['output_item_id']
    trChk['idsList'] = [trChk['sourceID']]
    # add a placeholder buy price
    trChk['buyPrice'] = None
    # get the item name
    trChk['name'] = gw2lib.findByID(trChk['sourceID'], masterItemList)['name']
    # deepcopy the ingredients list for this recipe
    trChk['ingredients'] = deepcopy( recObj['ingredients'] )
    for ingr in trChk['ingredients']:
        # add the name and a placeholder buy price for each ingredient
        ingr['name'] = gw2lib.findByID(ingr['item_id'], masterItemList)['name']
        ingr['buyPrice'] = None
        # and add the id to the ids list
        trChk['idsList'].append(ingr['item_id'])
        # call chkRec to get the same info for each ingredient
        ingr['ingredients'] = chkRec(ingr['item_id'], ingr['count'], trChk['idsList'])
    # append the dict to the tradeChecks list
    tradeChecks.append(trChk)

timeEnd = time.time()

a = {'item_id':46742, 'buyPrice':2, 'ingredients':[{'item_id':19721, 'count':1, 'buyPrice':2, 'ingredients':[]},
                                                   {'item_id':46747, 'count':10, 'buyPrice':2, 'ingredients':[]},
                                                   {'item_id':19684, 'count':50, 'buyPrice':2, 'ingredients':[{'source_output':19700, 'count':2, 'buyPrice':2, 'ingredients':[]}]
                                                    }
                                                   ]}

# output the info for some of the recipes to check if it's working
for x in tradeChecks[:]:
    print 'source id: ' + str(x['sourceID']) + ', name: ' + x['name'] + ', buy price: ' + str(x['buyPrice'])
    print len(x['idsList']), x['idsList']
    printRecTrail(x['ingredients'])
    print ''


print timeEnd-timeStart, 's'

import gw2lib
import sys
from copy import deepcopy
import json
from urllib2 import urlopen
import time
from operator import attrgetter


'''
craftingProfit will go through one/all your characters' known recipes and calculate the difference between the cost (on
trade) off all the ingredients and the sell price (minus fees) of the resulting item, and show you the most profitable
recipes you have
'''

'''
currently: gets a full recipe path with correct counts for each ingredient, adds prices for each ingredient from each
source for it (ex trade buy/sell if it's on trade, crafting price if it has ingredients itself, which is the sum of the
tp prices for all its ingredients [this may not be super clear, I might have to write a better explanation]), calculates
crafting costs vs tp costs, and shows the difference between crafting and trade price (for buy and sell trade price).
finally, sorts the recipe list by price difference (biggest to smallest) and shows the top x of them.

todo: figure out a way to get vendor/karma vendor costs for items that have that option, which sometimes includes things
that are also found on tp, so that's kinda annoying. the bigger issue is that there doesn't seem to be any way to get
that info from the api, or any place that can be accessed with code. so I might have to hand make a list of vendor
prices for every item involved in crafting. oh boy.
'''

def chkRec(itemID, count):
    # recursive function that adds the ingredients list of the recipe that produces the current item to that item's
    # ingredients dict

    # get the recipe object by searching the master recipe list for the given item id
    recObjs = gw2lib.findByX(itemID, 'output_item_id', masterRecipeList)
    # if there's exactly 1 resulting recipe:
    if len(recObjs) == 1:
        recObj = recObjs[0]
        # deepcopy the ingredients list (oh python, you crazy reference obsessed fool)
        recChk = deepcopy( recObj['ingredients'] )
        # go through each ingredient:
        for ingr in recChk:
            # set the buy price to 2 (will change later to actually get the buy price)
            ingr['costInfo'] = None
            # update the count- multiply the count of the ingredient by the count of the recipe 'above' it
            # this ensures nested recipes have the correct total counts for the ingredients at the bottom
            ingr['count'] *= count
            # add the id to the ids list, which for now just tracks every item id involved in the top level recipe
            ingrID = ingr['item_id']
            if masterItemList[str(ingrID)]['TPable']:
                tradeIDs.append(ingrID)
            else:
                allIDsDict[ingrID] = {'source':'something', 'cost':'someNumber'}
            # add the item name
            ingr['name'] = masterItemList[str(ingr['item_id'])]['name'] #gw2lib.findByID(ingr['item_id'], masterItemList)['name']
            # get the ingredients list (if it exists) for the recipe 'below'
            ingr['ingredients'] = chkRec(ingrID, ingr['count'])
        # return the updated ingredients list
        return recChk
    # if there are no recipes that produce itemID, return None
    elif len(recObjs) < 1:
        return None
    # if there are multiple recipes that produce an item, output a message about it; I'll figure out what to do about
    # it later
    else:
        print ">1 recipes found"
        return None

def fillCosts(ingredientList):
    # fillCosts goes through an ingredient list and fills out the costInfo dict with prices

    # ingredients best buy/sell price, set to 0 and summed up for all ingredients in the list and returned, to properly
    # count up crafting costs. crafting cost is the lower of the trading price or crafting price (each for buy or sell
    # prices on trade) of each of the ingredients
    ingrbbp = 0
    ingrbsp = 0

    # for each ingredient in the list:
    for ingr in ingredientList:
        # get the dictionary that will be costInfo from the allIDsDict, which contains price info and source location
        costInfo = allIDsDict[ingr['item_id']]
        # make a copy of it for the ingredient itself
        ingr['costInfo'] = costInfo.copy()
        # if it's on the trading post:
        if costInfo['source'] == 'trading post':
            # multiply the buy and sell prices by the count of the ingredient
            ingr['costInfo']['buyPrice'] *= ingr['count']
            ingr['costInfo']['sellPrice'] *= ingr['count']
        # if the ingredient ingredients list is empty:
        if ingr['ingredients'] is None:
            # this means it's a bottom level ingredient (no recipe creates it)
            # if it's on the trading post, the prices to sum for this ingredient, x (the buy price) and y (the sell
            # price) will just be the trading post prices
            if costInfo['source'] == 'trading post':
                x = ingr['costInfo']['buyPrice']
                y = ingr['costInfo']['sellPrice']
            # if it's not on trade, I have no way of getting the price right now (that'll come later), so just call it 0
            else:
                x = 0.0
                y = x
        # if there are ingredients, x and y will be the result of fillCosts() for those ingredients (whoo, recursion!)
        else:
            [x, y] = fillCosts(ingr['ingredients'])
        # this individual ingredient prices with be x and y
        ingr['costInfo']['craftBuyPrice'] = x
        ingr['costInfo']['craftSellPrice'] = y
        # if this ingredient is on trade, increase the ingredient sums by the lesser of the total ingredients cost or
        # the tp cost
        if costInfo['source'] == 'trading post':
            ingrbbp += min(x, ingr['costInfo']['buyPrice'])
            ingrbsp += min(y, ingr['costInfo']['sellPrice'])
        # if it's not on trade, just increase the ingredient sums by the ingredients cost
        else:
            ingrbbp += x
            ingrbsp += y
    # finally, return the sum of costs for this ingredients list
    return [ingrbbp, ingrbsp]

def printRecTrail(ingrs, nTabs=1):
    # this recursively prints the ingredients for a recipe
    # go through each ingredient
    for ingr in ingrs:
        # add tabs to visually show what 'level' these ingredients are on, print the item id, name, count, and buy price
        pstring = '\t'*nTabs + 'item id: ' + str(ingr['item_id']) + ', name: ' + ingr['name'] + ', count: ' +\
                  str(ingr['count'])
        if ingr['costInfo']['source'] == 'trading post':
            pstring += ', tp buy, sell prices: ' + str(ingr['costInfo']['buyPrice']) + ', ' +\
                       str(ingr['costInfo']['sellPrice'])
        else:
            pstring += ', price: ' + str(ingr['costInfo']['cost'])
        if ingr['ingredients'] is not None:
            pstring += ', crafting buy, sell prices: ' + str(ingr['costInfo']['craftBuyPrice']) + ', ' +\
                       str(ingr['costInfo']['craftSellPrice'])
        print pstring
        # if there are any further ingredients, call printRecTrail again to print them
        if ingr['ingredients'] is not None:
            printRecTrail(ingr['ingredients'], nTabs+1)

def printTrimRecTrail(ingrs, nTabs=1):
    # this recursively prints the trimmed ingredients for a recipe
    # go through each ingredient
    for ingr in ingrs:
        # add tabs to visually show what 'level' these ingredients are on, print the item id, name, count, and buy price
        pstring = '\t'*nTabs + 'item id: ' + str(ingr['item_id']) + ', name: ' + ingr['name'] + ', count: ' +\
                  str(ingr['count'])
        if ingr['costInfo']['source'] == 'trading post':
            pstring += ', tp buy, sell prices: ' + str(ingr['costInfo']['buyPrice']) + ', ' +\
                       str(ingr['costInfo']['sellPrice'])
        if ingr['ingredients'] is not None:
            pstring += ', crafting buy, sell prices: ' + str(ingr['costInfo']['craftBuyPrice']) + ', ' +\
                        str(ingr['costInfo']['craftSellPrice'])
        print pstring
        # if there are any further ingredients, call printRecTrail again to print them
        if ingr['ingredients'] is not None:
            printTrimRecTrail(ingr['ingredients'], nTabs+1)

def compByBuyDiff(x, y):
    return cmp(x['buyDiff'], y['buyDiff'])

def compBySellDiff(x, y):
    return cmp(x['sellDiff'], y['sellDiff'])

start = time.time()

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
masterItemList = gw2lib.getMILv2()
masterRecipeList = gw2lib.getMRLv2()

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
# hold trChk objects here, which will keep track of ids, counts, and buy/sell prices
recipeChecks = []
#print len(recipeList)

allIDsDict = {}
tradeIDs = []
# for the recipe ids you want to chcek (limited list for now, just to make sure things work):
for recID in recipeList[:]:
    # trChk will be the dict added to the tradeChecks list
    recChk = {}
    # get the recipe object for the given id
    recObj = masterRecipeList[str(recID)] #gw2lib.findByID(recID, masterRecipeList)
    # add the item id to the dict and the ids list
    sourceID = recObj['output_item_id']
    recChk['sourceID'] = sourceID
    if masterItemList[str(sourceID)]['TPable']:
        tradeIDs.append(sourceID)
    else:
        allIDsDict[sourceID] = {'source':'something', 'cost':'someNumber'}
    # add a placeholder buy price
    recChk['costInfo'] = None
    # get the item name
    recChk['name'] = masterItemList[str(sourceID)]['name'] #gw2lib.findByID(trChk['sourceID'], masterItemList)['name']
    # deepcopy the ingredients list for this recipe
    recChk['ingredients'] = deepcopy(recObj['ingredients'])
    for ingr in recChk['ingredients']:
        # add the name and a placeholder buy price for each ingredient
        ingr['name'] = masterItemList[str(ingr['item_id'])]['name'] #gw2lib.findByID(ingr['item_id'], masterItemList)['name']
        ingr['costInfo'] = None
        # and add the id to the ids list
        ingrID = ingr['item_id']
        if masterItemList[str(ingrID)]['TPable']:
            tradeIDs.append(ingrID)
        else:
            allIDsDict[ingrID] = {'source':'something', 'cost':'someNumber'}
        # call chkRec to get the same info for each ingredient
        ingr['ingredients'] = chkRec(ingrID, ingr['count'])
    # append the dict to the tradeChecks list
    recipeChecks.append(recChk)

urlReqList = gw2lib.makeReqUrlList(tradeIDs, gw2lib.apiBase+gw2lib.commercePricesSubsect+gw2lib.idsReq)[0]

tradePrices = []
# get all the trade objects and put them in tradePrices
for req in urlReqList:
    tradePrices += json.load(urlopen(req))

# add an entry for each item on tp into allIDsDict, which is a dict containing price info
for tp in tradePrices:
    iid = tp['id']
    allIDsDict[iid] = { 'source':'trading post', 'buyPrice':tp['buys']['unit_price'], 'sellPrice':tp['sells']['unit_price'] }

# go through all the recipes
for recipe in recipeChecks:
    # add the costInfo dict by copying it from  allIDsDict
    recipe['costInfo'] = allIDsDict[recipe['sourceID']].copy()
    # get the best buy price and best sell price of all the ingredients from fillCosts(), which goes through the entire
    # recipe trail recursively
    [bbp, bsp] = fillCosts(recipe['ingredients'])
    # set the craft buy/sell prices to bbp and bsp
    recipe['costInfo']['craftBuyPrice'] = bbp #gw2lib.formatCoins(bbp)[2]
    recipe['costInfo']['craftSellPrice'] = bsp #gw2lib.formatCoins(bsp)[2]

'''
# output the info for some of the recipes to check if it's working
for x in recipeChecks[-10:]:
    pstring = 'source id: ' + str(x['sourceID']) + ', name: ' + x['name']
    if x['costInfo']['source'] == 'trading post':
        pstring +=  ', tp buy, sell prices: ' + str(x['costInfo']['buyPrice']) + ', ' + str(x['costInfo']['sellPrice'])
    else:
        pstring += ', price: ' + str(x['costInfo']['cost'])
    pstring += ', crafting buy, sell prices: ' + str(x['costInfo']['craftBuyPrice']) + ', ' +\
               str(x['costInfo']['craftSellPrice'])
    print pstring
    printRecTrail(x['ingredients'])
    print ''
'''
# trimmed recipes is used to get only recipes whose final item can be sold on trade, to look at profits that can be made
trimmedRecipes = []
# for each recipe:
for rec in recipeChecks:
    # if its source is the trading post
    if rec['costInfo']['source'] == 'trading post':
        # calculate the difference when using all the buy or sell prices of the ingredients and the trade price
        rec['buyDiff'] = rec['costInfo']['buyPrice']*0.85 - rec['costInfo']['craftBuyPrice']
        rec['sellDiff'] = rec['costInfo']['sellPrice']*0.85 - rec['costInfo']['craftSellPrice']
        # and append it to the trimmed list
        trimmedRecipes.append(rec)

# sort the list to show only the x best recipes
trimmedRecipes = sorted(trimmedRecipes, cmp=compByBuyDiff, reverse=True)

# and go through each recipe, recursively, and output its info
for rec in trimmedRecipes[:10]:
    print 'source id: ' + str(rec['sourceID']) + ', name: ' + rec['name'] + ', tp buy, sell: ' +\
          gw2lib.formatCoins(rec['costInfo']['buyPrice'])[2] + ', ' + gw2lib.formatCoins(rec['costInfo']['sellPrice'])[2] +\
          ', crafting buy, sell: ' + gw2lib.formatCoins(rec['costInfo']['craftBuyPrice'])[2] + ', ' +\
          gw2lib.formatCoins(rec['costInfo']['craftSellPrice'])[2] + ', diffs: ' + gw2lib.formatCoins(rec['buyDiff'])[2]\
          + ', ' + gw2lib.formatCoins(rec['sellDiff'])[2]
    printTrimRecTrail(rec['ingredients'])
    print ''

end = time.time()

print (end-start)/60, 'minutes'

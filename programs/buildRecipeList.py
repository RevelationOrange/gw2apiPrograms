from urllib2 import urlopen
import gw2lib
#import codecs
import json
import time


'''
buildRecipeList is used to create and maintain the file masterRecipeList.json, which contains the json objects for every
recipe id in the guild wars 2 recipe api endpoint
'''

timeStart = time.time()

# holder for the master list
masterRecipeList = []
# increment isn't likely to change; it's the most ids that can be requested from the recipe endpoint
incr = 200

# this url will return a list of all recipe ids
url = gw2lib.apiBase + gw2lib.recipesSubsect
recipeIDlist = json.load(urlopen(url))

# the last ID isn't really important, just nice to know. lastListIndex is needed to build the list of url requests
lastListIndex = len(recipeIDlist)
lastRecipeID = recipeIDlist[-1]
print 'final recipe ID:', lastRecipeID, ', final list index:', lastListIndex

# get the list of request urls and filename ranges, output from makeReqUrlList()
[requestURLs, filenamesStartEnd] = gw2lib.makeReqUrlList(recipeIDlist, url+gw2lib.idsReq, incr)

# i keeps track of the index associated with each set of incr ids stored in requestURLs
i = 0
for req in requestURLs:
    # for each request url, get the json data for those incr recipes
    recipeList = json.load(urlopen(req))
    # add them to the  master list
    masterRecipeList += recipeList
    # make the filename string from filenamesStartEnd[i]
    filenameString = gw2lib.recipeListFolder+'ids'+str(filenamesStartEnd[i][0])+'_'+str(filenamesStartEnd[i][1])+'.json'
    # save each set of incr ids to a file (not particularly necessary unless the recipe list gets really big)
    with open(filenameString, 'w') as recipeFile:
        json.dump(recipeList, recipeFile)
    print filenameString,'written\n'
    i += 1

# finally dump the full list to masterRecipeList.json
with open(gw2lib.recipeListFolder+gw2lib.masterRecipeFilename, 'w') as masterRecipeFile:
    json.dump(masterRecipeList, masterRecipeFile)
print len(masterRecipeList),'ids saved to master recipe list'

timeEnd = time.time()
runTime = timeEnd-timeStart
if runTime > 3600:
    print str(runTime/3600.) + " hours"
elif runTime > 60:
    print str(runTime/60.) + " minutes"
else:
    print str(runTime) + " seconds"

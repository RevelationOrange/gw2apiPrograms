from urllib2 import urlopen
import gw2lib
import codecs
import json
import time


'''
buildRecipeList is used to create and maintain the file masterRecipeList.json, which contains the json objects for every
recipe id in the guild wars 2 recipe api endpoint
'''

timeStart = time.time()

masterRecipeList = []
incr = 200

url = gw2lib.apiBase + gw2lib.recipesSubsect
recipeIDlist = json.load(urlopen(url))

lastListIndex = len(recipeIDlist)
lastRecipeID = recipeIDlist[-1]
print 'final recipe ID:', lastRecipeID, ', final list index:', lastListIndex

[requestURLs, filenamesStartEnd] = gw2lib.makeReqUrlList(recipeIDlist, url+gw2lib.idsReq)

i = 0
for req in requestURLs:
    recipeList = json.load(urlopen(req))
    masterRecipeList += recipeList
    filenameString = gw2lib.recipeListFolder+'ids'+str(filenamesStartEnd[i][0])+'_'+str(filenamesStartEnd[i][1])+'.json'
    with open(filenameString, 'w') as recipeFile:
        json.dump(recipeList, recipeFile)
    print filenameString,'written\n'
    i += 1
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

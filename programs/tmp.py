import gw2lib
import os


masterItemList = gw2lib.getMIL()

name = 'Assassin\'s Auric Axe'
idNum = 7000

nameObj = gw2lib.findByX(name, 'name', masterItemList)
idNumObj = gw2lib.findByID(idNum, masterItemList)['name']
print len(nameObj)

print 'id of \'' + name + '\' search:', nameObj[0]['id']
print 'name of ' + str(idNum)+ ' search:', idNumObj

print 'line separator:', os.linesep
print 'name:', os.name
print 'parent dir string:', os.pardir
print 'patch sep:', os.pathsep
print 'path sep:', os.sep

masterRecipeList = gw2lib.getMRL()

recipeObj = gw2lib.findByID(11790, masterRecipeList)
print recipeObj

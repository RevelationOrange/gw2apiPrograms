import gw2lib
import os


masterItemList = gw2lib.getMIL()

name = 'Dragonhunter\'s Gauntlet'
idNum = 7000

nameObj = gw2lib.findByX(name, 'name', masterItemList)[0]['id']
idNumObj = gw2lib.findByID(idNum, masterItemList)['name']

print 'id of \'' + name + '\' search:', nameObj
print 'name of ' + str(idNum)+ ' search:', idNumObj

print 'line separator:',os.linesep
print 'name:', os.name
print 'parent dir string:', os.pardir
print 'patch sep:', os.pathsep
print 'path sep:', os.sep
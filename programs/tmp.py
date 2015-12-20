import gw2lib

masterItemList = gw2lib.getMIL()

name = 'Dragonhunter\'s Gauntlet'
idNum = 6999

nameObj = gw2lib.findByX(name, 'name', masterItemList)[0]['id']
idNumObj = gw2lib.findByID(idNum, masterItemList)['name']

print 'id of \'' + name + '\' search:', nameObj
print 'name of ' + str(idNum)+ ' search:', idNumObj
import gw2lib

masterItemList = gw2lib.getMIL()

idNum = gw2lib.findByX('Dragonhunter\'s Gauntlet', 'name', masterItemList)[0]['id']

print idNum

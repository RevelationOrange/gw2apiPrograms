import gw2lib

masterItemList = gw2lib.getMIL()

idNum = gw2lib.findByX('Baelfire\'s Weapons Box', 'name', masterItemList)[0]['id']

print idNum

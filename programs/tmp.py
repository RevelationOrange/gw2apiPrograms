import gw2lib
import os


'''
thermocatalytic reagent- 'vendor_vlaue' is 80, but gw2eff says get 50 of them for 74s80c, from a vendor?
7480/50. = 149.6, soooo... ?
obsidian shard- 'ascended material', can apparently be bought from a vendor with karma, 2100 per, but there doesn't seem
to be a way to determine that strictly from the item object. hrm.
'''

masterItemList = gw2lib.getMILv2()

name = 'Obsidian Shard'
idNum = 19925

nameObj = gw2lib.findByX(name, 'name', masterItemList)
#idNumObj = gw2lib.findByID(idNum, masterItemList)['name']
idNumObj = masterItemList[str(idNum)]

if len(nameObj) > 1:
    print 'more than 1 item found for that name, only printing the first'
print 'id of \'' + name + '\' search:', nameObj[0]['id']
print 'name of ' + str(idNum)+ ' search:', idNumObj['name']

print idNumObj

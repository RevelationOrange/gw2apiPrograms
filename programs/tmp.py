import gw2lib
import os
import time
import sys


'''
thermocatalytic reagent- 'vendor_vlaue' is 80, but gw2eff says get 50 of them for 74s80c, from a vendor?
7480/50. = 149.6, soooo... ?
obsidian shard- 'ascended material', can apparently be bought from a vendor with karma, 2100 per, but there doesn't seem
to be a way to determine that strictly from the item object. hrm.
'''

MILv2 = gw2lib.getMILv2()

apiKey = sys.argv[1]
chars = gw2lib.getAllCharacterData(apiKey)

totalBoxes = 0
for char in chars:
    if char['name'] == 'Elle Orange':
        for bag in char['bags']:
            if bag is not None:
                for item in bag['inventory']:
                    if item is not None:
                        itemName = MILv2[str(item['id'])]['name']
                        if itemName != 'Crude Salvage Kit':
                            totalBoxes += item['count']

print totalBoxes

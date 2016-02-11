import gw2lib
import os
import time
import sys




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

import gw2lib
import csv
import sys


nSlots = 8

apiKey = sys.argv[1]

chars = gw2lib.getAllCharacterData(apiKey)

headerLine = [''] + [x+1 for x in range(nSlots)]
bagLines = []

for char in chars:
    line = [char['name']]
    for bag in char['bags']:
        if bag is not None:
            line.append(bag['size'])
        else:
            line.append(0)
    bagLines.append(line)

bagLinesMarks = []
bagsLeft = 0
for x in bagLines:
    line = [x[0]]
    for y in x[1:]:
        if y == 20:
            line += 'X'
        else:
            line += 'O'
            bagsLeft += 1
    bagLinesMarks.append(line)

with open(gw2lib.charactersFolderName+'bags.csv', 'wb') as bagsFile:
    bagsWriter = csv.writer(bagsFile)
    bagsWriter.writerow(headerLine)
    print headerLine
    for line in bagLines:
        bagsWriter.writerow(line)
        print line
    bagsWriter.writerow(['']*(nSlots+1) + ['20 slotters left'] + [bagsLeft])
    print ['']*(nSlots+1) + ['20 slotters left'] + [bagsLeft]
    for line in bagLinesMarks:
        bagsWriter.writerow(line)
        print line

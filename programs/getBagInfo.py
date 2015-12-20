import gw2lib
import csv
import sys


'''
getBagInfo shows the number of bags and their size on each character, as well as a checklist of bag slots that don't
have 20 slot bags in them, and a count of 20 slotters left to get
prints the info, but also saves to a csv, where it's much more readable
'''

# this is the maximum number of bag slots any character can have. currently 8, may change, probly not.
nSlots = 8

# api key to use is gotten from the command line
apiKey = sys.argv[1]

# all character data grabbed
chars = gw2lib.getAllCharacterData(apiKey)

# a header line for formatting: empty cell, then numbered bag slots, 1 to 8
headerLine = [''] + [x+1 for x in range(nSlots)]
bagLines = []

# go through each character, first cell is their name, then append each existing bag size to the list, and append that
# line to the list of lines to print
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

# using a similar list, name first, but now mark an X if the bag is a 20 slotter, O if it isn't, and increment bagsLeft
# for each O
for x in bagLines:
    line = [x[0]]
    for y in x[1:]:
        if y == 20:
            line += 'X'
        else:
            line += 'O'
            bagsLeft += 1
    bagLinesMarks.append(line)

# write to file
# example output:

#       1   2   3   4   5   6   7   8
# name0 20  20  20  20  18
# name1 20  20  0   20  20  20
#                                       20 slotters left    2
# name0 X   X   X   X   O
# name1 X   X   O   X   X   X

# this is for 2 characters, one with no extra bag slots and one non-20, the other with one extra bag slot but nothing
# in it, and not in order
with open(gw2lib.charactersFolderName+'bagsOnAllCharacters.csv', 'wb') as bagsFile:
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

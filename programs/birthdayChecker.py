import gw2lib
import sys
import time


if len(sys.argv) < 2:
    print "No api key provided. Please provide your api key as the first argument. If you need to create one, you can "\
          "do so at https://account.arena.net/applications"
    print "Be sure to include the 'character' and 'inventories' permissions for this program to work."
    sys.exit()
else: apiKey = sys.argv[1]

# get the character info from the api
chars = gw2lib.getAllCharacterData(apiKey)

# keep the birthday info in a dict with the character name as the key
bdayInfo = {}
# nxs (nexts) is just a way to easily sort the names by creation date, as sorting the dictionary was really annoying
# it's just [name, daysSinceCreation] for each character
nxs = []
# keep track of the longest name, for formatting purposes
longNameLen = 0

# go through each character
for char in chars:
    # record the name, length, and creation date
    name = char['name']
    longNameLen = max(longNameLen, len(name))
    cdate = char['created']

    # here, I did a lot of (possibly unnecessary) stuff to get the creation date into a usable format
    # honestly, I'm not 100% sure the time zones match and everything, but it seems to agree pretty well with the
    # listed /age in game
    tupleSecs = time.strptime(cdate, "%Y-%m-%dT%H:%M:%SZ")
    secs = time.mktime(tupleSecs)
    secsSinceCreation = time.time() - secs
    daysSinceCreation = secsSinceCreation/(60.*60*24)
    # daysSinceCreation is self explanatory; nextCheck is the remainder of days either before the next birthday or since
    # the previous one
    # store these both in the bdayInfo dict
    nextCheck = daysSinceCreation - round(daysSinceCreation/365.)*365
    nxs.append([daysSinceCreation, name])
    bdayInfo[name] = {'daysSince': daysSinceCreation, 'next': nextCheck}

# here are the nicely formatted strings to print
reprStr = '{:%d}  {} {} days{} (created {} days ago)' % longNameLen
first = 'first birthday in'
coming = 'next birthday in'
passed = 'had a birthday'

# sort the characters by creation date, earliest first (technically by days since creation, but it ends up the same)
snxs = sorted(nxs, reverse=1)

for char in [x[1] for x in snxs]:
    ds = bdayInfo[char]['daysSince']
    nx = bdayInfo[char]['next']
    # if the character hasn't had a birthday yet:
    if ds < 365:
        # a negative 'next' value means 'next' is the days until the next birthday
        if nx < 0: print reprStr.format(char, first, -round(nx, 2), '', round(ds, 3))
        # a positive 'next' means it's the days since creation, so just subtract it from 365 to get days until first
        else: print reprStr.format(char, first, 365-round(nx, 2), '', round(ds, 3))
    # else if they have:
    # a negative 'next' means it's the days until the next bday
    elif nx < 0: print reprStr.format(char, coming, -round(nx, 2), '', round(ds, 3))
    # a positive 'next' means it's the days since the last bday
    else: print reprStr.format(char, passed, round(nx, 2), ' ago', round(ds, 3))

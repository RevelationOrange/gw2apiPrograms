# gw2apiPrograms
various useful tools using the gw2 api

first time use- no real setup is needed since all the database files are included here, but if you want to delete that folder and run everything clean:
$ python buildItemList.py -n
$ python buildRecipeList.py
$ python buildRSref.py
$ python getRSprices.py all
then make sure maintenance uses makeMILv2(), makeMRLv2(), updateMasterList('item'), updateMasterList('recipe') from gw2lib, then:
$ python maintenance.py

gw2lib.updateMasterList('item') and gw2lib.updateMasterList('recipe') should be run periodically (recipes much less often I think) to ensure the master lists are up to date.
and be sure to use buildRSref before using getRSprices if it's been a while.

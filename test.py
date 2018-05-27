#!/usr/bin/python3

import copy

# A function to create an x by y map of visited areas given a view with origin a,b

# curr is a rotated view
# a and b are the x and y co-ordinates of the middle tile of the view

# TODO
# add view updates for tree cuts, door opens and placed rocks

# currview is the current whole map view
# currx and curry are the dimensions of our current mapview (last index notation)
currx = 4
curry = 4
# size of map (defined as currx + 1 and curry + 1 respectively)
sizex = 5
sizey = 5
# player x and player y are the player location in our current all view
playerx = 2
playery = 2
# player orientation
playerOri = '^'
allview = [[' ',' ','k',' ',' '],
            [' ',' ',' ',' ',' '],
            [' ',' ','^',' ',' '],
            [' ',' ',' ',' ',' '],
            ['*','*','*','*','*']]

newview = [[' ',' ',' ',' ',' '],
            [' ',' ','k',' ',' '],
            [' ',' ','^',' ',' '],
            [' ',' ',' ',' ',' '],
            [' ',' ',' ',' ',' ']]

newview2 = [['*','*','*','*','*'],
            [' ',' ',' ',' ',' '],
            [' ',' ','^',' ',' '],
            [' ',' ',' ',' ',' '],
            [' ',' ',' ',' ',' ']]

newview3 = [['~','~','~','~','~'],
            ['*','*','*','*','*'],
            [' ',' ','^',' ',' '],
            [' ',' ',' ',' ',' '],
            [' ',' ',' ',' ',' ']]

newview4 = [['~','~','~','~','~'],
            ['*','*','*','*','*'],
            [' ',' ','>',' ','*'],
            [' ',' ',' ',' ','*'],
            [' ',' ',' ',' ','*']]

newview5 = [[' ',' ',' ',' ',' '],
            [' ',' ',' ',' ',' '],
            [' ',' ','v',' ',' '],
            ['*','*','*','*','*'],
            ['~','a','T','~','a']]

newview6 = [['-',' ','',' ',' '],
            ['~',' ',' ',' ',' '],
            ['~',' ','<',' ',' '],
            ['~','*','*','*','*'],
            ['~','~','a','T','~']]

newview7 = [['k','-','',' ',' '],
            ['T','~',' ',' ',' '],
            ['a','~','<',' ',' '],
            ['o','~','*','*','*'],
            ['-','~','~','a','T']]

# function that gets given the view and the new x and y location of the player 
# with respect to the old map that is to be replaced
def addView(view,x,y):
    global playerx
    global playery
    global currx
    global curry
    global allview
    global sizex
    global sizey

    findPlayer(allview)
    # horizontal move
    if x != playerx:

        # move right
        if x > playerx:
            print('right')
            # check if allview needs to be expanded
            if x + 2 > currx:
                # initiate new squares created with '?'
                allview = [m + ['?'] for m in allview]
                currx = currx + 1
                sizex = sizex + 1
            # check allview and replace squares since replacing older squares dont matter for correctness
            for i in range(5):
                # replace squares
                allview[playery - 2 + i][playerx + 3] = view[i][4]
            # change player location
            if view[2][1] == 'o':
                allview[playery][playerx] = 'o'
            else:                 
            # change so that rocks can be found
                allview[playery][playerx] = ' '
            allview[y][x] = '>'
            # updates to playerx and playery
            playerx = playerx + 1
            printDebug(x,y)
                
        # move left
        else:
            print('left')
            # check if allview needs to be expanded
            if x - 2 < 0:
                # initiate new squares created with '?'
                allview = addStartColumn(allview,sizex,sizey)
                playerx = playerx + 1
                currx = currx + 1
                sizex = sizex + 1
            # check allview and replace squares since replacing older squares dont matter for correctness
            for i in range(5):
                # replace squares
                allview[playery-2+i][playerx - 3] = view[i][0]
            # change player location
            if view[2][3] == 'o':
                allview[playery][playerx] = 'o'                 
            # checks if previous step is stone
            else:
            # moved playerx to account for new column
                allview[playery][playerx] = ' '
            allview[y][x+1] = '<'
            playerx = playerx - 1
            printDebug(x,y)

    # vertical move
    elif y != playery:
        # move down
        if y > playery:
            print('down')
            # check if allview needs to be expanded
            if y + 2 > curry:
                # initiate new squares created with '?'
                allview = allview + [['?' for i in range(sizex)]]
                curry = curry + 1
                sizey = sizey + 1
            # check allview and replace squares since replacing older squares dont matter for correctness
            for i in range(5):
                # replace squares
                allview[playery + 3][playerx - 2 + i] = view[4][i]
            # change player location 
            if view[1][2] == 'o':
                allview[playery][playerx] = 'o'                 
            # change so that rocks can be found
            else:
                allview[playery][playerx] = ' '
            allview[y][x] = 'v'
            # updates to playerx and playery
            playery = playery + 1
            printDebug(x,y)
        # move up
        else:
            print('up')
            # check if allview needs to be expanded
            if y - 2 < 0:
                # initiate new squares created with '?'
                allview = addStartRow(allview,sizex,sizey)
                # adjust playery to account for extra row 
                playery = playery + 1
                curry = curry + 1
                sizey = sizey + 1
            # check allview and replace squares since replacing older squares dont matter for correctness
            for i in range(5):
                # replace squares
                allview[playery - 3][playerx - 2 + i] = view[0][i]
            # change player location
            if view[3][2] == 'o':
                allview[playery][playerx] = 'o'                 
            # check if previous step was on a stone
            else:
            # moved playerx to account for new column
                allview[playery][playerx] = ' '
            playery = playery - 1
            allview[playery][playerx] = '^'
            printDebug(x,y)
        
    # no view to add
    else:
    #check what orientation you are in
    #look at the respective cell in view to see the cell that may have had an action taken
    #crossreference with the allview to see what changes have been made
    #update the changes
        if playerOri == '^':
            if view[1][2] == ' ' and allview[playery-1][playerx] == '-':
                allview[playery-1][playerx] == ' '
            elif view[1][2] == ' ' and allview[playery-1][playerx] == 'T':
                allview[playery-1][playerx] == ' ' 
        elif playerOri == 'v':
            if view[3][2] == ' ' and allview[playery+1][playerx] == '-':
                allview[playery+1][playerx] == ' '
            elif view[3][2] == ' ' and allview[playery+1][playerx] == 'T':
                allview[playery+1][playerx] == ' '
        elif playerOri == '<':
            if view[2][1] == ' ' and allview[playery][playerx-1] == '-':
                allview[playery][playerx-1] == ' '
            elif view[2][1] == ' ' and allview[playery][playerx-1] == 'T':
                allview[playery][playerx-1] == ' '
        elif playerOri == '^':
            if view[2][3] == ' ' and allview[playery][player+1] == '-':
                allview[playery][playerx+1] == ' '
            elif view[2][3] == ' ' and allview[playery][playerx+1] == 'T':
                allview[playery][playerx+1] == ' '
        else:
            pass

# a helper function to find the location of the player
def findPlayer(map):
    global playerx
    global playery
    global currx
    global curry
    global playerOri
    player = {'<':'left','v':'down','>':'right','^':'up'}

    for i in range(sizex):
        for j in range(sizey):
            if map[j][i] in player:
                playerx = i
                playery = j
                playerOri = map[j][i]
                return

# given a matrix and its current size, adds a '?' initiated column on x = 0
def addStartColumn(view,x,y):
    newview = copy.deepcopy(view)
    newview = [x + ['err'] for x in newview]
    for i in range(x):
        for j in range(y):
            newview[j][i+1] = view[j][i]
    for m in range(y):
        newview[m][0] = '?'
    return newview

# given a matrix and its current size, adds a '?' initiated row at the start
def addStartRow(view,x,y):
    newview = copy.deepcopy(view)
    newview = newview + [['?' for i in range(x)]]
    for i in range(x):
        for j in range(y):
            newview[j+1][i] = view[j][i]
    for m in range(x):
        newview[0][m] = '?'
    return newview

# a function to print any map (function strictly for testing)
def printMap(view):
    for i in view:
        for j in i:
            print('[' + j + ']',end='')
        print()

# print all variables DEBUG
def printDebug(x,y):
    print('Current x is ' + str(x))
    print('Current y is ' + str(y))
    print('Current playerx is ' + str(playerx))
    print('Current playery is ' + str(playery))
    print('Current currx is ' + str(currx))
    print('Current curry is ' + str(curry))



# BRIEF TEST CASES ==> where inputs to addview are the newview we want to add and the change in playerx or playery
def upRightTest():
    printMap(allview)
    addView(newview,playerx,playery-1)
    printMap(allview)
    addView(newview2,playerx,playery-1)
    printMap(allview)
    addView(newview3,playerx,playery-1)
    printMap(allview)
    addView(newview4,playerx+1,playery)
    printMap(allview)

def downLeftTest():
    printMap(allview)
    addView(newview5,playerx,playery+1)
    printMap(allview)
    addView(newview6,playerx-1,playery)
    printMap(allview)
    addView(newview7,playerx-1,playery)
    printMap(allview)

downLeftTest()

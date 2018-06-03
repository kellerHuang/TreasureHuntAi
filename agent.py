#!/usr/bin/python3
# ^^ note the python directive on the first line
# COMP 9414 agent initiation file 
# requires the host is running before the agent
# designed for python 3.6
# typical initiation would be (file in working directory, port = 31415)
#        python3 agent.py -p 31415
# created by Leo Hoare
# with slight modifications by Alan Blair

#Briefly describe how your program works, including any algorithms and data structures employed, and explain any design decisions you made along the way.

# When get action is called:
#Update map
#If we are currently following a path, continue to that destination.
#If you can see any items, can you reach them by walking?
#Are there any spots on land you haven't visited?
#Do you have a key, and are there any locked doors?
#Do i not have a raft, and are there any trees? Which tree gives highest entropy?
#Is there any water? Which entrance tile of water gives the highest entropy?
#Are we in a raft? Explore all water possible.
#Is there any trees i should cut despite already having a raft?
#Do we have enough resources to get treasure and return to origin?


#Our group utilized generic BFS and A* search with a birds eye distance heuristic
#We also utilized a variety of 2D matrices, dictionaries, tuples and lists
#Our ai aims to recreate human players by exploring all possible unknown cells to maximise their knowledge without recklessly spending resources.
#Only when it is forced to will it begin to take decisions that have a risk of causing a losing outcome, but only that of which has the lowest probability which we measure through our entropy calculation.
#Our Ai understands that water and land based traversal is unique and only explores in water once it is forced to do so and does so that it maximizes the possible future land connections
#Then when our ai has seen the treasure, it makes sure that it has the required resources to return to the origin
import sys
import socket
import random
import time
import copy
import re
import math

# declaring visible grid to agent
view = [['' for _ in range(5)] for _ in range(5)]
allview = [[]]
#2d matrix representing where we have been
exploreview = [[]]
stone = 0
usedStone = 0
axe = 0
raft = 0
key = 0
orientation = 0
inRaft = 0
# curr is a rotated view
# a and b are the x and y co-ordinates of the middle tile of the view

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

currentDest = ()
currentPath = []

moves = []
def rotateMatrix(mat):   
    # Consider all squares one by one
    for x in range(0, int(5/2)):
    # Consider elements in group   
    # of 4 in current square
        for y in range(x, 5-x-1):
            # store current cell in temp variable
            temp = mat[x][y]
            # move values from right to top
            mat[x][y] = mat[y][5-1-x]
            # move values from bottom to right
            mat[y][5-1-x] = mat[5-1-x][5-1-y]
            # move values from left to bottom
            mat[5-1-x][5-1-y] = mat[5-1-y][x]
            # assign temp to left
            mat[5-1-y][x] = temp

def bfs_closest(start,water = 0):
    Queue = [[start[0], start[1]]] #cells to be expanded
    seen = [] #cells already expanded
    obstacles = {'*':'Wall','T':'Tree','-':'Door','~':'Water','.':'OOB'}
    goal = ' '
    if key != 0:
        obstacles.pop('-', None)
    if water == 1:
        obstacles.pop('~', None)
        obstacles[' '] = 'Land'
        goal = '~'
        #print("WATER")
    while Queue != []:
        coord = Queue.pop(0) #take the first node in the queue
        if exploreview[coord[0]][coord[1]] == ' ' and allview[coord[0]][coord[1]] == goal:
           # print("BFS RETURN",end='')
           # print(coord)
            return coord #if it is empty, we have found out closest empty node
        elif allview[coord[0]][coord[1]] in obstacles:
            seen.append([coord[0], coord[1]]) #if it is not visitable unless using resources, ignore
        else: #for each neighbour, add to queue, with those facing front added first as they are closer               
            if [coord[0] - 1, coord[1]] not in seen:
                seen.append([coord[0]-1, coord[1]])
                Queue.append([coord[0]-1, coord[1]])
            if [coord[0], coord[1]-1] not in seen:
                seen.append([coord[0], coord[1]-1])
                Queue.append([coord[0], coord[1]-1])
            if [coord[0], coord[1]+1] not in seen:
                seen.append([coord[0], coord[1]+1])
                Queue.append([coord[0], coord[1]+1])
            if [coord[0] + 1, coord[1]] not in seen:
                seen.append([coord[0]+1, coord[1]])
                Queue.append([coord[0]+1, coord[1]]) 
    return ['false']  #if none found, return false

def Astar(player, coord, tree = 0, door = 0, water = 0): #generic astar function, same as psuedo code on wikipedia
    closed = [] #set of nodes already seen
    neighbours = [(player[0]-1, player[1]), (player[0]+1, player[1]), (player[0], player[1]+1), (player[0], player[1]-1)] #all possible adjacent cells
    open = [(player[0], player[1])] #set of nodes yet to be expanded
    cameFrom = {} #dict of where each node came from 
    gscore = {} #cost of getting from start to that node
    gscore[(player[0], player[1])] = 0
    fscore = {} #cost of getting from    start node to that node. Requires heuristic
    fscore[(player[0], player[1])] = math.sqrt(abs(player[0] - coord[0])**2 + abs(player[1] - coord[1])**2) #birds eye distance as heuristic
    obstacles = {'*':'wall','T':'tree','-':'door','~':'water'}
    if tree == 1:
        obstacles.pop('T')
    if door == 1:
        obstacles.pop('-')
    if water == 1:
        obstacles.pop('~')
        obstacles[' '] = 'land'
        obstacles['O'] = 'stone'
        obstacles['$'] = 'treasure'
    while open != []:
        current = open[0]
        for i in open:
            if i in fscore:
                if fscore[i] < fscore[current]:
                    current = i
        if current == coord: #if goal we are at where we need to be
            return reconstruct_path(cameFrom, current)
        # print("===========")
        # print(current)
        open.remove(current) 
        closed.append(current)
        if allview[current[0]][current[1]] in obstacles:
            continue #if requires resources or unvisitable, skip
        neighbours = []
        if current[0] > 0:
            neighbours.append((current[0]-1,current[1]))
           # print(current[0]-1,end=" ")
           # print(current[1])
        if current[0] < curry:
            neighbours.append((current[0]+1,current[1]))
          #  print(current[0]+1,end=" ")
          #  print(current[1])
        if current[1] > 0:
            neighbours.append((current[0],current[1]-1))
          #  print(current[0],end=" ")
          #  print(current[1]-1)
        if current[1] < currx:
            neighbours.append((current[0],current[1]+1))
           # print(current[0],end=" ")
           # print(current[1]+1)
        for i in neighbours: #for all the adjacent cells
            if i in closed: #if seen already,skip
                continue
            if i not in open: #if node not yet expanded, add to queue
                open.append(i)
            if current not in gscore.keys():
                gscore[current] = 10000
            if i not in gscore.keys():
                gscore[i] = 10000  
            tent = gscore[current] + abs(current[0] - coord[0]) + abs(current[1] - coord[1])
            if tent >= gscore[i]: #check if this distance is shorter than the previous
                continue #if not, ignore
            cameFrom[i] = current #otherwise, update where this node came from
            gscore[i] = tent
            fscore[i] = gscore[i] + math.sqrt(abs(current[0] - coord[0])**2 + abs(current[1] - coord[1])**2)

    return False #if not found, return false

def reconstruct_path(cameFrom, current): #backtrace function
    total_path = [current] 
    while current in cameFrom:
        current = cameFrom[current]
        total_path.append(current)
    return total_path

# function to take get action from AI or user
def get_action(view):
    global orientation
    global currentPath
    global currentDest
    orientation = 0
    global moves
    for i in moves:
        if i == 'l':
            orientation = (orientation - 1) % 4
        if i == 'r':
            orientation = (orientation + 1) % 4
    rotate = copy.deepcopy(view)
    turns = 4 - orientation
    while turns > 0:
        rotateMatrix(rotate)
        turns = turns - 1
    if orientation == 0:
        rotate[2][2] = '^'
    elif orientation == 1:
        rotate[2][2] = '>'
    elif orientation == 2:
        rotate[2][2] = 'v'
    else:
        rotate[2][2] = '<'
    #print_grid(rotate)
    #print('------')
    global playerx
    global playery
    global key
    global axe
    global stone
    global raft
    global allview
    obstacle = {'T':'Tree','*':'Wall','-':'Door'}
    if allview != [[]]:
        # check tile in front of us
        if orientation == 0:
            front = allview[playery-1][playerx]
        elif orientation == 1:
            front = allview[playery][playerx+1]
        elif orientation == 2:
            front = allview[playery+1][playerx]
        else:
            front = allview[playery][playerx-1]
    if moves != [] and moves[-1] == 'f' and front not in obstacle:
        if orientation == 0:
            addView(rotate,playerx,playery-1)
        elif orientation == 1:
            addView(rotate,playerx+1,playery)
        elif orientation == 2:
            addView(rotate,playerx,playery+1)
        else:
            addView(rotate,playerx-1,playery)
    else:
        addView(rotate,playerx,playery)
    exploreview[playery][playerx] = 'v' #set position to visited


    item = {'a':'axe','o':'rock','k':'key'}
    if currentDest != () and currentPath != []:
        #print("my current destination is")
        #print(currentDest)
        curMove = currentPath.pop(0)
        if curMove == 'f' and view[1][2] == '-':
            curMove = 'u'
        if curMove == 'f' and view[1][2] == 'T':
            raft = 1
            curMove = 'c'
        if curMove == 'f' and view[1][2] in item:
            z = view[1][2]
            if z == 'a':
                axe = 1
            elif z == 'k':
                key = 1
            else:
                stone = stone + 1
        if curMove == 'f' and view[1][2] == '~' and stone > 0:
            stone = stone-1
        moves.append(curMove)
        return curMove
    if currentPath == []:
        currentDest = ()

    ### Water Movement
    if inRaft == 1:
        print("IM IN A RAFT")
        goal = bfs_closest((playery,playerx),1)
        print(goal)
        if goal != ['false'] and Astar((playery,playerx),(goal[0],goal[1]),0,0,1):
            #print("WATER GOAL")
            #print(goal)
            goalTuple = (goal[0],goal[1])
            path = Astar((playery,playerx),goalTuple,0,0,1)
            #print(path)
            path1 = list(revPath(path))
            currentDest = goal
            currentPath = path1[1:]
            move = path1[0]
            moves.append(move)
            return move
        else:
            print("SWIM")
            printMap(swimmable())
            #for i in swimmable():
                

    resources = {'o':'Rock','k':'Key','a':'Axe'} 
    if key > 0:
        resources['-'] = 'Door'
    if axe > 0:
        resources['T'] = 'Tree'
    low = 6
    for i in range(5):
        for j in range(5):
            if view[i][j] in resources:
                if abs(i - 1) + abs (j - 2) < low:
                    y = i
                    x = j  
                    low = abs(i-1) + abs(j-2)

    coord = (playery,playerx) #the coordinates of the nearest unvisited cell
    result = bfs_closest(coord) #stores the nearest unvisited cell coordinates, returns false if no such cell
    # print("res")
    # print(result)
    try:
        if low < 6: #if there is an immediately reachable resource
            currentDest = (y,x)
            path = walkable(view,x,y)
            path1 = list(path)
        elif result[0] != 'false': #if there is an unvisited cell
            res_coord = (result[0], result[1])
            path = Astar([playery, playerx], res_coord) #astar returns the path from current player position to coord   
            currentDest = res_coord        
#            print(path)
            path1 = list(revPath(path))
#            print(path1)
        if path1[0] != 'F':
            #time.sleep(0.25)
            move = path1[0]
            if view[1][2] == 'T' and axe == 1 and move == 'f':
                raft =  1
                moves.append('c')
                return 'c'
            if view[1][2] == 'a' and axe == 0 and move == 'f':
                axe = 1
            if view[1][2] == 'k' and key == 0 and move == 'f':
                key = 1
            if view[1][2] == '-' and key == 1 and move == 'f':
                moves.append('u')
                return 'u'
            if view[1][2] == 'o' and move == 'f':
                stone = stone + 1
            moves.append(path1[0])
            currentPath = path1[1:]
           # print("added path")
           # print(path1)
            return path1[0]
        else:
            # no more paths left
            currentDest = ()
            # see if there's any trees to cut
            #result = bfs_closest((playery,playerx),1)
            # check if we found a tree to cut   
            #if result != ['false']:
            #    if 

            #optimal version
            #print("TREE")
            trees = {}
            entropy = analyse()
            for i in range(sizey):
                for j in range(sizex):
                    if allview[i][j] == 'T':
                        if Astar((playery,playerx),(i,j),1) != False:
                            trees[(i,j)] = entropy[i][j]
            
            # sort by entropy
            high = 0
            node = ()
            for i in trees:
                if trees[i] > high:
                    node = i
                    high = trees[i]
            # tree is found
            #print("NODE")
            #print(node)
            if node != ():
                path = Astar((playery,playerx),node,1)
                #print("XD")
                #print(path)
                #print(playery)
                #print(playerx)
                path1 = list(revPath(path))
                if len(path1) == 1:
                    move = 'c'
                    raft = 1
                    moves.append('c')
                    return move
                move = path1[0]
                currentDest = node
                currentPath = path1[1:]
                moves.append(move)
                return move
            else:
            # tree not found
                pass
            print("WALKABLE")
            print(walkableView())
            tiles = walkableView()
            res = []
            for i in tiles:
                if stoneBFS([i]) != False:
                    res = [i]
                    break
            p = []
            for i in res:
                test = copy.deepcopy(allview)
                allview[i[0]][i[1]] = ' '
                if Astar((playery,playerx),i) != False:
                    p = Astar((playery,playerx),i)
                    allview = test
                    break
                allview = test
            
            if p != []:
                sPath = list(revPath(p))
                print("PATH FOUND")
                print(sPath)
                currentDest = res[0]
                currentPath = sPath[1:]
                move = sPath[0]
                moves.append(move)
                return move


                

            
        raise NameError
    except NameError:
        while 1:
            print('random')
            inp = random.randrange(6)
            if inp < 4:
                move = 'f'
            if inp == 4:
                move = 'l'
            if inp == 5:
                move = 'r'
            if view[1][2] == 'T' and axe == 1:
                move = 'c'
                raft = raft + 1
            if view[1][2] == 'a' and axe == 0:
                axe = 1
                move = 'f'
            if view[1][2] == 'k' and key == 0:
                key = 1
                move = 'f'
            if view[1][2] == '-' and key == 1:
                move = 'u'
            if view[1][2] == 'o':
                move = 'f'
                stone = stone + 1
            if view[1][2] == '*' or view[1][2]== '.' or (view[1][2] == '~' and (stone == 0 and raft == 0)):
                #print('O a wall')
                x = random.randrange(2)
                if view[2][1] == '*':
                    move = 'r'
                elif view[2][3] == '*':
                    move = 'l'
                else:
                    if x == 0:
                        move = 'l'
                    else:
                        move = 'r'

            if view[1][2] == '~' and (stone > 0 or raft > 0) and move == 'f':
                if stone > 0:
                    stone = stone - 1
                else:
                    raft = 0
            #time.sleep(0.25)
            moves.append(move)
            return move

# checks resources on an island
def checkResources(location):
    change = 0
    test = copy.deepcopy(allview)
    free = {'o': 'stone', 'T':'Tree','a':'axe',' ':'land','k':'key'}
    stones = 0
    trees = 0
    axes = 0
    keys = 0
    allview[location[0]][location[1]] = 'C'
    while change == 1:
        change = 0
        for i in range(sizex):
            for j in range(sizey):
                if allview[j][i] == 'C':
                    if allview[j-1][i] in free:
                        if allview[j-1][i] == 'o':
                            stones = stones + 1
                        if allview[j-1][i] == 'T':
                            trees = trees + 1
                        if allview[j-1][i] == 'a':
                            axes = axes + 1
                        if allview[j-1][i] == 'k':
                            keys = keys + 1
                        allview[j-1][i] = 'C'
                        change = 1
                    if allview[j+1][i] in free:
                        if allview[j+1][i] == 'o':
                            stones = stones + 1
                        if allview[j+1][i] == 'T':
                            trees = trees + 1
                        if allview[j+1][i] == 'a':
                            axes = axes + 1
                        if allview[j+1][i] == 'k':
                            keys = keys + 1
                        allview[j+1][i] = 'C'
                        change = 1
                    if allview[j][i-1] in free:
                        if allview[j][i-1] == 'o':
                            stones = stones + 1
                        if allview[j][i-1] == 'T':
                            trees = trees + 1
                        if allview[j][i-1] == 'a':
                            axes = axes + 1
                        if allview[j][i-1] == 'k':
                            keys = keys + 1
                        allview[j][i-1] = 'C'
                        change = 1
                    if allview[j][i+1] in free:
                        if allview[j][i+1] == 'o':
                            stones = stones + 1
                        if allview[j][i+1] == 'T':
                            trees = trees + 1
                        if allview[j][i+1] == 'a':
                            axes = axes + 1
                        if allview[j][i+1] == 'k':
                            keys = keys + 1
                        allview[j][i+1] = 'C'
                        change = 1

def stoneBFS(rock):
    global allview
    test = copy.deepcopy(allview)
    for i in rock:
        print(i)
        allview[i[0]][i[1]] = ' '
        if bfs_closest((playery,playerx)) != False:
            allview = test
            return True
        else:
            allview = test
            return False

def revPath(path):
    fpath = path[::-1]

    # print("FPATH")
    # print(fpath)
    # print(orientation)
    curr = ()
    newP = ""
    for i in fpath:
        if curr == ():
            curr = i
            continue
        else:
            if curr[0] != i[0]:
                if curr[0] + 1 == i[0]:
                    newP = newP + "D"
                else:
                    newP = newP + "U"
            if curr[1] != i[1]:
                if curr[1] + 1 == i[1]:
                    newP = newP + "R"
                else:
                    newP = newP + "L"
        curr = i
    #print(newP)
    return turnToPath(newP,orientation)

def walkable(view,x,y):
    # find location of player
    test = copy.deepcopy(view)
    change = 1
    free = {'o':'Stone','k':'Key','a':'Axe',' ':'Space', 'O':'placed_Stone'}
    if key == 1:
        free['-'] = 'Door'
    if axe == 1:
        free['T'] = 'Tree'
    test[2][2] = '^'
    #print(orientation)
    while change == 1:
        change = 0
        for i in range(5):
            for j in range(5):
                check = re.sub('[RLUD]','',test[i][j])
                if check == '^':
                    if i < 4:
                        if test[i+1][j] in free:
                            test[i+1][j] = test[i][j] + 'D'
                            change = 1
                    if i > 0:
                        if test[i-1][j] in free:
                            test[i-1][j] = test[i][j] + 'U'
                            change = 1
                    if j < 4:
                        if test[i][j+1] in free:
                            test[i][j+1] = test[i][j] + 'R'
                            change = 1
                    if j > 0:
                        if test[i][j-1] in free:
                            test[i][j-1] = test[i][j] + 'L'
                            change = 1

    check = re.sub('[RLUD]','',test[y][x])
    if check == '^':
        return turnToPath(rotPath(test[y][x]))
    else:
        return 'False'

# rotates a path given an orientation
def rotPath(path):
    if orientation == 0:
        pass
    elif orientation == 1:
        path = path.replace('D','4')
        path = path.replace('U','6')
        path = path.replace('L','8')
        path = path.replace('R','2')
    elif orientation == 2:
        path = path.replace('D','8')
        path = path.replace('U','2')
        path = path.replace('L','6')
        path = path.replace('R','4')
    else:
        path = path.replace('D','6')
        path = path.replace('U','4')
        path = path.replace('L','2')
        path = path.replace('R','8')
    path = path.replace('2','D')
    path = path.replace('4','L')
    path = path.replace('6','R')
    path = path.replace('8','U')
    return path


# Similar to walkable but specifically for allview/exploreview
def walkableView():
    # find location of player
    test = copy.deepcopy(allview)
    change = 1
    free = {'o':'Stone','k':'Key','a':'Axe',' ':'Space', 'O':'placed_Stone'}
    test[playery][playerx] = 'W'
    water = []
    while change == 1:
        change = 0
        for i in range(sizey):
            for j in range(sizex):
                if test[i][j] == 'W':
                    if i < curry:
                        if test[i+1][j] in free:
                            test[i+1][j] ='W'
                            change = 1
                    if i > 0:
                        if test[i-1][j] in free:
                            test[i-1][j] = 'W'
                            change = 1
                    if j < currx:
                        if test[i][j+1] in free:
                            test[i][j+1] = 'W'
                            change = 1
                    if j > 0:
                        if test[i][j-1] in free:
                            test[i][j-1] = 'W'
                            change = 1
    # run once again but for '?'
    free = {'~':'water'}
    for i in range(sizey):
        for j in range(sizex):
            if test[i][j]== 'W':
                if i < curry:
                    if test[i+1][j] in free:
                        water.append((i+1,j))
                if i > 0:
                    if test[i-1][j] in free:
                        water.append((i-1,j))
                if j < currx:
                    if test[i][j+1] in free:
                        water.append((i,j+1))
                if j > 0:
                    if test[i][j-1] in free:
                        water.append((i,j-1))
    return water

def swimmable():
    test = copy.deepcopy(allview)
    free = {'~':'water'}
    test[playery][playerx] = 'S'
    change = 1
    while change == 1:
        change = 0
        for i in range(sizey):
            for j in range(sizex):
                if test[i][j] == 'S':
                        if i < curry:
                            if test[i+1][j] in free:
                                test[i+1][j] ='S'
                                change = 1
                        if i > 0:
                            if test[i-1][j] in free:
                                test[i-1][j] = 'S'
                                change = 1
                        if j < currx:
                            if test[i][j+1] in free:
                                test[i][j+1] = 'S'
                                change = 1
                        if j > 0:
                            if test[i][j-1] in free:
                                test[i][j-1] = 'S'
                                change = 1

    # once again to get land
    free = {' ':'land','$':'treasure','a':'axe','k':'key','o':'stone'}
    res = []
    for i in range(sizey):
        for j in range(sizex):
            if test[i][j] == 'S':
                    if i < curry:
                        if test[i+1][j] in free and (i+1,j) not in res:
                            res.append((i+1,j))
                    if i > 0:
                        if test[i-1][j] in free and (i-1,j) not in res:
                            res.append((i-1,j))
                    if j < currx:
                        if test[i][j+1] in free and (i,j+1) not in res:
                            res.append((i,j+1))
                    if j > 0:
                        if test[i][j-1] in free and (i,j-1) not in res:
                            res.append((i,j-1))
    
    return res

def rotate(dir, cur):
    if dir == cur:
        return ''
    if cur + 1 == dir:
        return 'r'
    if cur - 1 == dir:
        return 'l'
    if cur + 2 == dir or cur - 2 == dir:
        return 'rr'
    if cur - 3 == dir:
        return 'r'
    if cur + 3 == dir:
        return 'l'

def turnToPath(directions,facing = 0):
    arr = list(directions.replace("^",""))
    res = ''
    for i in arr:
        if i == 'U':
            res = res + rotate(0,facing) + 'f'
            facing = 0
        if i == 'R':
            res = res + rotate(1,facing) + 'f'
            facing = 1
        if i == 'D':
            res = res + rotate(2,facing) + 'f'
            facing = 2
        if i == 'L':
            res = res + rotate(3,facing) + 'f'
            facing = 3
    return res 
# rotates from current direction to desired direction
    

# helper function to print the grid
def print_grid(view):
    print("==========MOVE ",end="")
    print(len(moves),end="")
    print("==========")
    print('+-----+')
    for ln in view:
        print("|"+str(ln[0])+str(ln[1])+str(ln[2])+str(ln[3])+str(ln[4])+"|")
    print('+-----+')
    

# function that gets given the view and the new x and y location of the player 
# with respect to the old map that is to be replaced
def addView(view,x,y):
    global playerx
    global playery
    global currx
    global curry
    global allview
    global exploreview
    global sizex
    global sizey
    obstacle = {'T':'Tree','*':'Wall','.':'OOB'}
    if allview == [[]]:
        allview = copy.deepcopy(view)
        exploreview = copy.deepcopy(view) #copy the initial 5x5 view 
        for i in range(5):
            for j in range(5):
                if exploreview[i][j] in obstacle: #if the cell is a wall
                    exploreview[i][j] = 'v' #mark it as visited
                else:
                    exploreview[i][j] == ' ' #all other cells are unvisited
        return
    findPlayer(allview)
    # horizontal move
    if x != playerx:

        # move right
        if x > playerx:
            # print('right')
            # check if allview needs to be expanded
            if x + 2 > currx:
                # initiate new squares created with '?'
                allview = [m + ['?'] for m in allview]
                exploreview = [n + [' '] for n in exploreview] #extend the matrix with spaces
                currx = currx + 1
                sizex = sizex + 1
            # check allview and replace squares since replacing older squares dont matter for correctness
            for i in range(5):
                # replace squares
                allview[playery - 2 + i][playerx + 3] = view[i][4]
                if view[i][4] in obstacle or exploreview[playery - 2 + i][playerx + 3] == 'v': #if the new cell being added is a wall
                    exploreview[playery - 2 + i][playerx + 3] = 'v' #mark it as visited
                else:
                    exploreview[playery - 2 + i][playerx + 3] = ' ' #otherwise mark it as unvisited               
            # change player location
            if view[2][1] == 'O':
                allview[playery][playerx] = 'O'
            if view[2][1] == '~':
                allview[playery][playerx] = '~'
            else:                 
            # change so that rocks can be found
                allview[playery][playerx] = ' '
            # updates to playerx and playery
            playerx = playerx + 1
            allview[playery][playerx] = '>'
                
        # move left
        else:
            # print('left')
            # check if allview needs to be expanded
            if x - 2 < 0:
                # initiate new squares created with '?'
                allview = addStartColumn(allview,sizex,sizey,'?')
                exploreview = addStartColumn(exploreview,sizex,sizey,' ')
                playerx = playerx + 1
                currx = currx + 1
                sizex = sizex + 1
            # check allview and replace squares since replacing older squares dont matter for correctness
            for i in range(5):
                # replace squares
                allview[playery - 2 + i][playerx - 3] = view[i][0]
                if view[i][0] in obstacle or exploreview[playery - 2 + i][playerx - 3] == 'v': #same as above
                    exploreview[playery - 2 + i][playerx - 3] = 'v'
                else:
                    exploreview[playery - 2 + i][playerx - 3] = ' '                                  
            # change player location
            if view[2][3] == 'O':
                allview[playery][playerx] = 'O'                 
            # checks if previous step is stone
            if view[2][3] == '~':
                allview[playery][playerx] = '~' 
            else:
            # moved playerx to account for new column
                allview[playery][playerx] = ' '
            playerx = playerx - 1
            allview[playery][playerx] = '<'

    # vertical move
    elif y != playery:
        # move down
        if y > playery:
            # print('down')
            # check if allview needs to be expanded
            if y + 2 > curry:
                # initiate new squares created with '?'
                allview = allview + [['?' for i in range(sizex)]]
                exploreview = exploreview + [[' ' for j in range(sizex)]] #initialise the new cells into spaces
                curry = curry + 1
                sizey = sizey + 1
            # check allview and replace squares since replacing older squares dont matter for correctness
            for i in range(5):
                # replace squares
                allview[playery + 3][playerx - 2 + i] = view[4][i]
                if view[4][i] in obstacle or exploreview[playery + 3][playerx - 2 + i] == 'v': #same as above
                    exploreview[playery + 3][playerx - 2 + i] = 'v'
                else:
                    exploreview[playery + 3][playerx - 2 + i] = ' '                
            # change player location 
            if view[1][2] == 'O':
                allview[playery][playerx] = 'O'             
            # change so that rocks can be found
            if view[1][2] == '~':
                allview[playery][playerx] = '~'  
            else:
                allview[playery][playerx] = ' '
            # updates to playerx and playery
            playery = playery + 1
            allview[playery][playerx] = 'v'
        # move up
        else:
            # print('up')
            # check if allview needs to be expanded
            if y - 2 < 0:
                # initiate new squares created with '?'
                allview = addStartRow(allview,sizex,sizey,'?')
                exploreview = addStartRow(exploreview,sizex,sizey,' ')
                # TODO TURN THE ? into ' '
                # ^^^^^^^^^^^^^^^^^^^^^^^^^^ 
                playery = playery + 1
                curry = curry + 1
                sizey = sizey + 1
            # check allview and replace squares since replacing older squares dont matter for correctness
            for i in range(5):
                # replace squares
                allview[playery - 3][playerx - 2 + i] = view[0][i]
                if view[0][i] in obstacle or exploreview[playery - 3][playerx - 2 + i] == 'v': #same as above
                    exploreview[playery - 3][playerx - 2 + i] = 'v'
                else:
                    exploreview[playery - 3][playerx - 2 + i] = ' '                
            # change player location
            if view[3][2] == 'O':
                allview[playery][playerx] = 'O'     
            if view[3][2] == '~':
                allview[playery][playerx] = '~'                
            # check if previous step was on a stone
            else:
            # moved playerx to account for new column
                allview[playery][playerx] = ' '
            playery = playery - 1
            allview[playery][playerx] = '^'
        
    # no view to add
    else:
    #check what orientation you are in
    #look at the respective cell in view to see the cell that may have had an action taken
    #crossreference with the allview to see what changes have been made
    #update the changes
        if playerOri == '^':
            if view[1][2] == ' ' and allview[playery-1][playerx] == '-':
                allview[playery-1][playerx] = ' '
            elif view[1][2] == ' ' and allview[playery-1][playerx] == 'T':
                allview[playery-1][playerx] = ' ' 
        elif playerOri == 'v':
            if view[3][2] == ' ' and allview[playery+1][playerx] == '-':
                allview[playery+1][playerx] = ' '
            elif view[3][2] == ' ' and allview[playery+1][playerx] == 'T':
                allview[playery+1][playerx] = ' '
        elif playerOri == '<':
            if view[2][1] == ' ' and allview[playery][playerx-1] == '-':
                allview[playery][playerx-1] = ' '
            elif view[2][1] == ' ' and allview[playery][playerx-1] == 'T':
                allview[playery][playerx-1] = ' '
        elif playerOri == '^':
            if view[2][3] == ' ' and allview[playery][playerx+1] == '-':
                allview[playery][playerx+1] = ' '
            elif view[2][3] == ' ' and allview[playery][playerx+1] == 'T':
                allview[playery][playerx+1] = ' '
        else:
            pass
        parse = {0:'^',1:'>',2:'v',3:'<'}
        allview[playery][playerx] = parse[orientation]

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
def addStartColumn(view,x,y,ini):
    newview = copy.deepcopy(view)
    newview = [x + ['err'] for x in newview]
    for i in range(x):
        for j in range(y):
            newview[j][i+1] = view[j][i]
    for m in range(y):
        newview[m][0] = ini
    return newview

# given a matrix and its current size, adds a '?' initiated row at the start
def addStartRow(view,x,y,ini):
    newview = copy.deepcopy(view)
    newview = newview + [['err' for i in range(x)]]
    for i in range(x):
        for j in range(y):
            newview[j+1][i] = view[j][i]
    for m in range(x):
        newview[0][m] = ini
    return newview

# a function to print any map (function strictly for testing)
def printMap(view):
    for i in view:
        for j in i:
            print('[' + str(j) + ']',end='')
        print()

# a function to check entropy values of walkable areas
def analyse():
    test = copy.deepcopy(allview)
    for i in range(sizey):
        for j in range(sizex):
            entropy = 0
            # get bounds on where to search
            if i < 2:
                # need to search from 0 to i + 2
                iLBound = 0
                iHBound = i + 2
            elif i > sizey - 3:
                # need to search from i-2 to sizey - 1
                iLBound = i - 2
                iHBound = sizey - 1
            else:
                # need to search from i-2 to i+2
                iLBound = i - 2
                iHBound = i + 2
            if j < 2:
                # need to search from 0 to j + 2
                jLBound = 0
                jHBound = j + 2
            elif j > sizex - 3:
                # need to search from j - 2 to sizex - 1
                jLBound = j - 2
                jHBound = sizex - 1
            else:
                # need to search from j - 2 to j + 2
                jLBound = j - 2
                jHBound = j + 2
            
            for y in range(iHBound - iLBound + 1):
                for x in range(jHBound - jLBound + 1):
                    if allview[iLBound + y][jLBound + x] == '?':
                        entropy = entropy + 1
            
            # calculate excess not in map
            excessY = 5 - (iHBound - iLBound + 1) 
            excessX = 5 - (jHBound - jLBound + 1)
            if excessX == 0 and excessY != 0:
                entropy = entropy + excessY * 5
            elif excessY == 0 and excessX != 0:
                entropy = entropy + excessX * 5
            elif excessX != 0 and excessY != 0:
                entropy = entropy + excessX * 5 + excessY * 5 - excessX * excessY
            else:
                pass

            test[i][j] = entropy
    return test

            
            

            
if __name__ == "__main__":

    # checks for correct amount of arguments 
    if len(sys.argv) != 3:
        print("Usage Python3 "+sys.argv[0]+" -p port \n")
        sys.exit(1)

    port = int(sys.argv[2])

    # checking for valid port number
    if not 1025 <= port <= 65535:
        print('Incorrect port number')
        sys.exit()

    # creates TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
         # tries to connect to host
         # requires host is running before agent
         sock.connect(('localhost',port))
    except (ConnectionRefusedError):
         print('Connection refused, check host is running')
         sys.exit()

    # navigates through grid with input stream of data
    i=0
    j=0
    while 1:
        data=sock.recv(100)
        if not data:
            exit()
        for ch in data:
            if (i==2 and j==2):
                view[i][j] = '^'
                view[i][j+1] = chr(ch)
                j+=1 
            else:
                view[i][j] = chr(ch)
            j+=1
            if j>4:
                j=0
                i=(i+1)%5
        if j==0 and i==0:
            print_grid(view) # COMMENT THIS OUT ON SUBMISSION
            raftB = raft
            action = get_action(view) # gets new actions
            if action == 'f' and view[1][2] == '~' and raftB != raft:
                inRaft = 1
            step = {'O':'stone',' ':'land'}
            if action == 'f' and view[1][2] in step and inRaft == 1:
                print("INRAFT")
                inRaft = 0
            print("currentDest")
            print(currentDest)
            print("currentPath")
            print(currentPath)
            print("ACTION")
            print(action)
            printMap(allview)
            print("--------")
            printMap(exploreview)
            print(axe)
            print(key)
            print("STONE",end='')
            print(stone)
            print("Raft",end="")
            print(raft)
            print(inRaft)
            sock.send(action.encode('utf-8'))

    sock.close()

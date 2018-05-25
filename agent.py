#!/usr/bin/python3
# ^^ note the python directive on the first line
# COMP 9414 agent initiation file 
# requires the host is running before the agent
# designed for python 3.6
# typical initiation would be (file in working directory, port = 31415)
#        python3 agent.py -p 31415
# created by Leo Hoare
# with slight modifications by Alan Blair

import sys
import socket
import random
import time
import copy
import re
# declaring visible grid to agent
view = [['' for _ in range(5)] for _ in range(5)]

stone = 0
axe = 0
raft = 0
key = 0

# function to take get action from AI or user
def get_action(view):

    ## REPLACE THIS WITH AI CODE TO CHOOSE ACTION ##

    # input loop to take input from user (only returns if this is valid)

    global key
    global axe
    global stone
    global raft
    resources = {'o':'Rock','k':'Key','a':'Axe'} 
    low = 5
    for i in range(5):
        for j in range(5):
            if view[i][j] in resources:
                if abs(i - 1) + abs (j - 2) < low:
                    x = i
                    y = j  
                    low = abs(i-1) + abs(j-2)
    print(1)
    print(resources)
    try:
        path = walkable(view,y,x)
        path1 = list(path)
        if path1[0] != 'F':
            print(x)
            print(y)
            print(path)
            print(path1[0])
            #time.sleep(1)
            if view[1][2] == 'T' and axe == 1 and move == 'f':
                raft = raft + 1
                return 'c'
            if view[1][2] == 'a' and axe == 0 and move == 'f':
                axe = 1
            if view[1][2] == 'k' and key == 0 and move == 'f':
                key = 1
            if view[1][2] == '-' and key == 1 and move == 'f':
                return 'u'
            if view[1][2] == 'o' and move == 'f':
                stone = stone + 1
            return path[0]
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
            if view[1][2] == '*' or view[1][2]== '.':
                print('case')
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
                    raft = raft - 1
            #time.sleep(1)
            return move


def walkable(view,x,y):
    # find location of player
    test = copy.deepcopy(view)
    change = 1
    free = {'o':'Rock','k':'Key','a':'Axe',' ':'Space'}
    
    test[2][2] = '^'
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
        return turnToPath(test[y][x])
    else:
        return 'False'

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

def turnToPath(directions):
    arr = list(directions.replace("^",""))
    facing = 0
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
    print('+-----+')
    for ln in view:
        print("|"+str(ln[0])+str(ln[1])+str(ln[2])+str(ln[3])+str(ln[4])+"|")
    print('+-----+')

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
            action = get_action(view) # gets new actions
            sock.send(action.encode('utf-8'))

    sock.close()

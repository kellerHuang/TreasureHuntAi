#!/usr/bin/python3

import copy
import re

array = [[' ',' ',' ',' ',' '],
        [' ',' ',' ',' ',' '],
        [' ',' ','^','*',' '],
        [' ',' ','*',' ',' '],
        [' ',' ',' ',' ',' ']]

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
                            test[i][j+1] = test[i][j] + 'L'
                            change = 1
                    if j > 0:
                        if test[i][j-1] in free:
                            test[i][j-1] = test[i][j] + 'R'
                            change = 1
    
    check = re.sub('[RLUD]','',test[y][x])
    if check == '^':
        return test[y][x]
    else:
        return 'false'

print(walkable(array,4,2))
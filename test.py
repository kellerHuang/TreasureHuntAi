#!/usr/bin/python3

import copy

def revPath(path):
    fpath = path[::-1]
    curr = ()
    newP = ""
    for i in fpath:
        print('xd')
        if curr == ():
            curr = i
            continue
        else:
            if curr[0] != i[0]:
                if curr[0] + 1 == i[0]:
                    # move right
                    newP = newP + "R"
                else:
                    newP = newP + "L"
            if curr[1] != i[1]:
                if curr[1] + 1 == i[0]:
                    newP = newP + "D"
                else:
                    newP = newP + "U"
    turnToPath(newP,orientation)

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

path = [(1,1),(2,1)]
revPath(path)
# takes in a tuple turns into actual path

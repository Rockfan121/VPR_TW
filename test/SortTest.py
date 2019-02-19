#!/usr/bin/env python3
import sys
sys.path.insert(0,'../src')
from Read import Node, reorder

els = []
for j in range(10):
    i = j**2
    els.append(Node(10 - i, 20*i, 3*(10 - j)*((i+1)**2) + 20*i, i))

mix = [1, 3, 4, 5, 6, 2, 9, 7, 8, 0]
els2 = []
for e in mix:
    els2.append(els[e])

for e in els2:
    print(e.__dict__)

print("")
l = reorder(els2)
l = reorder(l)
for i in l:
    print(i.__dict__)

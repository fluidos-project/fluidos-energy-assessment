import itertools
import time 

box_2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
perm=[]
for p in itertools.product(box_2, repeat=6):
    perm.append(p)

print(perm)

time.sleep(10)
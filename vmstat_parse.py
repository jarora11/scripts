import re
mystring = """procs -----------memory---------- ---swap-- -----io---- --system-- -----cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 1  0      0 102906608 1489688 23418032    0    0     0     6    0    0  1  0 98  0  0
 0  0      0 102918560 1489688 23418056    0    0     0    36 23259 29572  2  0 98  0  0
 1  0      0 102919184 1489688 23418056    0    0     0     0 20951 26247  1  0 99  0  0
 0  0      0 102919440 1489688 23418056    0    0     0     0 18488 23607  1  0 99  0  0
 0  0      0 102920344 1489688 23418056    0    0     0   332 15752 19584  1  0 99  0  0
 """
vmstat = re.sub(r'^[^\n]*\n','',mystring)
vmstat = vmstat.splitlines()
vmstat = [x.split() for x in vmstat]
vmstat = [ row for row in vmstat if row]
ziplist = zip(*vmstat)
mydict = { x[0]:x[1:] for x in ziplist}

print mydict

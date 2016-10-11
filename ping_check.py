import re
from multiprocessing.pool import ThreadPool as pool
from subprocess import PIPE,Popen

def do_ping(hostname):
	proc = Popen(['ping','-c1',hostname],stdout=PIPE,stderr=PIPE)
	pout,perr = proc.communicate()
	retcode = proc.returncode
	if retcode == 0:
		print hostname + ' is alive\n'
	else:
		print hostname + ' is dead\n'
	return

def do_dig(ip):
	proc = Popen(['dig','-x',ip,'+short'],stdout=PIPE,stderr=PIPE)
	pout,perr = proc.communicate()
	return pout

if __name__=='__main__':
	_pool = pool(processes=50)

	with open('filename.txt','r') as tmpfile:
		hostlist = tmpfile.readlines()
	hostlist = [x.rstrip('\n') for x in hostlist]
	_pool.map(do_dig,hostlist)
	_pool.close()
	_pool.join()

import re

route_table = '''
      Destination        Gateway                      Dist/Metric Last Change
       -----------        -------                      ----------- -----------
  B EX 0.0.0.0/0          via 192.0.2.73                  20/100        4w0d
                          via 192.0.2.201
                          via 192.0.2.202
                          via 192.0.2.74
  B IN 192.0.2.76/30     via 203.0.113.183                200/100        4w2d
  B IN 192.0.2.204/30    via 203.0.113.183                200/100        4w2d
  B IN 192.0.2.80/30     via 203.0.113.183                200/100        4w2d
  B IN 192.0.2.208/30    via 203.0.113.183                200/100        4w2d
'''

tablist = re.findall(r'\d{1,}\.\d{1,}\.\d{1,}\.\d{1,}\/\d+|\d{1,}\.\d{1,}\.\d{1,}\.\d{1,}',route_table,re.DOTALL|re.MULTILINE)

routes = {}
current_prefix = ''
for host in tablist:
    if re.search('\/\d+',host):
        current_prefix = host
        routes[host]=[]
    elif current_prefix in routes.keys():
        routes[current_prefix].append(host)

print routes

#!C:\Python27\python.exe -u
#import mcafee_og
import mcafeeHelper
import sys
import getpass
'''
import execnet
def call_python_version(Version, Module, Function, ArgumentList):
    gw      = execnet.makegateway("popen//python=python%s" % Version)
    channel = gw.remote_exec("""
        from %s import %s as the_function
        channel.send(the_function(*channel.receive()))
    """ % (Module, Function))
    channel.send(ArgumentList)
    return channel.receive()
'''
policies = [
	"automated_import"
]
print("Login to McAfee...")
user = input("Enter username: ")
pwd = getpass.getpass('Enter password: ')

mc = mcafeeHelper.client('qdcws2893','8443',user,pwd,'https','json')
#mc = call_python_version("2.7", "mcafeeHelper", "client", ['qdcws2893','8443',user,pwd,'https','json'])

print(policies[0])

output = mc.policy.find(policies[0])

#productId = "ENDP_AM_1000"
'''
for row in output.split('\n'):
	if "productId" in row:
		productId = row.split(': ')[1].strip("\",")

policies = mc.policy.export(productId=productId)
sys.stdout = open("policies.xml",'w')
print (policies)
'''
#ADD HASHES TO POLICIES.XML

mc.policy.importPolicy(file='file:///automated_import_-_Testing.xml')#,force='true')

sys.stdout = open("results.txt",'w')

print (output)
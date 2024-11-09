import json
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

def DisconnectSi(si):
    Disconnect(si)
    print ("Disconnected")
    
with open('key.json') as json_auth_file:
    auth = json.load(json_auth_file)

host = auth["host"]
password = auth["pwd"]
username = auth["user"]

#Connexion à la plateforme ESXi

try:
    print ("Connecting to ESXi...")
    si  = SmartConnect(host=host, user=username, pwd=password, disableSslCertValidation=True)
except Exception as err:
    print("Erreur de connexion",err)
print("Connected")
content = si.RetrieveContent()
datacenter1 = content.rootFolder.childEntity[0]
print(type(content))
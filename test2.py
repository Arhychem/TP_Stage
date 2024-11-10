import json
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from cdrom_attach import cdrom,powerOnVm
from functions import DisconnectSi
  
with open('key.json') as json_auth_file:
    auth = json.load(json_auth_file)
host = auth["host"]
password = auth["pwd"]
username = auth["user"]

with open('vm_creation_attachement_config.json') as vm_params:
    params = json.load(vm_params)
isoPath = params["CD-ROM"]

#Connexion à la plateforme ESXi

try:
    print ("Connecting to ESXi...")
    si  = SmartConnect(host=host, user=username, pwd=password, disableSslCertValidation=True)
except Exception as err:
    print("Erreur de connexion",err)
print("Connected")
content = si.RetrieveContent()
datacenter1 = content.rootFolder.childEntity[0]
# datastoreName=datacenter1.datastore[0].name

# isoPath = '['+datastoreName+'] test/Core-5.4.iso'
print("Iso Path:",isoPath)
cdrom(si,vm_name="vm_max",iso_path=isoPath,datacenterName="ha-datacenter")
powerOnVm(si,"vm_max",datacenterName="ha-datacenter")
DisconnectSi(si,None)

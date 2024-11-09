import json
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from functions import DisconnectSi,getDatacenter
from OvfHandler import OvfHandler
import time

  
#Chargement des fichiers de configuration
with open('key.json') as json_auth_file:
    auth = json.load(json_auth_file)
with open('config.json') as configFile:
    config = json.load(configFile)

#paramètres de connexion
host = auth["host"]
password = auth["pwd"]
username = auth["user"]

#paramètres de configuration
vmBaseName = config["vm_Base_name"]
numInstances = config["number_of_instances"]


#Connexion à la plateforme ESXi

try:
    print ("Connecting to ESXi...")
    si  = SmartConnect(host=host, user=username, pwd=password, disableSslCertValidation=True)
except Exception as err:
    print("Erreur de connexion",err)
print("Connected")
content = si.RetrieveContent()
datacenter = getDatacenter(content,"ha-datacenter")
datastore=datacenter.datastore[0]
datastoreName=datacenter.datastore[0].name
computeRes = datacenter.hostFolder.childEntity[0]
vmResourcePool = computeRes.resourcePool
destinationHost = computeRes.host[0].name


def deployOva(resourcePool:vim.ResourcePool,datastore:vim.Datastore,host:str,ovaPath:str):
    ovf_handle = OvfHandler(ovaPath)
    ovf_manager = si.content.ovfManager
    # CreateImportSpecParams can specify many useful things such as
    # diskProvisioning (thin/thick/sparse/etc)
    # networkMapping (to map to networks)
    # propertyMapping (descriptor specific properties)
    cisp = vim.OvfManager.CreateImportSpecParams()
    cisr = ovf_manager.CreateImportSpec(
        ovf_handle.get_descriptor(), resourcePool, datastore, cisp)

    # These errors might be handleable by supporting the parameters in
    # CreateImportSpecParams
    if cisr.error:
        print("The following errors will prevent import of this OVA:")
        for error in cisr.error:
            print("%s" % error)
        return 1

    ovf_handle.set_spec(cisr)

    lease = resourcePool.ImportVApp(cisr.importSpec, datacenter.vmFolder)
    while lease.state == vim.HttpNfcLease.State.initializing:
        print("Waiting for lease to be ready...")
        time.sleep(1)

    if lease.state == vim.HttpNfcLease.State.error:
        print("Lease error: %s" % lease.error)
        return 1
    if lease.state == vim.HttpNfcLease.State.done:
        return 0

    print("Starting deploy...")
    return ovf_handle.upload_disks(lease, host)
result = deployOva(resourcePool=vmResourcePool,datastore=datastore,
                   host=host,ovaPath="/media/maxime/MAXIME/5GI The Last/Cloud/tinyVM.ova")
print(result)
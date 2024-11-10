import json
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from vm_creation import createAVm
from functions import DisconnectSi,getDatacenter

with open('key.json') as json_auth_file:
    auth = json.load(json_auth_file)

host = auth["host"]
password = auth["pwd"]
username = auth["user"]

with open('vm_creation_attachement_config.json') as vm_params:
    params = json.load(vm_params)
vmRam = params["RAM"]
vmDisk = params["Disk"]
vmNcpus = params["nCpus"]
vmName = params["vm_name"]

#Connexion à la plateforme ESXi

try:
    print ("Connecting to ESXi...")
    si  = SmartConnect(host=host, user=username, pwd=password, disableSslCertValidation=True)
except Exception as err:
    print("Erreur de connexion",err)
print("Connected")
content = si.RetrieveContent()

#On récupère un datacenter (ha-datacenter)
datacenter = getDatacenter(content,"ha-datacenter")
datastoreName=datacenter.datastore[0].name
print("dataStore Name:",datastoreName)
print("freeSpace on the datastore:",datacenter.datastore[0].summary.freeSpace/2**20,"mo")

#On récupère le ComputeResource associé au datacenter
computeRes = datacenter.hostFolder.childEntity[0]

#Déterminons le resourcePool
vmResourcePool = computeRes.resourcePool

##Déterminons maintenant l'hôte detenant le datacenter
container = content.viewManager.CreateContainerView(datacenter,[vim.HostSystem],True)
# équivalent à .computeRes.host[0]
destinationHost = container.view[0]

#Déteminons quelques spécificité liées au datacenter
numberOfCPU = destinationHost.hardware.cpuInfo.numCpuCores
availableRam = destinationHost.hardware.memorySize/2**20
print("number of host cpu:",numberOfCPU)
print("available host ram:",availableRam,"mo")
createAVm(destinationHost=destinationHost,datastoreName=datastoreName,guestName=vmName,description="vm created for the question 9.1 od the subject",
          resPool=vmResourcePool,vmRam=int(vmRam),nCpu=int(vmNcpus),diskSizeMB=vmDisk)
DisconnectSi(si,container)


import json
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from vm_creation import createAVm
from functions import DisconnectSi

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

#Connexion à la plateforme ESXi

try:
    print ("Connecting to ESXi...")
    si  = SmartConnect(host=host, user=username, pwd=password, disableSslCertValidation=True)
except Exception as err:
    print("Erreur de connexion",err)
print("Connected")
content = si.RetrieveContent()

#On récupère le premier datacenter
datacenter1 = content.rootFolder.childEntity[0]
print("dataStore Name:")
datastoreName=datacenter1.datastore[0].name
print(datastoreName)
print("freeSpace:",datacenter1.datastore[0].summary.freeSpace/2**20,"mo")

#On récupère le ComputeResource
computeRes = datacenter1.hostFolder.childEntity[0]

#Déterminons le resource pool de root (localhost)
vmResourcePool = computeRes.resourcePool

# équivalent à .computeRes.host[0]
container = content.viewManager.CreateContainerView(datacenter1,[vim.HostSystem],True)
destinationHost = container.view[0]
numberOfCPU = destinationHost.hardware.cpuInfo.numCpuCores
availableRam = destinationHost.hardware.memorySize/2**20
print("Host resourcePool:",vmResourcePool)
print("destinationHost:",destinationHost)
print("number of host cpu:",numberOfCPU)
print("available host ram:",availableRam,"mo")
createAVm(destinationHost=destinationHost,datastoreName=datastoreName,guestName="vm_max",description="vm created for the question 9.1 od the subject",
          resPool=vmResourcePool,vmRam=int(vmRam),nCpu=int(vmNcpus),diskSizeMB=vmDisk)
DisconnectSi(si,container)


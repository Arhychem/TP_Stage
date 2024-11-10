import json
from pyVmomi import vim
from pyVim.connect import SmartConnect
from functions import getDatacenter, getManagedObject,wait_for_task
from functions import DisconnectSi

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

def vm_cloning(
        content:vim.ServiceInstanceContent, vm_name:str, datacenterName:str, 
        clusterName:str, powerOn:bool, datastoreClusterName=None,resourcePoolName=None,datastoreName=None):
    datacenter = getDatacenter(content,datacenterName)
    destinationFolder = datacenter.vmFolder
    datastore = getManagedObject(content,[vim.Datastore],datastoreName)
    cluster = getManagedObject(content, [vim.ClusterComputeResource], clusterName)
    if not cluster:
        print(f"No cluster found. Using default resource pool for VM {vm_name}")
        cluster = getManagedObject(content, [vim.ResourcePool])

    resourcePool = getManagedObject(content,[vim.ResourcePool],resourcePoolName)
    if not resourcePoolName:
        resourcePool = cluster.resourcePool
        
    vmconf = vim.vm.ConfigSpec()
    template = getManagedObject(content,[vim.VirtualMachine],vm_name)
    if not template:
        print(f"VM {vm_name} not found.")
        return

    #Cette partie ne va probablement pas s'exécuter étant donné qu'il n'y a pas de cluster
    if datastoreClusterName:
        pod = getManagedObject(content, [vim.StoragePod], datastoreClusterName)
        podsel = vim.storageDrs.PodSelectionSpec()
        podsel.storagePod = pod
        storagespec = vim.storageDrs.StoragePlacementSpec()
        storagespec.podSelectionSpec = podsel
        storagespec.type = 'create'
        storagespec.folder = destinationFolder
        storagespec.resourcePool = resourcePool
        storagespec.configSpec = vmconf

        try:
            rec = content.storageResourceManager.RecommendDatastores(
                storageSpec=storagespec)
            rec_action = rec.recommendations[0].action[0]
            real_datastore_name = rec_action.destination.name
        except Exception:
            real_datastore_name = template.datastore[0].info.name

        datastore = getManagedObject(content, [vim.Datastore], real_datastore_name)
        
    # Définition des spécifications de relocation de la machine virtuelle, 
    # rien que le ResourcePool et le Datastore ont été changés
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    relospec.pool = resourcePool

    #Spécification pour le clonage
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = powerOn
    print(template)

    if not template.config.template:
        print(f"VM {vm_name} is not a template. Converting to template...")
        task = template.MarkAsTemplate()
        wait_for_task(task)

    print(f"clonage de la VM {vm_name}...")
    task = template.Clone(folder=destinationFolder, name=f"{vm_name}_clone", spec=clonespec)
    wait_for_task(task)
    return 

vm_cloning(content=content,vm_name="tinyVM",datacenterName="ha-datacenter",clusterName="",powerOn=False)
DisconnectSi(si,None)
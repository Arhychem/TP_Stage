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

def get_or_create_folder_in_vmFolder(datacenter:vim.Datacenter, folder_name:str):
    """
    Récupère un dossier par nom dans vmFolder du datacenter ou le crée s'il n'existe pas.
    """
    # Recherchez si le dossier existe déjà
    existing_folder = next((folder for folder in datacenter.vmFolder.childEntity 
                            if isinstance(folder, vim.Folder) and folder.name == folder_name), None)
    if existing_folder:
        print(f"Dossier '{folder_name}' déjà existant dans '{datacenter.name}'.")
        return existing_folder

    # Créer le dossier directement dans vmFolder
    try:
        new_folder = datacenter.vmFolder.CreateFolder(name=folder_name)
        print(f"Dossier '{folder_name}' créé dans le datacenter '{datacenter.name}' dans vmFolder.")
        return new_folder
    except Exception as e:
        print(f"Erreur lors de la création du dossier '{folder_name}': {e}")
        raise

def copy_vm(content, source_vm_name, new_vm_name, datacenter_name, resource_pool, datastore_name):
    # On récupère le datacenter et les objets nécessaires
    datacenter = [d for d in content.rootFolder.childEntity if d.name == datacenter_name][0]
    source_vm = [vm for vm in datacenter.vmFolder.childEntity if vm.name == source_vm_name][0]
    datastore = [ds for ds in datacenter.datastoreFolder.childEntity if ds.name == datastore_name][0]

    # Configuration de la nouvelle VM
    files = vim.vm.FileInfo()
    files.vmPathName = "["+datastore.name+"]"
    config_spec = vim.vm.ConfigSpec(
        name=new_vm_name,
        memoryMB=source_vm.config.hardware.memoryMB,
        numCPUs=source_vm.config.hardware.numCPU,
        guestId=source_vm.config.guestId,
        version=source_vm.config.version,
        files = files,
        annotation = "clone d'une vm"
    )
    size=0
     # Clonage des disques et configuration réseau
    for device in source_vm.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualDisk):
            size = device.capacityInKB
    """ Ajout d'un disque avec une taille prédéfinie """
    #création d'un VirtualDisk et configuration de celui-ci
    disk = vim.vm.device.VirtualDisk()
    disk.key = 0
    disk.unitNumber = 0
    disk.capacityInKB = size   # Convertir le MB en KB
    disk.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
    disk.backing.fileName = "[" + datastore.name + "]"
    disk.backing.diskMode = "persistent"
    disk.backing.thinProvisioned = True
    disk.controllerKey = 1000
    
     # Créattion d'un controleur SCSI controller pour le disque
    controller = vim.vm.device.VirtualLsiLogicController()
    controller.key = 1000
    controller.busNumber = 0
    controller.sharedBus = vim.vm.device.VirtualSCSIController.Sharing.noSharing
    
     # Ajout du VirtualDisk et du controleur à config
    config_spec.deviceChange = [
        vim.vm.device.VirtualDeviceSpec(
            operation=vim.vm.device.VirtualDeviceSpec.Operation.add,
            device=controller
        ),
        vim.vm.device.VirtualDeviceSpec(
            operation=vim.vm.device.VirtualDeviceSpec.Operation.add,
            fileOperation=vim.vm.device.VirtualDeviceSpec.FileOperation.create, # à préciser, sinon la taille du disque n'est pas prise en compte
            device=disk
        )
    ] 

    network_spec = vim.vm.device.VirtualDeviceSpec()
    network_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    network_spec.device = vim.vm.device.VirtualVmxnet3(
        backing=vim.vm.device.VirtualEthernetCard.NetworkBackingInfo(
            deviceName="VM Network"
        )
    )
    config_spec.deviceChange.append(network_spec)

    # Création de la VM
    print(f"Copie de la VM '{new_vm_name}'...")
    task = datacenter.vmFolder.CreateVM_Task(config=config_spec, pool=resource_pool)
    wait_for_task(task)

    
datacenter = getDatacenter(content,"ha-datacenter")
computeRes = datacenter.hostFolder.childEntity[0]
vmResourcePool = computeRes.resourcePool


copy_vm(
    content,
    source_vm_name="tinyVM",
    new_vm_name="vm_max_clone",
    datacenter_name="ha-datacenter",
    resource_pool=vmResourcePool,
    datastore_name="datastore1"
) 
DisconnectSi(si,None)
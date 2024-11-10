import sys
from pyVmomi import vim
from pyVim.task import WaitForTask

def createAVm(destinationHost:vim.HostSystem,datastoreName:str,guestName:str,
              description:str,resPool:vim.ResourcePool,vmRam:int,nCpu:int,diskSizeMB:int):
    config = createConfig(guestName=guestName,description=description,datastoreName=datastoreName,memory=vmRam,numCPUs=nCpu,diskSizeMB=diskSizeMB)
    """ 
    Déterminons le vm_folder correspondant au destinationHost
    ## Étapes:
        ->destinationHost.parent renvoie un ComputeResource
        ->destinationHost.parent.parent renvoie un Folder (hostFolder)
        ->destinationHost.parent.parent.parent renvoie le datacenter correspondant
        ->destinationHost.parent.parent.parent.vmFolder renvoie le vmFolder du datacenter
    """
    vm_folder:vim.Folder=destinationHost.parent.parent.parent.vmFolder
    """ 
    ## Autre méthode: 
    
    for child in content.rootFolder.childEntity:
        if child.name == datacenterName:
            vm_folder = child.vmFolder  # ici child est un datacenter
            # Étant donné qu'il n'y a qu'un seul datacenter, on aurait pu juste le passer en paramètre et l'utiliser...
            break
        else: 
            print (f"Datacenter {datacenterName} not found")
            sys.exit()
    """
    try:
        WaitForTask(vm_folder.CreateVm(config=config,pool=resPool,host=destinationHost))
        print(f"Machine virtuelle {guestName} crée")
    except vim.fault.DuplicateName:
        print("VM duplicate name: %s" % guestName, file=sys.stderr)
    except vim.fault.AlreadyExists:
        print("VM name %s already exists." % guestName, file=sys.stderr)
    

def createConfig(guestName:str,description:str,datastoreName:str,diskSizeMB:int,memory=64,numCPUs=1,guestOS="otherGuest"):
    config = vim.vm.ConfigSpec()
    config.annotation = description
    config.memoryMB = int(memory)
    config.guestId = guestOS #Famille de système destiné à être installé sur la vm
    config.name = guestName #Nom de la machine virtuelle
    config.numCPUs = numCPUs
    files = vim.vm.FileInfo()
    files.vmPathName = "["+datastoreName+"]"
    config.files = files
    
    """ Ajout d'un disque avec une taille prédéfinie """
    #création d'un VirtualDisk et configuration de celui-ci
    disk = vim.vm.device.VirtualDisk()
    disk.key = 0
    disk.unitNumber = 0
    disk.capacityInKB = diskSizeMB * 1024   # Convertir le MB en KB
    disk.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
    disk.backing.fileName = "[" + datastoreName + "]"
    disk.backing.diskMode = "persistent"
    disk.backing.thinProvisioned = True
    disk.controllerKey = 1000
    
     # Créattion d'un controleur SCSI controller pour le disque
    controller = vim.vm.device.VirtualLsiLogicController()
    controller.key = 1000
    controller.busNumber = 0
    controller.sharedBus = vim.vm.device.VirtualSCSIController.Sharing.noSharing
    
     # Ajout du VirtualDisk et du controleur à config
    config.deviceChange = [
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
    
    return config
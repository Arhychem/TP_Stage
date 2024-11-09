import json
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

#Retourne le datacenter ayant pour nom le contenu de la variable name
def getDatacenter(content:vim.ServiceInstanceContent,name:str):
    for datacenter in content.rootFolder.childEntity:
        if datacenter.name==name: # "ha-datacenter" par exemple
            return datacenter
        else:
            raise Exception(f"failed to find {name} datacenter")
        
""" 
# Retourne le premier cd_rom trouvé
# J'ai remarqué 2 types de scsiLun (SCSI logical units ) : les "disk" et les "cd-rom"
"""
def getPhysicalCdrom(host:vim.HostSystem):
    for device in host.configManager.storageSystem.storageDeviceInfo.scsiLun:
        if device.lunType=="cdrom":
            return device
        return None # Il faut gérer ce cas dans le process
    
""" 
#On cherche un controleur IDE libre
# Constat: Sur les machines tinyVM crées à artir de tinyVM.ova, dev.device vaut un nombre grand(3000,3002)
tandis que sur celle ajoutée grace à la question 1, cette proptiété ne vaut Unset
"""
def findFreeIdeController(vm:vim.VirtualMachine):
    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualIDEController):
            # If there are less than 2 devices attached, we can use it.
            if len(dev.device) < 2:
                return dev
    return None
    
""" 
    On cherche tous les VirtualCdRom
"""
def getVirtualCdroms(vm:vim.VirtualMachine):
    result = []
    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualCdrom):
            result.append(dev)
    return result

""" 
On définit les spécificités du CD ROM
"""
def new_cdrom_spec(controller_key, backing):
    connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    connectable.allowGuestControl = True
    connectable.startConnected = True

    cdrom = vim.vm.device.VirtualCdrom()
    cdrom.controllerKey = controller_key
    cdrom.key = -1
    cdrom.connectable = connectable
    cdrom.backing = backing
    return cdrom


def cdrom(si:vim.ServiceInstance,vm_name:str,iso_path:str,datacenterName:str):
    content = si.RetrieveContent()
    datacenter = getDatacenter(content,datacenterName)
    #On cherche la machine virtuelle sur laquelle installer l'iso
    vm = content.searchIndex.FindChild(datacenter.vmFolder,vm_name)
    if vm is None:
        raise Exception(f'Failed to find VM {vm_name} in datacenter {datacenterName}')
    
    cdrom = None
    host = vm.runtime.host
    
    cdrom_lun = getPhysicalCdrom(host=host)
    return
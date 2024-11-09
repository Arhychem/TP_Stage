from pyVmomi import vim,vmodl
from pyVim.connect import SmartConnect, Disconnect
from pyVim.task import WaitForTask


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
# Constat: Sur les machines tinyVM crées à artir de tinyVM.ova, dev.device contient au moins un nombre (3000,3001,...)
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
    
    #On définit le controller
    controller = findFreeIdeController(vm)
    if controller is None:
        raise Exception('Failed to find a free slot on the IDE controller')
    
    cdrom = None
    host = vm.runtime.host
    
    cdrom_lun = getPhysicalCdrom(host=host)
    """ 
    # Modification des informations sur la sauvegarde (backingInfo)du VirtualCdrom
    #Le type d'objet de données VirtualDeviceSpec encapsule les spécifications de 
        modification pour un périphérique virtuel individuel
    # Reconfiguration de la machine virtuelle
    """
    if cdrom_lun is not None:
        backing = vim.vm.device.VirtualCdrom.AtapiBackingInfo()
        backing.deviceName = cdrom_lun.deviceName
        device_spec = vim.vm.device.VirtualDeviceSpec()
        device_spec.device = new_cdrom_spec(controller.key, backing)
        device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        config_spec = vim.vm.ConfigSpec(deviceChange=[device_spec])
        WaitForTask(vm.Reconfigure(config_spec))

        cdroms = getVirtualCdroms(vm)
        # TODO isinstance(x.backing, type(backing))
        cdrom = next(filter(lambda x: type(x.backing) == type(backing) and
                     x.backing.deviceName == cdrom_lun.deviceName, cdroms))
        # print("cdrom_lun, cdrom",cdrom)
    else:
        print('Skipping physical CD-Rom test as no device present.')
        
    cdrom_operation = vim.vm.device.VirtualDeviceSpec.Operation
    iso = iso_path
    
    """ 
    
    """
    if iso is not None:
        device_spec = vim.vm.device.VirtualDeviceSpec()
        if cdrom is None:  # Ajout d'un cdrom
            print("Ajout d'un cdrom...")
            backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(fileName=iso)
            cdrom = new_cdrom_spec(controller.key, backing)
            device_spec.operation = cdrom_operation.add
        else:  # modification d'un cdrom existant
            backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(fileName=iso)
            cdrom.backing = backing
            device_spec.operation = cdrom_operation.edit
        device_spec.device = cdrom
        config_spec = vim.vm.ConfigSpec(deviceChange=[device_spec])
        WaitForTask(vm.Reconfigure(config_spec))

        cdroms = getVirtualCdroms(vm)
        # print(backing)
        # print("cdroms",cdroms)
        cdrom = next(filter(lambda x: type(x.backing) == type(backing) and
                     x.backing.fileName == iso, cdroms))
        # print("iso, cd_rom",cdrom)
    else:
        print('Skipping ISO test as no iso provided.')  
        
    """ if cdrom is not None:  # L'opération est terminée, on enlève le cd_rom
        device_spec = vim.vm.device.VirtualDeviceSpec()
        device_spec.device = cdrom
        device_spec.operation = cdrom_operation.remove
        config_spec = vim.vm.ConfigSpec(deviceChange=[device_spec])
        WaitForTask(vm.Reconfigure(config_spec))
        print("Chargement de l'iso terminé") """
        
def powerOnVm(si:vim.ServiceInstance,vm_name:str,datacenterName:str):
    content = si.RetrieveContent()
    datacenter = getDatacenter(content,datacenterName)
    #On cherche la machine virtuelle sur laquelle installer l'iso
    vm = content.searchIndex.FindChild(datacenter.vmFolder,vm_name)
    if vm is None:
        raise Exception(f'Failed to find VM {vm_name} in datacenter {datacenterName}')
    try:
        vm.PowerOn()
        print(f"Machine virtuelle {vm_name} démarée")
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
    except Exception as error:
        print("Caught Exception : " + str(error))
    return
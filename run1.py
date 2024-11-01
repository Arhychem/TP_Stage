#CHEMI MAXIME, 5GI, ENSPY

import json
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

from tools import cli, service_instance, tasks, pchelper

def create_dummy_vm(vm_name, si, vm_folder, resource_pool,
                    datastore):
    """Creates a dummy VirtualMachine with 1 vCpu, 128MB of RAM.

    :param name: String Name for the VirtualMachine
    :param si: ServiceInstance connection
    :param vm_folder: Folder to place the VirtualMachine in
    :param resource_pool: ResourcePool to place the VirtualMachine in
    :param datastore: DataStrore to place the VirtualMachine on
    """
    datastore_path = '[' + datastore + '] ' + vm_name

    # bare minimum VM shell, no disks. Feel free to edit
    vmx_file = vim.vm.FileInfo(logDirectory=None,
                               snapshotDirectory=None,
                               suspendDirectory=None,
                               vmPathName=datastore_path)

    config = vim.vm.ConfigSpec(name=vm_name, memoryMB=128, numCPUs=1,
                           files=vmx_file, guestId='otherGuest',  
                           version='vmx-14') 

    print("Creating VM {}...".format(vm_name))
    task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
    tasks.wait_for_tasks(si, [task])

# On charge le JSON
with open('config.json') as json_config_file:
    config = json.load(json_config_file)

vmName = config['vm_name']
numInstances = config['number_of_instances']

# Détails de connexion ESXi
hostname = "192.168.72.53"
username = "root"

#Mauvaise pratique, mais allons-y
password = "Mchemi2024#"

disableSslCertValidation=True
si = SmartConnect(host=hostname, user=username, pwd=password, disableSslCertValidation=True)
print("Connecté à l'hôte ESXi")
content = si.RetrieveContent()
vmfolder = pchelper.get_obj(content, [vim.Folder], "datastore")

#création de la ressourcePool
resource_pool = pchelper.get_obj(content, [vim.ResourcePool], "Resources")

    
#On déploie toute les vM
for i in range(numInstances):
    instance_name = f"{vmName}_{i+1}"
    create_dummy_vm(vmName, si, vmfolder, resource_pool,
                    "datastore1")
    print(f"Déployé {instance_name}")

# Déconnexion de ESXi
Disconnect(si)
print("Déconnexion")

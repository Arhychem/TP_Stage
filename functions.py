from pyVmomi import vim
from pyVim.connect import Disconnect

def DisconnectSi(si:vim.ServiceInstance,container:vim.ServiceInstanceContent):
    if(container is not None):
        container.Destroy()
    Disconnect(si)
    print ("Disconnected")
    

def getDatacenter(content:vim.ServiceInstanceContent,name:str)->vim.Datacenter:
    """ Fonction de recheche de datacenter
        Params:
            content : la propriété content du ServiceInstance
            name: le nom du datacenter recherché
        Returns:
            retourne le datacenter s'il existe, sinon lève une exception
    """
    for datacenter in content.rootFolder.childEntity:
        if datacenter.name==name: # "ha-datacenter" par exemple
            return datacenter
        else:
            raise Exception(f"failed to find {name} datacenter")
          
def getManagedObject(content:vim.ServiceInstanceContent, vim_type, name=None):
    """
    Recherche d'un Managed Object du nom et type sécifié. Il y'a toute fois quelques contraintes: 
        -si le name vaut None:
            on retourne le premier Managed Object du type spécifié
        -si pas de managed object trouvé on lève une exception sauf si c'est un vim.ClusterComputeResource (là on ne retourne rien)

    Exemple 
    getManagedObject(content, [vim.Datacenter], "Datacenter Name")
    """
    
    folder = content.rootFolder
    container = content.viewManager.CreateContainerView(folder, vim_type, True)
    
    for managedObject in container.view:
        if name==None:
            return managedObject
        if managedObject.name == name:
            return managedObject
    if vim.ClusterComputeResource in vim_type:
        return
    raise Exception(f"Managed Object of type {vim_type} with the name \"{name}\" was not found")
       
def wait_for_task(task):
    """ wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            print("there was an error")
            print(task.info.error)
            task_done = True

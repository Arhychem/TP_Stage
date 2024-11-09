from pyVmomi import vim
from pyVim.connect import Disconnect

def DisconnectSi(si:vim.ServiceInstance,container:vim.ServiceInstanceContent):
    if(container is not None):
        container.Destroy()
    Disconnect(si)
    print ("Disconnected")
    
#Retourne le datacenter ayant pour nom le contenu de la variable name
def getDatacenter(content:vim.ServiceInstanceContent,name:str):
    for datacenter in content.rootFolder.childEntity:
        if datacenter.name==name: # "ha-datacenter" par exemple
            return datacenter
        else:
            raise Exception(f"failed to find {name} datacenter")
       


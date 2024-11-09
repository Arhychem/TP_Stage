def getVmFolder(content,si):
    datacenter = si.content.rootFolder.childEntity[0] 
    vms = datacenter.vmFolder.childEntity 

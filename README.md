# TP_Stage
## But du TP
Le tp a pour but de créer des machines virtuelles avec python en utilisant le module pyVmomi

## Partie1 (entièrement réalisée)
### Problèmes rencontrés
la RAM aloué (4096 Mo) ne permet pas à la machine virtuelle de se lancer
#### Solution: 
Ouvrir VMWare Workstation en mode sudo et configurer un swap pour les machines virtuelles

## Partie 2: Développement python
### Problèmes rencontrés:
##### L'exécution du script produit l'erreur suivante:

'''
 Traceback (most recent call last):
  File "run1.py", line 62, in <module>
    create_dummy_vm(vmName, si, vmfolder, resource_pool,
  File "run1.py", line 33, in create_dummy_vm
    tasks.wait_for_tasks(si, [task])
  File "/media/maxime/MAXIME/5GI The Last/Cloud/TP_Stage/tools/tasks.py", line 55, in wait_for_tasks
    raise task.info.error
pyVmomi.VmomiSupport.NotSupported: (vmodl.fault.NotSupported) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   msg = 'The operation is not supported on the object.',
   faultCause = <unset>,
   faultMessage = (vmodl.LocalizableMessage) []
}
'''
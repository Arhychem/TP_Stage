# TP_Stage
## But du TP
Le tp a pour but de créer des machines virtuelles avec python en utilisant le module pyVmomi

## Partie1 (entièrement réalisée)
### Problèmes rencontrés
la RAM aloué (4096 Mo) ne permet pas à la machine virtuelle de se lancer
#### Solution: 
Ouvrir VMWare Workstation en mode sudo et configurer un swap pour les machines virtuelles

## Partie 2: Développement python
<strong>Pour toute les questions le fichier de configuration contenant les credentials de connexion à la plateforme est : `key.json`</strong>
### <u>Question 7</u>
#### <u>Fichiers Importants:</u>
``` 
config.json 
ova_deployement.py
functions.py
OvfHandler.py 
```
#### <u>Exécution du code</u>
<b> Dans le fichier `ova_deployment.py` , veuillez modifier le chemin de l'image tinyVM.ova (paramètre ovaPath). Celui-ci vaut actuellement ovaPath1</b> (défini par rapport à mon terminal)<br>
<b>Vous pouvez le remplacer par ovaPath2, qui lui pointe vers une ressource en ligne (http://menaud.fr/Cours/Cloud/TP/PS1/OVA-Linux/tinyVM.ova)</b>
Les valeurs ovaPath2, tout comme ovaPath1 sont définies dans le fichier `config.json`
```python
  #modifier le paramètre ovaPath
  #remplacer le par ovaPath2 par exemple
   deployOva(resourcePool=vmResourcePool,datastore=datastore,
              host=host,ovaPath=ovaPath1)
```
Pour lancer le déploiement exécuter la commande suivante dans un terminal : <br>
`python ova_deployement.py`
### <u>Question 8</u>
<strong>Le clonage de la machine virtuelle en exécutant notre code `python vm_cloning.py` lève l'exception suivante: </strong>
```
(vmodl.fault.NotSupported) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   msg = 'The operation is not supported on the object.',
   faultCause = <unset>,
   faultMessage = (vmodl.LocalizableMessage) []
}
```
<strong>Autre approche: transformer la machine virtuelle en template avec la méthode MarkAsTemplate et cloner celui-ci</strong><br>
```python
if not template.config.template:
        print(f"VM {vm_name} is not a template. Converting to template...")
        task = template.MarkAsTemplate()
        wait_for_task(task)
```
<strong>Malheureusement même cette approche provoque une erreur: <strong>
```
Traceback (most recent call last):
  File "vm_cloning.py", line 89, in <module>
    vm_cloning(content=content,vm_name="tinyVM",datacenterName="ha-datacenter",clusterName="",powerOn=False)
  File "vm_cloning.py", line 81, in vm_cloning
    task = template.MarkAsTemplate()
  File "/home/maxime/.local/lib/python3.8/site-packages/pyVmomi/VmomiSupport.py", line 614, in <lambda>
    self.f(*(self.args + (obj,) + args), **kwargs)
  File "/home/maxime/.local/lib/python3.8/site-packages/pyVmomi/VmomiSupport.py", line 387, in _InvokeMethod
    return self._stub.InvokeMethod(self, info, args)
  File "/home/maxime/.local/lib/python3.8/site-packages/pyVmomi/SoapAdapter.py", line 1472, in InvokeMethod
    raise obj  # pylint: disable-msg=E0702
pyVmomi.VmomiSupport.NotSupported: (vmodl.fault.NotSupported) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   msg = 'The operation is not supported on the object.',
   faultCause = <unset>,
   faultMessage = (vmodl.LocalizableMessage) []
}
```
signifiant que l'opération n'est pas supportée ur cet objet (la VM)
####Alternative
Comme alternative, on a crée une machine virtuelle à l'image de la première
Pour cela on éxécute le code se trouvant dans `vm_cloning2.py`

### <u>Question 9</u>
#### <u>Question 9.1:</u> Ici, il nous était demandé de créer une machine virtuelle vide avec des caractéristiques définies
##### <u>Fichiers importants:</u>
```python
vm_creation.py #Dans ce fichier se trouve la fonction createVm permettant de créer la machine virtuelle
test.py #C'est ce fichier qu'il faut utiliser pour lancer la création de la machine virtuelle
functions.py # Contient certaines fonctions importantes comme getdatacenter(content, name)
vm_creation_attachement_config.json #Ce fichier contient les informations de configuration de la machine à créer
```
##### Exécution du code
Dans un terminal, tapper la commande `python test.py`

#### <u>Question 9.2 et 9.3: </u> Ici, il nous était demandé de :
- créer le CDROM, attacher l’ISO et modifier la VM
- Allumer la VM
##### <u>Fichiers importants:</u>
```python
cdrom_attach.py # Ce fichier contient diverses fonction dont la fonction cdrom qui permet de créer un VirtualCdrom et un controller associé et de les ajouter à la Vm
test2.py #C'est ce fichier qu'il faut utiliser pour lancer le processus, il charge le chemin de l'iso à partir du fichier vm_creation_attachement_config.json 
functions.py # Contient certaines fonctions importantes comme getdatacenter(content, name)
vm_creation_attachement_config.json #Ce fichier contient les informations de configuration de la machine crée
```
##### <u>Exécution du code</u>
Dans un terminal, tapper la commande `python test2.py`

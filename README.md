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
<code>
 python ova_deployement.py 
</code>
### <u>Question 8</u>

### <u>Question 9</u>
#### <u>Question 9.1:</u> Ici, il nous était demandé de créer une machine virtuelle vide avec des caractéristiques définies
##### <u>Fichiers importants:</u>
```python
vm_creation.py #Dans ce fichier se trouve la fonction createVm permettant de créer la machine virtuelle
test.py #C'est ce fichier qu'il faut utiliser pour lancer la création de la machine virtuelle
functions.py # Contient certaines fonctions importantes comme getdatacenter(content, name)
vm_creation_attachement_config.json #Ce fichier contient les informations de configuration de la machine à créer
```
##### <u>Exécution du code</u>
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
### Problèmes rencontrés:
##### L'exécution du script produit l'erreur suivante:


### Démarche:
Modification des paramètres RessourcePool et folder puis vérification
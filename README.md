Création du virtualenv

    /opt/Python-3.7.1/python -m venv env/

Instrallation des dépendances

    pip install hapic[serpyco]
    pip install aiohttp
    pip install aiohttp_autoreload
    
Scenario :

créer une API web qui permet de piloter un capteur (virtuel)

- configuration du capteur : nom
- configuration de la geolocalisation
- gestion des tags associés au capteur

- récupération de la température courante
- récupération de l'historique de temperature (stream)
- reset de l'historique
- récupération de la description du capteur


## Etape 1 : créer un hello world

### Objectif

Créer une api avec un endpoint `/about` qui renvoie :

- l'adresse IP de la machine
- la date et l'heure courante
- la version de python

### Eléments présentés :

- mécanisme général de création de routes
- mécanisme de serialisation
- génération de la documentation d'API

## Etape 2 : un capteur qui a un nom et qui est géolocalisé

### Objectif

Ajouter à l'API trois nouvelles routes :

- `PUT /sensor/name` pour configurer le nom du capteur
- `PUT /sensor/location` pour configurer la géolocalisation du capteur 
- `GET /sensor` pour récupérer les informations

- possibilité de mettre à jour le nom du capteur
- définition de la géolocalisation du capteur


```
$ http PUT http://localhost:8080/sensor/name name="Guido van Rossum"

HTTP/1.1 200 OK
Content-Length: 46
Content-Type: application/json
Date: Mon, 28 Jan 2019 05:45:51 GMT
Server: Python/3.7 aiohttp/3.5.4

{
    "location": null, 
    "name": "Guido van Rossum"
}
```

```
$ http PUT http://localhost:8080/sensor/location lon=5.95950 lat=45.17109


HTTP/1.1 200 OK
Content-Length: 46
Content-Type: application/json
Date: Mon, 28 Jan 2019 05:45:51 GMT
Server: Python/3.7 aiohttp/3.5.4

{
    "location": null, 
    https://www.openstreetmap.org/search?query=grenoble#map=13/45.1700/5.9600
    "name": "Guido van Rossum"
}
```


### Éléments présentés :

- champ optionnel
- génération d'erreurs
- Input_body

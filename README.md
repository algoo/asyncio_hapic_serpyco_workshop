Création du virtualenv

    /opt/Python-3.7.1/python -m venv env/

Instrallation des dépendances

    pip install hapic[serpyco]
    pip install aiohttp
    pip install aiohttp_autoreload
    
Scenario :

Créer une API web qui permet de configurer et lire un capteur de température géolocalisé

Ce qu'on veut pouvoir faire :

- récupérer la configuration système (date et heure courante, adresse IP, verion de python)
- récupérer la configuration du capteur et la mettre à jour (nom, géolocalisation du capteur)
- lire la valeur courante (sous forme de stream)
- être prévenu de modifications de configuration (websocket) 

```
GET /about
GET /sensor
PATCH /sensor
GET /sensor/live
```

Les contraintes du projet sont :

- de l'embarqué x86, donc programmation asynchrone et performance
- séparation des fonctionnalités métier / api



# SimpleWebSocketClient plugin firefox
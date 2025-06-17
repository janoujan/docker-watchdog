# docker-watchdog
 Un outil Python destiné aux administrateurs système pour suivre et obtenir des statistiques 
sur les conteneurs Docker en cours d'exécution.

 ## Objectif du projet
 Ce script interroge le démon Docker local et retourne une liste des conteneurs présents, 
avec leur nom, image et statut d'exécution, RAM et CPU

  #### Projet à but educatif

  ## Installation
  
  1-/ cloner le projet 
  ou telecharger le .zip et le decompresser à l'endroit souhaité 
 
  2-/ positionner vous dans le projet 
  ~cd /docker-watchdog

   ## Utilisation

  3 -/ run the watchdog
[~/docker-watchdog]: python3 src/docker-watchdog

   ## Dockerisation
    prerequisites: 
        Docker
        Docker-compose

    to compose the container:
    docker-compose up --build

    to shudown and wipe it out (container + image + volume)
    docker-compose down --rmi all --volumes



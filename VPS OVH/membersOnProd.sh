#!/bin/bash

cd ./

# Exécution du script d'ajout des adhérents
python3 ./get_members.py

sleep 5

# Copie du fichier sur le serveur
sshpass -p "your password" scp -P 22 ./JSON/donnees_adherents_2024.json  VPS@ssh.cluster.ovh.net:./adherents_2024.json


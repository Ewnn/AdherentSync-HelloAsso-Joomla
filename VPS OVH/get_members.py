# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import requests
import logging
import os
import json
from datetime import datetime
from glob import glob

# Configuration des chemins
dossier_journal = "log/"
dossier_json = "JSON/"
os.makedirs(dossier_journal, exist_ok=True)
os.makedirs(dossier_json, exist_ok=True)

# Suppression des fichiers journaux existants
journaux_existant = glob(os.path.join(dossier_journal, "connexion_HelloAsso*.log"))
for chemin_fichier_journal in journaux_existant:
    try:
        os.remove(chemin_fichier_journal)
    except Exception as e:
        logging.error(f"Erreur lors de la suppression du fichier journal {chemin_fichier_journal}: {str(e)}")

# Configuration de la journalisation
fichier_journal = os.path.join(dossier_journal, "connexion_HelloAsso{}.log".format(datetime.now().strftime('%d-%m-%Y_%H-%M-%S')))
logging.basicConfig(filename=fichier_journal, level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')

# Fonction pour effectuer une requête POST
def execute_post_request(url, payload, operation):
    try:
        response = requests.post(url, data=payload, verify=True)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors de l'opération {operation} : {str(e)}")
        raise

# Fonction pour obtenir le jeton HelloAsso avec rafraîchissement automatique
def obtenir_jeton_helloasso():
    logging.info("Obtention du jeton HelloAsso...")
    auth_url = "https://api.helloasso.com/oauth2/token"
    payload = {
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret',
        'grant_type': 'client_credentials'
    }


    try:
        response = execute_post_request(auth_url, payload, "obtention du jeton HelloAsso")
        access_token = response.get('access_token')
        refresh_token = response.get('refresh_token')

        return access_token, refresh_token
    except Exception as e:
        logging.error(f"Erreur lors de l'obtention du jeton HelloAsso : {str(e)}")
        raise

# Fonction pour rafraîchir le jeton HelloAsso
def rafraichir_jeton_helloasso(refresh_token):
    logging.info("Rafraîchissement du jeton HelloAsso...")
    auth_url = "https://api.helloasso.com/oauth2/token"
    payload = {
        'client_id': 'your_client_id',
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    try:
        response = execute_post_request(auth_url, payload, "Rafraîchissement du jeton HelloAsso")
        access_token = response.get('access_token')
        refresh_token = response.get('refresh_token')

        logging.info("Jeton HelloAsso rafraîchi avec succès.")
        return access_token, refresh_token
    except Exception as e:
        logging.error(f"Erreur lors du rafraîchissement du jeton HelloAsso : {str(e)}")
        raise

# Fonction pour récupérer les adhérents depuis HelloAsso en gérant le rafraîchissement du token
def obtenir_adherents_depuis_helloasso(jeton_acces, refresh_token):
    logging.info("Récupération des adhérents depuis HelloAsso...")
    
    # Mise à jour de l'URL pour l'année 2024
    url_evenement = "https://api.helloasso.com/v5/organizations/your_organization"
    
    headers = {'Authorization': f'Bearer {jeton_acces}'}

    try:
        response_adherents = requests.get(url_evenement, headers=headers, verify=True)
        response_adherents.raise_for_status()

        donnees_adherents = response_adherents.json().get('data', [])

        chemin_fichier_json = os.path.join(dossier_json, "donnees_adherents_2024.json")
        save_to_json(donnees_adherents, chemin_fichier_json, "Adhérents récupérés depuis HelloAsso")

        logging.info("Adhérents récupérés avec succès pour l'année 2024.")
        
        return donnees_adherents
    except requests.exceptions.RequestException as e:
        if 'invalid_token' in str(e).lower():
            # Le token est probablement expiré, essayons de le rafraîchir
            logging.info("Tentative de rafraîchissement du jeton HelloAsso...")
            access_token, new_refresh_token = rafraichir_jeton_helloasso(refresh_token)
            logging.info("Rafraîchissement du jeton réussi. Utilisation du nouveau jeton.")
            return obtenir_adherents_depuis_helloasso(access_token, new_refresh_token)
        else:
            logging.error(f"Erreur lors de la récupération des adhérents depuis HelloAsso pour l'année 2024 : {str(e)}")
            raise

# Fonction pour sauvegarder des données au format JSON dans un fichier
def save_to_json(data, file_path, operation):
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        logging.info(f"{operation} : Données sauvegardées dans {file_path}.")
    except Exception as e:
        logging.error(f"Erreur lors de l'opération {operation} : {str(e)}")
        raise

# Fonction principale du script
def main():
    connexion_joomla = None

    try:
        logging.info("Démarrage du script...")

        # Obtenir le jeton HelloAsso
        jeton_acces, refresh_token = obtenir_jeton_helloasso()

        # Récupérer les adhérents depuis HelloAsso
        adherents = obtenir_adherents_depuis_helloasso(jeton_acces, refresh_token)
        logging.info(f"{len(adherents)} adhérent(s) récupéré(s) depuis HelloAsso.")

    except Exception as e:
        logging.error(f"Erreur lors de l'exécution du script : {str(e)}")
        if connexion_joomla:
            connexion_joomla.rollback()  # Annuler les modifications en cas d'erreur
    finally:
        # Fermer la connexion à la base de données
        if connexion_joomla:
            connexion_joomla.close()
            logging.info("Connexion à la base de données fermée.")

if __name__ == "__main__":
    main()

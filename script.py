# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import requests
import hashlib
import mysql.connector
import random
import string
import logging
import os
import json
from datetime import datetime
from glob import glob

# Configuration des chemins
dossier_journal = "Log/"
dossier_json = "JSON/"
os.makedirs(dossier_journal, exist_ok=True)
os.makedirs(dossier_json, exist_ok=True)

# Suppression des fichiers journaux existants
journaux_existant = glob(os.path.join(dossier_journal, "log_ajout_adherents*.log"))
for chemin_fichier_journal in journaux_existant:
    try:
        os.remove(chemin_fichier_journal)
    except Exception as e:
        logging.error(f"Erreur lors de la suppression du fichier journal {chemin_fichier_journal}: {str(e)}")

# Configuration de la journalisation
fichier_journal = os.path.join(dossier_journal, "log_ajout_adherents_{}.log".format(datetime.now().strftime('%d-%m-%Y_%H-%M-%S')))
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

# Fonction pour générer un mot de passe aléatoire
def generer_mot_de_passe_aleatoire(longueur=15):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for i in range(longueur))

# Fonction pour vérifier si un utilisateur est déjà présent dans Joomla
def utilisateur_existe_dans_joomla(email, curseur):
    try:
        requete = "SELECT COUNT(*) FROM db.jos3_users WHERE LOWER(email) = LOWER(%s)"
        curseur.execute(requete, (email,))
        compte = curseur.fetchone()[0]
        return compte > 0
    except Exception as e:
        logging.error(f"Erreur lors de la vérification de l'existence de l'utilisateur dans Joomla : {str(e)}")
        raise

# Fonction pour vérifier si un utilisateur est déjà présent dans jos3_comprofiler
def utilisateur_existe_dans_jos3_comprofiler(email, curseur):
    try:
        requete = """
            SELECT user_id
            FROM db.jos3_comprofiler
            WHERE user_id = (
                SELECT id
                FROM db.jos3_users
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
            )
        """
        curseur.execute(requete, (email,))
        result = curseur.fetchone()

        return result is not None
    except Exception as e:
        logging.error(f"Erreur lors de la vérification de l'existence de l'utilisateur dans jos3_comprofiler : {str(e)}")
        raise

# Fonction de génération des requêtes SQL d'insertion dans jos3_users
def generer_requete_insertion_jos3_users(donnees):
    try:
        if not isinstance(donnees, dict):
            logging.error(f"Format de données invalide. Attendu : dictionnaire, Obtenu : {type(donnees)}")
            raise ValueError("Format de données invalide. Un dictionnaire était attendu.")

        # Extraction des informations du paiement
        info_payeur = donnees.get("payer", {})
        nom_complet = info_payeur.get("firstName", "") + " " + info_payeur.get("lastName", "")
        email = info_payeur.get("email", "")
        date_adhesion = info_payeur.get("dateOfBirth", "")

        # Vérification et conversion de la date
        date_adhesion = date_adhesion[:19] if date_adhesion else '2024-02-15 10:30:00'

        # Génération d'un mot de passe aléatoire et hachage avec MD5
        mot_de_passe = generer_mot_de_passe_aleatoire()
        chaine_a_hasher = mot_de_passe
        resultat = hashlib.md5(chaine_a_hasher.encode())
        final = resultat.hexdigest()

        # Requête d'insertion dans jos3_users
        requete_utilisateur_joomla = """INSERT INTO db.jos3_users (
                name,
                username,
                email,
                password,
                block,
                sendEmail,
                registerDate,
                activation,
                params,
                resetCount,
                otpKey,
                otep,
                requireReset
                ) VALUES (
                %s, %s, %s, %s, 0, 1, %s, 0,
                '{"admin_style":"","admin_language":"","language":"","editor":"","timezone":""}',
                0, '', '', 1
                );
            """

        # Requête d'insertion dans jos3_user_usergroup_map
        requete_usergroup_map = """
            INSERT INTO db.jos3_user_usergroup_map (user_id, group_id)
            VALUES ((SELECT id FROM db.jos3_users WHERE email = %s), 12)
        """

        logging.info("Création de l'utilisateur dans jos3_users")
        logging.info(f"Nom complet: {nom_complet}, Email: {email}, Date d'adhésion: {date_adhesion}")

        return requete_utilisateur_joomla, requete_usergroup_map % email

    except Exception as e:
        logging.error("Erreur lors de la génération des requêtes SQL : {}".format(str(e)))
        raise
    else:
        logging.info("La génération des requêtes SQL s'est déroulée sans erreur.")

# Fonction de génération des requêtes SQL d'insertion dans jos3_comprofiler
def generer_requete_insertion_jos3_comprofiler(donnees):
    try:
        if not isinstance(donnees, dict):
            logging.error(f"Format de données invalide. Attendu : dictionnaire, Obtenu : {type(donnees)}")
            raise ValueError("Format de données invalide. Un dictionnaire était attendu.")

        # Extraction des informations du paiement
        info_payeur = donnees.get("payer", {})
        firstname = info_payeur.get("firstName", "")
        email = info_payeur.get("email", "")
        lastname = info_payeur.get("lastName", "")

        # Requête pour l'insertion dans jos3_comprofiler seulement si l'utilisateur n'existe pas déjà
        requete_insertion_jos3_comprofiler = """INSERT INTO db.jos3_comprofiler (
                `user_id`,
                `firstname`,
                `lastname`,
                `hits`,
                `message_last_sent`,
                `message_number_sent`,
                `avatar`,
                `avatarapproved`,
                `canvas`,
                `canvasapproved`,
                `canvasposition`,
                `approved`,
                `confirmed`,
                `lastupdatedate`,
                `registeripaddr`,
                `cbactivation`,
                `banned`,
                `banneddate`,
                `unbanneddate`,
                `bannedby`,
                `unbannedby`,
                `bannedreason`,
                `acceptedterms`,
                `acceptedtermsconsent`,
                `cb_presentation`,
                `cb_telephone`,
                `cb_site_web`,
                `cb_secteur_activite`,
                `cb_nomentreprise`,
                `cb_image_profil`,
                `cb_image_profilapproved`,
                `cb_lienlinkedin`
            ) VALUES (
                %s,  # user_id
                %s,  # firstname
                %s,  # lastname
                0,   # hits
                '0000-00-00 00:00:00',  
                0,
                '',
                4,
                NULL,
                1,
                50,
                1,
                1,
                '0000-00-00 00:00:00',
                '',
                '',
                0,
                NULL,
                NULL,
                NULL,
                0,
                NULL,
                0,
                '0000-00-00 00:00:00',
                NULL,  
                NULL,  
                NULL,  
                NULL,  
                NULL,  
                NULL,  
                1, 
                NULL  
            );"""

        return requete_insertion_jos3_comprofiler

    except Exception as e:
        raise ValueError(f"Erreur lors de la génération de la requête d'insertion dans jos3_comprofiler : {str(e)}")

# Fonction de génération des requêtes SQL de mise à jour dans jos3_users
def generer_requete_mise_a_jour_jos3_users(donnees):
    try:
        if not isinstance(donnees, dict):
            raise ValueError("Format de données invalide. Un dictionnaire était attendu.")

        # Extraction des informations du paiement
        info_payeur = donnees.get("payer", {})
        prenom = info_payeur.get("firstName", "")
        nom = info_payeur.get("lastName", "")
        nom_complet = prenom + " " + nom
        date_enregistrement = info_payeur.get("dateEnregistrement", "")

        # Vérification et formatage de la date
        date_enregistrement = date_enregistrement[:19] if date_enregistrement else '2024-02-15 10:30:00'

        # Requête de mise à jour de jos3_users avec INSERT INTO ... ON DUPLICATE KEY UPDATE
        requete_mise_a_jour_jos3_users = """
            INSERT INTO db.jos3_users (name, username, registerDate, email, params)
            VALUES ('%s', '%s', '%s', '%s', '{"admin_style":"","admin_language":"","language":"","editor":"","timezone":""}')
            ON DUPLICATE KEY UPDATE name = VALUES(name), username = VALUES(username), registerDate = VALUES(registerDate)"""

        return requete_mise_a_jour_jos3_users % (nom_complet, nom_complet, date_enregistrement, donnees.get("payer", {}).get("email", ""))

    except Exception as e:
        raise ValueError(f"Erreur lors de la génération de la requête de mise à jour de jos3_users: {str(e)}")

# Fonction de génération de la requête SQL de mise à jour dans jos3_comprofiler
def generer_requete_mise_a_jour_jos3_comprofiler(donnees, email):
    try:
        if not isinstance(donnees, dict):
            raise ValueError("Format de données invalide. Un dictionnaire était attendu.")

        # Extraction des informations du paiement
        info_payeur = donnees.get("payer", {})
        email = info_payeur.get("email", "")
        prenom = info_payeur.get("firstName", "")
        nom = info_payeur.get("lastName", "")

        logging.info(f"L'utilisateur existe déjà ! Tentative de mise à jour de l'utilisateur avec l'adresse e-mail {email} dans jos3_comprofiler...")

        # Mettre à jour les champs nom et prenom
        requete_mise_a_jour_jos3_comprofiler = """
            UPDATE db.jos3_comprofiler
            SET firstname = '%s', lastname = '%s'
            WHERE user_id = (
                SELECT id
                FROM db.jos3_users
                WHERE LOWER(email) = LOWER('%s')
                LIMIT 1
            )
        """ % (prenom, nom, email)

        return requete_mise_a_jour_jos3_comprofiler

    except Exception as e:
        raise ValueError(f"Erreur lors de la génération de la requête de mise à jour dans jos3_comprofiler : {str(e)}")

# Fonction d'écriture des requêtes dans le fichier SQL
def ecrire_requetes_sql_fichier(requetes, fichier_sql):
    try:
        with open(fichier_sql, 'w', encoding='utf-8') as sql_file:
            for requete in requetes:
                # Assurez-vous que la requête est une chaîne avant de l'écrire dans le fichier
                if not isinstance(requete, str):
                    logging.error(f"Format de requête invalide. Attendu : chaîne, Obtenu : {type(requete)}")
                    raise ValueError("Format de requête invalide. Une chaîne était attendue.")
                else:
                    sql_file.write(requete + '\n\n')

        # Définir les permissions (chmod) sur le fichier
        os.chmod(fichier_sql, 0o755)
        logging.info(f"Requêtes SQL écrites avec succès dans le fichier {fichier_sql} et permissions définies.")

    except Exception as e:
        logging.error(f"Erreur lors de l'écriture des requêtes SQL dans le fichier {fichier_sql}: {str(e)}")
        raise

# Fonction principale du script
def main():
    connexion_joomla = None
    fichier_sql = "requetes_insertion_et_mise_a_jour.sql"
    requetes_sql = []

    try:
        logging.info("Démarrage du script...")

        # Obtenir le jeton HelloAsso
        jeton_acces, refresh_token = obtenir_jeton_helloasso()

        # Récupérer les adhérents depuis HelloAsso
        adherents = obtenir_adherents_depuis_helloasso(jeton_acces, refresh_token)
        logging.info(f"{len(adherents)} adhérent(s) récupéré(s) depuis HelloAsso.")

        # Connexion à la base de données
        logging.info("Connexion à la base de données ...")
        connexion_joomla = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db",
            port=3306
        )
        logging.info("Connexion effectuée !")

        curseur_joomla = connexion_joomla.cursor()

        # Traitement des adhérents et génération des requêtes SQL
        for adherent in adherents:
            email_utilisateur = adherent.get("payer", {}).get("email", "")
            nom_complet = adherent.get("payer", {}).get("firstName", "") + " " + adherent.get("payer", {}).get("lastName", "")
            logging.info(f"Vérification de l'existence de l'utilisateur avec l'email : '{email_utilisateur}' dans les différentes tables...")

            utilisateur_existe_jos3_users = utilisateur_existe_dans_joomla(email_utilisateur, curseur_joomla)
            utilisateur_existe_jos3_comprofiler = utilisateur_existe_dans_jos3_comprofiler(email_utilisateur, curseur_joomla)

            # Traitement des cas d'existence de l'utilisateur dans les tables Joomla
            if utilisateur_existe_jos3_users:
                logging.info(f"L'utilisateur avec l'email '{email_utilisateur}' existe dans la table jos3_users.")
                if utilisateur_existe_jos3_comprofiler:
                    logging.info(f"L'utilisateur avec l'email '{email_utilisateur}' existe également dans la table jos3_comprofiler.")

                    # Générer la requête de mise à jour dans jos3_users
                    requetes_sql.append(generer_requete_mise_a_jour_jos3_users(adherent))
                    # Générer la requête de mise à jour dans jos3_comprofiler
                    requetes_sql.append(generer_requete_mise_a_jour_jos3_comprofiler(adherent, email_utilisateur))
                    
                else:
                    logging.info(f"L'utilisateur avec l'email '{email_utilisateur}' n'existe pas dans la table jos3_comprofiler.")

                    # Générer la requête de mise à jour dans jos3_users
                    requetes_sql.append(generer_requete_mise_a_jour_jos3_users(adherent))
                    # Générer la requête d'insertion dans jos3_comprofiler
                    requetes_sql.append(generer_requete_insertion_jos3_comprofiler(adherent))

            else:
                logging.info(f"L'utilisateur avec l'email '{email_utilisateur}' n'existe pas dans la table jos3_users.")
                if utilisateur_existe_jos3_comprofiler:
                    logging.info(f"L'utilisateur avec l'email '{email_utilisateur}' existe dans la table jos3_comprofiler mais pas dans jos3_users.")

                    # Générer la requête de mise à jour dans jos3_comprofiler
                    requetes_sql.append(generer_requete_mise_a_jour_jos3_comprofiler(adherent))
                    # Générer la requête d'insertion dans jos3_users
                    requetes_sql.append(generer_requete_insertion_jos3_users(adherent))

                else:
                    logging.info(f"L'utilisateur avec l'email '{email_utilisateur}' n'existe pas dans la table jos3_comprofiler ni dans jos3_users.")

                    # Générer la requête d'insertion dans jos3_users
                    requetes_sql.append(generer_requete_insertion_jos3_users(adherent))
                    # Générer la requête d'insertion dans jos3_comprofiler
                    requetes_sql.append(generer_requete_insertion_jos3_comprofiler(adherent))

        # Écriture des requêtes SQL dans le fichier
        ecrire_requetes_sql_fichier(requetes_sql, fichier_sql)

        # Exécution des requêtes SQL
        for requete in requetes_sql:
            curseur_joomla.execute(requete)

        # Valider les modifications dans la base de données
        connexion_joomla.commit()
        logging.info("Modifications dans la base de données validées avec succès.")

    except Exception as e:
        logging.error(f"Erreur lors de l'exécution du script : {str(e)}")
    finally:
        # Fermer la connexion à la base de données
        if connexion_joomla:
            connexion_joomla.close()
            logging.info("Connexion à la base de données fermée.")

if __name__ == "__main__":
    main()
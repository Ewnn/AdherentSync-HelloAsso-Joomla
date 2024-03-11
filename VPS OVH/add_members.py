# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import hashlib
import mysql.connector
from mysql.connector import Error
import random
import string
import logging
import os
import json
from datetime import datetime
from glob import glob

# Configuration des chemins
dossier_journal = "log/"
os.makedirs(dossier_journal, exist_ok=True)

# Suppression des fichiers journaux existants
journaux_existant = glob(os.path.join(dossier_journal, "log_ajout_adherents*.log"))
for chemin_fichier_journal in journaux_existant:
    try:
        os.remove(chemin_fichier_journal)
    except Exception as e:
        logging.error(
            f"Erreur lors de la suppression du fichier journal {chemin_fichier_journal}: {str(e)}"
        )

# Configuration de la journalisation
fichier_journal = os.path.join(
    dossier_journal,
    "log_ajout_adherents_{}.log".format(datetime.now().strftime("%d-%m-%Y_%H-%M-%S")),
)
logging.basicConfig(
    filename=fichier_journal,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
)

# Chargement du fichier JSON
def charger_donnees_json(chemin_fichier):
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            donnees_json = json.load(f)
        return donnees_json
    except Exception as e:
        logging.error(f"Erreur lors du chargement du fichier JSON : {str(e)}")
        raise

# Connexion à la base de données MySQL
def connecter_mysql():
    try:
        connection = mysql.connector.connect(
            user="", # Your username
            password="", # Your password
            host="", # Your host
            database="" # Your database
        )
        if connection.is_connected():
            return connection
    except Error as e:
        logging.error(f"Erreur lors de la connexion à MySQL : {e}")
        raise

# Fonction pour générer un mot de passe aléatoire
def generer_mot_de_passe_aleatoire(longueur=15):
    caracteres = string.ascii_letters + string.digits
    return "".join(random.choice(caracteres) for i in range(longueur))

# Fonction pour vérifier si un utilisateur est déjà présent dans Joomla
def utilisateur_existe_dans_joomla(email, curseur):
    try:
        requete = (
            "SELECT COUNT(*) FROM yourdatabase.jos3_users WHERE LOWER(email) = LOWER(%s)"
        )
        curseur.execute(requete, (email,))
        compte = curseur.fetchone()[0]
        return compte > 0
    except Exception as e:
        logging.error(
            f"Erreur lors de la vérification de l'existence de l'utilisateur dans Joomla : {str(e)}"
        )
        raise

# Fonction de génération des requêtes SQL d'insertion dans jos3_users
def inserer_utilisateur_dans_jos3_users(donnees, curseur):
    try:
        if not isinstance(donnees, dict):
            logging.error(
                f"Format de données invalide. Attendu : dictionnaire, Obtenu : {type(donnees)}"
            )
            raise ValueError(
                "Format de données invalide. Un dictionnaire était attendu."
            )

        # Extraction des informations du paiement
        info_payeur = donnees.get("payer", {})
        prenom = info_payeur.get("firstName", "")
        nom = info_payeur.get("lastName", "")
        nomComplet = f"{prenom} {nom}"
        pseudo_base = (prenom[:1].lower() + nom.lower()) if prenom and nom else ""
        email = info_payeur.get("email", "")
        date_adhesion = info_payeur.get("dateOfBirth", "")

        # Vérification et conversion de la date
        date_adhesion = date_adhesion[:19] if date_adhesion else "2024-02-15 10:30:00"

        # Génération d'un mot de passe aléatoire et hachage avec MD5
        mot_de_passe = generer_mot_de_passe_aleatoire()
        chaine_a_hasher = mot_de_passe
        resultat = hashlib.md5(chaine_a_hasher.encode())
        final = resultat.hexdigest()

        # Vérification de l'existence du pseudo dans la base de données
        pseudo = pseudo_base
        i = 1
        while True:
            try:
                # Requête de vérification d'existence du pseudo
                curseur.execute("SELECT id FROM yourdatabase.jos3_users WHERE username = %s", (pseudo,))
                result = curseur.fetchone()
                if result:
                    # Pseudo existant, ajouter un chiffre à la fin du nom de famille
                    pseudo = f"{pseudo_base}{i}"
                    i += 1
                else:
                    break  # Pseudo disponible
            except Exception as e:
                logging.error(
                    "Erreur lors de la vérification de l'existence du pseudo : {}".format(
                        str(e)
                    )
                )
                raise

        # Requête d'insertion dans jos3_users
        requete_utilisateur_joomla = """
            INSERT INTO yourdatabase.jos3_users (
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
                requireReset,
                authProvider
            ) VALUES (
                %s, %s, %s, %s, 0, 1, %s, 0, '{"admin_style":"","admin_language":"","language":"","editor":"","timezone":""}', 0, '', '', 1, ''
            )
        """
        valeurs = (nomComplet, pseudo, email, final, date_adhesion)

        logging.info("Création de l'utilisateur dans jos3_users")
        logging.info(
            f"Nom complet: {nomComplet}, Pseudo: {pseudo}, Email: {email}, Date d'adhésion: {date_adhesion}"
        )

        # Exécuter la requête avec les valeurs
        curseur.execute(requete_utilisateur_joomla, valeurs)
        
    except Exception as e:
        logging.error(
            "Erreur lors de l'insertion de l'utilisateur dans jos3_users : {}".format(
                str(e)
            )
        )
        raise

# Fonction de génération de la requête d'insertion dans jos3_user_usergroup_map
def usergroup_map(donnees, curseur):
    try:
        if not isinstance(donnees, dict):
            logging.error(
                f"Format de données invalide. Attendu : dictionnaire, Obtenu : {type(donnees)}"
            )
            raise ValueError(
                "Format de données invalide. Un dictionnaire était attendu."
            )

        # Extraction des informations du paiement
        info_payeur = donnees.get("payer", {})
        email = info_payeur.get("email", "")

        requete_usergroup_map = """INSERT INTO yourdatabase.jos3_user_usergroup_map (
                    user_id, 
                    group_id
                    ) SELECT id, 12 FROM yourdatabase.jos3_users WHERE email = %s;
                """

       # Exécuter la requête avec l'email comme valeur
        curseur.execute(requete_usergroup_map, (email,))
        logging.info("Attribution du groupe adhérent effectué avec succès !")

    except Exception as e:
        logging.error(
            "Erreur lors de la génération des requêtes SQL pour l'attribution du groupe adhérent : {}".format(
                str(e)
            )
        )
        raise

# Fonction pour récupérer le dernier ID inséré dans la table jos3_users
def dernier_id_inserer(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(id) FROM jos3_users")
        last_id = cursor.fetchone()[0]
        return last_id
    except Error as e:
        logging.error(f"Erreur lors de la récupération du dernier ID inséré : {e}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()

# Fonction de génération des requêtes SQL d'insertion dans jos3_comprofiler
def inserer_utilisateur_dans_jos3_comprofiler(donnees, curseur, connection):
    try:
        # Récupérer le dernier ID inséré dans jos3_users
        last_user_id = dernier_id_inserer(connection)
        user_ID = last_user_id

        # Logger la valeur de last_user_id
        logging.info(f"Dernier ID d'utilisateur inséré : {last_user_id}")

        if not isinstance(donnees, dict):
            logging.error(
                f"Format de données invalide. Attendu : dictionnaire, Obtenu : {type(donnees)}"
            )
            raise ValueError(
                "Format de données invalide. Un dictionnaire était attendu."
            )

        # Extraction des informations du paiement
        info_payeur = donnees.get("payer", {})
        firstname = info_payeur.get("firstName", "")
        lastname = info_payeur.get("lastName", "")
        nomComplet = f"{firstname} {lastname}"

        # Requête d'insertion dans jos3_comprofiler
        requete_insertion_jos3_comprofiler = """
            INSERT INTO yourdatabase.jos3_comprofiler (
                `id`,
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
                `cb_lienlinkedin`,
                `nom_complet`
            ) VALUES (
                %s, %s, %s, %s, 0, '0000-00-00 00:00:00', 0, '', 4, NULL, 1, 50, 1, 1, '0000-00-00 00:00:00', '', '', 0, NULL, NULL, NULL, 0, NULL, 0, '0000-00-00 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, %s
            )
        """
        valeurs = (user_ID, user_ID, firstname, lastname, nomComplet)

        logging.info("Création de l'utilisateur dans jos3_comprofiler")

        # Exécuter la requête avec les valeurs
        curseur.execute(requete_insertion_jos3_comprofiler, valeurs)

    except Exception as e:
        logging.error(
            "Erreur lors de l'insertion de l'utilisateur dans jos3_comprofiler : {}".format(
                str(e)
            )
        )
        raise

# Fonction principale du script
def main():
    connexion_joomla = None

    try:
        logging.info("Démarrage du script...")

        # Appel à la fonction pour charger les données JSON
        chemin_fichier_json = "./adherents_2024.json"
        adherents = charger_donnees_json(chemin_fichier_json)

        # Connexion à la base de données
        logging.info("Connexion à la base de données ...")
        connexion_joomla = connecter_mysql()
        logging.info("Connexion effectuée !")

        curseur_joomla = connexion_joomla.cursor()

        # Traitement des adhérents et insertion dans les tables Joomla
        for adherent in adherents:
            email_utilisateur = adherent.get("payer", {}).get("email", "")
            logging.info(
                f"Vérification de l'existence de l'utilisateur avec l'email : '{email_utilisateur}' dans les différentes tables..."
            )

            utilisateur_existe_jos3_users = utilisateur_existe_dans_joomla(
                email_utilisateur, curseur_joomla
            )

            # Traitement des cas d'existence de l'utilisateur dans les tables Joomla
            if utilisateur_existe_jos3_users:
                logging.info(
                    f"L'utilisateur avec l'email '{email_utilisateur}' existe dans la table jos3_users et jos3_comprofiler."
                )
            else:
                logging.info(
                    f"L'utilisateur avec l'email '{email_utilisateur}' n'existe pas dans la table jos3_comprofiler ni dans jos3_users."
                )
                inserer_utilisateur_dans_jos3_users(adherent, curseur_joomla)
                usergroup_map(adherent, curseur_joomla)
                inserer_utilisateur_dans_jos3_comprofiler(adherent, curseur_joomla, connexion_joomla)

        connexion_joomla.commit()  # Valider les modifications

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

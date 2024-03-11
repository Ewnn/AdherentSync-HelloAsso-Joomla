# [ENGLISH] HelloAsso-Joomla-Account-Creator

This automated Python script facilitates the creation and updating of member accounts on a Joomla site by synchronizing data with HelloAsso. It utilizes the HelloAsso APIs to retrieve member data and connects to the Joomla database to ensure smooth member management.

## Features

- **Automatic Creation:** Automatically generates member accounts on Joomla from HelloAsso data.
- **Continuous Update:** Synchronizes member information to maintain consistency between HelloAsso and Joomla.
- **Integrated Security:** Utilizes the HelloAsso API securely and manages automatic token refresh.
- **Flexible Configuration:** Easily modifiable settings to adapt to various membership scenarios.
- **Detailed Logging:** Provides detailed logs to track operations and detect potential errors.

## Prerequisites

- Python 3.x installed on the execution server.
- Access to HelloAsso APIs with necessary permissions.
- Self-hosted or tooling server to run the `get_members.py` script.
- VPS production server hosted at OVH

## Usage

1. **Setting up the Script on the Server:** Place the `get_members.py` file on a server that allows connections to HelloAsso APIs. This can be a self-hosted server or a tooling server.

2. **Configuration of HelloAsso APIs:** Modify the API credentials in the `get_members.py` script with your own credentials.

3. **Running the Script:** When running the `get_members.py` script, a JSON folder will be created containing a `.json` file with member information.

4. **Transferring Data to the OVH Server:**
   - Use the `membersOnProd.sh` script in the crontab to execute the Python file `get_members.py` and send the JSON folder's content to the OVH VPS via SSH.

5. **Configuration on the OVH VPS:**
   - Place the `add-members.py` file at the root of the OVH VPS.
   - Modify the information in the `connecter_mysql` function in the `add-members.py` file with the Joomla database connection details on the OVH VPS.

6. **Setting up Cron on the OVH VPS:**
   - Place the `cronPython.php` file on the OVH VPS.
   - Configure a cron job on the `cronPython.php` file to periodically execute the `add-members.py` script.

## Logging

Log files are saved in the `log/` directory with names such as `log_adding_members_YYYY-MM-DD_HH-MM-SS.log`.





# [FRENCH] HelloAsso-Joomla-Account-Creator

Ce script Python automatisé facilite la création et la mise à jour des comptes adhérents sur un site Joomla en synchronisant les données avec HelloAsso. Il utilise les API HelloAsso pour récupérer les données des adhérents et se connecte à la base de données Joomla pour assurer une gestion fluide des membres.

## Fonctionnalités

- **Création Automatique :** Génère automatiquement des comptes d'adhérents sur Joomla à partir des données HelloAsso.
- **Mise à Jour Continue :** Synchronise les informations des adhérents pour maintenir la cohérence entre HelloAsso et Joomla.
- **Sécurité Intégrée :** Utilise l'API HelloAsso de manière sécurisée et gère le rafraîchissement automatique du jeton.
- **Configuration Flexible :** Paramètres facilement modifiables pour s'adapter à divers scénarios d'adhésion.
- **Journalisation Détaillée :** Fournit des journaux détaillés pour suivre les opérations et détecter d'éventuelles erreurs.

## Prérequis

- Python 3.x installé sur le serveur d'exécution.
- Accès aux API HelloAsso avec les autorisations nécessaires.
- Serveur auto-hébergé ou d'outillage pour exécuter le script `get_members.py`.
- Serveur de production VPS hébergé chez OVH

## Utilisation

1. **Mise en Place du Script sur le Serveur :** Placez le fichier `get_members.py` sur un serveur qui autorise les connexions aux API HelloAsso. Cela peut être un serveur auto-hébergé ou un serveur d'outillage.

2. **Configuration des API HelloAsso :** Modifiez les informations d'identification de l'API HelloAsso dans le script `get_members.py` avec vos propres informations.

3. **Exécution du Script :** Lors de l'exécution du script `get_members.py`, un dossier JSON sera créé contenant un fichier `.json` avec les informations des adhérents.

4. **Transfert des Données vers le Serveur OVH :** Utilisez le script `membersOnProd.sh` dans la crontab pour exécuter le fichier Python `get_members.py` et envoyer le contenu du dossier JSON vers le VPS OVH via SSH.

5. **Configuration sur le VPS OVH :**
   - Placez le fichier `add-members.py` à la racine du VPS OVH.
   - Modifiez les informations de la fonction `connecter_mysql` dans le fichier `add-members.py` avec les informations de connexion à la base de données Joomla sur le VPS OVH.

6. **Configuration de la Cron sur le VPS OVH :**
   - Placez le fichier `cronPython.php` sur le VPS OVH.
   - Configurez une tâche cron sur le fichier `cronPython.php` pour exécuter périodiquement le script `add-members.py`.

## Journalisation

Les fichiers journaux sont enregistrés dans le répertoire `log/` avec des noms tels que `log_ajout_adherents_YYYY-MM-DD_HH-MM-SS.log`.

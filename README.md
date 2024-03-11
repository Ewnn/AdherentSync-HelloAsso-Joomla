# [English] HelloAsso-Joomla-Account-Creator

This automated Python script facilitates the creation and updating of member accounts on a Joomla site by synchronizing data with HelloAsso. It utilizes HelloAsso APIs and connects to the Joomla database to ensure smooth member management.

## Features

- **Automatic Creation:** Automatically generates member accounts on Joomla based on HelloAsso data.
- **Continuous Update:** Synchronizes member information to maintain consistency between HelloAsso and Joomla.
- **Integrated Security:** Uses HelloAsso API securely and manages automatic token refresh.
- **Flexible Configuration:** Easily modifiable parameters to adapt to various membership scenarios.
- **Detailed Logging:** Provides detailed logs to track operations and detect potential errors.

## Prerequisites

- Python 3.x installed on the execution server.
- Access to HelloAsso and Joomla APIs with necessary permissions.

## Usage

1. **Install Dependencies:** Before using the script, make sure to install the required dependencies by running the following command in the script directory:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration:** Replace the placeholders with your HelloAsso and Joomla credentials.

3. **Generate SQL Queries:** The script checks the presence of each member in the Joomla database. It then generates insertion or update queries based on this check. These queries are stored in an SQL file (`insertion_and_update_queries.sql`).

   **Note:** You can manually execute this SQL file on your server to bypass shared server restrictions. If necessary, the script can be modified to directly execute these SQL queries.

4. **Periodic Execution:** Run the script periodically to maintain synchronization.

## Logging

Log files are saved in the `log/` directory with names such as `log_add_members_YYYY-MM-DD_HH-MM-SS.log`.





# [FRENCH] HelloAsso-Joomla-Account-Creator

Ce script Python automatisé facilite la création et la mise à jour des comptes adhérents sur un site Joomla en synchronisant les données avec HelloAsso. Il utilise les API HelloAsso et se connecte à la base de données Joomla pour assurer une gestion fluide des membres.

## Fonctionnalités

- **Création Automatique :** Génère automatiquement des comptes d'adhérents sur Joomla à partir des données HelloAsso.
- **Mise à Jour Continue :** Synchronise les informations des adhérents pour maintenir la cohérence entre HelloAsso et Joomla.
- **Sécurité Intégrée :** Utilise l'API HelloAsso de manière sécurisée et gère le rafraîchissement automatique du jeton.
- **Configuration Flexible :** Paramètres facilement modifiables pour s'adapter à divers scénarios d'adhésion.
- **Journalisation Détaillée :** Fournit des journaux détaillés pour suivre les opérations et détecter d'éventuelles erreurs.

## Prérequis

- Python 3.x installé sur le serveur d'exécution.
- Accès aux API HelloAsso et Joomla avec les autorisations nécessaires.

## Utilisation

1. **Installation des Dépendances :** Avant d'utiliser le script, assurez-vous d'installer les dépendances nécessaires en exécutant la commande suivante dans le répertoire du script :
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration :** Remplacez les placeholders avec vos identifiants HelloAsso et Joomla.

3. **Génération des Requêtes SQL :** Le script vérifie la présence de chaque adhérent dans la base de données Joomla. Ensuite, il génère des requêtes d'insertion ou de mise à jour en fonction de cette vérification. Ces requêtes sont stockées dans un fichier SQL (`requetes_insertion_et_mise_a_jour.sql`).

   **Remarque :** Vous pouvez exécuter manuellement ce fichier SQL sur votre serveur pour contourner les restrictions des serveurs mutualisés. Si nécessaire, le script peut être modifié pour exécuter directement ces requêtes SQL.

4. **Exécution Périodique :** Lancez le script périodiquement pour maintenir la synchronisation.

## Journalisation

Les fichiers journaux sont enregistrés dans le répertoire `log/` avec des noms tels que `log_ajout_adherents_YYYY-MM-DD_HH-MM-SS.log`.

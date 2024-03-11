# HelloAsso-Joomla-Account-Creator

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

Les fichiers journaux sont enregistrés dans le répertoire `Log/` avec des noms tels que `log_ajout_adherents_YYYY-MM-DD_HH-MM-SS.log`.
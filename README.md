# download-master-yt
Script de telechargement de liens Youtube
Download Master-YT V1.1 🎥🎵
Un utilitaire tout-en-un pour le téléchargement YouTube.


Download Master-YT est une solution graphique complète développée en Python pour extraire du contenu depuis YouTube. L'outil est conçu pour être autonome et ne nécessite aucune configuration complexe grâce à l'intégration directe des moteurs de traitement dans le dossier racine.

✨ Points forts

Gestion de file d'attente : Ajoutez autant de liens que nécessaire pour un téléchargement automatisé en série.

Flexibilité des formats :


[FULL] : Vidéo et audio fusionnés en MP4 à la résolution maximale.


[720p] : Vidéo HD optimisée pour réduire le poids du fichier.


[MP3] : Extraction audio pure en haute fidélité.


Diagnostic Intégré : Un système de vérification interne contrôle la présence de yt-dlp.exe, ffmpeg.exe et la validité de votre connexion internet.

Expérience Utilisateur :

Barre de progression dynamique avec calcul du pourcentage en temps réel.

Console de logs en direct pour suivre chaque étape du processus.

Option de vidage automatique de la liste après un téléchargement réussi.

🔍 Fonctionnement technique
L'application repose sur une synergie entre trois composants :


L'Interface (Python/Tkinter) : Gère l'interaction utilisateur et l'affichage.


Le Moteur (yt-dlp) : Gère la communication avec les serveurs YouTube et le téléchargement des flux.


Le Convertisseur (FFmpeg) : Réalise la conversion finale en MP3 ou la fusion (muxing) des flux vidéo et audio haute définition.

🛠️ Installation et Prérequis
1. Téléchargement
Puisque le dépôt inclut déjà les exécutables nécessaires, il vous suffit de cloner le projet :

Bash
git clone https://github.com/Popov2026/download-master-yt.git
cd download-master-yt
2. Dépendance Python
L'application utilise uniquement les bibliothèques standards de Python, aucune installation via pip n'est requise.

3. Fichiers inclus dans le dossier
Pour que l'outil fonctionne, assurez-vous que ces fichiers sont présents dans le même dossier:

Download_Master-YT_V1.1.pyw

yt-dlp.exe

ffmpeg.exe

🚀 Guide d'utilisation
Lancement : Exécutez Download_Master-YT_V1.1.pyw.


Ajout : Collez votre URL et cliquez sur 📋 Coller ou ✚ Ajouter.

Réglages :

Sélectionnez votre format préféré dans la liste déroulante.

Choisissez le dossier de destination (par défaut : C:\youtube).


Vérification : Un clic sur 🔍 Diag permet de confirmer que les outils sont bien détectés.


Action : Cliquez sur 🚀 LANCER LE TÉLÉCHARGEMENT.

📁 Structure du projet

Download_Master-YT_V1.1.pyw : Code source de l'interface graphique.


yt-dlp.exe : Moteur de téléchargement.


ffmpeg.exe : Processeur de conversion multimédia.

⚖️ Licence & Responsabilité
Cet outil est destiné à un usage personnel et pédagogique uniquement. L'utilisateur est responsable du respect des droits d'auteur et des conditions d'utilisation de la plateforme YouTube.

Optimisé pour Windows par Popov © 2026

# Programme controle Robot

Le cerveau central du robot est la RASPI 4.
Pour y acceder se connecter au réseau local et acceder au PI:
- User: tpuser
- IP: 192.168.0.114

## Fonctionnement

Tout est gérer en Python
1. Initialisation des PINS GPIO, ....
2. Lancement des Threads LIDAR et ROUTINE
   - LIDAR: Analyse des data du LIDAR afin de gérer l'évitement.
   - ROUTINE: Les routines sont codés dans notre propre language. Le fichier est analyser, parser puis les instruction UART sont envoyés aux moteurs et actionneurs.

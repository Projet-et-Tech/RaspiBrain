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


- - -

## Log

```
python3 main.py --test 1
[22:24:24] CRITICAL main.py:143: PROGRAMME DE TEST
[22:24:24] DEBUG    main.py:149: Initialisation des interfaces UART
[22:24:24] DEBUG    UART.py:16: Port série /dev/ttyAMA5 initialisé avec succès à 115200 bauds.
[22:24:24] DEBUG    UART.py:16: Port série /dev/serial0 initialisé avec succès à 115200 bauds.
[22:24:24] DEBUG    main.py:155: Creation and strating of Threads
######################################
ok
[22:24:24] CRITICAL main.py:100: ROUTINE_v1_JAUNE.txt
[22:24:24] INFO     Routine.py:250: [COMMANDE](0 / 22) - LIDAR ON
[22:24:24] INFO     Routine.py:250: [COMMANDE](1 / 22) - ATTENTE_ACK TIRETTE
[22:24:24] INFO     Routine.py:250: [COMMANDE](2 / 22) - RESET_CM
[22:24:24] INFO     Routine.py:250: [COMMANDE](3 / 22) - ATTENTE_ACK MOTEUR
[22:24:24] INFO     Routine.py:250: [COMMANDE](4 / 22) - SETPOS -250 -1250 0
[22:24:24] INFO     Routine.py:250: [COMMANDE](5 / 22) - ATTENTE_ACK MOTEUR
[22:24:24] INFO     Routine.py:250: [COMMANDE](6 / 22) - ACTIONNEUR BANIERE SERVOMOTEUR BOUGER 0 90
[22:24:24] INFO     Routine.py:250: [COMMANDE](7 / 22) - ATTENTE_ACK ACTIONNEUR
[22:24:24] INFO     Routine.py:250: [COMMANDE](8 / 22) - DEPLACEMENT -450 -1250 0
[22:24:24] INFO     Routine.py:250: [COMMANDE](9 / 22) - ATTENTE_ACK MOTEUR
[22:24:24] INFO     Routine.py:250: [COMMANDE](10 / 22) - ACTIONNEUR BANIERE SERVOMOTEUR BOUGER 0 0
[22:24:24] INFO     Routine.py:250: [COMMANDE](11 / 22) - ATTENTE_ACK ACTIONNEUR
[22:24:24] INFO     Routine.py:250: [COMMANDE](12 / 22) - DEPLACEMENT -250 -1250 0
[22:24:24] INFO     Routine.py:250: [COMMANDE](13 / 22) - ATTENTE_ACK MOTEUR
[22:24:24] INFO     Routine.py:250: [COMMANDE](14 / 22) - DEPLACEMENT -600 -1250 0
[22:24:24] INFO     Routine.py:250: [COMMANDE](15 / 22) - ATTENTE_ACK MOTEUR
[22:24:24] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:24] INFO     Routine.py:250: [COMMANDE](16 / 22) - DEPLACEMENT -600 -2150 0
[22:24:24] INFO     Routine.py:250: [COMMANDE](17 / 22) - ATTENTE_ACK MOTEUR
[22:24:24] INFO     Routine.py:250: [COMMANDE](18 / 22) - WAITFOREND
[22:24:24] INFO     Routine.py:250: [COMMANDE](19 / 22) - DEPLACEMENT -1800 -2150 0
[22:24:24] INFO     Routine.py:250: [COMMANDE](20 / 22) - ATTENTE_ACK MOTEUR
[22:24:24] INFO     Routine.py:250: [COMMANDE](21 / 22) - ATTENTE_ACK TIRETTE
[22:24:24] DEBUG    main.py:103: 22 commandes chargées
[22:24:24] INFO     main.py:124: Exécution de la routine ...
[22:24:24] DEBUG    Routine.py:412: Traitement commande (1/22) - LIDAR ON
[22:24:24] INFO     Routine.py:493: Swithcing LIDAR ON
[22:24:24] DEBUG    Routine.py:412: Traitement commande (2/22) - ATTENTE_ACK TIRETTE
[22:24:24] DEBUG    Routine.py:451: ATTENTE_ACK Detectée - En attente ...
[22:24:27] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:28] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:31] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:31] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:34] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:34] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:36] DEBUG    main.py:62: Interruption Tirette reçu
[22:24:36] DEBUG    Routine.py:302: FLAG ACK - TIRETTE reçu
[22:24:36] CRITICAL Routine.py:457: Routine started at: 1748640276.7208114
[22:24:36] DEBUG    Routine.py:412: Traitement commande (3/22) - RESET_CM
[22:24:36] DEBUG    Routine.py:412: Traitement commande (4/22) - ATTENTE_ACK MOTEUR
[22:24:36] DEBUG    Routine.py:451: ATTENTE_ACK Detectée - En attente ...
[22:24:37] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:37] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:40] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:40] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:43] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:43] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:46] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:46] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:49] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:49] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:52] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:53] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:56] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:56] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:24:59] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:24:59] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:25:02] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:25:02] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:25:05] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:25:05] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:25:08] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:25:08] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:25:11] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:25:11] INFO     lib_lidar.py:276: Debut mesure LIDAR
[22:25:14] ERROR    lib_lidar.py:307: Erreur: Descriptor length mismatch
[22:25:14] INFO     lib_lidar.py:276: Debut mesure LIDAR
^C[22:25:14] WARNING  main.py:169: Arrêt demandé par l'utilisateur
[22:25:14] DEBUG    main.py:172: Nettoyage et arrêt des threads
```

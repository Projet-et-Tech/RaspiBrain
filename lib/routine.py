import re
import time
import traceback

from lib.UART import envoie_deplacement

from lib.logger_manager import LoggerManager

logger = LoggerManager("main").get_logger()

################################
# GLOBAL VARIABLES
################################

global flag_ACK
global flag_STOP
global stop_handled
global match_timer

flag_ACK = 0
flag_STOP = 0
stop_handled = True
points = 0
DEBUG = 1
match_timer = 0
lidar_on = False


def analyser_routine_complete(chemin_fichier):
    """
    Analyse complète du fichier Routine.txt et détection de tous les types de commandes

    Args:
        chemin_fichier (str): Chemin vers le fichier routine.txt

    Returns:
        list: Liste ordonnée de toutes les commandes avec leur type et détails
    """
    commandes = []

    # Patterns regex pour les différents types de commandes
    patterns = {
        #'DEPLACEMENT': re.compile(r'^DEPLACEMENT\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$'),
        #'DEPLACEMENT_VITESSE': re.compile(r'^DEPLACEMENT_VITESSE\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$'), # Déplacement avec une vitesse MAX
        #'DEPLACEMENT_RELATIF': re.compile(r'^DEPLACEMENT_RELATIF\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$'), # Déplacement relatif par rapport à la position actuelle du robot
        'DEPLACEMENT': re.compile(r'^DEPLACEMENT\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)$'),
        'SETPOS': re.compile(r'^SETPOS\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)$'),
        'DEPLACEMENT_VITESSE': re.compile(r'^DEPLACEMENT_VITESSE\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)$'),  # Déplacement avec une vitesse MAX
        'DEPLACEMENT_RELATIF': re.compile(r'^DEPLACEMENT_RELATIF\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)$'),  # Déplacement relatif par rapport à la position actuelle du robot
        'ACTIONNEUR': re.compile(
            r'^ACTIONNEUR\s+'
            r'(?P<module>\w+)\s+'
            r'(?P<type_actionneur>\w+)\s+'
            r'(?P<action>\w+)'
            r'(?:\s+(?P<speed>\d+))?'
            r'(?:\s+(?P<valeur>\d+))?$'
        ),
        'ATTENTE_ACK': re.compile(
            r'^\s*ATTENTE_ACK\s+(?P<attente_ack>\w+)\s*$', re.IGNORECASE
        ),
        'DELAI': re.compile(
            r'^\s*DELAI\s+(?P<temps_delai>\w+)\s*$', re.IGNORECASE
        ),
        'ADDPOINT': re.compile(
            r'^\s*ADDPOINT\s+(?P<nb_points>\w+)\s*$', re.IGNORECASE
        ),
        'LIDAR': re.compile(
            r'^\s*LIDAR\s+(?P<state>\w+)\s*$', re.IGNORECASE
        ),
    }

    try:
        with open(chemin_fichier, 'r') as fichier:
            for ligne_num, ligne in enumerate(fichier, 1):
                ligne = ligne.strip()
                if not ligne:  # Ignorer les lignes vides
                    continue

                # Ignorer les commentaires
                if "//" in ligne or "#" in ligne:
                    continue

                # Détection du type de commande
                if ligne.startswith('DEPLACEMENT'):
                    match = patterns['DEPLACEMENT'].match(ligne)
                    if match:
                        commandes.append({
                            'type': 'DEPLACEMENT',
                            'x': int(match.group(1)),
                            'y': int(match.group(2)),
                            'theta': int(match.group(3)),
                            'ligne': ligne_num,
                            'raw': ligne,
                        })
                    else:
                        logger.error(f"Format DEPLACEMENT ligne {ligne_num}: {ligne}")

                elif ligne.startswith('SETPOS'):
                    match = patterns['SETPOS'].match(ligne)
                    if match:
                        commandes.append({
                            'type': 'SETPOS',
                            'x': int(match.group(1)),
                            'y': int(match.group(2)),
                            'theta': int(match.group(3)),
                            'ligne': ligne_num,
                            'raw': ligne,
                        })
                    else:
                        logger.error(f"Format SETPOS ligne {ligne_num}: {ligne}")

                elif ligne.startswith('DEPLACEMENT_VITESSE'):
                    match = patterns['DEPLACEMENT_VITESSE'].match(ligne)
                    if match:
                        commandes.append({
                            'type': 'DEPLACEMENT_VITESSE',
                            'x': int(match.group(1)),
                            'y': int(match.group(2)),
                            'theta': int(match.group(3)),
                            'speed': int(match.group(4)),
                            'ligne': ligne_num,
                            'raw': ligne,
                        })
                    else:
                        logger.error(f"Format DEPLACEMENT_VITESSE ligne {ligne_num}: {ligne}")

                elif ligne.startswith('DEPLACEMENT_RELATIF'):
                    match = patterns['DEPLACEMENT_RELATIF'].match(ligne)
                    if match:
                        commandes.append({
                            'type': 'DEPLACEMENT_RELATIF',
                            'x': int(match.group(1)),
                            'y': int(match.group(2)),
                            'theta': int(match.group(3)),
                            'ligne': ligne_num,
                            'raw': ligne,
                        })
                    else:
                        logger.error(f"Format DEPLACEMENT_RELATIF ligne {ligne_num}: {ligne}")

                elif ligne.startswith('ACTIONNEUR'):
                    match = patterns['ACTIONNEUR'].match(ligne)
                    if match:
                        cmd = match.groupdict()
                        cmd['type'] = 'ACTIONNEUR'
                        cmd['raw'] = ligne
                        cmd['ligne'] = ligne_num
                        if cmd.get('speed') != None:
                            cmd['speed'] = int(cmd['speed'])
                        if cmd.get('valeur') != None:
                            cmd['valeur'] = int(cmd['valeur'])
                        commandes.append(cmd)
                    else:
                        logger.error(f"Format ACTIONNEUR ligne {ligne_num}: {ligne}")

                elif ligne.startswith('ATTENTE_ACK'):
                    match = patterns['ATTENTE_ACK'].match(ligne)
                    if match:
                        cmd = match.groupdict()
                        cmd['type'] = 'ATTENTE_ACK'
                        cmd['raw'] = ligne
                        cmd['ligne'] = ligne_num
                        commandes.append(cmd)
                    else:
                        logger.error(f"Format ATTENTE_ACK ligne {ligne_num}: {ligne}")

                elif ligne.startswith('DELAI'):
                    match = patterns['DELAI'].match(ligne)
                    if match:
                        cmd = match.groupdict()
                        cmd['type'] = 'DELAI'
                        cmd['raw'] = ligne
                        cmd['ligne'] = ligne_num
                        commandes.append(cmd)
                    else:
                        logger.error(f"Format DELAI ligne {ligne_num}: {ligne}")

                elif ligne.startswith('ADDPOINT'):
                    match = patterns['ADDPOINT'].match(ligne)
                    if match:
                        cmd = match.groupdict()
                        cmd['type'] = 'ADDPOINT'
                        cmd['raw'] = ligne
                        cmd['ligne'] = ligne_num
                        commandes.append(cmd)
                    else:
                        logger.error(f"Format DELAI ligne {ligne_num}: {ligne}")

                elif ligne.startswith('LIDAR'):
                    match = patterns['LIDAR'].match(ligne)
                    if match:
                        cmd = match.groupdict()
                        cmd['type'] = 'LIDAR'
                        cmd['raw'] = ligne
                        cmd['ligne'] = ligne_num
                        commandes.append(cmd)
                    else:
                        logger.error(f"Format DELAI ligne {ligne_num}: {ligne}")

                # ===================================================== #
                # OTHER ACTIONS
                # ===================================================== #
                elif ligne.startswith('EXIT'):
                    break
                elif ligne.startswith('WAITFOREND'):
                    cmd = {}
                    cmd['type'] = 'WAITFOREND'
                    cmd['raw'] = ligne
                    cmd['ligne'] = ligne_num
                    commandes.append(cmd)
                elif ligne.startswith('RESET_CM'):
                    cmd = {}
                    cmd['type'] = 'RESET_CM'
                    cmd['raw'] = ligne
                    cmd['ligne'] = ligne_num
                    commandes.append(cmd)

                elif ligne.startswith('RESET_CA'):
                    cmd = {}
                    cmd['type'] = 'RESET_CA'
                    cmd['raw'] = ligne
                    cmd['ligne'] = ligne_num
                    commandes.append(cmd)

                elif ligne.startswith('READ_POS'):
                    cmd = {}
                    cmd['type'] = 'READ_POS'
                    cmd['raw'] = ligne
                    cmd['ligne'] = ligne_num
                    commandes.append(cmd)
                else:
                    pass
                    """
                    commandes.append({
                        'type': 'inconnu',
                        'commande': ligne,
                        'ligne': ligne_num
                    })
                    """

                # ===================================================== #
                # ===================================================== #

    except FileNotFoundError:
        logger.error(f"Fichier {chemin_fichier} introuvable")
        return []
    except Exception as e:
        logger.error(f"Lecture fichier: {str(e)}")
        return []

    for i, cmd in enumerate(commandes):
        logger.info(f"[COMMANDE]({i} / {len(commandes)}) - {cmd['raw']}")

    return commandes


def Compute_Attente_ACK(cmd):
    global flag_ACK
    """
	Traduit une commande d'attente et patiente jusqu'à reception de l'ack

	Args:
		cmd: Dictionnaire qui contient
		- L'ACK qui est attendu (qui vient de la carte actionneur ou moteur) : 'ACTIONNEUR, 'MOTEUR' 'TIRETTE'
    """
    # Dictionnaire pour attente_ack :
    ATTENTE_ACK = {
        'MOTEUR': 1,
        'ACTIONNEUR': 2,
        'TIRETTE': 3,
        'TOUS': 4,
    }

    try:
        # Conversion des valeurs textuelles en codes numériques
        attente_ack = ATTENTE_ACK.get(cmd['attente_ack'])
        if attente_ack is None:
            raise ValueError(f"attente_ack inconnu: {cmd['attente_ack']}")

        if attente_ack == 4:
            ctrl_sum = 0
            while True:
                time.sleep(100)
                if (flag_ACK == 1 and ctrl_sum in [0, 2]):
                    ctrl_sum += 1
                    flag_ACK = 0
                    logger.debug("FLAG ACK MOTEUR")
                    if ctrl_sum != 3:
                        logger.debug("Attente ACK ACTIONNEUR")
                elif (flag_ACK == 2 and ctrl_sum in [0, 1]):
                    ctrl_sum += 2
                    flag_ACK = 0
                    logger.debug("FLAG ACK ACTIONNNEUR")
                    if ctrl_sum != 3:
                        logger.debug("Attente ACK MOTEUR")

                if ctrl_sum == 3:
                    break
        else:
            #On patiente tant que l'interruption indiquant l'ack est pas arrivée
            while(flag_ACK != attente_ack):
                time.sleep(0.1)
                pass
            logger.debug(f"FLAG ACK - {cmd['attente_ack']} reçu")
            flag_ACK = 0
    except KeyError as ke:
        logger.error(f"Champ manquant dans la commande - {ke}")
    except ValueError as ve:
        logger.error(f"{ve}")
    except Exception as e:
        logger.error(f"{e}")

    return False


def Compute_Actionneur(ser, cmd):
    """
    Traduit une commande sémantique en commande numérique et l'envoie à l'actionneur

    Args:
        ser: Objet Serial pour la communication UART
        cmd: Dictionnaire de commande contenant:
            - module: 'ASCENSEUR', 'PETITE_PINCE', 'FOURCHE', 'BANIERE'
            - action: 'INITIALISATION', 'OUVRIR', 'FERMER', 'BOUGER'
            - type_actionneur: 'TOUS', 'STEPPER', 'SERVOMOTEUR', 'DYNAMIXEL'
            - valeur: optionnel (0-255)

    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    # Dictionnaires de correspondance pour une meilleure maintenabilité
    MODULES = {
        'ASCENSEUR': 0,
        'PETITE_PINCE': 1,
        'FOURCHE': 2,
        'BANIERE': 3
    }

    ACTIONS = {
        'INITIALISATION': 0,
        'OUVRIR': 2,
        'FERMER': 3,
        'BOUGER': 1
    }

    TYPES = {
        'TOUS': 3,
        'STEPPER': 0,
        'SERVOMOTEUR': 1,
        'DYNAMIXEL': 2
    }
    try:
        # Conversion des valeurs textuelles en codes numériques
        module = MODULES.get(cmd['module'])
        if module is None:
            raise ValueError(f"[ERREUR] - Module inconnu: {cmd['module']}")

        action = ACTIONS.get(cmd['action'])
        if action is None:
            raise ValueError(f"[ERREUR] - Action inconnue: {cmd['action']}")

        type_actionneur = TYPES.get(cmd['type_actionneur'])
        if type_actionneur is None:
            raise ValueError(f"[ERREUR] - Type d'actionneur inconnu: {cmd['type_actionneur']}")



        speed = cmd.get('speed',0)
        speed = 0 if speed == None else speed
        if not 0 <= speed <=1:
            raise ValueError("[ERREUR] - Valeur de speed entre 0 et 1")


        # Gestion de la valeur par défaut
        valeur = cmd.get('valeur', 0)
        valeur = 0 if valeur == None else valeur

        # Validation de la valeur
        if not 0 <= valeur <= 1024:
            raise ValueError("[ERREUR] - La valeur doit être entre 0 et 255")

        # Envoi de la commande
        return envoie_actionneur(ser, module, type_actionneur, action, valeur, speed)



    except KeyError as ke:
        logger.error(f"Champ manquant dans la commande - {ke}")
    except ValueError as ve:
        logger.error(f"{ve}")
    except Exception as e:
        logger.error(f"{e}")

    return False



#Implanter les deux UART différents ==> Fait, a tester
def routine(toutes_commandes, serial1, serial2, debug=False):
    global stop_handled
    """
    Exécute une routine complète à partir d'un fichier de configuration

    Args:
        serial1: Objet Serial initialisé pour la communication UART Moteur
        serial2 : Objet Serial initialisé pour la communication UART Acionneur
        debug: Booléen pour activer les messages de débogage (défaut: False)
    """
    try:
        # 2. Exécution des commandes
        for idx, cmd in enumerate(toutes_commandes, 1):
            try:
                if debug:
                    logger.debug(f"Traitement commande ({idx}/{len(toutes_commandes)}) - {cmd['raw']}")

                if cmd['type'] == "DEPLACEMENT":
                    if debug:
                        logger.debug("Déplacement détecté")

                    envoie_deplacement(serial1, cmd['x'], cmd['y'], cmd['theta'])  # timeout=0
                    logger.info("DEPLACEMENT")

                elif cmd['type'] == "ACTIONNEUR":
                    if debug:
                        logger.debug("Actionneur détecté")

                    Compute_Actionneur(serial2, cmd)
                    logger.info("ACTIONNEUR")

                elif cmd['type'] == "DEPLACEMENT_VITESSE":
                    if debug:
                        logger.debug("Déplacement vitesse détecté")

                    envoie_deplacement(serial1, cmd['x'], cmd['y'], cmd['theta'], cmd["speed"])  # timeout=0
                    logger.info("DEPLACEMENT_VITESSE")

                elif cmd['type'] == "DEPLACEMENT_RELATIF":
                    if debug:
                        logger.debug("Déplacement relatif détecté")

                    envoie_deplacement(serial1, cmd['x'], cmd['y'], cmd['theta'], 0, False)  # timeout=0
                    logger.info("DEPLACEMENT_RELATIF")

                elif cmd['type'] == "SETPOS":
                    if debug:
                        logger.debug("Mise à jour de la position détecté")

                    envoie_deplacement(serial1, cmd['x'], cmd['y'], cmd['theta'], set_position=True)  # timeout=0
                    logger.info("SETPOS")

                elif cmd['type'] == "ATTENTE_ACK":
                    if debug:
                        logger.debug("ATTENTE_ACK Detectée - En attente ...")

                    Compute_Attente_ACK(cmd)

                    if "TIRETTE" in cmd['raw']:
                        match_timer = time.time()
                        logger.fatal(f"Routine started at: {match_timer}")

                    last_cmd = toutes_commandes[idx-2]

                    # Only resend for movement commands
                    if last_cmd['type'] not in ["DEPLACEMENT", "DEPLACEMENT_VITESSE"]:
                        continue

                    while stop_handled == False and idx != 1:
                        logger.info("ATTENTE_ACK - ACK STOP")
                        logger.debug("On attend qu'il n'y ait plus d'obstacle")

                        # On attend qu'il n'y ait plus d'obstacle après N scans du LIDAR
                        while flag_STOP != 0:
                            pass

                        logger.warn("RESUME_CM command envoyé")
                        envoie_RESUME_CM(serial1)

                        # Stop handled
                        stop_handled = True
                        logger.info("ATTENTE_ACK fin déplacement")
                        Compute_Attente_ACK(toutes_commandes[idx-1])

                # On attend x secondes (can be a float)
                elif cmd['type'] == "DELAI":
                    logger.info(f"Waiting {cmd['temps_delai']} seconds")
                    time.sleep(float(cmd['temps_delai']))

                # On ajoute N points au compteur de points
                elif cmd['type'] == "ADDPOINT":
                    logger.info(f"Adding {cmd['nb_points']} points")
                    points += int(cmd['nb_points'])

                # On ACTIVE / DESACTIVE le LIDAR
                elif cmd['type'] == "LIDAR":
                    logger.info(f"Swithcing LIDAR {cmd['state']}")
                    if cmd['state'] == 'ON':
                        lidar_on = True
                    elif cmd['state'] == 'OFF':
                        lidar_on = False

                elif cmd['type'] == "RESET_CM":
                    envoie_RESET_CM(serial1)

                elif cmd['type'] == "RESET_CA":
                    # TODO:
                    pass

                elif cmd['type'] == "READ_POS":
                    # TODO:
                    pass

                elif cmd['type'] == "WAITFOREND":
                    logger.info("WAITFOREND")
                    logger.info(f"Waiting for {95 - (time.time() - match_timer)} seconds")
                    while time.time() - match_timer <= 90:
                        time.sleep(0.1)

                    # TODO: Do something

            except KeyError as ke:
                logger.error(f"Champ manquant dans la commande {idx} - {ke}")
                if debug:
                    traceback.print_exc()
            except ValueError as ve:
                logger.error(f"{idx}: {ve}")
            except Exception as cmd_error:
                logger.error(f"{idx}: {cmd_error}")
                if debug:
                    traceback.print_exc()

    except FileNotFoundError:
        logger.error("Fichier Routine.txt introuvable")
    except json.JSONDecodeError:
        logger.error("Fichier Routine.txt mal formaté")
    except Exception as main_error:
        logger.error(f"{main_error}")
        if debug:
            traceback.print_exc()
    finally:
        if debug:
            logger.debug("Routine terminée !")

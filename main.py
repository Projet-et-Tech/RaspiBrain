import sys
import time
import threading
import queue
import RPi.GPIO as GPIO

# PIPOU

from UART import init_uart, envoie_deplacement, envoie_actionneur
from lib_lidar import LIDAR_mesurement
import Routine
from settings import DISTANCE_LIDAR_TEST

from logger_manager import LoggerManager

logger = LoggerManager("main").get_logger()


#################################################
# CONSTANTES
#################################################

VERBOSE = False
IRQPIN_MOTEUR = 24
IRQPIN_ACTIONNEUR = 25
IRQPIN_TIRETTE = 7
PIN_CHOIX_EQUIPE = 17
ROUTINE_FILE = "ROUTINE_v1_JAUNE.txt"

# Queue pour échanger des données entre threads
lidar_data_queue = queue.Queue()
stop_event = threading.Event()

#################################################
# FONCTIONS
#################################################

def run_lidar(serial_m):
    while not stop_event.is_set():
        try:
            # Récupération des données LIDAR
            if len(sys.argv) > 1:
                if sys.argv[1] == '--test':
                    LIDAR_mesurement(serial_m, DITANCE_LIDAR_TEST)
            else:
                LIDAR_mesurement(serial_m)
            # Wait before restarting
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"{e}")
            break

def actionneur_callback(channel):
	Routine.flag_ACK = 2
	logger.debug("Interruption Actionneur reçu")

def moteur_callback(channel):
	Routine.flag_ACK = 1
	logger.debug("Interruption Moteur reçu")

def tirette_callback(channel):
	Routine.flag_ACK = 3
	logger.debug("Interruption Tirette reçu")


def run_routine(serial_m, serial_a, debug=1):
    # Initialisation des pin en Interruption METTRE PULL DOWN SINON CA CRASH
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IRQPIN_ACTIONNEUR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(IRQPIN_MOTEUR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(IRQPIN_TIRETTE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIN_CHOIX_EQUIPE, GPIO.IN)
    GPIO.add_event_detect(IRQPIN_ACTIONNEUR, GPIO.FALLING, callback=actionneur_callback, bouncetime=200)
    GPIO.add_event_detect(IRQPIN_MOTEUR, GPIO.FALLING, callback=moteur_callback, bouncetime=200)
    GPIO.add_event_detect(IRQPIN_TIRETTE, GPIO.FALLING, callback=tirette_callback, bouncetime=200)

    try:
        # Lecture du PIN pour le choix de l'équipe
        # JUMPER HIGH (3.3V / 5V) => JAUNE
        # JUMPER LOW  (GND)  => BLEU
        if len(sys.argv) > 1:
            if sys.argv[1] == '--test':
                ROUTINE_FILE = f"ROUTINE_v{int(sys.argv[2])}_JAUNE.txt"
        else:
            VERSION_ROUTINE = 4
            if VERSION_ROUTINE not in [0, 1, 2]:
                VERSION_ROUTINE = 1

            if GPIO.input(PIN_CHOIX_EQUIPE):
                logger.info("Choix équipe JAUNE !")
                VERSION_ROUTINE = 5
                ROUTINE_FILE = f"ROUTINE_v{VERSION_ROUTINE}_JAUNE.txt"
            else:
                logger.info("Choix équipe BLEU !")
                VERSION_ROUTINE = 5
                ROUTINE_FILE = f"ROUTINE_v{VERSION_ROUTINE}_BLEU.txt"

        # 1. Lecture du fichier de routine
        logger.fatal(f"{ROUTINE_FILE}")
        toutes_commandes = Routine.analyser_routine_complete("routines/" + ROUTINE_FILE)
        if debug:
            logger.debug(f"{len(toutes_commandes)} commandes chargées")

        
        # # # if len(sys.argv) == 1:
        # # #     is_ack = False
        # # #     for cmd in toutes_commandes:
        # # #         if "ATTENTE_ACK TIRETTE" in cmd['raw']:
        # # #             is_ack = True
        # # #             break

        # # #     if is_ack == False:
        # # #         toutes_commandes.insert(0,
        # # #             {
        # # #                 'type': "ATTENTE_ACK",
        # # #                 'attente_ack': "TIRETTE"
        # # #             }
        # # #         )
        

        while not stop_event.is_set():
            # Votre routine principale
            logger.info("Exécution de la routine ...")
            Routine.routine(toutes_commandes, serial_m, serial_a, True)
            time.sleep(0.1)  # Délai entre les commandes

    except Exception as e:
        logger.error(f"{e}")
    finally:
        if serial_moteur:
            serial_moteur.close()
        if serial_actionneur:
            serial_actionneur.close()

###########################################################
# MAIN
###########################################################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            logger.fatal("PROGRAMME DE TEST")
    else:
        logger.debug("PROGRAMME DE MATCH")

    try :
        # Initialisation des UART
        logger.debug("Initialisation des interfaces UART")

        # UART1 utiliser pour le moteur
        serial_moteur = init_uart('/dev/ttyAMA5', 115200, 1, Routine.DEBUG)
        serial_actionneur = init_uart('/dev/serial0', 115200, 1, Routine.DEBUG)

        logger.debug("Creation and strating of Threads")

        # Création des threads
        thread_lidar = threading.Thread(
            target=run_lidar,
            args=[serial_moteur],
            daemon=True
        )

        thread_routine = threading.Thread(
            target=run_routine,
            args=[serial_moteur, serial_actionneur, Routine.DEBUG],
            daemon=True
        )

        # Lancement des threads
        lidar_thread.start()
        routine_thread.start()

        lidar_thread.join()
        routine_thread.join()

    except KeyboardInterrupt:
        logger.warning("Arrêt demandé par l'utilisateur")
    finally:
        stop_event.set()  # Demande l'arrêt propre des threads
        logger.debug("Nettoyage et arrêt des threads")

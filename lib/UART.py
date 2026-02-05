import time
import serial
import struct

from lib.logger_manager import LoggerManager

logger = LoggerManager("main").get_logger()

def init_uart(port, baudrate, timeout, debug=0):
    try:
        # Initialisation de la connexion série
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)

        # Vérifier si la connexion a bien été établie
        if ser.is_open:
            if debug:
                logger.debug(f"Port série {port} initialisé avec succès à {baudrate} bauds.")
            return ser
        else:
            logger.error(f"Impossible d'ouvrir le port {port}.")
            return None

    except serial.SerialException as e:
        logger.error(f"Erreur d'initialisation de {port}: {e}")
        return None

def envoie_stop(ser, debug=0):
	# Vérifier que la connexion série est bien ouverte
    if not ser.is_open:
        logger.error("La connexion série n'est pas ouverte.")
        return
    command = bytes([0x0F])
    if debug:
        logger.debug(f"STOP envoyé : {message.hex()}")

    message = command +  b'\r'
    try:
        ser.write(message)
    except serial.SerialException as e:
        logger.error(f"Erreur d'écriture sur le port série : {e}")
        return
    except Exception as e:
        logger.error(f"Une erreur inconnue est survenue lors de l'écriture : {e}")
        return

    if debug:
        logger.debug("Message envoyé avec succès.")


def envoie_reset_cm(ser, debug=0):
	# Vérifier que la connexion série est bien ouverte
    if not ser.is_open:
        logger.error("La connexion série n'est pas ouverte.")
        return

    command = bytes([0xFF])
    if debug:
        logger.debug(f"RESET_CM envoyé : {message.hex()}")

    message = command +  b'\r'
    try:
        ser.write(message)
    except serial.SerialException as e:
        logger.error(f"Erreur d'écriture sur le port série : {e}")
        return
    except Exception as e:
        logger.error(f"Une erreur inconnue est survenue lors de l'écriture : {e}")
        return

    if debug:
        logger.debug("Message envoyé avec succès.")

def envoie_resume_cm(ser, debug=0):

	# Vérifier que la connexion série est bien ouverte
    if not ser.is_open:
        logger.error("La connexion série n'est pas ouverte.")
        return

    command = bytes([0x2F])
    if debug:
        logger.debug(f"RESUME_CM envoyé : {message.hex()}")

    message = command +  b'\r'
    try:
        ser.write(message)
    except serial.SerialException as e:
        logger.error(f"Erreur d'écriture sur le port série : {e}")
        return
    except Exception as e:
        logger.error(f"Une erreur inconnue est survenue lors de l'écriture : {e}")
        return

    if debug:
        logger.debug("Message envoyé avec succès.")


def envoie_deplacement(ser, x, y, theta, speed=0, relative=False, set_position=False, debug=0):
    # Vérifier que la connexion série est bien ouverte
    if not ser.is_open:
        logger.error("La connexion série n'est pas ouverte.")
        return

    """
    if not (0 <= x <= 65535):
        logger.error(f"La valeur de x ({x}) est hors de la plage valide (0 à 65535).")
        return
    if not (0 <= y <= 65535):
        logger.error(f"La valeur de y ({y}) est hors de la plage valide (0 à 65535).")
        return
    if not (0 <= theta <= 65535):
        logger.error(f"La valeur de theta ({theta}) est hors de la plage valide (0 à 65535).")
        return
    if not (0 <= speed <= 65535):
        logger.error(f"La valeur de theta ({theta}) est hors de la plage valide (0 à 65535).")
        return
    """

    if speed == 0:
        command = bytes([0x01])
    else:
        command = bytes([0x02])

    if relative == True:
        command = bytes([0x03])
    elif set_position == True:
        command = bytes([0x07])

    # Convertir les valeurs x, y, theta en format binaire Big endian (2 octets)
    try:
        x_bytes = struct.pack('>h', x)
        y_bytes = struct.pack('>h', y)
        theta_bytes = struct.pack('>h', theta)
    except Exception as e:
        logger.error(f"Erreur lors de la conversion des données : {e}")
        return

    if speed == 0:
        message = command + x_bytes + y_bytes + theta_bytes + b'\r'
    else:
        message = command + x_bytes + y_bytes + theta_bytes + struct.pack('>H', speed) + b'\r'

    if debug:
        logger.debug(f"Deplacement envoyé : {message.hex()}")

    try:
        ser.write(message)
    except serial.SerialException as e:
        logger.error(f"Erreur d'écriture sur le port série : {e}")
        return
    except Exception as e:
        logger.error(f"Une erreur inconnue est survenue lors de l'écriture : {e}")
        return

    if debug:
        logger.debug("Message envoyé avec succès.")


def envoie_actionneur(ser, module, type_actionneur, action, position=0, speed = 0, debug=1):
    """
    Envoie une commande à un actionneur via UART

    Args:
        ser: objet Serial ouvert pour la communication UART
        module: 2 bits (0-3)
        type_actionneur: 2 bits (0-3)
        action: 2 bits (0-3)
        position: 8 bits (0-255, défaut 0)
        speed : 1 bit (0 mode normal, 1 mode lent)

    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    # Vérification initiale de la connexion série
    if not ser or not ser.is_open:
        logger.error("Port série non initialisé ou non ouvert")
        return False

    try:
        # Validation des paramètres avec messages d'erreur précis
        validations = [
            (0 <= module <= 0b11, "Module doit être codé sur 2 bits (0-3)"),
            (0 <= type_actionneur <= 0b11, "Type_actionneur doit être codé sur 2 bits (0-3)"),
            (0 <= action <= 0b11, "Action doit être codée sur 2 bits (0-3)"),
            (0 <= position <= 0x3FF, "Position doit être codée sur 10 bits (0-255)"),
            (0 <= speed <= 0b1, "Speed sur 1 bit")
        ]

        for condition, error_msg in validations:
            if not condition:
                raise ValueError(error_msg)

        # Construction de la trame 16 bits (big-endian)
        trame = (module << 14) | (type_actionneur << 12) | (action << 10) | (speed << 9) | (position >> 8) << 8 | (position & 0xFF)
        # Conversion en bytes (2 octets big-endian)
        data = trame.to_bytes(2, byteorder='big', signed=False)

        if debug:
            logger.debug(trame)
            logger.debug(hex(data[1]))
            logger.debug(hex(data[0]))

        # Envoi avec vérification
        bytes_written = ser.write(data)
        ser.flush()  # Attente de l'achèvement de la transmission

        if bytes_written != len(data):
            logger.error(f"Seulement {bytes_written}/2 octets écrits")
            return False

        return True

    except ValueError as ve:
        logger.error(f"Erreur de validation : {ve}")
    except serial.SerialException as se:
        logger.error(f"Erreur de communication série : {se}")
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}")

    return False

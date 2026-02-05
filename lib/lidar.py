# =============================================================================== #
# =============================================================================== #
#
# CUSTOM FUNCTIONS TO FILTER AND PROCESS MEASURED POINTS
#
# =============================================================================== #
# =============================================================================== #


def clean_values(tab_dist, min_detect=200, max_detect=3500, max_consec_var=50):
    """
    Search for outlier values and remove them from the list

    Parameters:
    tab_dist (list): List of distance values
    min_detect (int, optional): Minimal distance we should detect objects (default: 200)
    max_detect (int, optional): Maximal distance we should detect objects (default: 3500)
    max_consec_var (int, optional): Maximal distance acceptable between two consecutive angles (default: 50)

    Returns:
    list: List of cleaned distance values
    """

    N = len(tab_dist)
    new_tab_dist = [0] * N

    for angle in range(N):
        if tab_dist[angle] > min_detect and tab_dist[angle] < max_detect:
            if (
                abs(tab_dist[angle] - tab_dist[(angle - 1) % N]) < max_consec_var
                or abs(tab_dist[angle] - tab_dist[(angle + 1) % N]) < max_consec_var
            ):
                new_tab_dist[angle] = tab_dist[angle]

    return new_tab_dist


def detect_objects(tab_dist, max_consec_var=50):
    """
    Detects objects in a lidar scan based on the given distance measurements.
    Args:
        tab_dist (list): A list of distance measurements from the lidar scan.
        max_consec_var (int, optional): The maximum consecutive variation allowed between distance measurements
            to consider them as part of the same object. Defaults to 50.
    Returns:
        tuple: A tuple containing two elements:
            - tab_objects (list): A list of sublists representing the detected objects. Each sublist contains
              the starting and ending angles of an object.
            - nb_objects (int): The total number of detected objects.
    Example:
        >>> tab_dist = [0, 0, 10, 15, 20, 0, 0, 0, 30, 35, 40, 0, 0]
        >>> objects, num_objects = detect_objects(tab_dist)
        >>> print(objects)
        [[2, 4], [8, 10]]
        >>> print(num_objects)
        2
    """

    tab_objects = []
    nb_objects = 0
    is_object_here = False
    is_object_debut = tab_dist[0] != 0

    if is_object_debut:
        tab_objects += [[-1, -1]]
        nb_objects = 1
        is_object_here = True

    for angle in range(1, len(tab_dist)):

        # Début d'un objet
        if not is_object_here and tab_dist[angle] != 0:
            nb_objects += 1
            is_object_here = True
            tab_objects += [[angle, -1]]


        # Fin d'un objet
        elif is_object_here and tab_dist[angle] == 0:
            is_object_here = False
            tab_objects[nb_objects - 1][1] = angle - 1


        # Un objet est devant ou derière un autre
        elif (
            is_object_here
            and abs(tab_dist[angle] - tab_dist[angle - 1]) > max_consec_var
        ):
            nb_objects += 1
            is_object_here = True
            tab_objects[nb_objects - 1 - 1][1] = angle - 1  # Fin du précédent objet
            tab_objects += [[angle, -1]]  # Début du nouvel objet

    if is_object_debut and tab_objects[-1][1] == -1:

        # Un objet commence au début et un autre finit à la fin des angles
        if abs(tab_dist[0] - tab_dist[-1]) > max_consec_var:
            tab_objects[0][0] = 0
            tab_objects[-1][1] = len(tab_dist) - 1
        # Un objet finit au début et commence à la fin
        else:
            tab_objects[0][0] = tab_objects[-1][0]
            tab_objects.pop()
        nb_objects -= 1

    # Si un objet finit au dernier angle
    elif not is_object_debut and tab_objects[-1][1] == -1:
        tab_objects[-1][1] = 359

    return tab_objects, nb_objects


def detect_objects_center(tab_dist, tab_obj):
    """
    Calculate the center angles of detected objects based on the given distance and object arrays.
    Args:
        tab_dist (list): A list of distances from the lidar sensor.
        tab_obj (list): A list of object indices representing the start and end points of each object.
    Returns:
        list: A list of center angles for each detected object.
    Raises:
        None
    Examples:
        >>> tab_dist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> tab_obj = [[2, 4], [6, 8]]
        >>> detect_objects_center(tab_dist, tab_obj)
        [3, 7]
    """

    centres_obj = [-1 for i in range(len(tab_obj))]
    debut = 0

    # Handle the special case separately
    if tab_obj[0][0] > tab_obj[0][1]:

        debut = 1
        debut_obj = tab_obj[0][0]
        fin_obj = tab_obj[0][1]

        # Find the angle of the minimum distance for object 0
        dist_mini_objet1, angle1 = min(
            (v, i) for i, v in enumerate(tab_dist[: fin_obj + 1])
        )
        dist_mini_objet2, angle2 = min(
            (v, i) for i, v in enumerate(tab_dist[debut_obj:])
        )

        # Angle of the minimum distance for object 0 in the special case
        if dist_mini_objet1 < dist_mini_objet2:
            centres_obj[0] = 0 + angle1

        # Angle of the minimum distance for object 0 in the special case
        else:
            centres_obj[0] = debut_obj + angle2

    # Process the objects starting from index 'debut'
    for i in range(debut, len(tab_obj)):
        debut_obj = tab_obj[i][0]
        fin_obj = tab_obj[i][1]

        # Find the angle of the minimum distance for object i
        _, angle = min((v, i) for i, v in enumerate(tab_dist[debut_obj : fin_obj + 1]))
        centres_obj[i] = debut_obj + angle

    return centres_obj


def detect_is_in_terrain(
    dist, angle_obj, x, y, angle_robot, max_detect=3500, terrain_x=2000, terrain_y=3000
):
    """
    Detect if an object is within the terrain boundaries.

    Parameters:
    dist (float): The distance to the object.
    angle_obj (float): The angle of the object.
    x (float): The x-coordinate of the robot.
    y (float): The y-coordinate of the robot.
    angle_robot (float): The angle of the robot.
    max_detect (float, optional): The maximum distance to detect an object. Default is 3500.
    terrain_x (float, optional): The width of the terrain. Default is 2000.
    terrain_y (float, optional): The height of the terrain. Default is 3000.

    Returns:
    tuple: A tuple containing the x-coordinate, y-coordinate, and a boolean indicating if the object is within the terrain.
    """

    # Check if the object is too far
    if dist > max_detect:
        pos_x, pos_y = 0, 0
        is_in_terrain = False

    else:
        angle = (angle_obj + angle_robot) % 360
        pos_x = x + dist * cos(pi * angle / 180)
        pos_y = y + dist * sin(pi * angle / 180)

        # Check if the object is within the terrain boundaries
        if pos_x >= 0 and pos_x <= terrain_x and pos_y >= 0 and pos_y <= terrain_y:
            is_in_terrain = True
        else:
            is_in_terrain = False

    return (pos_x, pos_y, is_in_terrain)


def detect_is_too_close(dist, dist_min=450):

    if dist > dist_min:
        return False
    else:
        return True


def alarm_isTooClose(tab_dist, objects_angle, dist_min=450):

    for i in range(len(objects_angle)):
        if detect_is_too_close(tab_dist[objects_angle[i]], dist_min):
            return True

    return False


def clean_out_objects(
    tab_dist, objects_angle, x, y, angleRobot, terrainX=2000, terrainY=3000
):

    objects_angle_in = []

    for i in range(len(objects_angle)):
        _, _, isInTerrain = detect_is_in_terrain(
            tab_dist[objects_angle[i]],
            objects_angle[i],
            x,
            y,
            angleRobot,
            terrainX,
            terrainY,
        )
        if isInTerrain:
            objects_angle_in += [objects_angle_in[i]]

    return objects_angle_in


# =============================================================================== #
# =============================================================================== #
#
# TEST CUSTOM RPLIDAR LIBRARY
#
# =============================================================================== #
# =============================================================================== #

import time
import numpy as np
from math import floor

import serial
import Routine
import UART

from lib.adafruit_rplidar import RPLidar
from lib.settings import NB_SCAN_SAFE, MIN_DISTANCE

from lib.logger_manager import LoggerManager

logger = LoggerManager("main").get_logger()


def LIDAR_mesurement(ser, min_dist=MIN_DISTANCE):
    # Setup the RPLidar
    PORT_NAME = "/dev/ttyUSB0"
    lidar = RPLidar(None, PORT_NAME, timeout=3)

    try:
        not_detect_counter = 0
        time_detected = 0

        logger.info("Debut mesure LIDAR")

        state = []
        for point in lidar.iter_points():
            if any(state):
                # Ajouter ici les actions à faire en cas de détection
                if Routine.flag_STOP == 0:
                    logger.warn("ALERTE: Objet trop proche détecté !")
                    time_detected = time.time()
                    UART.envoie_STOP(ser)
                    Routine.flag_STOP = 1
                    Routine.stop_handled = False
            elif Routine.flag_STOP == 1 and (True not in state) and point[0]:
                not_detect_counter += 1
                if not_detect_counter == NB_SCAN_SAFE:
                    logger.info(f"INFO: Objet plus détecté ({(time.time() - time_detected):.3f} s) !")
                    time_detected = 0
                    Routine.flag_STOP = 0
                    not_detect_counter = 0

            # If new scan, reset state array
            if point[0]:
                state = []

            # Check fi distance within STOP range
            if 15 <= point[-1] <= min_dist:
                state.append(True)
            else:
                state.append(False)

    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
    except KeyboardInterrupt:
        logger.error("Arrêt demandé par l'utilisateur")
    finally:
        lidar.stop()
        lidar.disconnect()

import colorlog
import logging
import datetime

#################################################
# LOGGING
#################################################

formatter= colorlog.ColoredFormatter(
	"[%(asctime)s] %(log_color)s%(levelname)-8s%(reset)s %(light_black)s%(filename)s:%(lineno)d:%(reset)s %(message)s",
	datefmt="%H:%M:%S",
	reset=True,
	log_colors={
		'DEBUG': 'cyan',
		'INFO':  'green',
		'WARNING':  'yellow',
		'ERROR': 'red',
		'CRITICAL': 'red,bg_white',
	},
	secondary_log_colors={},
	style='%'
)
handler = colorlog.StreamHandler()
handler.setFormatter(formatter)
logger = colorlog.getLogger("rasp_log")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

file_formatter = logging.Formatter(
	"[%(asctime)s] %(levelname)-8s %%(filename)s:%(lineno)d: %(message)s",
	datefmt="%H:%M:%S",
)
file_handler = logging.FileHandler(f"logs/{datetime.datetime.now():%H-%M-%S}-logs.txt")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

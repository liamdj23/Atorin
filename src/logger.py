import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # move to config
log_formatter = logging.Formatter('%(asctime)s [%(filename)s|%(funcName)s] -%(levelname)s- :: %(message)s ')
err_handler = logging.StreamHandler()
err_handler.setLevel(logging.ERROR)
err_handler.setFormatter(log_formatter)
logger.addHandler(err_handler)
info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(log_formatter)
logger.addHandler(info_handler)

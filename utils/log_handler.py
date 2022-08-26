# STANDART MODÜLLER İÇERİ AKTARILIR
# /////////////////////////////////////////////////////////////////////////////
import logging
import sys
from datetime import datetime
import os

logger = logging.getLogger(__name__)

PATH = "./logs"
TODAY_STR = datetime.today().strftime("%Y%m%d")


class LogHandler:

    # LOG AYARLARI YAPILIR
    # /////////////////////////////////////////////////////////////////////////
    @staticmethod
    def set_basic_config():

        # eğer dizin yoksa oluşturulur
        if not os.path.exists(PATH):
            os.makedirs(PATH)

        file_handler = logging.FileHandler(
            f"{PATH}/dir-sync-{TODAY_STR}.log",
            encoding="utf-8",
            mode="a"
        )

        stream_handler = logging.StreamHandler(stream=sys.stdout)

        logging.basicConfig(
            handlers=[file_handler, stream_handler],
            format='%(asctime)s - %(levelname)s - %(name)s: %(message)s',
            level=logging.INFO,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        sys.excepthook = LogHandler.handle_unhandled_exception

    @staticmethod
    def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
        """Handler for unhandled exceptions that will write to the logs"""
        if issubclass(exc_type, KeyboardInterrupt):
            # call the default excepthook saved at __excepthook__
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

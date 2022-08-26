# STANDART MODÜLLER İÇERİ AKTARILIR
# /////////////////////////////////////////////////////////////////////////////
import locale
import logging

# 3. PARTİ PAKETLERİN MODÜLLERİ İÇERİ AKTARILIR
# /////////////////////////////////////////////////////////////////////////////
from dotenv import load_dotenv

# BANA AİT MODÜLLER İÇERİ AKTARILIR
# /////////////////////////////////////////////////////////////////////////////
from utils.log_handler import LogHandler

logger = logging.getLogger(__name__)


class App:

    @staticmethod
    # UYGULAMA BAŞLATICISI
    # /////////////////////////////////////////////////////////////////////////
    def start():
        # YAZILIM ORTAMINA UYGUN DEĞİŞKENLER ALINIR
        # /////////////////////////////////////////////////////////////////////
        load_dotenv(dotenv_path=".env", encoding="UTF-8", override=True)
        logger.info("Ortam değişkenleri alındı.")

        # LOG AYARLARI YAPILIR
        # /////////////////////////////////////////////////////////////////////
        LogHandler.set_basic_config()
        logger.info("Log ayarları yapıldı")

        # YAZILIM YERELLEŞTİRİLİR
        # /////////////////////////////////////////////////////////////////////
        locale.setlocale(locale.LC_ALL, 'tr_TR.utf8')
        logger.info("Yazılım dili yerelleştirildi")


app = App()

# STANDART MODÜLLER İÇERİ AKTARILIR
# /////////////////////////////////////////////////////////////////////////////
import os

# BANA AİT MODÜLLER İÇERİ AKTARILIR
# /////////////////////////////////////////////////////////////////////////////
from utils.app_handler import app
from modules.dir_sync import sync


def main() -> None:
    sync(os.getenv("PC"), os.getenv("DRIVE"))


if __name__ == '__main__':
    app.start()
    main()

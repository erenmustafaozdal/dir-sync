"""
dir-sync

İki dizini önceki halleriyle kıyaslayarak,
dosyaların zaman damgalarını dikkate alarak,
birbiriyle senkronize eder.

(c) Eren Mustafa Özdal 2022

Thomas Khyn tarafından geliştirilmiş olan
dirsync paketinden esinlenmiştir.

"""

import logging
import time
from typing import Union
from pathlib import Path
from .version import __pkg_name__
class Syncer:
    """ Dizinleri senkronize etme sınıfı """

    def __init__(self, pc_path, drive_path):
        self.logger = logging.getLogger("dir-sync")

        self._pc_path = Path(pc_path)
        self._drive_path = Path(drive_path)
        self._trash_path = Path("./trash")

        self._db_file = ".dir-sync"

        self._trashed_paths = {}
        self._deleted_paths = {}

        # kaynak dizinin kendi içinde karşılaştırması
        self._cmp_pc: Union[DCMP, None] = None
        # hedef dizinin kendi içinde karşılaştırması
        self._cmp_drive: Union[DCMP, None] = None
        # kaynak ve hedef dizinin karşılaştırması
        self._dcmp: Union[DCMP, None] = None

        # istatistik değişkenleri
        self._numdirs = 0
        self._numfiles = 0
        self._numdelfiles = 0
        self._numdeldirs = 0
        self._numtrashfiles = 0
        self._numtrashdirs = 0
        self._numnewdirs = 0
        self._numtimeupdates = 0
        self._starttime = 0.0
        self._endtime = 0.0

        # başarısız işlem istatistik değişkenleri
        self._numcopyfld = 0
        self._numupdsfld = 0
        self._numdirsfld = 0
        self._numdelffld = 0
        self._numtrashffld = 0
        self._numdeldfld = 0

    def log(self, msg=''):
        self.logger.info(msg)

    def do_work(self):
        """ İşlemleri başlatan metot """

        self._starttime = time.time()

        # eğer drive yolu (sabit disk vb.) takılı değilse dön
        if not self._drive_path.exists():
            self.log(f"Hedef drive yolu bulunamadı: {self._drive_path}")
            return None

        # All right!
        self._endtime = time.time()

    def report(self):
        """ Print report of work at the end """

        # We need only the first 4 significant digits
        tt = (str(self._endtime - self._starttime))[:4]

        self.log(f'{__pkg_name__}, işlemleri {tt} saniyede tamamladı.')
        self.log(f'{self._numdirs} klasör tarandı, '
                 f'{self._numfiles} dosya kopyalandı.')

        if self._numtrashfiles:
            self.log(f'{self._numtrashfiles} dosya geri dönüşüme gönderildi.')
        if self._numtrashdirs:
            self.log(f'{self._numtrashdirs} klasör geri dönüşüme gönderildi.')
        if self._numdelfiles:
            self.log(f'{self._numdelfiles} dosya silindi.')
        if self._numdeldirs:
            self.log(f'{self._numdeldirs} klasör silindi.')
        if self._numnewdirs:
            self.log(f'{self._numnewdirs} klasör oluşturuldu.')
        if self._numtimeupdates:
            self.log(f'{self._numtimeupdates} dosya '
                     f'zaman damgasına göre güncellendi.')

        # Failure stats
        print("")
        if self._numcopyfld:
            self.log(f'{self._numcopyfld} dosya kopyalanırken hata oldu.')
        if self._numdirsfld:
            self.log(f'{self._numdirsfld} klasör oluşturulurken hata oldu.')
        if self._numupdsfld:
            self.log(f'{self._numupdsfld} dosya güncellenirken hata oldu.')
        if self._numdeldfld:
            self.log(f'{self._numdeldfld} klasör silinirken hata oldu.')
        if self._numdelffld:
            self.log(f'{self._numdelffld} dosya silinirken hata oldu.')

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


class DCMP:
    """Dizinleri kıyaslarken verileri saklamak için kullanılan sahte obje"""
    def __init__(self, left, right, common, db=None):
        self.left_only: set = left  # kaynak veya geçmiş
        self.right_only: set = right  # hedef veya şu an
        self.common: set = common  # ortak
        self.db: Union[dict, None] = db


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
        self.sync()
        self._endtime = time.time()

    def sync(self):

        self.log(f'Dizinler senkronize ediliyor:'
                 f' "{self._pc_path}" & "{self._drive_path}"')

        # kaynak pc dizini taraması yapılır
        pc_paths, self._cmp_pc = self._self_compare(self._pc_path)
        # hedef drive dizin taraması yapılır
        drive_paths, self._cmp_drive = self._self_compare(self._drive_path)
        # iki dizin arasındaki farklar alınır
        self._dcmp = self._compare(pc_paths, drive_paths)
    @staticmethod
    def _compare(pc_paths: set, drive_paths: set) -> DCMP:
        """
        Dizinlerin dosya ve klasör yollarını alır, farklılıkları döndürür

        :param pc_paths: kaynak dizin yolu
        :type pc_paths: set
        :param drive_paths: hedef dizin yolu
        :type drive_paths: set
        :return: farklılıklar
        :rtype: DCMP
        """

        common = pc_paths.intersection(drive_paths)
        pc_paths.difference_update(common)
        drive_paths.difference_update(common)

        return DCMP(pc_paths, drive_paths, common)

    def _self_compare(self, comp_dir: Path) -> tuple:
        """
        Dizini kendi içinde tarama yapar ve dosyalar ile farklılıkları döndürür

        :param comp_dir: dizin yolu
        :type comp_dir: str
        :return: dosyalar ile farklılıklar (set, DCMP)
        :rtype: tuple
        """

        self.log(f'Taranıyor: {comp_dir}')
        self._numdirs += 1

        # önceki tarama sonucu alınır
        db = self._read_db(comp_dir)
        last_paths = set(db.keys())

        # dizin gezilir
        paths = set(self._walk_in_dir(comp_dir).keys())
        new_paths = paths.copy()

        # önceki hali ile ortak dosyalar ve farklı dosyalar belirlenir
        common = paths.intersection(last_paths)
        new_paths.difference_update(common)
        last_paths.difference_update(common)

        return paths, DCMP(last_paths, new_paths, common, db)

    def _walk_in_dir(self, comp_dir: Path, counting: bool = True) -> dict:
        """
        Dizin içinde gezer ve dosyaları/klasöri döndürür

        :param comp_dir: dizin yolu
        :type comp_dir: str

        :return: dosya ve klasörlerin yolları
        :rtype: set
        """

        paths = {}
        for cwd, dirs, files in os.walk(comp_dir):
            self._numdirs += len(dirs) if counting else 0
            for f in dirs + files:
                if f == self._db_file:
                    continue

                full_path = Path(cwd).joinpath(f)
                re_path = str(full_path.relative_to(comp_dir))
                paths[re_path] = self.get_file_info(full_path)

        return paths

    @staticmethod
    def get_file_info(full_path) -> dict:
        info = {}

        # klasör mü?
        is_dir = full_path.is_dir()
        info["is_dir"] = is_dir

        # eğer klasör değilse dosya bilgilerini ekle
        if not is_dir:
            info["file_name"] = full_path.stem
            info["file_extension"] = full_path.suffix

        # dosya klasör zaman bilgilerini alalım
        path_stat = full_path.stat()
        info["updated_at"] = path_stat.st_mtime
        info["created_at"] = path_stat.st_ctime

        return info

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

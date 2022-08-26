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

        # Kaynakta silinmişler hedefte de silinir
        self._sync_remove(self._cmp_pc, self._drive_path)
        # Hedefte silinmişler kaynakta da silinir
        self._sync_remove(self._cmp_drive, self._pc_path)

        # Sadece kaynakta yer alanlar hedefe de eklenir
        self._sync_copy(self._dcmp.left_only, self._pc_path, self._drive_path)
        # Sadece hedefte yer alanlar kaynağa da eklenir
        self._sync_copy(self._dcmp.right_only, self._drive_path, self._pc_path)

        # İki kaynakta da yer alan dosyaları son değişikliğe göre güncelle
        self._sync_update(self._dcmp, self._pc_path, self._drive_path)

    def _sync_update(self, cmp: DCMP, dir1: Path, dir2: Path):
        """ Her iki tarafta da olan dosyaları zaman damgasına göre günceller """
        for f in cmp.common:
            file1 = dir1.joinpath(f)
            file2 = dir2.joinpath(f)

            try:
                st1 = file1.stat()
                st2 = file2.stat()
            except os.error:
                return -1

            # eğer dosya ise
            if stat.S_ISREG(st1.st_mode):
                need_update = self._cmptimestamps(st1, st2)
                if not need_update:
                    continue

                direction = ">>" if need_update > 0 else "<<"
                self.log(f'Dosya güncelleniyor:'
                         f' {f} - {dir1} {direction} {dir2}')

                from_file = file1 if need_update > 0 else file2
                to_file = file1 if need_update < 0 else file2
                self._update(from_file, to_file)

    def _update(self, from_file: Path, to_file: Path) -> int:
        """
        Dosya günceleme işlemini yapar

        :param from_file: yeni dosya
        :type from_file: Path
        :param to_file: eski dosya
        :type to_file: Path
        :return:
        """

        try:
            os.chmod(to_file, 1638)  # 1638 = 0o666

            try:
                self._copy_file_proc(from_file, to_file)
                self._numtimeupdates += 1
                return 0
            except (IOError, OSError) as e:
                self.log(str(e))
                self._numupdsfld += 1
                return -1

        except Exception as e:
            self.log(str(e))
            return -1

    @staticmethod
    def _cmptimestamps(filest1, filest2) -> Union[bool, int]:
        """ Compare time stamps of two files and return True
        if file1 (source) is more recent than file2 (target) """

        # kaynak dosya ve hedef dosya değişim tarihi farkı alınır
        diff = int((filest1.st_mtime - filest2.st_mtime) * 1000)

        # eğer dosyalar aynı ise False döndür
        if diff == 0:
            return False

        # değişmiş ise farkı döndür
        # pozitif ise kaynak daha yeni
        # negatif ise hedef daha yeni
        return diff

    def _sync_copy(self, created: set, source: Path, target: Path) -> None:
        """ yeni oluşturulması gereken dosya ve klasörleri oluşturur """
        for f in created:
            full_f = source.joinpath(f)
            try:
                st = full_f.stat()
            except os.error:
                continue

            if stat.S_ISREG(st.st_mode):
                # dosya kopyalanır
                self._copy(f, source, target)
            elif stat.S_ISDIR(st.st_mode):
                to_make = target.joinpath(f)
                if not os.path.exists(to_make):
                    self._create_dir(to_make)

    def _copy(self, path: str, source: Path, target: Path) -> None:
        """
        Dosya kopyalama işlemi yapar

        :param path: dosya adı
        :type path: str
        :param source: kaynak dizin
        :type source: Path
        :param target: hedef dizin
        :type target: Path
        :return:
        """

        rel_path = Path(path)
        rel_dir = rel_path.parent
        filename = rel_path.name

        dir2_root = target

        dir1 = source.joinpath(rel_dir)
        dir2 = target.joinpath(rel_dir)

        self.log(f'Dosya kopyalanıyor: {filename} - {dir1} >> {dir2}')

        try:
            # hedef klasör yoksa oluşturulur
            if not os.path.exists(dir2):
                # 1911 = 0o777
                os.chmod(os.path.dirname(dir2_root), 1911)
                self._create_dir(dir2)

            os.chmod(dir2, 1911)  # 1911 = 0o777

            sourcefile = dir1.joinpath(filename)
            targetfile = dir2.joinpath(filename)
            # kaynağın tipine göre (sembolik link veya dosya) kopyalama yapılır
            try:
                self._copy_file_proc(sourcefile, targetfile)
                self._numfiles += 1
            except (IOError, OSError) as e:
                self.log(str(e))
                self._numcopyfld += 1

        except Exception as e:
            self.log(f'Dosya kopyalanırken bir hata oldu {filename}')
            self.log(str(e))

    @staticmethod
    def _copy_file_proc(sourcefile, targetfile):
        if os.path.islink(sourcefile):
            os.symlink(os.readlink(sourcefile), targetfile)
        else:
            try:
                shutil.copy2(sourcefile, targetfile)
            except PermissionError:
                if os.path.exists(targetfile):
                    os.chmod(targetfile, stat.S_IWRITE)
                shutil.copy2(sourcefile, targetfile)

    def _sync_remove(self, cmp: DCMP, target: Path) -> None:
        """ silinmesi gereken dosya ve klasörleri siler """

        for f in cmp.left_only:
            full_f = target.joinpath(f)

            try:
                full_trash = Path(self._trash_path).joinpath(f)
                # eğer daha önce geri dönüşüme gönderildi isegeç
                if full_trash.exists():
                    continue

                # geri dönüşüm dizinleri oluşturulur
                trash_dir = full_trash.parent
                if not trash_dir.exists():
                    self._create_dir(trash_dir)

                # eğer yol (path) varsa taşıma işlemi yapılır
                # eğer yol yoksa; yani ana klasör ile taşınma işlemi yapıldıysa
                # taşıma işlemine girilmez, sadece veritabanı kaydı için
                # geri dönüşüme gönderilenler arasında kaydedilir
                if full_f.exists():
                    self.log(f'Geri dönüşüme gönderiliyor: {full_f}')
                    trash_dir.chmod(1911)  # 1911 = 0o777
                    shutil.move(full_f, full_trash)

                # dosya veya klasör sayı bilgileri işlenir
                if full_trash.is_dir():
                    self._numtrashdirs += 1
                else:
                    self._numtrashfiles += 1

                # silinenlere eklenir
                self._trashed_paths[f] = self.get_file_info(full_trash) | {
                    "trashed_at": datetime.now().timestamp(),
                    "trash_from": str(target),
                }
            except Exception as e:
                self.log(str(e))
                self._numtrashffld += 1
                continue

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

    def _create_dir(self, _dir: Path) -> bool:
        """
        Gelen dizin yolunu oluşturur. Hata olmazsa True, olurse False döndürür
        :param _dir: dizin yolu
        :type _dir: str
        :return: sonucu döndürür
        :rtype: bool
        """

        self.log(f'Yeni klasör oluşturuluyor: {_dir}')
        try:
            os.makedirs(_dir)
            self._numnewdirs += 1
            return True
        except Exception as e:
            self.log(str(e))
            self._numdirsfld += 1
            return False

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

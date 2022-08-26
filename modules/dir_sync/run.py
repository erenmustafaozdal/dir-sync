"""
dir-sync çalıştırma fonksiyonu
"""

from .syncer import Syncer


def sync(sourcedir, targetdir):

    copier = Syncer(sourcedir, targetdir)
    copier.do_work()

    # raporu yazdır
    copier.report()

"""
Proje versiyon bilgileri
"""

import subprocess

__pkg_name__ = 'dir-sync'

__version_info__ = (1, 0, 0, 'beta', 1)


def get_version(version=__version_info__):

    dev_st = {'alpha': 'a', 'beta': 'b', 'rc': 'c', 'final': ''}

    assert len(version) == 5
    assert version[3] in dev_st.keys()

    version_str = '.'.join([str(v) for v in version[:3]])

    if version[3] == 'final':
        return version_str

    if version[3:] == ('alpha', 0):
        return '%s.dev0+%s' % (version_str, get_git_chgset())
    else:
        return f'{version_str}-{dev_st[version[3]]}.{version[4]}'


def get_git_chgset():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'],
                                       universal_newlines=True).strip()[:-1]
    except:
        return '?'


__version__ = get_version()

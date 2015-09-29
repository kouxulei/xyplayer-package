# Copyright (C) 2013-2014 Zheng-Yejian <1035766515@qq.com>
# Use of this source code is governed by GPLv3 license that can be found
# in the LICENSE file.

import os

__doc__ = '''This is a simple musicplayer that can search, play, download musics from the Internet.'''

app_version = 'v0.8.2-2'
app_version_num = 822

class Configures(object):
#    INSTALLPATH = '/usr/lib/python3/dist-packages/xyplayer'
    FILE_LENGTH_MB = 1000000
    LINE_HEIGHT = 28.11
    LINE_WRAP_WIDTH = 350
    NOERROR = -1
    URLERROR = -2
    TYPEERROR = -3
    PATHERROR = -4
    NONETERROR = -5
    UpdateSucceed = 0
    UpdateStarted = 1
    UpdateDropped = 2
    UpdateFailed = 3
    homeDir = os.path.expanduser('~')
    cacheDir = os.path.join(homeDir, '.xyplayer')
    musicsDir = os.path.join(cacheDir, 'downloads')
    imagesDir = os.path.join(cacheDir, 'images')
    artistInfosDir = os.path.join(cacheDir, 'infos')
    debsDir = os.path.join(cacheDir, 'debs')
    lrcsDir = os.path.join(cacheDir, 'lrcs')
    settingFile = os.path.join(cacheDir, 'settings')
    db = os.path.join(cacheDir, 'xyplayer_new.db')
    changelog = os.path.join(cacheDir, 'changelog')
    #urlCache = os.path.join(cacheDir, 'urlcache.json')
    
    @classmethod
    def check_dirs(cls):
        dirs = [cls.musicsDir, cls.imagesDir, cls.lrcsDir, cls.artistInfosDir, cls.debsDir]
        if not os.path.exists(cls.cacheDir):
            os.makedirs(cls.cacheDir)
        for dir in dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
        if not os.path.exists(cls.settingFile):
            with open(cls.settingFile, 'w') as f:
                f.write(cls.musicsDir)
                f.close()

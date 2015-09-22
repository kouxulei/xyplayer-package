import os

class Configures():
#    INSTALLPATH = '/usr/lib/python3/dist-packages/xyplayer'
    FILE_LENGTH_MB = 1000000
    LINE_HEIGHT = 28.11
    LINE_WRAP_WIDTH = 350
    NOERROR = -1
    URLERROR = -2
    TYPEERROR = -3
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
    urlCache = os.path.join(cacheDir, 'urlcache.json')
    
    def check_dirs(self):
        dirs = [self.musicsDir, self.imagesDir, self.lrcsDir, self.artistInfosDir, self.debsDir]
        if not os.path.exists(self.cacheDir):
            os.makedirs(self.cacheDir)
        for dir in dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
        #if not os.path.exists(self.urlCache):
            #with open(self.urlCache, 'w') as f:
                #f.close()
        if not os.path.exists(self.settingFile):
            with open(self.settingFile, 'w') as f:
                f.write(self.musicsDir)
                f.close()
            

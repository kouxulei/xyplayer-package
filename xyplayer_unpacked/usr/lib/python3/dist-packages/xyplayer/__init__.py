# Copyright (C) 2015-2016 Zheng-Yejian <1035766515@qq.com>
# Use of this source code is governed by GPLv3 license that can be found
# in the LICENSE file.

import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

__doc__ = '''This is a simple musicplayer that can search, play, download musics from the Internet.'''

app_version = 'v0.8.3-1'
app_version_num = 80301

NDEBUG = True    #调试模式指示器

desktopSize =  QApplication.desktop().screenGeometry()

class Configures(object):
#    INSTALLPATH = '/usr/lib/python3/dist-packages/xyplayer'
    LINE_HEIGHT = 28.11
    LINE_WRAP_WIDTH = 350
    NOERROR = -1
    URLERROR = -2
    TYPEERROR = -3
    PATHERROR = -4
    NONETERROR = -5
    IconsDir = 'xyplayer/icons/default'
    LicenseFile = 'LICENSE'    #协议文件路径
    if NDEBUG:
        IconsDir = '/usr/lib/python3/dist-packages/xyplayer/icons/default'
        LicenseFile = '/usr/lib/python3/dist-packages/xyplayer/LICENSE'
        
    NoLink = 'nolink'    #未获取在线MP3的链接之前用NoLink标记
    LocalMusicId = 'local'    #用于表示本地歌曲的musicId
    ZeroTime = '00:00'    #音乐时段显示的初值
    
    #软件更新的几个状态
    UpdateSucceed = 0
    UpdateStarted = 1
    UpdateDropped = 2
    UpdateFailed = 3
    
    #下载管理中的下载状态
    DownloadReady = -1    #准备下载
    DownloadCompleted = 0    #已完成下载
    Downloading = 1    #正在下载
    DownloadPaused = 2    #已暂停
    DownloadCancelled = 3    #已取消
    DownloadError = 4    #下载出错
    
    #系统自带的几张数据库表名
    PlaylistDefault = '默认列表'
    PlaylistFavorite = '我的收藏'
    PlaylistDownloaded = '我的下载'
    PlaylistOnline = '试听列表'
    BasicPlaylists = [PlaylistOnline, PlaylistDefault, PlaylistFavorite, PlaylistDownloaded]
    DownloadWorksTable = 'downloadworkstable'    #用来保存下载任务信息的数据库表
    PlaylistsManageTable = 'playlistsmanagetable'    #用来记录所有歌曲列表名
    
    #三种播放模式
    PlaymodeRandom = 0
    PlaymodeOrder = 1
    PlaymodeSingle = 2
    PlaymodeRandomText = '随机播放'
    PlaymodeOrderText = '顺序播放'
    PlaymodeSingleText = '单曲循环'
    
    homeDir = os.path.expanduser('~')
    cacheDir = os.path.join(homeDir, '.xyplayer')
    musicsDir = os.path.join(cacheDir, 'downloads')
    imagesDir = os.path.join(cacheDir, 'images')
    artistInfosDir = os.path.join(cacheDir, 'infos')
    debsDir = os.path.join(cacheDir, 'debs')
    lrcsDir = os.path.join(cacheDir, 'lrcs')
    settingFile = os.path.join(cacheDir, 'settings')
    DataBase = os.path.join(cacheDir, 'xyplayer_083.db')    #sqlite数据库文件
    changelog = os.path.join(cacheDir, 'changelog')
    
    @classmethod
    def check_dirs(cls):
        dirs = [cls.musicsDir, cls.imagesDir, cls.lrcsDir, cls.artistInfosDir, cls.debsDir]
        if not os.path.exists(cls.cacheDir):
            os.makedirs(cls.cacheDir)
        for dir in dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
        if not os.path.exists(Configures.DataBase):
            with open(Configures.DataBase, 'w') as f:
                f.close()
        if not os.path.exists(cls.settingFile):
            with open(cls.settingFile, 'w') as f:
                f.write(cls.musicsDir)
                f.close()

class SqlOperator(object):
    def __init__(self):
        dbOpened = self.createConnection()
        self.query = QSqlQuery()
        if dbOpened:
            self.createTables()
        else:
            print("无法连接到数据库：%s"%Configures.DataBase)            
        
    def createConnection(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(Configures.DataBase)
        return db.open()
    
    def createOnlineListTable(self):
        self.query.exec_("create table %s (paths varchar(65), title varchar(50), length varchar(10), album varchar(40), size varchar(20), \
        frequency integer, musicId varchar primary key, spare1 varchar, spare2 varchar, spare3 varchar, spare4 varchar, spare5 varchar)"%Configures.PlaylistOnline)        
    
    def createTable(self, tableName):
        self.query.exec_("create table %s (paths varchar(65) primary key, title varchar(50), length varchar(10), album varchar(40), size varchar(20), \
        frequency integer, musicId varchar, spare1 varchar, spare2 varchar, spare3 varchar, spare4 varchar, spare5 varchar)"%tableName)
    
    def renameTable(self, oldName, newName):
        self.query.exec_("alter table %s rename to %s"%(oldName, newName))
    
    def dropTable(self, tableDeleted):
        self.query.exec_("drop table %s"%tableDeleted)
    
    def createTables(self):
        self.query.exec_("create table %s (id integer primary key autoincrement, tableName varchar(50), spare1 varchar, spare2 varchar, spare3 varchar, spare4 varchar, spare5 varchar, spare6 varchar)"%Configures.PlaylistsManageTable)
        self.query.exec_("create table %s (id integer primary key autoincrement, title varchar(50), downloadedsize varchar(20), size varchar(20), album varchar(20), songLink varchar(30), musicPath varchar(30),\
        musicId varchar(10), status varchar(20), spare1 varchar, spare2 varchar, spare3 varchar, spare4 varchar, spare5 varchar, spare6 varchar)"%Configures.DownloadWorksTable )
        for index, tableName in enumerate(Configures.BasicPlaylists):
            self.query.exec_("insert into %s values(%i, '%s', Null, Null, Null, Null, Null, Null)"%(Configures.PlaylistsManageTable, index, tableName))
            if tableName == Configures.PlaylistOnline:
                self.createOnlineListTable()
            else:
                self.createTable(tableName)
            
Configures.check_dirs()
sqlOperator = SqlOperator()

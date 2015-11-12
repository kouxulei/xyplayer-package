# Copyright (C) 2015-2016 Zheng-Yejian <1035766515@qq.com>
# Use of this source code is governed by GPLv3 license that can be found
# in the LICENSE file.

import os
import shutil
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

__doc__ = '''This is a simple musicplayer that can search, play, download musics from the Internet.'''

app_name = 'xyplayer'
app_version = '0.8.4-2'
app_version_num = 80402

NDEBUG = True    #调试模式指示器

desktopSize =  QApplication.desktop().screenGeometry()

settings = QSettings('xyplayer', 'xysettings')
settingsFileName = settings.fileName()    #配置文件路径
print('Using configuration file: ', settingsFileName)
settingsDir = os.path.split(settingsFileName)[0]    #放置程序配置文件的目录

class Configures(object):
    InstallPath = '/usr/lib/python3/dist-packages/xyplayer'
    IconsDir = 'xyplayer/icons/default'
    LicenseFile = 'LICENSE'    #协议文件路径
    if NDEBUG:
        IconsDir = os.path.join(InstallPath, 'icons/default')
        LicenseFile = os.path.join(InstallPath, LicenseFile)
        
    NoLink = 'nolink'    #未获取在线MP3的链接之前用NoLink标记
    LocalMusicId = 'local'    #用于表示本地歌曲的musicId
    ZeroTime = '00:00'    #音乐时段显示的初值
    Hyphen = '._.'    #歌手名与歌曲名的连字符，三者组成歌曲的标题
    MusicMp3 = 'mp3'

    #程序中可能产生的几种错误类型
    NoError = 0
    UrlError = 1
    PathError = 2
    DisnetError = 3
    
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
    
    #获取歌词内容的几个状态
    LyricSucceed = 0
    LyricNetError = 1
    LyricNone = 2
    
    #系统自带的几张数据库表名
    PlaylistDefault = '默认列表'
    PlaylistFavorite = '我的收藏'
    PlaylistDownloaded = '我的下载'
    PlaylistOnline = '试听列表'
    BasicPlaylists = (PlaylistOnline, PlaylistDefault, PlaylistFavorite, PlaylistDownloaded)
    DownloadWorksTable = 'downloadworkstable'    #用来保存下载任务信息的数据库表
    PlaylistsManageTable = 'playlistsmanagetable'    #用来记录所有歌曲列表名
    
    #三种播放模式
    PlaymodeRandom = 0
    PlaymodeOrder = 1
    PlaymodeSingle = 2
    PlaymodeRandomText = '随机播放'
    PlaymodeOrderText = '顺序播放'
    PlaymodeSingleText = '单曲循环'
    
    #选项页面的各个分页名
    SettingsBasicTab = '常规设置'
    SettingsDownloadTab = '下载设置'
    SettingsDesktopLyricTab = '桌面歌词'
    
    #选项页面常规设置“关闭主面板时”的两种行为
    SettingsHide = 0
    SettingsExit = 1
    SettingsFontForms = ('常规', '粗体', '斜体', '粗斜')
    SettingsFontSizes = tuple(range(20, 65, 5))
    SettingsNormColors = (
        'aqua', 'black', 'blue', 'fuchsia', 
        'gray', 'green', 'lime', 'maroon', 
        'navy', 'olive', 'orange', 'purple', 
        'red', 'silver', 'teal', 'white', 'yellow')
    SettingsRange1 = tuple(range(18, 31))
    SettingsRange2 = tuple(range(12, 25))
    
    HomeDir = os.path.expanduser('~')
    CacheDir = os.path.join(HomeDir, '.xyplayer')
    MusicsDir = os.path.join(CacheDir, 'downloads')
    ImagesDir = os.path.join(CacheDir, 'images')
    ArtistinfosDir = os.path.join(CacheDir, 'infos')
    DebsDir = os.path.join(CacheDir, 'debs')
    LrcsDir = os.path.join(CacheDir, 'lrcs')
    DataBase = os.path.join(settingsDir, 'xyplayer_083.db')    #sqlite数据库文件
    Changelog = os.path.join(settingsDir, 'changelog')
    
    @classmethod
    def check_dirs(cls):
        cls.correct_file_positions()
        dirs = [cls.MusicsDir, cls.ImagesDir, cls.LrcsDir, cls.ArtistinfosDir, cls.DebsDir]
        if not os.path.exists(cls.CacheDir):
            os.makedirs(cls.CacheDir)
        for dir in dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
        if not os.path.exists(Configures.DataBase):
            with open(Configures.DataBase, 'w') as f:
                f.close()
    
    @classmethod
    def correct_file_positions(cls):
        """将原来放在.xyplayer目录下的数据库文件等转移到.config/xyplayer目录中。"""
        oldDatabasePath = os.path.join(cls.CacheDir, 'xyplayer_083.db')
        oldChangelogPath = os.path.join(cls.CacheDir, 'changelog')
        if not os.path.exists(settingsDir):
            os.makedirs(settingsDir)
        if os.path.exists(oldDatabasePath):
            shutil.move(oldDatabasePath, cls.DataBase)
        if os.path.exists(oldChangelogPath):
            shutil.move(oldChangelogPath, cls.Changelog)
    
    @classmethod
    def clean_old_settings_file(cls):
        """读取原来放在.xyplayer目录下的settings文件中的值，然后清理这个文件。"""
        oldSettingsFile = os.path.join(cls.CacheDir, 'settings')
        if os.path.exists(oldSettingsFile):
            with open(oldSettingsFile, 'r') as f:
                downloadPathSetted = f.read().strip()
                f.close()
            os.remove(oldSettingsFile)
            return downloadPathSetted
        return None

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

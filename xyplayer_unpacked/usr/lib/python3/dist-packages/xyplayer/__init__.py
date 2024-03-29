# Copyright (C) 2015-2016 Zheng-Yejian <1035766515@qq.com>
# Use of this source code is governed by GPLv3 license that can be found
# in the LICENSE file.

"""
This is a simple musicplayer that can search, play, download musics from the Internet and manage local music files.
"""

import os
import sys
import shutil
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings

app_name = 'xyplayer'
app_version = '0.8.7-2'
app_version_num = 80702

NDEBUG = True    #调试模式指示器
if len(sys.argv) > 1 and sys.argv[1] in ['-D', '-d']:
    NDEBUG = False
    print('Debugging...')

class Configures(object):
    DesktopSize =  QApplication.desktop().screenGeometry()
    WindowWidth = 930
    WindowHeight = 620
    
    Settings = QSettings(app_name, 'xysettings')
    SettingsFileName = Settings.fileName()    #配置文件路径
    print('Using configuration file: ', SettingsFileName)
    SettingsDir = os.path.split(SettingsFileName)[0]    #放置程序配置文件的目录
    
    InstallPath = os.path.join(os.path.split(sys.argv[0])[0], 'xyplayer')
    if NDEBUG:
        InstallPath = '/usr/lib/python3/dist-packages/xyplayer'
    IconsDir = os.path.join(InstallPath, 'icons/default')
    LicenseFile = os.path.join(InstallPath, 'licenses/GPLv3')
    QssFileDefault = os.path.join(InstallPath, 'qss/default.qss')
        
    NoLink = 'nolink'    #未获取在线MP3的链接之前用NoLink标记
    LocalMusicId = 'local'    #用于表示本地歌曲的musicId
    ZeroTime = '00:00'    #音乐时段显示的初值
    Hyphen = '._.'    #歌手名与歌曲名的连字符，三者组成歌曲的标题
    MusicMp3 = 'mp3'
    NumSearchOneTime = 14    #一次搜索返回的结果数目

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
    DownloadLogFile = os.path.join(SettingsDir, 'downloadworksinfoslog')
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
    
    #歌曲列表相关的参数
    PlaylistsDir = os.path.join(SettingsDir, 'playlists')
    PlaylistsExt = '.xypl'    #列表文件的后缀名
    PlaylistKeyQueue= 'queue'    #歌曲列表结构的两个键
    PlaylistKeyGroup = 'group'
    PlaylistDefault = '默认列表'
    PlaylistFavorite = '我的收藏'
    PlaylistDownloaded = '我的下载'
    PlaylistOnline = '试听列表'
    PlaylistsManager = os.path.join(SettingsDir, 'playlistsmanager')
    BasicPlaylists = (PlaylistOnline, PlaylistDefault, PlaylistFavorite, PlaylistDownloaded)
    DownloadWorksTable = 'downloadworkstable'    #用来保存下载任务信息的数据库表
    PlaylistsManageTable = 'playlistsmanagetable'    #用来记录所有歌曲列表名
    
    #管理歌曲播放次数等信息的参数
    PlaybackHistoryLog = os.path.join(SettingsDir, 'playback_history.csv')
    HistoryLoggedItems = ['date', 'musicfilename', 'musicname', 'artistname', 
        'album', 'totaltime', 'playedtime', 'playlist', 'path', 
        'markedfaverite', 'sourcetrace', 'playmode', 'clickplay', 
        'reserved1', 'reserved2', 'reserved3', 'reserved4', 'reserved5']
    SonginfosManager = os.path.join(SettingsDir, 'songinfosmanager')
    SonginfosFreq = 'freq'
    SonginfosStars = 'stars'
    SonginfosNearPlayedDate = 'nearplayeddate'
    SonginfosMusicName = 'musicname'
    SonginfosArtistName = 'artistname'
    SonginfosTotalTime = 'totaltime'
    SonginfosAlbum = 'album'
    SonginfosNearPlayedList = 'nearplayedlist'
    SonginfosPlayedTimeSpans = 'playedtimespans'
    SonginfosPlayedTimeSpanMax = 'playedtimespanmax'
    SonginfosNearPlayedTime = 'nearplayedtime'
    SonginfosClickPlayTimes = 'clickplaytimes'
    
    #三种播放模式
    Playmodes = ('random', 'order', 'single')
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
        'aqua', 'black', 'blue', 'fuchsia', 'cyan', 'chocolate', 
        'gray', 'green', 'lime', 'maroon', 'gold', 'deepskyblue', 
        'navy', 'olive', 'orange', 'purple', 'origin', 'violet', 
        'red', 'silver', 'teal', 'white', 'yellow', 'darkred')
    SettingsRange1 = tuple(range(18, 31))
    SettingsRange2 = tuple(range(12, 25))
    
    HomeDir = os.path.expanduser('~')
    CacheDir = os.path.join(HomeDir, '.xyplayer')
    MusicsDir = os.path.join(CacheDir, 'downloads')
    ImagesDir = os.path.join(CacheDir, 'images')
    ArtistinfosDir = os.path.join(CacheDir, 'infos')
    DebsDir = os.path.join(CacheDir, 'debs')
    LrcsDir = os.path.join(CacheDir, 'lrcs')
    Changelog = os.path.join(SettingsDir, 'changelog')
    
    @classmethod
    def check_dirs(cls):
        cls.correct_file_positions()
        dirs = [cls.MusicsDir, cls.ImagesDir, cls.LrcsDir, cls.ArtistinfosDir, cls.DebsDir, cls.PlaylistsDir]
        if not os.path.exists(cls.CacheDir):
            os.makedirs(cls.CacheDir)
        for dir in dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
    
    @classmethod
    def correct_file_positions(cls):
        """将原来放在.xyplayer目录下的数据库文件等转移到.config/xyplayer目录中。"""
        oldChangelogPath = os.path.join(cls.CacheDir, 'changelog')
        if not os.path.exists(cls.SettingsDir):
            os.makedirs(cls.SettingsDir)
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

Configures.check_dirs()

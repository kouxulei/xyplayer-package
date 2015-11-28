import os
from xyplayer import Configures

class IconsHub(object):
    """用于收集图标路径的类"""
    @classmethod
    def set_attrs(cls, dict):
        def _get_icon_path(iconName, dir=Configures.IconsDir):
            return os.path.join(dir, '%s.png'%iconName)
        for icon, value in dict.items():
            iconPath = _get_icon_path(value)
            setattr(IconsHub, icon, iconPath)

iconsDict = {
    'DownloadPause': 'download_pause',     #下载暂停时的图标
    'DownloadStart': 'download_start',     #下载开始时的图标
    'DownloadCompleted':  'download_completed',    #下载完成
    'DownloadKill':  'download_kill',    #取消下砸任务按钮图标
    'DownloadPath': 'download_path', 
    'Back': 'back', 
    'Refresh': 'refresh', 
    'Close': 'close', 
    'ShowMainWindow': 'show_main_window', 
    'DesktopLyric': 'desktop_lyric', 
    'ControlPlay': 'control_play', 
    'ControlPause': 'control_pause', 
    'ControlPrevious': 'control_previous', 
    'ControlNext': 'control_next', 
    'ControlStop': 'control_stop', 
    'Anonymous': 'anonymous', 
    'Info': 'info', 
    'Xyplayer': 'xyplayer',    
    'Functions': 'functions', 
    'PlaymodeRandom': 'playmode_random',     #随机循环
    'PlaymodeOrder': 'playmode_order',    #顺序循环
    'PlaymodeSingle': 'playmode_single',     #单曲循环
    'PlaymodeSelected': 'playmode_selected',
    'PlaymodeSelectedNo': 'playmode_selected_no', 
    'Background': 'background',     #背景图
    'CloseButton': 'close_button', 
    'MinButton': 'min_button', 
    'HideButton': 'hide_button', 
    'GlobalBack': 'global_back', 
    'GlobalMainpage': 'global_mainpage', 
    'GlobalFunctions': 'global_functions', 
    'Favorites': 'favorites', 
    'FavoritesNo': 'favorites_no', 
    'Settings': 'settings', 
    'ExitmodeTimeout': 'exitmode_timeout', 
    'ExitmodeCountout': 'exitmode_countout', 
    'Functions': 'functions', 
    'Search': 'search',
    'SearchAlbum': 'search_album', 
    'SearchArtist': 'search_artist', 
    'SearchMusictitle': 'search_musictitle', 
    'Delete': 'delete', 
    'Preference': 'preference', 
    'HeadIcon': 'head_icon', 
    'RemovePlaylist': 'download_kill'
}

IconsHub.set_attrs(iconsDict)

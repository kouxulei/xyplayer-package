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
    'Download': 'download', 
    'DownloadPause': 'download_pause',     #下载暂停时的图标
    'DownloadStart': 'download_start',     #下载开始时的图标
    'DownloadCompleted':  'download_completed',    #下载完成
    'DownloadKill':  'download_kill',    #取消下砸任务按钮图标
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
    'PlaymodeRandom': 'playmode_random',     #随机循环
    'PlaymodeOrder': 'playmode_order',    #顺序循环
    'PlaymodeSingle': 'playmode_single',     #单曲循环
    'PlaymodeSelected': 'playmode_selected',
    'PlaymodeSelectedNo': 'playmode_selected_no', 
    'Background': 'background',     #背景图
    'CloseButton': 'close_button', 
    'MinButton': 'min_button', 
    'HideButton': 'hide_button', 
    'Home': 'home', 
    'Favorites': 'favorites', 
    'FavoritesNo': 'favorites_no', 
    'Exitmode': 'exitmode', 
    'Functions': 'functions', 
    'Musics': 'musics', 
    'Search': 'search',
    'SearchAlbum': 'search_album', 
    'SearchArtist': 'search_artist', 
    'SearchMusictitle': 'search_musictitle', 
    'AboutButton': 'about_button', 
    'LyricOffset': 'lyric_offset', 
    'PlaylistAdd': 'playlist_add', 
    'PlaylistDelete': 'playlist_delete', 
    'PlaylistFold': 'playlist_fold', 
    'PlaylistRename': 'playlist_rename', 
    'PlaylistUnfold': 'playlist_unfold', 
    'PlaylistWidgetHover': 'playlist_widget_hover', 
    'PreferenceButton': 'preference_button', 
    'RemovePlaylist': 'download_kill', 
    'Update': 'update', 
    'Volume': 'volume', 
    'VolumeMuted': 'volume_muted'
}

IconsHub.set_attrs(iconsDict)

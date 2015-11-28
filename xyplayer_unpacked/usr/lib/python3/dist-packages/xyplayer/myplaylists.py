import os
from xyplayer import Configures
from xyplayer.utils import (read_music_info, composite_playlist_path_use_name, wrap_playlist_datas, 
    wrap_datas, parse_json_file, write_into_disk, rename_playlist, remove_playlist)

class DownloadWorksModel(object):
    def __init__(self):
        self.logFile = Configures.DownloadLogFile
        if not os.path.exists(self.logFile):
            write_into_disk(self.logFile, wrap_datas([]))
        try:
            self.infosList = parse_json_file(self.logFile)
        except:
            self.infosList = []
    
    def add_record(self, songLink, musicPath, title, album , musicId, size, downloadedsize, status=Configures.DownloadPaused):
        self.infosList.append([songLink, musicPath, title, album , musicId, size, downloadedsize, status]) 
    
    def get_length(self):
        return len(self.infosList)
    
    def commit_records(self):
        write_into_disk(self.logFile, wrap_datas(self.infosList))
    
    def get_work_info_at_row(self, row):
        return self.infosList[row][:6]
    
    def clear_log_file(self):
        write_into_disk(self.logFile, wrap_datas([]))
        self.infosList.clear()

class PlaylistBasic(object):
    def __init__(self):
        self.itemsQueue = []
        self.infosGroup = {}
    
    def copy_to(self, playlist):
        playlist.itemsQueue = self.itemsQueue.copy()
        playlist.infosGroup = self.infosGroup.copy()
    
    def get_value_from_dict(self, dict):
        self.itemsQueue = dict.get(Configures.PlaylistKeyQueue, [])
        self.infosGroup = dict.get(Configures.PlaylistKeyGroup, {})
    
    def get_items_queue(self):
        return self.itemsQueue
    
    def get_item_from_queue(self, row):
        return self.itemsQueue[row]
    
    def get_infos_group(self):
        return self.infosGroup
    
    def get_item_index(self, item):
        try:
            return self.itemsQueue.index(item)
        except ValueError:
            return self.length()
    
    def length(self):
        return len(self.itemsQueue)
    
    def clear_list(self):
        self.itemsQueue.clear()
        self.infosGroup.clear()
    
    def get_record_at(self, index):
        id = self.itemsQueue[index]
        return self.infosGroup[id]
    
    def add_item(self, id, info):
        self.itemsQueue.append(id)
        self.infosGroup[id] = info
    
    def remove_item_at(self, index, deleteFlag=False):
        if deleteFlag:
            path = self.itemsQueue[index]
            if os.path.exists(path):
                os.remove(path)
        del self.infosGroup[self.itemsQueue[index]]
        del self.itemsQueue[index]
    
    def get_wrap_playlist_datas(self):
        return wrap_playlist_datas(self.itemsQueue, self.infosGroup)
    
    def get_infos_at(self, row):
        return self.infosGroup[self.itemsQueue[row]]

class Playlist(PlaylistBasic):
    def __init__(self):
        super(Playlist, self).__init__()
        self.currentRow = -1
        self.listName = ''
        self.playlistFile = ''
    
    def copy(self):
        playlist = Playlist()
        playlist.currentRow = self.currentRow
        playlist.listName = self.listName
        playlist.playlistFile = self.playlistFile
        PlaylistBasic.copy_to(self, playlist)
        return playlist
    
    def set_current_row(self, row):
        self.currentRow = row
    
    def fill_list(self, listName):
        self.listName = listName
        self.set_current_row(-1)
        self.playlistFile = composite_playlist_path_use_name(listName)
        if not os.path.exists(self.playlistFile):
            print('列表"%s"不存在'%listName)
            self.clear_list()
            self.listName = ''
            self.playlistFile = ''
            return
        try: 
            self.get_value_from_dict(parse_json_file(self.playlistFile))
        except ValueError:
            self.clear_list()
            print('加载列表内容出错！')
    
    def clear_list(self):
        PlaylistBasic.clear_list(self)
        self.set_current_row(-1)
    
    def get_name(self):
        return self.listName
    
    def set_name(self, name):
        self.listName = name
    
    def get_current_row(self):
        return self.currentRow
    
    def add_record(self, id, title, totalTime, album, path, size, musicId=Configures.LocalMusicId, freq=0):
        self.add_item(id, [title, totalTime, album, path, size, musicId, freq, 0, 0, 0, 0, 0])
    
    def get_music_path_at(self, row):
        return self.get_infos_at(row)[3]
    
    def get_music_title_at(self, row):
        return self.get_infos_at(row)[0]
    
    def get_music_album_at(self, row):
        return self.get_infos_at(row)[2]

    def get_music_id_at(self, row):
        return self.get_infos_at(row)[5]
    
    def get_music_time_at(self, row):
        return self.get_infos_at(row)[1]

    def add_item_from_path(self, path):
        title, album, totalTime =  read_music_info(path)
        size = os.path.getsize(path)
        self.add_record(path, title, totalTime, album, path, size)   
        return title, totalTime 
    
    def get_titles(self):
        titles = []
        for i in range(self.length()):
            titles.append(self.get_music_title_at(i))
        return titles
    
    def set_music_path_at(self, row, path):
        self.get_infos_at(row)[3] = path
        self.commit_records()
    
    def set_music_time_at(self, row, time):
        self.get_infos_at(row)[1] = time
        self.commit_records()
    
    def commit_records(self):
        if os.path.exists(self.playlistFile):
            datas = self.get_wrap_playlist_datas()
            write_into_disk(self.playlistFile, datas)
            print('数据提交成功！')
        else:
            print('未创建列表：%s'%self.listName)

class PlaylistsManager(object):
    """管理歌曲列表的结构。"""
    def __init__(self):
        self.playlistNames = []
        self.check_exists_playlists()
    
    def get_list_names_from_file(self):
        if not os.path.exists(Configures.PlaylistsManager):
            write_into_disk(Configures.PlaylistsManager, wrap_datas())
            return Configures.BasicPlaylists
        return tuple(parse_json_file(Configures.PlaylistsManager))
    
    def check_exists_playlists(self):
        existsNames = self.get_list_names_from_file()
        for listName in Configures.BasicPlaylists:
            self.create_a_playlist(listName)
        for listName in existsNames:
            if listName not in Configures.BasicPlaylists:
                self.create_a_playlist(listName)
        self.clean_other_files_in_playlists_dir()
    
    def clean_other_files_in_playlists_dir(self):
        for item in os.listdir(Configures.PlaylistsDir):
            link = os.path.join(Configures.PlaylistsDir, item)
            if os.path.isdir(link):
                os.removedirs(link)
            elif item[-5:] != Configures.PlaylistsExt or os.path.splitext(item)[0] not in self.playlistNames:
                os.remove(link)
    
    def get_play_list_count(self):
        return len(self.playlistNames)
    
    def get_play_list_names(self):
        return self.playlistNames
    
    def commit_records(self):
        write_into_disk(Configures.PlaylistsManager, wrap_datas(self.playlistNames))
    
    def create_a_playlist(self, listName):
        playlistFile = composite_playlist_path_use_name(listName)
        if not os.path.exists(playlistFile):
            write_into_disk(playlistFile, wrap_playlist_datas())
        self.playlistNames.append(listName)
        self.commit_records()
    
    def rename_a_playlist(self, oldName, newName):
        self.playlistNames[self.playlistNames.index(oldName)] = newName
        rename_playlist(oldName, newName)
        self.commit_records()
    
    def remove_a_playlist(self, name):
        del self.playlistNames[self.playlistNames.index(name)]
        remove_playlist(name)
        self.commit_records()
            
playlistsManager = PlaylistsManager()

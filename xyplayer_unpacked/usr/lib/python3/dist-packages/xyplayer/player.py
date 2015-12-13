import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import QUrl
from xyplayer import Configures
from xyplayer.myicons import IconsHub
from xyplayer.mythreads import DownloadLrcThread
from xyplayer.urlhandle import SearchOnline
from xyplayer.mysettings import globalSettings
from xyplayer.utils import (parse_lrc, get_full_music_name_from_title,composite_lyric_path_use_title, 
    get_artist_and_musicname_from_title)
from xyplayer.player_ui import PlayerUi

class Player(PlayerUi):
    def __init__(self, parent = None):
        super(Player, self).__init__(parent)
        self.initial_parameters()
        self.create_connections()

    def create_connections(self):      
        PlayerUi.create_connections(self)
        self.playbackPanel.update_window_lyric_signal.connect(self.update_lyric)
        self.playbackPanel.current_media_changed_signal.connect(self.current_media_changed)
        self.playbackPanel.muted_changed_signal.connect(self.managePage.set_muted)
        self.playbackPanel.media_player_notify_signal.connect(self.syc_lyric)
        
        self.managePage.changeVolume.connect(self.playbackPanel.set_volume)
        self.managePage.changeMuting.connect(self.playbackPanel.set_muted)

        self.playbackPanel.mark_favorite_completed_signal.connect(self.marked_favorite_completed)
        self.playbackPanel.playmode_changed_signal.connect(self.playmode_changed)

        self.managePage.updatePanel.updatingStateChanged.connect(self.updating_state_changed)
        self.managePage.playlist_removed_signal.connect(self.playlist_removed)
        self.managePage.playlist_renamed_signal.connect(self.playlist_renamed)
        self.managePage.current_table_changed_signal.connect(self.current_table_changed)
        self.managePage.playlistWidget.play_music_at_row_signal.connect(self.playbackPanel.set_media_source_at_row)
        self.managePage.playlistWidget.play_or_pause_signal.connect(self.playbackPanel.decide_to_play_or_pause)
        self.managePage.playlistWidget.playlist_changed_signal.connect(self.switch_to_new_playing_list)
        self.managePage.playlistWidget.musics_added_signal.connect(self.musics_added)
        self.managePage.playlistWidget.musics_removed_signal.connect(self.musics_removed)
        self.managePage.playlistWidget.musics_cleared_signal.connect(self.musics_cleared)
        self.managePage.playlistWidget.musics_marked_signal.connect(self.musics_marked)
        self.managePage.playlistWidget.download_signal.connect(self.online_list_song_download)
        self.managePage.playlistWidget.tag_values_changed_signal.connect(self.tag_values_changed)
        self.managePage.downloadPage.work_complete_signal.connect(self.refresh_playlist_downloaded)
        self.managePage.downloadPage.titleLabel.clicked.connect(self.open_download_dir)
        self.managePage.searchFrame.listen_online_signal.connect(self.begin_to_listen)
        self.managePage.searchFrame.add_to_download_signal.connect(self.add_to_download)
        self.managePage.searchFrame.add_bunch_to_list_succeed.connect(self.refresh_playlist_online)

        self.managePage.settingsFrame.download_dir_changed.connect(self.set_new_download_dir)
        self.managePage.settingsFrame.desktop_lyric_style_changed.connect(self.update_desktop_lyric_style)
        self.managePage.settingsFrame.close_button_act_changed.connect(self.set_new_close_button_act)
        self.managePage.settingsFrame.window_lyric_style_changed.connect(self.set_new_window_lyric_style)
        self.managePage.exitmodePanel.timeoutDialog.time_out_signal.connect(self.close)
        self.managePage.lyricText.lyric_offset_changed_signal.connect(self.lyric_offset_changed)
    
    def set_new_download_dir(self, newDir):
        self.playbackPanel.set_download_dir(newDir)
        self.managePage.set_download_dir(newDir)
    
    def set_new_close_button_act(self, act):
        self.closeButtonAct = act
    
    def update_desktop_lyric_style(self):
        self.playbackPanel.desktopLyric.set_color(self.managePage.settingsFrame.get_lyric_colors())
        self.playbackPanel.desktopLyric.set_font_style(*self.managePage.settingsFrame.get_lyric_font_styles())
    
    def set_new_window_lyric_style(self):
        params = self.managePage.settingsFrame.get_window_lyric_params()
        self.managePage.lyricText.set_new_window_lyric_style(params)
        if len(self.lyricDict) and self.managePage.lyricText.document.blockCount():
            self.managePage.lyricText.set_html(self.j, self.lyricDict, self.t)
        
    def initial_parameters(self):
        self.closeButtonAct = globalSettings.CloseButtonAct
        self.forceCloseFlag = False    #跳过确认窗口强制关闭程序的标志
        self.lyricOffset = 0
        self.cTime = self.totalTime = Configures.ZeroTime
        self.currentTable = Configures.PlaylistDefault
        self.lyricDict = {}
        self.j = -5
        self.set_new_download_dir(globalSettings.DownloadfilesPath)
        self.switch_to_new_playing_list()

    def open_download_dir(self, name):
        """点击下载任务标题栏打开下载目录。"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.managePage.get_download_dir()))

    def refresh_playlist_online(self):
        """当批量添加试听歌曲到“在线试听”歌单后更新显示"""
        if self.playbackPanel.playlist.get_name() == Configures.PlaylistOnline:
            self.playlist_refresh_with_name(Configures.PlaylistOnline)
        if self.currentTable == Configures.PlaylistOnline and not self.managePage.playlistTableUnfold.isHidden():
            self.managePage.playlistWidget.set_playlist_use_name(self.currentTable)

    def refresh_playlist_downloaded(self):
        if self.playbackPanel.playlist.get_name() == Configures.PlaylistDownloaded:
            self.playlist_refresh_with_name(Configures.PlaylistDownloaded)
        if self.currentTable == Configures.PlaylistDownloaded:
            self.managePage.playlistWidget.set_playlist_use_name(Configures.PlaylistDownloaded)
        self.managePage.downloadPage.remove_work_from_download_list(self.managePage.downloadPage.completedWorkNames)

    def tag_values_changed(self, row, oldTitle, title, album):
        widget = self.managePage.playlistWidget
        playlist = widget.get_playlist()
        if widget.get_playing_used_state():
            self.playbackPanel.playlist.set_music_title_at(row, title, False)
            self.playbackPanel.playlist.set_music_album_at(row, album, False)
            self.playbackPanel.playlist.commit_records()
            if row == self.playbackPanel.currentSourceRow:
                artistName, musicName = get_artist_and_musicname_from_title(title)
                self.playbackPanel.playAction.setText(musicName)
                self.playbackPanel.musicTitleLabel.setText(title)
        if playlist.get_name() == Configures.PlaylistFavorite:
            index = self.playbackPanel.lovedSongs.index(oldTitle)
            self.playbackPanel.lovedSongs[index] = title
        thread = DownloadLrcThread(((title, Configures.LocalMusicId), ))
        thread.setDaemon(True)
        thread.setName("downloadLrc")
        thread.start()

    def musics_added(self, showAddInfo):
        widget = self.managePage.playlistWidget
        playlist = widget.get_playlist()
        newAddedTitles = []
        if widget.get_playing_used_state():
            self.playlist_modified()
        for index in widget.addedIndexes:
            title = playlist.get_music_title_at(index)
            newAddedTitles.append((title, Configures.LocalMusicId))
            if playlist.get_name() == Configures.PlaylistFavorite:
                self.playbackPanel.lovedSongs.append(title)
        if playlist.get_name() == Configures.PlaylistFavorite:
            self.playbackPanel.check_favorite()
        if showAddInfo:
            if len(newAddedTitles):
                thread = DownloadLrcThread(newAddedTitles)
                thread.setDaemon(True)
                thread.setName("downloadLrc")
                thread.start()
            addCount = len(widget.files)
            newAddedCount = len(newAddedTitles)
            text = "您选择了%s首歌曲！\n新添加了%s首歌曲，其他歌曲已在列表中不被添加！"%(addCount, newAddedCount)
            if newAddedCount >0 and addCount == newAddedCount:
                text = "已添加%s首歌曲!"%newAddedCount
            if newAddedCount == 0:
                text = "选择的歌曲已在列表中！"
            QMessageBox.information(self, "添加完成", text)   

    def musics_removed(self):
        widget = self.managePage.playlistWidget
        playlist = widget.get_playlist()
        if widget.removedIndexes:
            if widget.get_playing_used_state():
                self.playlist_modified()
                self.managePage.playlistWidget.select_row()
                if self.playbackPanel.playlist.get_current_row()  < 0:
                    self.ui_initial()
            for row in widget.removedIndexes:
                if playlist.get_name() == Configures.PlaylistFavorite:
                    del self.playbackPanel.lovedSongs[row] 
            if playlist.get_name() == Configures.PlaylistFavorite:
                self.playbackPanel.check_favorite()

    def musics_cleared(self):
        widget = self.managePage.playlistWidget
        playlist = widget.get_playlist()
        if widget.get_playing_used_state():
            self.playlist_modified()
            self.ui_initial()
        if playlist.get_name() == Configures.PlaylistFavorite:
            self.playbackPanel.lovedSongs.clear() 
            self.playbackPanel.favoriteButton.setIcon(QIcon(IconsHub.FavoritesNo))
    
    def musics_marked(self):
        widget = self.managePage.playlistWidget
        self.playbackPanel.musics_marked(widget)

    def marked_favorite_completed(self):
        if self.managePage.playlistWidget.get_playlist().get_name() == Configures.PlaylistFavorite:
            self.managePage.playlistWidget.set_playlist_use_name(Configures.PlaylistFavorite)   

    def begin_to_listen(self, title, album, songLink, musicId):
        if not songLink:
            QMessageBox.critical(self, '错误', '链接为空，无法播放！')
            return
        widget = self.managePage.playlistWidget
        widget.set_playlist_use_name(Configures.PlaylistOnline)
        playlist = self.managePage.playlistWidget.playlist
        k = playlist.get_item_index(musicId)
        if k == playlist.length():
            widget.add_record_with_full_info(musicId, title, Configures.ZeroTime, album, songLink, 0, musicId)
            playlist.commit_records()
            self.refresh_playlist_online()
        else:
            if self.playbackPanel.playlist.get_name() == Configures.PlaylistOnline and self.playbackPanel.currentSourceRow == k:
                return
        widget.double_click_to_play_with_row(k)

    def add_to_download(self):
        for songInfoList in self.managePage.searchFrame.readyToDownloadSongs:
            songLink = songInfoList[0]
            musicPath = songInfoList[1]
            title = songInfoList[2]
            album = songInfoList[3]
            musicId = songInfoList[4]
            self.managePage.downloadPage.add_a_download_work(songLink, musicPath, title, album, musicId, 0, self.managePage.get_threading_lock())

    def online_list_song_download(self):
        widget = self.managePage.playlistWidget
        playlist = widget.get_playlist()
        selecteds = widget.selectedIndexes()
        isExistsSongs = []
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                songLink = playlist.get_music_path_at(row)
                title = playlist.get_music_title_at(row)
                musicId = playlist.get_music_id_at(row)
                album = playlist.get_music_album_at(row)
                musicName = get_full_music_name_from_title(title)
                musicPath = os.path.join(self.managePage.get_download_dir(), musicName)
                musicPathO = os.path.join(Configures.MusicsDir, musicName)
                if  os.path.exists(musicPath):
                    isExistsSongs.append('%s : %s'%(title, musicPath))
                    continue
                if os.path.exists(musicPathO):
                    isExistsSongs.append('%s : %s'%(title, musicPathO))
                    continue
                self.managePage.downloadPage.add_a_download_work(songLink, musicPath, title, album, musicId, 0, self.managePage.get_threading_lock())
        if len(isExistsSongs):
            existsSongs = '\n'.join(isExistsSongs)
            QMessageBox.information(self, "提示", 
                "以下歌曲已在下载目录中不再进行下载，您可以在不联网的情况下点击在线列表播放！\n%s"%existsSongs)

    def syc_lyric(self, currentTime):
        """同步歌词"""
        if len(self.lyricDict) and self.managePage.lyricText.document.blockCount():
            if currentTime+self.lyricOffset <= self.t[0]:
                self.managePage.lyricText.set_html(0, self.lyricDict, self.t)
                self.playbackPanel.desktopLyric.set_text(self.lyricDict[self.t[0]])
            else:
                for i in range(len(self.t) - 1):
                    if self.t[i] < currentTime+self.lyricOffset and self.t[i + 1] > currentTime+self.lyricOffset and i!= self.j:
                        self.j = i
                        text = self.lyricDict[self.t[i]]
                        self.managePage.lyricText.set_html(i, self.lyricDict, self.t)
                        if not self.playbackPanel.desktopLyric.isHidden() and self.playbackPanel.desktopLyric.text() != text:
                            self.playbackPanel.desktopLyric.set_text(text)
                        break

    def current_media_changed(self):  
        self.managePage.playlistWidget.select_row()
        self.check_mountout_state()

    def check_mountout_state(self):
        if self.managePage.exitmodePanel.mountoutDialog.countoutMode:
            if not self.managePage.exitmodePanel.mountoutDialog.remainMount:
                self.close()
            self.managePage.exitmodePanel.mountoutDialog.remainMount -= 1
            self.managePage.exitmodePanel.mountoutDialog.spinBox.setValue(self.managePage.exitmodePanel.mountoutDialog.remainMount)

    def update_lyric(self, title, musicId):
        self.lyricOffset = 0     
        self.lrcPath = composite_lyric_path_use_title(title)
        lyric = SearchOnline.get_lrc_contents(title, musicId)
        if lyric == Configures.LyricNetError:
            self.playbackPanel.desktopLyric.set_text("网络出错，无法搜索歌词！")
            self.lyricDict.clear()
            self.managePage.lyricText.url_error_lyric()
        elif lyric == Configures.LyricNone:
            self.playbackPanel.desktopLyric.set_text("搜索不到匹配歌词！")
            self.lyricDict.clear()
            self.managePage.lyricText.no_matched_lyric()
        else:
            self.lyricOffset, self.lyricDict = parse_lrc(lyric)
            self.lyricDict[3000000] = ''
            self.t = sorted(self.lyricDict.keys())
            self.managePage.lyricText.set_lyric_offset(self.lyricOffset, self.lyricDict, self.lrcPath)

    def lyric_offset_changed(self, offset):
        self.lyricOffset = offset

    def current_table_changed(self, tableName):
        self.currentTable = tableName

    def updating_state_changed(self, updateState):
        """处理不同的软件更新状态。"""
        if updateState == Configures.UpdateStarted:
            self.playbackPanel.stop_music()
            self.hide()
        else:
            closeFlag = False
            if updateState == Configures.UpdateSucceed:
                closeFlag = True
                tips = '更新成功，请重新打开播放器！'
            elif updateState == Configures.UpdateDropped:
                tips = '更新已被放弃！'
            elif updateState == Configures.UpdateFailed:
                tips = '更新失败，请检查是否成功下载新的软件包！'
            QMessageBox.information(self, '提示', tips)
            if closeFlag:
                self.force_close()
            else:
                self.show()

    def switch_to_new_playing_list(self):
        self.playlist_modified()
        self.playbackPanel.set_media_source_at_row(self.playbackPanel.playlist.get_current_row())
    
    def playlist_modified(self):
        self.playbackPanel.set_playlist(self.managePage.playlistWidget.get_playlist())
        self.managePage.playlistWidget.set_playing_status(self.playbackPanel.playlist)    
   
    def playlist_refresh_with_name(self, listName):
        self.playbackPanel.playlist.fill_list(listName)
        self.managePage.playlistWidget.set_playing_status(self.playbackPanel.playlist)     

    def playlist_removed(self, name):
        if name == self.playbackPanel.playlist.get_name():
            self.ui_initial()
            self.managePage.playlistWidget.set_playlist_use_name(Configures.PlaylistDefault)
            self.switch_to_new_playing_list()
    
    def playlist_renamed(self, name, newName):
        if name == self.playbackPanel.playlist.get_name():
            self.playbackPanel.playlist.set_name(newName)
            self.managePage.playlistWidget.set_playing_status(self.playbackPanel.playlist)   

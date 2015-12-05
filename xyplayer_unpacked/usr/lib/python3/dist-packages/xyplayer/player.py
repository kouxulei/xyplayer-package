import os
import random
import threading
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices
from PyQt5.QtCore import QTime, QUrl, QPoint
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from xyplayer import Configures
from xyplayer.myplaylists import Playlist
from xyplayer.myicons import IconsHub
from xyplayer.mythreads import DownloadLrcThread
from xyplayer.urlhandle import SearchOnline
from xyplayer.mysettings import globalSettings
from xyplayer.utils import (parse_lrc, get_full_music_name_from_title,composite_lyric_path_use_title, 
    format_position_to_mmss, get_artist_and_musicname_from_title, convert_B_to_MB)
from xyplayer.player_ui import PlayerUi

class Player(PlayerUi):
    def __init__(self, parent = None):
        super(Player, self).__init__(parent)
        self.initial_mediaplayer()
        self.initial_parameters()
        self.initial_widget_parameters()
        self.create_connections()
        self.managePage.downloadPage.reload_works_from_database(self.lock)

    def create_connections(self):      
        PlayerUi.create_connections(self)
        self.mediaPlayer.positionChanged.connect(self.tick)        
        self.mediaPlayer.stateChanged.connect(self.state_changed)      
        self.mediaPlayer.currentMediaChanged.connect(self.source_changed)
        self.mediaPlayer.mediaStatusChanged.connect(self.media_status_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.mutedChanged.connect(self.functionsFrame.set_muted)

        self.playbackPage.seekSlider.valueChanged.connect(self.slider_value_changed)
        self.playbackPage.seekSlider.sliderPressed.connect(self.slider_pressed)
        self.playbackPage.seekSlider.sliderReleased.connect(self.seek)
        self.playbackPage.lyric_offset_changed_signal.connect(self.lyric_offset_changed)
        self.playbackPage.favoriteButton.clicked.connect(self.mark_as_favorite)
        self.playbackPage.select_current_row_signal.connect(self.select_current_source_row)
        self.playbackPage.playmode_changed_signal.connect(self.playmode_changed)
        self.playbackPage.play_from_music_list_signal.connect(self.decide_to_play_or_pause)
        self.playbackPage.show_music_info_signal.connect(self.show_music_info_at_row)

        self.managePage.randomOneButton.clicked.connect(self.listen_random_one)
        self.managePage.playlist_removed_signal.connect(self.playlist_removed)
        self.managePage.playlist_renamed_signal.connect(self.playlist_renamed)
        self.managePage.current_table_changed_signal.connect(self.current_table_changed)
        self.managePage.playlistWidget.play_music_at_row_signal.connect(self.set_media_source_at_row)
        self.managePage.playlistWidget.play_or_pause_signal.connect(self.decide_to_play_or_pause)
        self.managePage.playlistWidget.playlist_changed_signal.connect(self.switch_to_new_playing_list)
        self.managePage.playlistWidget.musics_added_signal.connect(self.musics_added)
        self.managePage.playlistWidget.musics_removed_signal.connect(self.musics_removed)
        self.managePage.playlistWidget.musics_cleared_signal.connect(self.musics_cleared)
        self.managePage.playlistWidget.musics_marked_signal.connect(self.musics_marked)
        self.managePage.playlistWidget.switch_to_search_page_signal.connect(self.managePage.show_search_frame)
        self.managePage.playlistWidget.download_signal.connect(self.online_list_song_download)
        self.managePage.playlistWidget.tag_values_changed_signal.connect(self.tag_values_changed)
        self.managePage.downloadPage.work_complete_signal.connect(self.refresh_playlist_downloaded)
        self.managePage.downloadPage.titleLabel.clicked.connect(self.open_download_dir)
        self.managePage.searchFrame.listen_online_signal.connect(self.begin_to_listen)
        self.managePage.searchFrame.add_to_download_signal.connect(self.add_to_download)
        self.managePage.searchFrame.add_bunch_to_list_succeed.connect(self.refresh_playlist_online)

        self.functionsFrame.settingsFrame.download_dir_changed.connect(self.set_new_download_dir)
        self.functionsFrame.settingsFrame.desktop_lyric_style_changed.connect(self.update_desktop_lyric_style)
        self.functionsFrame.settingsFrame.close_button_act_changed.connect(self.set_new_close_button_act)
        self.functionsFrame.settingsFrame.window_lyric_style_changed.connect(self.set_new_window_lyric_style)
        self.functionsFrame.aboutPage.updatingStateChanged.connect(self.updating_state_changed)
        self.functionsFrame.timeoutDialog.time_out_signal.connect(self.close)
        self.functionsFrame.changeVolume.connect(self.mediaPlayer.setVolume)
        self.functionsFrame.changeMuting.connect(self.mediaPlayer.setMuted)
    
    def set_new_download_dir(self, newDir):
        self.downloadDir = newDir
        self.managePage.searchFrame.set_download_dir(newDir)
        self.managePage.playlistWidget.set_download_dir(newDir)
    
    def set_new_close_button_act(self, act):
        self.closeButtonAct = act
    
    def update_desktop_lyric_style(self):
        self.playbackPage.desktopLyric.set_color(self.functionsFrame.settingsFrame.get_lyric_colors())
        self.playbackPage.desktopLyric.set_font_style(*self.functionsFrame.settingsFrame.get_lyric_font_styles())
    
    def set_new_window_lyric_style(self):
        params = self.functionsFrame.settingsFrame.get_window_lyric_params()
        self.playbackPage.set_new_window_lyric_style(params)
        if len(self.lyricDict) and self.playbackPage.document.blockCount():
            self.playbackPage.set_html(self.j, self.lyricDict, self.t)
    
    def initial_mediaplayer(self):
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayer.setNotifyInterval(500)
    
    def initial_widget_parameters(self):
        self.managePage.playlistWidget.set_playlist_use_name(Configures.PlaylistDefault)
        self.managePage.playlistWidget.set_download_dir(self.downloadDir)
        self.managePage.playlistWidget.set_lock(self.lock)
        self.switch_to_new_playing_list()
        
    def initial_parameters(self):
        self.closeButtonAct = globalSettings.CloseButtonAct
        self.forceCloseFlag = False    #跳过确认窗口强制关闭程序的标志
        self.lock = threading.Lock()    #设置一个线程锁，为了防止下载任务完成后向“我的下载”添加记录时与当前在此表上的其他操作产生冲突。
        self.dragPosition = QPoint(0, 0)
        self.lyricOffset = 0
        self.currentSourceRow = -1
        self.cTime = self.totalTime = Configures.ZeroTime
        self.currentTable = Configures.PlaylistDefault
        self.noError = 1
        self.nearPlayedSongs = []
        self.lyricDict = {}
        self.j = -5
        self.deleteLocalfilePermit = False
        self.downloadDir = globalSettings.DownloadfilesPath
        playlistTemp = Playlist()
        playlistTemp.fill_list(Configures.PlaylistFavorite)
        self.lovedSongs = playlistTemp.get_titles()

    def open_download_dir(self, name):
        """点击下载任务标题栏打开下载目录。"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.downloadDir))

    def refresh_playlist_online(self):
        """当批量添加试听歌曲到“在线试听”歌单后更新显示"""
        if self.playlist.get_name() == Configures.PlaylistOnline:
            self.playlist_refresh_with_name(Configures.PlaylistOnline)
            for item in self.managePage.searchFrame.added_items:
                self.playbackPage.add_widget_into_musiclist(item[1], item[0])

    def refresh_playlist_downloaded(self):
        if self.playlist.get_name() == Configures.PlaylistDownloaded:
            exists = self.playlist.get_items_queue()
            self.playlist_refresh_with_name(Configures.PlaylistDownloaded)
            for name in self.managePage.downloadPage.completedWorkNames:
                work = self.managePage.downloadPage.allDownloadWorks[name][0]
                if name not in exists:
                    self.playbackPage.add_widget_into_musiclist(name, work.title)
        if self.currentTable == Configures.PlaylistDownloaded:
            self.managePage.playlistWidget.set_playlist_use_name(Configures.PlaylistDownloaded)
        self.managePage.downloadPage.remove_work_from_download_list(self.managePage.downloadPage.completedWorkNames)
    
    def select_current_source_row(self):
        """当点击playbackPage的歌单按键，系统选中到当前播放的那首歌。"""
        self.playbackPage.musicList.selectRow(self.currentSourceRow)

    def slider_pressed(self):
        self.mediaPlayer.positionChanged.disconnect(self.tick)

    def seek(self):
        if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.mediaPlayer.play()
            self.mediaPlayer.setPosition(self.playbackPage.seekSlider.value())
        else:
            self.mediaPlayer.setPosition(self.playbackPage.seekSlider.value())
            self.mediaPlayer.play()
        self.mediaPlayer.positionChanged.connect(self.tick)

    def tag_values_changed(self, row, oldTitle, title, album):
        widget = self.managePage.playlistWidget
        playlist = widget.get_playlist()
        if widget.get_playing_used_state():
            self.playlist.set_music_title_at(row, title, False)
            self.playlist.set_music_album_at(row, album, False)
            self.playlist.commit_records()
            self.playbackPage.musicList.get_item_at_row(row).set_title(title)
            if row == self.currentSourceRow:
                artistName, musicName = get_artist_and_musicname_from_title(title)
                self.playAction.setText(musicName)
                self.playbackPage.musicNameLabel.setText(musicName)
                self.managePage.artistNameLabel.setText(artistName)
                self.managePage.musicNameLabel.setText(musicName)
        if playlist.get_name() == Configures.PlaylistFavorite:
            index = self.lovedSongs.index(oldTitle)
            self.lovedSongs[index] = title
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
            path = playlist.get_music_path_at(index)
            newAddedTitles.append((title, Configures.LocalMusicId))
            if playlist.get_name() == Configures.PlaylistFavorite:
                self.lovedSongs.append(title)
            if widget.get_playing_used_state():
                self.playbackPage.add_widget_into_musiclist(path, title)
        if playlist.get_name() == Configures.PlaylistFavorite:
            self.check_favorite()
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
                if self.playlist.get_current_row()  < 0:
                    self.ui_initial()
            for row in widget.removedIndexes:
                if playlist.get_name() == Configures.PlaylistFavorite:
                    del self.lovedSongs[row] 
                if widget.get_playing_used_state():
                    self.playbackPage.musicList.remove_item_at_row(row)
            if playlist.get_name() == Configures.PlaylistFavorite:
                self.check_favorite()

    def musics_cleared(self):
        widget = self.managePage.playlistWidget
        playlist = widget.get_playlist()
        if widget.get_playing_used_state():
            self.playlist_modified()
            self.playbackPage.musicList.clear_list()
            self.ui_initial()
        if playlist.get_name() == Configures.PlaylistFavorite:
            self.lovedSongs.clear() 
            self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.FavoritesNo))
    
    def musics_marked(self):
        widget = self.managePage.playlistWidget
        playlist = widget.get_playlist()       
        if self.playlist.get_name() == Configures.PlaylistFavorite:
            self.playlist_refresh_with_name(Configures.PlaylistFavorite)
        for index in widget.markedIndexes:
            title = playlist.get_music_title_at(index)
            path = playlist.get_music_path_at(index)
            self.lovedSongs.append(title)
            if self.playlist.get_name() == Configures.PlaylistFavorite:
                self.playbackPage.add_widget_into_musiclist(path, title)
        self.check_favorite()

    def mark_as_favorite(self):   
        if self.playlist.get_name() == Configures.PlaylistFavorite or not self.playlist.length() or self.currentSourceRow < 0:
            return
        path = self.playlist.get_music_path_at(self.currentSourceRow)
        title = self.playlist.get_music_title_at(self.currentSourceRow)
        if self.playlist.get_name() == Configures.PlaylistOnline:
            musicName = get_full_music_name_from_title(title)
            musicPath = os.path.join(self.downloadDir, musicName)
            musicPathO = os.path.join(Configures.MusicsDir, musicName)
            if not os.path.exists(musicPath) and not os.path.exists(musicPathO):
                QMessageBox.information(self, '提示', '请先下载该歌曲再添加喜欢！')
                return
            if os.path.exists(musicPath):
                path = musicPath
            else:
                path = musicPathO
        elif not os.path.exists(path):
            QMessageBox.information(self, "提示", "路径'"+"%s"%path+"'无效，无法标记喜欢！")
            return
        playlistTemp = Playlist()
        playlistTemp.fill_list(Configures.PlaylistFavorite)
        if title in self.lovedSongs:
            playlistTemp.remove_item_at(self.lovedSongs.index(title))
            playlistTemp.commit_records()
            self.lovedSongs.remove(title)
            self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.FavoritesNo))
            self.playbackPage.favoriteButton.setToolTip("收藏")
        else:
            playlistTemp.add_item_from_path(path)
            playlistTemp.commit_records()
            self.lovedSongs.append(title)
            self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
            self.playbackPage.favoriteButton.setToolTip("取消收藏")
        if self.managePage.playlistWidget.get_playlist().get_name() == Configures.PlaylistFavorite:
            self.managePage.playlistWidget.set_playlist_use_name(Configures.PlaylistFavorite)

    def check_favorite(self):
        if self.currentSourceRow >= 0:
            if self.playlist.get_music_title_at(self.currentSourceRow) in self.lovedSongs:
                self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
                self.playbackPage.favoriteButton.setToolTip('取消收藏')
            else:
                self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.FavoritesNo))
                self.playbackPage.favoriteButton.setToolTip('收藏')
            if self.playlist.get_name() == Configures.PlaylistFavorite:
                self.playbackPage.favoriteButton.setToolTip('收藏')

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
            if self.playlist.get_name() == Configures.PlaylistOnline:
                self.playbackPage.add_widget_into_musiclist(musicId, title)
                self.playlist.fill_list(Configures.PlaylistOnline)
                widget.set_playing_status(self.playlist) 
        else:
            if self.playlist.get_name() == Configures.PlaylistOnline and self.currentSourceRow == k:
                return
        widget.double_click_to_play_with_row(k)

    def add_to_download(self):
        for songInfoList in self.managePage.searchFrame.readyToDownloadSongs:
            songLink = songInfoList[0]
            musicPath = songInfoList[1]
            title = songInfoList[2]
            album = songInfoList[3]
            musicId = songInfoList[4]
            self.managePage.downloadPage.add_a_download_work(songLink, musicPath, title, album, musicId, 0, self.lock)

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
                musicPath = os.path.join(self.downloadDir, musicName)
                musicPathO = os.path.join(Configures.MusicsDir, musicName)
                if  os.path.exists(musicPath):
                    isExistsSongs.append('%s : %s'%(title, musicPath))
                    continue
                if os.path.exists(musicPathO):
                    isExistsSongs.append('%s : %s'%(title, musicPathO))
                    continue
                self.managePage.downloadPage.add_a_download_work(songLink, musicPath, title, album, musicId, 0, self.lock)
        if len(isExistsSongs):
            existsSongs = '\n'.join(isExistsSongs)
            QMessageBox.information(self, "提示", 
                "以下歌曲已在下载目录中不再进行下载，您可以在不联网的情况下点击在线列表播放！\n%s"%existsSongs)

    def duration_changed(self, duration):
        self.playbackPage.seekSlider.setMaximum(duration)
        exactTotalTime = format_position_to_mmss(self.mediaPlayer.duration()//1000)
        if self.totalTime != exactTotalTime:
            self.totalTime = exactTotalTime
            self.managePage.timeLabel.setText('%s/%s'%(Configures.ZeroTime, self.totalTime))
            self.playbackPage.timeLabel2.setText(self.totalTime)
            self.playlist.set_music_time_at(self.currentSourceRow, exactTotalTime)
            if self.currentTable == self.playlist.get_name():
                self.managePage.playlistWidget.set_playlist_use_name(self.currentTable)
                self.managePage.playlistWidget.select_row()

    def tick(self):
        currentTime = self.mediaPlayer.position()
        self.syc_lyric(currentTime)
        self.playbackPage.seekSlider.setValue(currentTime)
        self.cTime = format_position_to_mmss(currentTime//1000)
        totalTimeValue = self.mediaPlayer.duration()
        try:
            ratio = currentTime/totalTimeValue
        except ZeroDivisionError:
            ratio = 0
        self.managePage.frameBottomWidget.setGradient(ratio)
        self.managePage.timeLabel.setText(self.cTime + '/' + self.totalTime)
        self.playbackPage.timeLabel1.setText(self.cTime)

    def syc_lyric(self, currentTime):
        """同步歌词"""
        if len(self.lyricDict) and self.playbackPage.document.blockCount():
            if currentTime+self.lyricOffset <= self.t[0]:
                self.managePage.lyricLabel.setText('歌词同步显示')
            for i in range(len(self.t) - 1):
                if self.t[i] < currentTime+self.lyricOffset and self.t[i + 1] > currentTime+self.lyricOffset and i!= self.j:
                    self.j = i
                    if self.lyricDict[self.t[i]]:
                        self.managePage.lyricLabel.setText(self.lyricDict[self.t[i]])
                        self.playbackPage.set_html(i, self.lyricDict, self.t)
                    else:
                        self.managePage.lyricLabel.setText("音乐伴奏... ...")
                    break
            text = self.managePage.lyricLabel.text()
            if not self.playbackPage.desktopLyric.isHidden() and self.playbackPage.desktopLyric.text() != text:
                self.playbackPage.desktopLyric.set_text(text)

    def state_changed(self, newState):
        if newState in [QMediaPlayer.PlayingState, QMediaPlayer.PausedState, QMediaPlayer.StoppedState]:
            if not self.playlist.length():
                return        
            iconPath = IconsHub.ControlPause
            isPaused = False
            if newState in [QMediaPlayer.StoppedState, QMediaPlayer.PausedState]:
                iconPath = IconsHub.ControlPlay
                isPaused = True
            icon = QIcon(iconPath)
            self.playAction.setIcon(icon)
            try:
                self.playbackPage.musicList.get_item_at_row(self.currentSourceRow).set_pause_state(isPaused)
            except:
                pass

    def source_changed(self):  
        if not self.playlist.length():
            return 
        self.check_mountout_state()
        self.managePage.frameBottomWidget.setGradient(0)
        self.update_parameters()
        if self.playlist.get_name() == Configures.PlaylistOnline or os.path.exists(self.playlist.get_music_path_at(self.currentSourceRow)) :
            self.update_artist_info()
            self.update_lyric()
        else:
            self.managePage.lyricLabel.setText('歌词同步显示')
            self.lyricDict.clear()
            self.managePage.artistHeadLabel.setPixmap(QPixmap(IconsHub.Anonymous))
        self.update_near_played_queue()
        self.check_favorite()

    def check_mountout_state(self):
        if self.functionsFrame.mountoutDialog.countoutMode:
            if not self.functionsFrame.mountoutDialog.remainMount:
                self.close()
            self.functionsFrame.mountoutDialog.remainMount -= 1
            self.functionsFrame.mountoutDialog.spinBox.setValue(self.functionsFrame.mountoutDialog.remainMount)

    def update_parameters(self):
        oldSourceRow = self.currentSourceRow
        self.currentSourceRow = self.playlist.get_current_row()
        self.playbackPage.musicList.get_item_at_row(self.currentSourceRow).set_pause_state(False)
        try:
            self.playbackPage.musicList.get_item_at_row(oldSourceRow).set_pause_state(True)
        except:
            pass
        self.playbackPage.musicList.selectRow(self.currentSourceRow)
        title = self.playlist.get_music_title_at(self.currentSourceRow)
        artistName, musicName = get_artist_and_musicname_from_title(title)
        self.playAction.setText(musicName)
        self.playbackPage.musicNameLabel.setText(musicName)
        self.managePage.artistNameLabel.setText(artistName)
        self.managePage.musicNameLabel.setText(musicName)
        self.totalTime = self.playlist.get_music_time_at(self.currentSourceRow)
        self.managePage.timeLabel.setText('%s/%s'%(Configures.ZeroTime, self.totalTime))
        self.playbackPage.timeLabel2.setText(self.totalTime)

    def update_near_played_queue(self):
        currentSourceId = self.playlist.get_music_path_at(self.currentSourceRow)
        if self.playlist.get_name() == Configures.PlaylistOnline:
            currentSourceId = self.playlist.get_music_id_at(self.currentSourceRow)
        if currentSourceId not in self.nearPlayedSongs:
            self.nearPlayedSongs.append(currentSourceId)
        while len(self.nearPlayedSongs) >= self.playlist.length() * 4 / 5:
            del self.nearPlayedSongs[0]

    def update_artist_info(self):
        title = self.playlist.get_music_title_at(self.currentSourceRow)
        pixmap = self.playbackPage.update_artist_info(title)
        self.managePage.artistHeadLabel.setPixmap(pixmap)

    def update_lyric(self):
        self.managePage.lyricLabel.setToolTip("正常")
        self.lyricOffset = 0     
        title = self.playlist.get_music_title_at(self.currentSourceRow)
        musicId = self.playlist.get_music_id_at(self.currentSourceRow)
        self.lrcPath = composite_lyric_path_use_title(title)
        lyric = SearchOnline.get_lrc_contents(title, musicId)
        if lyric == Configures.LyricNetError:
            self.managePage.lyricLabel.setText("网络出错，无法搜索歌词！")
            self.playbackPage.desktopLyric.set_text("网络出错，无法搜索歌词！")
            self.lyricDict.clear()
            self.playbackPage.url_error_lyric()
        elif lyric == Configures.LyricNone:
            self.managePage.lyricLabel.set_text("搜索不到匹配歌词！")
            self.playbackPage.desktopLyric.set_text("搜索不到匹配歌词！")
            self.lyricDict.clear()
            self.playbackPage.no_matched_lyric()
        else:
            self.managePage.lyricLabel.set_text("歌词同步显示")
            self.lyricOffset, self.lyricDict = parse_lrc(lyric)
            self.lyricDict[3000000] = ''
            self.t = sorted(self.lyricDict.keys())
            self.playbackPage.set_lyric_offset(self.lyricOffset, self.lyricDict, self.lrcPath)

    def lyric_offset_changed(self, offset):
        self.lyricOffset = offset
        if len(self.lyricDict):
            if self.lyricOffset < 0:
                self.managePage.lyricLabel.setToolTip("已延迟%s秒"%(self.lyricOffset/1000))
            elif self.lyricOffset > 0:
                self.managePage.lyricLabel.setToolTip("已提前%s秒"%(abs(self.lyricOffset/1000)))
            else:
                self.managePage.lyricLabel.setToolTip("正常")
        else:
            self.managePage.lyricLabel.setToolTip("歌词显示")

    def current_table_changed(self, tableName):
        self.currentTable = tableName

    def decide_to_play_or_pause(self, row):
        if  row!= self.currentSourceRow or self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.set_media_source_at_row(row)
        elif self.mediaPlayer.state()  == QMediaPlayer.PausedState:
            self.mediaPlayer.play()
        elif self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
    
    def ui_initial(self):
        self.stop_music()
        PlayerUi.ui_initial(self)

    def slider_value_changed(self, value):
        minutes = (value / 60000) % 60
        seconds = (value / 1000) % 60
        cTime = QTime(0, minutes, seconds ).toString('mm:ss')
        self.managePage.timeLabel.setText('%s/%s'%(cTime, self.totalTime))
        self.playbackPage.timeLabel1.setText(cTime)
        self.playbackPage.timeLabel2.setText(self.totalTime)
        self.syc_lyric(value)

    def set_media_source_at_row(self, row):
        if not self.playlist.length() or row < 0:
            return 
        self.stop_music()
        self.playlist.set_current_row(row)
        self.managePage.playlistWidget.select_row()
        sourcePath = self.playlist.get_music_path_at(row)
        title = self.playlist.get_music_title_at(row)
        musicName = get_full_music_name_from_title(title)
        musicPathO = os.path.join(Configures.MusicsDir, musicName)
        musicPath = os.path.join(self.downloadDir, musicName)
        isAnUrl = False
        errorType = Configures.NoError
        isAnUrl = False
        if not os.path.exists(sourcePath):
            if  os.path.exists(musicPath):
                sourcePath = musicPath
            elif os.path.exists(musicPathO):
                sourcePath = musicPathO
            elif self.playlist.get_name() == Configures.PlaylistOnline:
                if sourcePath == Configures.NoLink:
                    musicId = self.playlist.get_music_id_at(row)
                    sourcePath = SearchOnline.get_song_link(musicId)
                    if sourcePath:
                        self.playlist.set_music_path_at(row, sourcePath)
                    else:
                        errorType = Configures.UrlError
                isAnUrl = True
            else:
                self.noError = 0
                errorType = Configures.PathError
                sourcePath = "/usr/share/sounds/error_happened.ogg"
        if errorType != Configures.NoError:       
            if self.isHidden():
                self.show()
            if errorType == Configures.DisnetError:
                QMessageBox.critical(self, "错误", "联网出错！\n无法联网播放歌曲'%s'！\n您最好在网络畅通时下载该曲目！"%self.playlist.get_music_title_at(row))
            elif errorType == Configures.PathError:
                QMessageBox.information(self, "提示", "路径'%s'无效，请尝试重新下载并添加对应歌曲！"%self.playlist.get_music_path_at(row))
            self.noError = 1 
            return
        if isAnUrl:
            url = QUrl(sourcePath)
        else:
            url = QUrl.fromLocalFile(sourcePath)
        self.play_from_url(url)       

    def play_from_url(self, url):
        mediaContent = QMediaContent(url)
        self.mediaPlayer.setMedia(mediaContent)
        self.mediaPlayer.play()

    def play_music(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState :
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def stop_music(self):
        self.mediaPlayer.stop()
        self.playbackPage.seekSlider.setValue(0)
        self.syc_lyric(-0.5)

    def previous_song(self):
        if not self.playlist.length():
            return
        self.stop_music()
        nextRow = 0
        if self.playbackPage.playmode == Configures.PlaymodeRandom:
            nextSongPath = self.random_a_song()
            nextRow = self.playlist.get_items_queue().index(nextSongPath)
        elif self.playbackPage.playmode == Configures.PlaymodeOrder:
            if self.currentSourceRow - 1 >= 0:
                nextRow = self.currentSourceRow - 1
            else:
                nextRow = self.playlist.length() - 1
        elif self.playbackPage.playmode == Configures.PlaymodeSingle:
            nextRow = self.currentSourceRow
            if nextRow < 0:
                nextRow = 0
        self.set_media_source_at_row(nextRow)

    def random_a_song(self):
        listTemp = list(set(self.playlist.get_items_queue())-set(self.nearPlayedSongs))
        ran = random.randint(0, len(listTemp)-1)
        return listTemp[ran]

    def next_song(self):
        if not self.playlist.length():
            return
        self.stop_music()
        nextRow = 0
        if self.playbackPage.playmode == Configures.PlaymodeRandom:
            nextSongPath = self.random_a_song()
            nextRow = self.playlist.get_items_queue().index(nextSongPath)
        elif self.playbackPage.playmode == Configures.PlaymodeOrder:
            if  self.currentSourceRow + 1 < self.playlist.length():
                nextRow = self.currentSourceRow + 1
            else:
                nextRow = 0
        elif self.playbackPage.playmode == Configures.PlaymodeSingle:
            nextRow = self.currentSourceRow
            if nextRow < 0:
                nextRow = 0
        self.set_media_source_at_row(nextRow)

    def listen_random_one(self):
        playmodeTemp = self.playbackPage.playmode
        self.playbackPage.playmode = Configures.PlaymodeRandom
        self.next_song()
        self.playbackPage.playmode = playmodeTemp

    def music_finished(self):
        if self.noError:
            self.next_song()

    def media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.music_finished()

    def music_table_select_current_row(self):
        """当点击播放页面的"歌单"时，歌单选中到当前正在播放的那首歌。"""
        if self.playbackPage.musicList.rowCount():
            self.playbackPage.musicList.selectRow(self.currentSourceRow)

    def updating_state_changed(self, updateState):
        """处理不同的软件更新状态。"""
        if updateState == Configures.UpdateStarted:
            self.mediaPlayer.stop()
            self.functionsFrame.close()
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
        self.playbackPage.musicList.clear_list()
        for i in range(0, self.playlist.length()):
            ident = self.playlist.get_music_path_at(i)
            if self.playlist.get_name() == Configures.PlaylistOnline:
                ident = self.playlist.get_music_id_at(i)
            title = self.playlist.get_music_title_at(i)
            self.playbackPage.add_widget_into_musiclist(ident, title) 
        self.set_media_source_at_row(self.playlist.get_current_row())
    
    def playlist_modified(self):
        self.playlist = self.managePage.playlistWidget.get_playlist()
        self.managePage.playlistWidget.set_playing_status(self.playlist)    
        self.currentSourceRow = self.playlist.get_current_row()       
    
    def playlist_refresh_with_name(self, listName):
        self.playlist.fill_list(listName)
        self.managePage.playlistWidget.set_playing_status(self.playlist)     

    def playlist_removed(self, name):
        if name == self.playlist.get_name():
            self.ui_initial()
            self.managePage.playlistWidget.set_playlist_use_name(Configures.PlaylistDefault)
            self.managePage.change_list_buttons_color(name, Configures.PlaylistDefault)
            self.switch_to_new_playing_list()
    
    def playlist_renamed(self, name, newName):
        if name == self.playlist.get_name():
            self.playlist.set_name(newName)
            self.managePage.playlistWidget.set_playing_status(self.playlist)   
    
    def show_music_info_at_row(self, row):
        title, totalTime, album, path, size, musicId = self.playlist.get_record_at(row)[:6]
        artist, musicName = get_artist_and_musicname_from_title(title)
        if self.playlist.get_name() == Configures.PlaylistOnline:
            information = "歌手： %s\n曲名： %s\n专辑： %s\n时长： %s\n歌曲ID： %s\n网址： %s"%(artist, musicName, album, totalTime, musicId, path)
        else:
            information = "歌手： %s\n曲名： %s\n专辑： %s\n时长： %s\n大小： %.2f MB\n路径： %s"%(artist, musicName, album, totalTime, convert_B_to_MB(size), path)
        QMessageBox.information(self, "歌曲详细信息", information) 

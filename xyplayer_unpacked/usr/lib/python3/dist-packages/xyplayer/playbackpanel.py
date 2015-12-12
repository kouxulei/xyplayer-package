import os
import random
from PyQt5.QtWidgets import QLabel, QToolButton, QSlider, QHBoxLayout, QVBoxLayout, QMessageBox, QAction
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from xyplayer import Configures
from xyplayer.myicons import IconsHub
from xyplayer.myplaylists import Playlist
from xyplayer.mywidgets import SpecialLabel, NewLabel, LabelButton
from xyplayer.mypages import desktop_lyric
from xyplayer.mysettings import globalSettings
from xyplayer.urlhandle import SearchOnline
from xyplayer.utils import format_position_to_mmss, get_full_music_name_from_title, get_artist_and_musicname_from_title

class PlaybackPanel(SpecialLabel):
    desktop_lyric_state_changed_signal = pyqtSignal(bool)
    playmode_changed_signal = pyqtSignal(int, int)
    media_player_notify_signal = pyqtSignal(int)
    muted_changed_signal = pyqtSignal(int)
    mark_favorite_completed_signal = pyqtSignal()
    current_media_changed_signal = pyqtSignal()
    update_window_lyric_signal = pyqtSignal(str, str)
    show_artist_info_signal = pyqtSignal(str)
    def __init__(self, parent=None):
        super(PlaybackPanel, self).__init__(parent)
        self.initial_mediaplayer()
        self.create_actions()
        self.setup_ui()
        self.create_connections()
        self.initial_params()
    
    def create_connections(self):
        self.artistHeadLabel.clicked.connect(self.show_artist_info)
        self.desktopLyric.hide_desktop_lyric_signal.connect(self.desktop_lyric_closed)
        self.seekSlider.valueChanged.connect(self.slider_value_changed)
        self.seekSlider.sliderPressed.connect(self.slider_pressed)
        self.seekSlider.sliderReleased.connect(self.seek)
        self.mediaPlayer.positionChanged.connect(self.tick)        
        self.mediaPlayer.mutedChanged.connect(self.muted_changed_signal.emit)
        self.mediaPlayer.stateChanged.connect(self.state_changed)   
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.mediaStatusChanged.connect(self.media_status_changed)
        self.mediaPlayer.currentMediaChanged.connect(self.current_media_changed)
    
    def initial_mediaplayer(self):
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayer.setNotifyInterval(500)
    
    def initial_params(self):
        self.playlist = None
        self.artistName = 'Zheng-Yejian'
        self.noError = 1
        self.currentSourceRow = -1
        self.nearPlayedSongs = []
        self.downloadDir = globalSettings.DownloadfilesPath
        self.totalTime = Configures.ZeroTime
        self.playmode = Configures.PlaymodeRandom    #播放模式指示器
        playlistTemp = Playlist()
        playlistTemp.fill_list(Configures.PlaylistFavorite)
        self.lovedSongs = playlistTemp.get_titles()
    
    def set_playlist(self, playlist):
        self.playlist = playlist
        self.currentSourceRow = self.playlist.get_current_row()    
    
    def create_actions(self):
        self.nextAction = QAction(
            QIcon(IconsHub.ControlNext), "下一首", 
            self, enabled = True,
            triggered = self.next_song)
        
        self.playAction = QAction(
            QIcon(IconsHub.ControlPlay), "播放/暂停",
            self, enabled = True,
            triggered = self.play_music)
        
        self.previousAction = QAction(
            QIcon(IconsHub.ControlPrevious), "上一首", 
            self, enabled = True,
            triggered = self.previous_song)

        self.stopAction = QAction(
            QIcon(IconsHub.ControlStop), "停止",
            self, enabled = True,
            triggered = self.stop_music)
    
    def get_play_button_action(self):
        return self.playAction
    
    def get_previous_button_action(self):
        return self.previousAction
    
    def get_next_button_action(self):
        return self.nextAction
    
    def get_stop_button_action(self):
        return self.stopAction
    
    def set_download_dir(self, dir):
        self.downloadDir = dir
    
    def setup_ui(self):
        self.setFixedHeight(50)
#桌面歌词标签
        self.desktopLyric = desktop_lyric.DesktopLyric()
        self.desktopLyric.set_color(globalSettings.DesktoplyricColors)
#3个标签
        self.artistHeadLabel = LabelButton()
        self.artistHeadLabel.setFixedSize(QSize(45, 45))
        self.artistHeadLabel.setScaledContents(True)
        self.artistHeadLabel.setPixmap(QPixmap(IconsHub.Anonymous))

        self.musicTitleLabel = NewLabel()
        self.musicTitleLabel.setFixedSize(QSize(300, 20))
        self.musicTitleLabel.setText("Zheng-Yejian._.XYPLAYER")
        self.timeLabel = QLabel("00:00/00:00")
        self.timeLabel.setFixedHeight(20)
        self.timeLabel.setAlignment(Qt.AlignRight and Qt.AlignVCenter)

#五个基本按键
        self.playmodeButton = QToolButton(clicked=self.change_playmode)
        self.playmodeButton.setFocusPolicy(Qt.NoFocus)

        self.playmodeButton.setIcon(QIcon(IconsHub.PlaymodeRandom))
        self.playmodeButton.setIconSize(QSize(25, 25))
        self.playmodeButton.setToolTip('随机播放')
        
        self.favoriteButton = QToolButton(clicked=self.mark_as_favorite)
        self.favoriteButton.setFocusPolicy(Qt.NoFocus)
        self.favoriteButton.setToolTip('收藏')
        self.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
        self.favoriteButton.setIconSize(QSize(20, 20))

        self.previousButton = QToolButton()
        self.previousButton.setFocusPolicy(Qt.NoFocus)
        self.previousButton.setIconSize(QSize(40, 40))
        self.previousButton.setShortcut(QKeySequence("Ctrl + Left"))
        self.previousButton.setDefaultAction(self.previousAction)

        self.playButton = QToolButton()
        self.playButton.setFocusPolicy(Qt.NoFocus)
        self.playButton.setIconSize(QSize(40, 40))
        self.playButton.setShortcut(QKeySequence("Ctrl + Down"))
        self.playButton.setDefaultAction(self.playAction)
        
        self.nextButton = QToolButton()
        self.nextButton.setFocusPolicy(Qt.NoFocus)
        self.nextButton.setIconSize(QSize(40, 40))
        self.nextButton.setFocusPolicy(Qt.NoFocus)
        self.nextButton.setShortcut(QKeySequence("Ctrl + Right"))
        self.nextButton.setDefaultAction(self.nextAction)
        
        self.desktopLyricButton = QToolButton(clicked = self.show_desktop_lyric)
        self.desktopLyricButton.setFocusPolicy(Qt.NoFocus)
        self.desktopLyricButton.setIcon(QIcon(IconsHub.DesktopLyric))
        self.desktopLyricButton.setIconSize(QSize(25, 25))

        self.seekSlider = QSlider(Qt.Horizontal)
        self.seekSlider.setFixedHeight(20)
#        self.seekSlider.setMinimumWidth(400)
        self.seekSlider.setFocusPolicy(Qt.NoFocus)
        self.seekSlider.setRange(0, 0)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.favoriteButton)
        hbox1.addWidget(self.musicTitleLabel)
        hbox1.addStretch()
        hbox1.addWidget(self.timeLabel)
        vbox1 = QVBoxLayout()
        vbox1.addLayout(hbox1)
        vbox1.setSpacing(5)
        vbox1.addWidget(self.seekSlider)
        
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.artistHeadLabel)
        mainLayout.addWidget(self.previousButton)
        mainLayout.addWidget(self.playButton)
        mainLayout.addWidget(self.nextButton)
        mainLayout.addLayout(vbox1)
        mainLayout.addWidget(self.playmodeButton)
        mainLayout.addWidget(self.desktopLyricButton)

    def show_desktop_lyric(self):
        if self.desktopLyric.isHidden():
            beToOff = True
            self.desktopLyric.show()
            self.desktopLyric.original_place()
        else:
            beToOff = False
            self.desktopLyric.hide()  
        self.desktop_lyric_state_changed_signal.emit(beToOff)
        
    def desktop_lyric_closed(self):
        self.desktop_lyric_state_changed_signal.emit(False)

    def change_playmode(self):
        oldPlaymode = self.playmode
        if self.playmode == Configures.PlaymodeRandom:
            self.set_new_playmode(Configures.PlaymodeOrder)
        elif self.playmode == Configures.PlaymodeOrder:
            self.set_new_playmode(Configures.PlaymodeSingle)
        elif self.playmode == Configures.PlaymodeSingle:
            self.set_new_playmode(Configures.PlaymodeRandom)
        self.playmode_changed_signal.emit(oldPlaymode, self.playmode)

    def set_new_playmode(self, playmode):
        self.playmode = playmode
        if playmode == Configures.PlaymodeRandom:
            iconPath = IconsHub.PlaymodeRandom
            toolTip = Configures.PlaymodeRandomText
        elif playmode == Configures.PlaymodeOrder:
            iconPath = IconsHub.PlaymodeOrder
            toolTip = Configures.PlaymodeOrderText
        else:
            iconPath = IconsHub.PlaymodeSingle
            toolTip = Configures.PlaymodeSingleText
        self.playmodeButton.setIcon(QIcon(iconPath))
        self.playmodeButton.setToolTip(toolTip)

    def update_desktop_lyric_style(self):
        self.desktopLyric.set_color(self.managePage.settingsFrame.get_lyric_colors())
        self.desktopLyric.set_font_style(*self.managePage.settingsFrame.get_lyric_font_styles())

    def ui_initial(self):
        self.mediaPlayer.stop()
        self.totalTime = '00:00'
        self.playAction.setIcon(QIcon(IconsHub.ControlPlay))
        self.musicTitleLabel.setText("Zheng-Yejian._.XYPLAYER")
        self.artistName = 'Zheng-Yejian'
        self.artistHeadLabel.setPixmap(QPixmap(IconsHub.HeadIcon))
        self.seekSlider.setRange(0, 0)
        self.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
        self.favoriteButton.setToolTip('收藏')
        self.timeLabel.setText("00:00/00:00")

    def set_volume(self, volume):
        self.mediaPlayer.setVolume(volume)
    
    def set_muted(self, muted):
        self.mediaPlayer.setMuted(muted)
    
    def tick(self):
        currentTime = self.mediaPlayer.position()
        self.seekSlider.setValue(currentTime)
        cTime = format_position_to_mmss(currentTime//1000)
        self.timeLabel.setText(cTime + '/' + self.totalTime)
        self.media_player_notify_signal.emit(currentTime)

    def slider_value_changed(self, value):
        cTime = format_position_to_mmss(value//1000)
        self.timeLabel.setText('%s/%s'%(cTime, self.totalTime))
        self.media_player_notify_signal.emit(value)

    def slider_pressed(self):
        self.mediaPlayer.positionChanged.disconnect(self.tick)

    def seek(self):
        if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.mediaPlayer.play()
            self.mediaPlayer.setPosition(self.seekSlider.value())
        else:
            self.mediaPlayer.setPosition(self.seekSlider.value())
            self.mediaPlayer.play()
        self.mediaPlayer.positionChanged.connect(self.tick)

    def duration_changed(self, duration):
        self.seekSlider.setMaximum(duration)
        exactTotalTime = format_position_to_mmss(self.mediaPlayer.duration()//1000)
        self.timeLabel.setText('%s/%s'%(Configures.ZeroTime, exactTotalTime))
        if self.totalTime != exactTotalTime:
            self.totalTime = exactTotalTime
            self.playlist.set_music_time_at(self.currentSourceRow, exactTotalTime)

    def check_favorite(self):
        if self.currentSourceRow >= 0:
            if self.playlist.get_music_title_at(self.currentSourceRow) in self.lovedSongs:
                self.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
                self.favoriteButton.setToolTip('取消收藏')
            else:
                self.favoriteButton.setIcon(QIcon(IconsHub.FavoritesNo))
                self.favoriteButton.setToolTip('收藏')
            if self.playlist.get_name() == Configures.PlaylistFavorite:
                self.favoriteButton.setToolTip('收藏')

    def musics_marked(self, widget):
        playlist = widget.get_playlist()       
        if self.playlist.get_name() == Configures.PlaylistFavorite:
            self.playlist_refresh_with_name(Configures.PlaylistFavorite)
        for index in widget.markedIndexes:
            title = playlist.get_music_title_at(index)
            self.lovedSongs.append(title)
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
            self.favoriteButton.setIcon(QIcon(IconsHub.FavoritesNo))
            self.favoriteButton.setToolTip("收藏")
        else:
            playlistTemp.add_item_from_path(path)
            playlistTemp.commit_records()
            self.lovedSongs.append(title)
            self.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
            self.favoriteButton.setToolTip("取消收藏")
        self.mark_favorite_completed_signal.emit()

    def show_artist_info(self):
        if self.artistName:
            self.show_artist_info_signal.emit(self.artistName)

    def decide_to_play_or_pause(self, row):
        if  row!= self.currentSourceRow or self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.set_media_source_at_row(row)
        elif self.mediaPlayer.state()  == QMediaPlayer.PausedState:
            self.mediaPlayer.play()
        elif self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()

    def set_media_source_at_row(self, row):
        if not self.playlist.length() or row < 0:
            return 
        self.stop_music()
        self.playlist.set_current_row(row)
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

    def state_changed(self, newState):
        if newState in [QMediaPlayer.PlayingState, QMediaPlayer.PausedState, QMediaPlayer.StoppedState]:
            if not self.playlist.length():
                return        
            iconPath = IconsHub.ControlPause
            if newState in [QMediaPlayer.StoppedState, QMediaPlayer.PausedState]:
                iconPath = IconsHub.ControlPlay
            icon = QIcon(iconPath)
            self.playAction.setIcon(icon)

    def media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.music_finished()

    def music_finished(self):
        if self.noError:
            self.next_song()

    def play_music(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState :
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def previous_song(self):
        if not self.playlist.length():
            return
        self.stop_music()
        nextRow = 0
        if self.playmode == Configures.PlaymodeRandom:
            nextSongPath = self.random_a_song()
            nextRow = self.playlist.get_items_queue().index(nextSongPath)
        elif self.playmode == Configures.PlaymodeOrder:
            if self.currentSourceRow - 1 >= 0:
                nextRow = self.currentSourceRow - 1
            else:
                nextRow = self.playlist.length() - 1
        elif self.playmode == Configures.PlaymodeSingle:
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
        if self.playmode == Configures.PlaymodeRandom:
            nextSongPath = self.random_a_song()
            nextRow = self.playlist.get_items_queue().index(nextSongPath)
        elif self.playmode == Configures.PlaymodeOrder:
            if  self.currentSourceRow + 1 < self.playlist.length():
                nextRow = self.currentSourceRow + 1
            else:
                nextRow = 0
        elif self.playmode == Configures.PlaymodeSingle:
            nextRow = self.currentSourceRow
            if nextRow < 0:
                nextRow = 0
        self.set_media_source_at_row(nextRow)

    def stop_music(self):
        self.mediaPlayer.stop()
        self.seekSlider.setValue(0)
        self.media_player_notify_signal.emit(-0.5)

    def current_media_changed(self):  
        if not self.playlist.length():
            return 
        self.current_media_changed_signal.emit()
        self.update_parameters()
        self.update_near_played_queue()
        self.check_favorite()

    def update_parameters(self):
        self.currentSourceRow = self.playlist.get_current_row()
        self.totalTime = self.playlist.get_music_time_at(self.currentSourceRow)
        title = self.playlist.get_music_title_at(self.currentSourceRow)
        self.musicTitleLabel.setText(title)
        self.artistName, musicName = get_artist_and_musicname_from_title(title)
        self.playAction.setText(musicName)
        imagePath = SearchOnline.get_artist_image_path(self.artistName)
        if imagePath:
            pixmap = QPixmap(imagePath)
        else:
            self.artistName = ''
            pixmap = QPixmap(IconsHub.Anonymous)
        self.artistHeadLabel.setPixmap(pixmap)
        musicId = self.playlist.get_music_id_at(self.currentSourceRow)
        self.update_window_lyric_signal.emit(title, musicId)
    
    def update_near_played_queue(self):
        currentSourceId = self.playlist.get_music_path_at(self.currentSourceRow)
        if self.playlist.get_name() == Configures.PlaylistOnline:
            currentSourceId = self.playlist.get_music_id_at(self.currentSourceRow)
        if currentSourceId not in self.nearPlayedSongs:
            self.nearPlayedSongs.append(currentSourceId)
        while len(self.nearPlayedSongs) >= self.playlist.length() * 4 / 5:
            del self.nearPlayedSongs[0]

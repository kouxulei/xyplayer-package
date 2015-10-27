import os
import random
import threading
from functools import wraps
from PyQt5.QtWidgets import QMessageBox, QLineEdit, QInputDialog, QFileDialog
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QTime, QUrl, QPoint
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from xyplayer import Configures, sqlOperator
from xyplayer.iconshub import IconsHub
from xyplayer.mythreads import DownloadLrcThread
from xyplayer.urlhandle import SearchOnline
from xyplayer.utils import (read_music_info, parse_lrc, trace_to_keep_time, get_full_music_name_from_title,
    format_position_to_mmss, get_artist_and_musicname_from_title)
from xyplayer.player_ui import PlayerUi

class Player(PlayerUi):
    def __init__(self, parent = None):
        super(Player, self).__init__(parent)
        self.initial_mediaplayer()
        self.initial_parameters()
        self.create_connections()
        self.managePage.downloadPage.reload_works_from_database(self.lock)

    def create_connections(self):      
        self.mediaPlayer.positionChanged.connect(self.tick)        
        self.mediaPlayer.stateChanged.connect(self.state_changed)      
        self.mediaPlayer.currentMediaChanged.connect(self.source_changed)
        self.mediaPlayer.mediaStatusChanged.connect(self.media_status_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.mutedChanged.connect(self.settingFrame.set_muted)

        self.playbackPage.seekSlider.valueChanged.connect(self.slider_value_changed)
        self.playbackPage.seekSlider.sliderPressed.connect(self.slider_pressed)
        self.playbackPage.seekSlider.sliderReleased.connect(self.seek)
        self.playbackPage.desktop_lyric_state_changed_signal.connect(self.desktop_lyric_state_changed)
        self.playbackPage.lyric_offset_changed_signal.connect(self.lyric_offset_changed)
        self.playbackPage.favoriteButton.clicked.connect(self.mark_as_favorite)
        self.playbackPage.backButton.clicked.connect(self.show_mainstack_0)
        self.playbackPage.select_current_row_signal.connect(self.select_current_source_row)
        self.playbackPage.playmode_changed_signal.connect(self.playmode_changed)

        self.managePage.current_table_changed_signal.connect(self.current_table_changed)
        self.managePage.show_lists_manage_frame_signal.connect(self.show_current_table)
        self.managePage.listsFrame.titleLabel.clicked.connect(self.lists_frame_title_label_clicked)
        self.managePage.add_a_list_signal.connect(self.add_tables)
        self.managePage.randomOneButton.clicked.connect(self.listen_random_one)
        self.managePage.listsFrame.musicTable.addMusicAction.triggered.connect(self.add_files)
        self.managePage.listsFrame.musicTable.markSelectedAsFavoriteAction.triggered.connect(self.mark_selected_as_favorite)
        self.managePage.listsFrame.musicTable.deleteAction.triggered.connect(self.delete_localfile)
        self.managePage.listsFrame.musicTable.deleteSelectedsAction.triggered.connect(self.delete_selecteds)
        self.managePage.listsFrame.musicTable.clearTheListAction.triggered.connect(self.check_and_clear_music_table)
        self.managePage.listsFrame.musicTable.downloadAction.triggered.connect(self.online_list_song_download)
        self.managePage.listsFrame.musicTable.songSpecAction.triggered.connect(self.song_spec)
        self.managePage.listsFrame.musicTable.switchToSearchPageAction.triggered.connect(self.managePage.show_search_frame)
        self.managePage.listsFrame.musicTable.doubleClicked.connect(self.music_table_clicked)

        self.managePage.listsFrame.manageTable.addTableAction.triggered.connect(self.add_tables)
        self.managePage.listsFrame.manageTable.addMusicHereAction.triggered.connect(self.add_files)
        self.managePage.listsFrame.manageTable.renameTableAction.triggered.connect(self.rename_tables)
        self.managePage.listsFrame.manageTable.deleteTableAction.triggered.connect(self.delete_tables)
        self.managePage.listsFrame.manageTable.pressed.connect(self.manage_table_clicked)
        
        self.managePage.downloadPage.work_complete_signal.connect(self.refresh_playlist_downloaded)
        self.managePage.downloadPage.titleLabel.clicked.connect(self.open_download_dir)

        self.managePage.searchFrame.switch_to_online_list.connect(self.switch_to_online_list)
        self.managePage.searchFrame.listen_online_signal.connect(self.begin_to_listen)
        self.managePage.searchFrame.listen_local_signal.connect(self.listen_local)
        self.managePage.searchFrame.add_to_download_signal.connect(self.add_to_download)
        self.managePage.searchFrame.add_bunch_to_list_succeed.connect(self.refresh_playlist_online)
        self.managePage.frameBottomWidget.clicked.connect(self.show_mainstack_1)
        self.managePage.lyricLabel.clicked.connect(self.show_mainstack_1)

        self.settingFrame.pathsetFrame.downloadDirChanged.connect(self.set_new_downloaddir)
        self.settingFrame.aboutPage.updatingStateChanged.connect(self.updating_state_changed)
        self.settingFrame.timeoutDialog.time_out_signal.connect(self.close)
        self.settingFrame.changeVolume.connect(self.mediaPlayer.setVolume)
        self.settingFrame.changeMuting.connect(self.mediaPlayer.setMuted)

    def initial_mediaplayer(self):
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayer.setNotifyInterval(500)

    def initial_parameters(self):
        self.forceCloseFlag = False    #跳过确认窗口强制关闭程序的标志
        self.lock = threading.Lock()    #设置一个线程锁，为了防止下载任务完成后向“我的下载”添加记录时与当前在此表上的其他操作产生冲突。
        self.dragPosition = QPoint(0, 0)
        self.lyricOffset = 0
        self.currentSourceRow = -1
        self.cTime = self.totalTime = Configures.ZeroTime
        self.playTable =  Configures.PlaylistDefault
        self.currentTable = Configures.PlaylistDefault
        self.noError = 1
        self.allPlaySongs = []
        self.nearPlayedSongs = []
        self.lyricDict = {}
        self.j = -5
        self.deleteLocalfilePermit = False
        try:
            with open(Configures.SettingFile, 'r') as f:
                self.downloadDir = f.read()
        except:
            self.downloadDir = Configures.MusicsDir
        self.model.initial_model(Configures.PlaylistFavorite)
        self.lovedSongs = []  
        for i in range(0, self.model.rowCount()):
            self.lovedSongs.append(self.model.get_record_title(i))     

        self.model.initial_model(Configures.PlaylistDefault)
        self.musicTable.initial_view(self.model)
        for i in range(0, self.model.rowCount()):
            ident = self.model.get_record_paths(i)
            title = self.model.get_record_title(i)
            self.playback_musictable_add_widget(ident, title)

    def operate_after_check_thread_locked_state(func):
        """用于判断当前线程锁的状态的修饰器，主要用在添加、删除、清空列表几个操作。"""
        @wraps(func)
        def _call(*args, **kwargs):
            obj = args[0]
            if obj.currentTable == Configures.PlaylistDownloaded:
                if obj.lock.acquire():
                    result = func(*args, **kwargs)
                    obj.lock.release()
            else:
                result = func(*args, **kwargs)
            print('%s执行成功!'%func.__name__)
            return result
        return _call

    def open_download_dir(self, name):
        """点击下载任务标题栏打开下载目录。"""
        with open(Configures.SettingFile, 'r') as f:
            downloadDir = f.read()
        print(downloadDir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(downloadDir))

    def delete_localfile(self):
        self.deleteLocalfilePermit = True
        self.delete_selecteds()
        self.deleteLocalfilePermit = False

    def song_spec(self):
        row = self.managePage.listsFrame.musicTable.currentIndex().row()
        self.show_music_info(self.managePage.listsFrame.model, row)


    def show_music_info(self, model, row):
        title = model.record(row).value("title")
        album = model.record(row).value("album")
        timeLength = model.record(row).value("length")
        path = model.record(row).value("paths")
        artist, musicName = get_artist_and_musicname_from_title(title)
        if musicName:
            information = "歌手：%s\n曲名：%s\n时长：%s\n专辑：%s\n路径：%s"%(artist, musicName, timeLength, album, path)
        else:
            information = "标题：%s\n时长：%s\n专辑：%s\n路径：%s"%(title, timeLength, album, path)
        QMessageBox.information(self, "歌曲详细信息", information)

    def refresh_playlist_online(self):
        """当批量添加试听歌曲到“在线试听”歌单后更新显示"""
        if self.playTable == Configures.PlaylistOnline:
            self.model.initial_model(Configures.PlaylistOnline)
            self.musicTable.initial_view(self.model)
            for item in self.managePage.searchFrame.added_items:
                self.playback_musictable_add_widget(item[1], item[0])

    def refresh_playlist_downloaded(self):
        if self.playTable == Configures.PlaylistDownloaded:
            self.model.initial_model(Configures.PlaylistDownloaded)
            self.musicTable.initial_view(self.model)
            for name in self.managePage.downloadPage.completedWorkNames:
                work = self.managePage.downloadPage.allDownloadWorks[name][0]
                if name not in self.allPlaySongs:
                    self.playback_musictable_add_widget(name, work.title)
        if self.currentTable == Configures.PlaylistDownloaded:
            self.managePage.listsFrame.model.initial_model(Configures.PlaylistDownloaded)
            self.managePage.listsFrame.musicTable.selectRow(self.currentSourceRow)
        self.managePage.downloadPage.remove_work_from_download_list(self.managePage.downloadPage.completedWorkNames)
    
    def select_current_source_row(self):
        """当点击playbackPage的歌单按键，系统选中到当前播放的那首歌。"""
        self.playbackPage.musicList.selectRow(self.currentSourceRow)
    
    def set_new_downloaddir(self, newDir):
        self.downloadDir = newDir

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
        
    def delete_selecteds(self): 
        selections = self.managePage.listsFrame.musicTable.selectionModel()
        selecteds = selections.selectedIndexes()
        cnt = len(selecteds)//12       
        if not cnt:
            return
        selectedsSpan = selecteds[-1].row() - selecteds[0].row()  + 1
        cnt1 = 0
        cnt2 = 0
        for index in selecteds:
            if  index.row() < self.currentSourceRow and index.column() == 0:
                cnt1 += 1
            if index.row() == self.currentSourceRow and self.playTable == self.currentTable:
                cnt2 = 1
        if self.deleteLocalfilePermit:
            text_tmp1 = "移除并删除本地文件"
            text_tmp2 = "有%s首歌曲将被移出列表，并被彻底删除，请确认!"%cnt
        else:
            text_tmp1 = "移除选中项"
            text_tmp2 = "有%s首歌曲将被移出列表!"%cnt
        ok = QMessageBox.warning(self, text_tmp1, text_tmp2, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok == QMessageBox.Yes:
            self.setCursor(QCursor(Qt.BusyCursor))
            if not cnt2:               
                self.delete_selecteds_after_check_thread_lock(selecteds)
                if self.playTable == self.currentTable:
                    self.playback_page_delete_selected(selecteds)
                    self.currentSourceRow  -=  cnt1
                    self.model.initial_model(self.playTable)
                    self.musicTable.selectRow(self.currentSourceRow)
                    self.managePage.listsFrame.musicTable.selectRow(self.currentSourceRow)
            else:
                currentMusic = self.managePage.listsFrame.model.get_record_title(self.currentSourceRow)
                if self.deleteLocalfilePermit:
                    text_tmp3 = "移除并删除当前歌曲"
                    text_tmp4 = "当前播放的歌曲: %s 将会被移除并被删除！\n请确认！"%currentMusic
                else:
                    text_tmp3 = "移除当前歌曲"
                    text_tmp4 = "当前播放的歌曲: %s 将会被移除!\n您是否要移除这首歌曲？"%currentMusic
                ok = QMessageBox.warning(self, text_tmp3, text_tmp4, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
                if ok  == QMessageBox.Yes:
                    if cnt ==  self.managePage.listsFrame.model.rowCount():
                        self.clear_music_table()
                        if self.deleteLocalfilePermit:
                            self.managePage.listsFrame.model.delete_localfiles(selecteds)
                    elif cnt == selectedsSpan and selecteds[-1].row() == self.managePage.listsFrame.model.rowCount() - 1:
                        self.delete_selecteds_after_check_thread_lock(selecteds)     
                        self.playback_page_delete_selected(selecteds)   
                        self.model.initial_model(self.playTable)     
                        self.set_media_source_at_row(0)
                        self.managePage.listsFrame.musicTable.selectRow(0)
                    else:     
                        firstDeletedRow = selecteds[0].row()
                        self.delete_selecteds_after_check_thread_lock(selecteds)
                        self.playback_page_delete_selected(selecteds)
                        self.model.initial_model(self.playTable)
                        self.set_media_source_at_row(firstDeletedRow)
                        self.managePage.listsFrame.musicTable.selectRow(firstDeletedRow)
                elif ok  == QMessageBox.No:
                    selecteds1 = []
                    for index in selecteds:
                        row = index.row()
                        if self.managePage.listsFrame.model.get_record_paths(row) ==  self.managePage.listsFrame.model.get_record_paths(self.currentSourceRow):
                            continue
                        selecteds1.append(index)
                    self.delete_selecteds_after_check_thread_lock(selecteds1)     
                    self.playback_page_delete_selected(selecteds1)   
                    self.model.initial_model(self.playTable) 
                    self.currentSourceRow  -=  cnt1
                    self.managePage.listsFrame.musicTable.selectRow(self.currentSourceRow)
                    self.musicTable.selectRow(self.currentSourceRow)
            self.setCursor(QCursor(Qt.ArrowCursor))
            if self.currentTable == Configures.PlaylistFavorite:
                self.lovedSongs.clear()
                for i in range(0, self.managePage.listsFrame.model.rowCount()):
                    self.lovedSongs.append(self.managePage.listsFrame.model.get_record_title(i))      
            self.check_favorite()

    @operate_after_check_thread_locked_state
    def delete_selecteds_after_check_thread_lock(self, selecteds):
        if self.deleteLocalfilePermit:
            self.managePage.listsFrame.model.delete_localfiles(selecteds)
        self.managePage.listsFrame.model.delete_selecteds(selecteds)

#标记选中项为喜欢
    def mark_selected_as_favorite(self):
        self.setCursor(QCursor(Qt.BusyCursor))
        selections = self.managePage.listsFrame.musicTable.selectionModel()
        selecteds = selections.selectedIndexes()
        marked = []
        marked.clear()
        for index in selecteds:
            row = index.row()
            record = self.managePage.listsFrame.model.record(row)
            title = record.value("title")
            path = record.value("paths")
            if index.column() == 0:
                if title not in self.lovedSongs and os.path.exists(record.value("paths")):
                    if self.playTable == Configures.PlaylistFavorite:
                        self.playback_musictable_add_widget(path, title)
                    marked.append(title)
                    self.lovedSongs.append(title)
                    self.model.initial_model(Configures.PlaylistFavorite)
                    self.model.add_record(record.value('title'), record.value('length'), record.value('album'), record.value('paths'), record.value('size'))
                    self.model.submitAll()
        self.model.initial_model(self.playTable)
        self.musicTable.initial_view(self.model)
        self.check_favorite()
        self.setCursor(QCursor(Qt.ArrowCursor))

    def mark_as_favorite(self):   
        if self.playTable == Configures.PlaylistFavorite or not self.model.rowCount() or self.currentSourceRow < 0:
            return
        record = self.model.record(self.currentSourceRow)
        path = record.value("paths")
        title = record.value("title")
        if self.playTable == Configures.PlaylistOnline:
            musicName = get_full_music_name_from_title(title)
            musicPath = os.path.join(self.downloadDir, musicName)
            musicPathO = os.path.join(Configures.MusicsDir, musicName)
            if not os.path.exists(musicPath) and not os.path.exists(musicPathO):
                QMessageBox.information(self, '提示', '请先下载该歌曲再添加喜欢！')
                return
            if os.path.exists(musicPath):
                record.setValue("paths", musicPath)
            else:
                record.setValue("paths", musicPathO)
        elif not os.path.exists(path):
            QMessageBox.information(self, "提示", "路径'"+"%s"%path+"'无效，无法标记喜欢！")
            return
        self.model.initial_model(Configures.PlaylistFavorite)
        if title in self.lovedSongs:
            self.model.removeRow(self.lovedSongs.index(title))
            self.model.submitAll()
            self.lovedSongs.remove(title)
            self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.FavoritesNo))
            self.playbackPage.favoriteButton.setToolTip("收藏")
        else:
            self.model.add_record(record.value('title'), record.value('length'), record.value('album'), record.value('paths'), record.value('size'))
            self.lovedSongs.append(title)
            self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
            self.playbackPage.favoriteButton.setToolTip("取消收藏")
        self.model.initial_model(self.playTable)
        self.musicTable.initial_view(self.model)
        if self.currentTable == Configures.PlaylistFavorite:
            self.managePage.listsFrame.model.initial_model(self.currentTable)
            self.managePage.listsFrame.musicTable.setModel(self.managePage.listsFrame.model)

    def check_favorite(self):
        if self.model.get_record_title(self.currentSourceRow) in self.lovedSongs:
            self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
            self.playbackPage.favoriteButton.setToolTip('取消收藏')
        else:
            self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.FavoritesNo))
            self.playbackPage.favoriteButton.setToolTip('收藏')
        if self.playTable == Configures.PlaylistFavorite:
            self.playbackPage.favoriteButton.setToolTip('收藏')

    def listen_local(self, toListen):
        if self.currentTable != Configures.PlaylistDownloaded:
            self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(3, 0))
        k = self.add_only(self.managePage.downloadPage.valid)[3]
        if self.playTable == Configures.PlaylistDownloaded:
            self.model.initial_model(self.currentTable)    
            self.musicTable.initial_view(self.model)
        if toListen:
            self.music_table_clicked(self.managePage.listsFrame.model.index(k, 0))

    def begin_to_listen(self, title, album, songLink, musicId):
        if not songLink:
            QMessageBox.critical(self, '错误', '链接为空，无法播放！')
            return
        if self.currentTable != Configures.PlaylistOnline:
            self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(0, 0))
        k = -1
        for i in range(0, self.managePage.listsFrame.model.rowCount()):
            if self.managePage.listsFrame.model.get_record_musicId(i) == musicId:
                k = i
                break
        if k == -1:
            self.managePage.listsFrame.model.add_record(title, Configures.ZeroTime, album, songLink, 0, musicId)
            if self.playTable == Configures.PlaylistOnline:
                self.playback_musictable_add_widget(musicId, title)
                self.model.initial_model(Configures.PlaylistOnline)
                self.musicTable.initial_view(self.model)
            self.music_table_clicked(self.managePage.listsFrame.model.index(self.managePage.listsFrame.model.rowCount()-1, 0))
        else:
            if self.playTable == Configures.PlaylistOnline and self.currentSourceRow == k:
                return
            self.music_table_clicked(self.managePage.listsFrame.model.index(k, 0))

    def add_to_download(self):
        for songInfoList in self.managePage.searchFrame.readyToDownloadSongs:
            songLink = songInfoList[0]
            musicPath = songInfoList[1]
            title = songInfoList[2]
            album = songInfoList[3]
            musicId = songInfoList[4]
            self.managePage.downloadPage.add_a_download_work(songLink, musicPath, title, album, musicId, 0, self.lock)

    def online_list_song_download(self):
        selections = self.managePage.listsFrame.musicTable.selectionModel()
        selecteds = selections.selectedIndexes()
        isExistsSongs = []
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                songLink = self.managePage.listsFrame.model.get_record_paths(row)
                title = self.managePage.listsFrame.model.get_record_title(row)
                musicId = self.managePage.listsFrame.model.get_record_musicId(row)
                album = self.managePage.listsFrame.model.get_record_album(row)
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


    #note: in pyqt5, function 'QFileDialog.getopenFileNames' return a tuple, it structs like "(['/home/xxx/file.mp3'], '*.mp3')"
    #      while in pyqt4,just a list. 
    def add_files(self):
        files = QFileDialog.getOpenFileNames(self, "选择音乐文件",
                self.downloadDir, self.tr("*.mp3"))[0]
        if not files:
            return
        addCount, newAddedCount = self.add_and_choose_play(files)
        text = "您选择了%s首歌曲！\n新添加了%s首歌曲，其他歌曲已在列表中不被添加！"%(addCount, newAddedCount)
        if newAddedCount >0 and addCount == newAddedCount:
            text = "已添加%s首歌曲!"%newAddedCount
        if newAddedCount == 0:
            text = "选择的歌曲已在列表中！"
        QMessageBox.information(self, "添加完成", text)

    @operate_after_check_thread_locked_state
    @trace_to_keep_time
    def add_only(self, files):
        if not len(files):
            return
        addCount = len(files)
        pathsInTable = []
        newAddedTitles = []
        for i in range(0, self.managePage.listsFrame.model.rowCount()):
            pathsInTable.append(self.managePage.listsFrame.model.get_record_paths(i))
        newAddedCount = 0
        for item in list(set(files)-set(pathsInTable)):
            self.setCursor(QCursor(Qt.BusyCursor))
            title, album, totalTime =  read_music_info(item)
            if self.currentTable == Configures.PlaylistFavorite:
                self.lovedSongs.append(title)
            if self.currentTable == self.playTable:
                self.playback_musictable_add_widget(item, title)
            size = os.path.getsize(item)
            self.managePage.listsFrame.model.add_record(title, totalTime, album, item, size)  
            newAddedTitles.append((title, Configures.LocalMusicId))
        width = self.managePage.listsFrame.musicTable.columnWidth(1)
        self.managePage.listsFrame.model.initial_model(self.currentTable)
        self.managePage.listsFrame.musicTable.initial_view(self.managePage.listsFrame.model)
        self.managePage.listsFrame.musicTable.setColumnWidth(1, width)
        newAddedCount = len(newAddedTitles)
        try:
            index = pathsInTable.index(files[0])
        except:
            index = len(pathsInTable)
        self.managePage.listsFrame.musicTable.selectRow(index)
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.check_favorite()
        if len(newAddedTitles):
            thread = DownloadLrcThread(newAddedTitles)
            thread.setDaemon(True)
            thread.setName("downloadLrc")
            thread.start()
        return addCount, newAddedCount, index

    def add_and_choose_play(self, files):
        addCount, newAddedCount, k = self.add_only(files)
        if self.playTable == self.currentTable:
            self.model.initial_model(self.currentTable)    
            self.musicTable.selectRow(k)
            self.set_media_source_at_row(k)
        return addCount, newAddedCount

    def duration_changed(self, duration):
        self.playbackPage.seekSlider.setMaximum(duration)
        exactTotalTime = format_position_to_mmss(self.mediaPlayer.duration()//1000)
        if self.totalTime != exactTotalTime:
            self.totalTime = exactTotalTime
            self.managePage.timeLabel.setText('%s/%s'%(Configures.ZeroTime, self.totalTime))
            self.playbackPage.timeLabel2.setText(self.totalTime)
            self.model.setData(self.model.index(self.currentSourceRow, 2), self.totalTime)
            self.model.submitAll()
            self.musicTable.selectRow(self.currentSourceRow)
            if self.currentTable == self.playTable:
                self.managePage.listsFrame.model.initial_model(self.playTable)
                self.managePage.listsFrame.musicTable.setModel(self.managePage.listsFrame.model)
                self.managePage.listsFrame.musicTable.selectRow(self.currentSourceRow)

    def tick(self):
        if not self.musicTable.currentIndex():
            self.musicTable.selectRow(self.currentSourceRow)
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
            if currentTime-self.lyricOffset <= self.t[0]:
                self.managePage.lyricLabel.setText('歌词同步显示')
            for i in range(len(self.t) - 1):
                if self.t[i] < currentTime-self.lyricOffset and self.t[i + 1] > currentTime-self.lyricOffset and i!= self.j:
                    self.j = i
                    if self.lyricDict[self.t[i]]:
                        self.managePage.lyricLabel.setText(self.lyricDict[self.t[i]])
                        self.playbackPage.set_html(i, self.lyricDict, self.t)
                    else:
                        self.managePage.lyricLabel.setText("音乐伴奏... ...")
                    break
            text = self.managePage.lyricLabel.text()
            if not self.playbackPage.desktopLyric.isHidden() and self.playbackPage.desktopLyric.text() != text:
                x, y, old_width, height = self.playbackPage.desktopLyric.geometry_info()
                width = self.playbackPage.desktopLyric.fontMetrics().width(text)
                self.playbackPage.desktopLyric.setFixedWidth(width)
                self.playbackPage.desktopLyric.setText(text)
                self.playbackPage.desktopLyric.setGeometry(x + (old_width - width) / 2, y, width, height)

    def state_changed(self, newState):
        if newState in [QMediaPlayer.PlayingState, QMediaPlayer.PausedState, QMediaPlayer.StoppedState]:
            self.managePage.listsFrame.manageTable.setToolTip('当前播放列表：\n    %s'%self.playTable)
            self.managePage.listsFrame.musicTable.setToolTip('当前播放列表：\n    %s\n'%self.playTable + '当前曲目：\n  %s'%self.model.get_record_title(self.currentSourceRow))      
            if not self.model.rowCount():
                return        
            if not self.musicTable.currentIndex:
                self.musicTable.selectRow(self.currentSourceRow)
            iconPath = IconsHub.ControlPause
            isPaused = False
            if newState in [QMediaPlayer.StoppedState, QMediaPlayer.PausedState]:
                iconPath = IconsHub.ControlPlay
                isPaused = True
            icon = QIcon(iconPath)
            self.playAction.setIcon(icon)
            try:
                self.playbackPage.musicList.allListItems[self.currentSourceRow].set_pause_state(isPaused)
            except:
                pass

    def source_changed(self):  
        if not self.model.rowCount():
            return
        self.check_mountout_state()
        self.managePage.frameBottomWidget.setGradient(0)
        self.update_parameters()
        if self.playTable == Configures.PlaylistOnline or os.path.exists(self.model.get_record_paths(self.currentSourceRow)) :
            self.update_artist_info()
            self.update_lyric()
        else:
            self.managePage.lyricLabel.setText('歌词同步显示')
            self.lyricDict.clear()
            self.managePage.artistHeadLabel.setPixmap(QPixmap(IconsHub.Anonymous))
        self.update_near_played_queue()
        self.check_favorite()

    def check_mountout_state(self):
        if self.settingFrame.mountoutDialog.countoutMode:
            if not self.settingFrame.mountoutDialog.remainMount:
                self.close()
            self.settingFrame.mountoutDialog.remainMount -= 1
            self.settingFrame.mountoutDialog.spinBox.setValue(self.settingFrame.mountoutDialog.remainMount)

    def update_parameters(self):
        oldSourceRow = self.currentSourceRow
        self.currentSourceRow = self.musicTable.currentIndex().row()
        self.playbackPage.musicList.allListItems[self.currentSourceRow].set_pause_state(False)
        try:
            self.playbackPage.musicList.allListItems[oldSourceRow].set_pause_state(True)
        except:
            pass
        self.playbackPage.musicList.selectRow(self.currentSourceRow)
        title = self.model.get_record_title(self.currentSourceRow)
        artistName, musicName = get_artist_and_musicname_from_title(title)
        self.playAction.setText(musicName)
        self.playbackPage.musicNameLabel.setText(musicName)
        self.managePage.artistNameLabel.setText(artistName)
        self.managePage.musicNameLabel.setText(musicName)
        self.totalTime = self.model.get_record_length(self.currentSourceRow)
        self.managePage.timeLabel.setText('%s/%s'%(Configures.ZeroTime, self.totalTime))
        self.playbackPage.timeLabel2.setText(self.totalTime)

    def update_near_played_queue(self):
        currentSourceId = self.model.get_record_paths(self.currentSourceRow)
        if self.playTable == Configures.PlaylistOnline:
            currentSourceId = self.model.get_record_musicId(self.currentSourceRow)
        if currentSourceId not in self.nearPlayedSongs:
            self.nearPlayedSongs.append(currentSourceId)
        while len(self.nearPlayedSongs) >= self.model.rowCount() * 4 / 5:
            del self.nearPlayedSongs[0]

    def update_artist_info(self):
        title = self.model.get_record_title(self.currentSourceRow)
        pixmap = self.playbackPage.update_artist_info(title)
        self.managePage.artistHeadLabel.setPixmap(pixmap)

    def update_lyric(self):
        self.managePage.lyricLabel.setToolTip("正常")
        self.lyricOffset = 0     
        title = self.model.get_record_title(self.currentSourceRow)
        musicId = self.model.get_record_musicId(self.currentSourceRow)
        self.lrcPath = SearchOnline.is_lrc_path_exists(title)
        if not self.lrcPath:
            self.lrcPath = SearchOnline.get_lrc_path(title, musicId)
        with open(self.lrcPath, 'r+') as f:
            lyric = f.read()
        if lyric == 'Configures.UrlError':
            self.lrcPath = SearchOnline.get_lrc_path(title, musicId)
            with open(self.lrcPath, 'r+') as f:
                lyric = f.read()
            if lyric == 'Configures.UrlError':
                self.managePage.lyricLabel.setText("网络出错，无法搜索歌词！")
                self.playbackPage.desktopLyric.setText("网络出错，无法搜索歌词！")
                self.lyricDict.clear()
                self.playbackPage.url_error_lyric()
        elif lyric == 'None':
            self.managePage.lyricLabel.setText("搜索不到匹配歌词！")
            self.playbackPage.desktopLyric.setText("搜索不到匹配歌词！")
            self.lyricDict.clear()
            self.playbackPage.no_matched_lyric()
        else:
            self.managePage.lyricLabel.setText("歌词同步显示")
            self.lyricOffset, self.lyricDict = parse_lrc(lyric)
            self.lyricDict[3000000] = ''
            self.t = sorted(self.lyricDict.keys())
            self.playbackPage.set_lyric_offset(self.lyricOffset, self.lyricDict, self.lrcPath)

    def lyric_offset_changed(self, offset):
        self.lyricOffset = offset
        if len(self.lyricDict):
            if self.lyricOffset > 0:
                self.managePage.lyricLabel.setToolTip("已延迟%s秒"%(self.lyricOffset/1000))
            elif self.lyricOffset < 0:
                self.managePage.lyricLabel.setToolTip("已提前%s秒"%(abs(self.lyricOffset/1000)))
            else:
                self.managePage.lyricLabel.setToolTip("正常")
        else:
            self.managePage.lyricLabel.setToolTip("歌词显示")

    def manage_table_clicked(self, index):
        row = index.row()
        tableName = self.managePage.listsFrame.manageModel.record(row).value('tableName')
        self.currentTable = tableName
        self.managePage.listsFrame.manageTable.selectRow(row)
        self.managePage.listsFrame.check_actions_in_page(row)
        self.managePage.listsFrame.model.initial_model(tableName)
        self.managePage.listsFrame.musicTable.setModel(self.managePage.listsFrame.model)
        if tableName == self.playTable:
            self.managePage.listsFrame.musicTable.selectRow(self.currentSourceRow)

    def add_tables(self):
        existTables = []
        for i in range(0, self.managePage.listsFrame.manageModel.rowCount()):
            existTables.append(self.managePage.listsFrame.manageModel.record(i).value("tableName"))
        j = 1
        while True:            
            textOld = "我的列表%s"%j
            if textOld not in existTables:
                break
            j += 1            
        text, ok = QInputDialog.getText(self, "添加列表", "请输入列表名：", QLineEdit.Normal, textOld)
        if ok:
            if text:
                if text in existTables:
                    QMessageBox.critical(self, "注意！", "列表'%s'已存在！\n请重新添加！"%text)
                    return
                if text in [Configures.PlaylistsManageTable, Configures.DownloadWorksTable]:
                    QMessageBox.critical(self, "注意！", "列表名'％s'与'%s'为系统所用，请选择其他名称!"%(Configures.PlaylistsManageTable, Configures.DownloadWorksTable))
                    return
                self.managePage.listsFrame.manageTable.add_tables(self.managePage.listsFrame.manageModel, "%s"%text)
            else:
                self.managePage.listsFrame.manageTable.add_tables(self.managePage.listsFrame.manageModel, "%s"%textOld)
                text = textOld
            sqlOperator.createTable(text)
            self.managePage.add_a_widget_to_table(text)
            self.managePage.listsFrame.manageModel.setTable(Configures.PlaylistsManageTable)
            self.managePage.listsFrame.manageModel.setHeaderData(1, Qt.Horizontal, "*所有列表*")
            self.managePage.listsFrame.manageModel.select()
            self.managePage.listsFrame.manageTable.initial_view(self.managePage.listsFrame.manageModel)
            self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(self.managePage.listsFrame.manageModel.rowCount() - 1, 0))
            self.managePage.listsFrame.manageTable.selectRow(self.managePage.listsFrame.manageModel.rowCount() - 1)

    def rename_tables(self):
        selections = self.managePage.listsFrame.manageTable.selectionModel()
        selecteds = selections.selectedIndexes()
        selectedsRow = selecteds[0].row()
        oldName = self.managePage.listsFrame.manageModel.data(self.managePage.listsFrame.manageModel.index(selectedsRow, 1))
        newName, ok = QInputDialog.getText(self, "重命名列表", "请输入新列表名：", QLineEdit.Normal, oldName)
        if ok:
            if newName:
                for i in range(0, self.managePage.listsFrame.manageModel.rowCount()):
                    if newName == self.managePage.listsFrame.manageModel.record(i).value("tableName"):
                        QMessageBox.critical(self, "注意！", "列表'%s'已存在！\n请重新修改！"%newName)
                        return
                try:
                    int(newName[0])
                    QMessageBox.critical(self, "注意！", "列表名不能以数字开头！")
                    return
                except:pass
                if newName in [Configures.PlaylistsManageTable, Configures.DownloadWorksTable]:
                    QMessageBox.critical(self, "注意！", "列表名'%s'与'%s'为系统所用，请选择其他名称!"%(Configures.PlaylistsManageTable, Configures.DownloadWorksTable))
                    return
                sqlOperator.renameTable(oldName, newName)
                self.managePage.listsFrame.manageModel.setData(self.managePage.listsFrame.manageModel.index(selectedsRow, 1), newName)
                self.managePage.listsFrame.manageModel.submitAll()
                self.managePage.listButtons[selectedsRow].set_text(newName)
                self.managePage.listsFrame.manageModel.setTable(Configures.PlaylistsManageTable)
                self.managePage.listsFrame.manageModel.setHeaderData(1, Qt.Horizontal, "所有列表")
                self.managePage.listsFrame.manageModel.select()
                if oldName == self.playTable:
                    self.playTable = newName
                self.manage_table_clicked(selecteds[0])
                self.managePage.listsFrame.manageTable.selectRow(selectedsRow)

    def delete_tables(self):    
        selections = self.managePage.listsFrame.manageTable.selectionModel()
        selecteds = selections.selectedIndexes()
        row =  selecteds[0].row()
        tablenameDeleted = self.managePage.listsFrame.manageModel.data(self.managePage.listsFrame.manageModel.index(row, 1))
        ok = QMessageBox.warning(self, "删除列表", "列表'%s'将被删除，表中记录将被全部移除！\n您是否继续？"%tablenameDeleted, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok == QMessageBox.Yes:
            sqlOperator.dropTable(tablenameDeleted)
            self.managePage.listsFrame.manage_model_remove_row(row)
            self.managePage.myListTable.removeRow(row - 4)
            del self.managePage.listButtons[row]
            if self.playTable!= tablenameDeleted:
                for i in range(0, self.managePage.listsFrame.manageModel.rowCount()):
                    if self.managePage.listsFrame.manageModel.record(i).value("tableName") == self.playTable:
                        break
                self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(i, 0))
            else:
                self.ui_initial()
                self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(1, 0))
                self.managePage.listsFrame.musicTable.selectRow(0)
                self.music_table_clicked(self.managePage.listsFrame.musicTable.currentIndex())

    def decide_to_play_or_pause(self, row):
        if  row!= self.currentSourceRow or self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.set_media_source_at_row(row)
        elif self.mediaPlayer.state()  == QMediaPlayer.PausedState:
            self.mediaPlayer.play()
        elif self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()

    def music_table_clicked(self, index):
        row = index.row()
        self.managePage.listsFrame.musicTable.selectRow(row)
        if self.managePage.listsFrame.model.tableName() == self.playTable:
            self.decide_to_play_or_pause(row)
        else:
            playTableOld = self.playTable
            self.playTable = self.managePage.listsFrame.model.tableName()
            self.managePage.change_list_buttons_color(playTableOld, self.playTable)
            self.managePage.listsFrame.stateLabel.setText("当前播放列表：%s"%self.playTable)
            self.model.initial_model(self.managePage.listsFrame.model.tableName())
            self.musicTable.initial_view(self.model)
            self.allPlaySongs = []
            self.playbackPage.musicList.clear_list()
            for i in range(0, self.model.rowCount()):
                ident = self.model.get_record_paths(i)
                if self.playTable == Configures.PlaylistOnline:
                    ident = self.model.get_record_musicId(i)
                title = self.model.get_record_title(i)
                self.playback_musictable_add_widget(ident, title)
            self.set_media_source_at_row(row)

    def playback_page_to_listen(self, ident):
        row = self.playbackPage.musicList.row_of_item(ident)
        self.decide_to_play_or_pause(row)

    def playback_page_music_info(self, ident):
        row = self.playbackPage.musicList.row_of_item(ident)
        self.show_music_info(self.model, row)

    def playback_page_delete_selected(self, selecteds):
        if len(selecteds):
            for i in sorted(range(len(selecteds)), reverse=True):
                index = selecteds[i]
                row = index.row()
                if index.column() == 0:
                    self.playbackPage.musicList.remove_item_at_row(row)
                    del self.allPlaySongs[row]

    def check_and_clear_music_table(self):
        if not self.managePage.listsFrame.model.rowCount():
            return
        ok = QMessageBox.warning(self, "清空列表", "当前列表的所有歌曲(包括当前播放歌曲)都将被移除，请确认!", QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok  == QMessageBox.Yes:
            self.clear_music_table()
            
    @operate_after_check_thread_locked_state
    def clear_music_table(self):
        currentIndex = self.managePage.listsFrame.manageTable.currentIndex()
        sqlOperator.dropTable(self.currentTable)
        sqlOperator.createTable(self.currentTable)
        self.manage_table_clicked(currentIndex)
        if self.playTable == self.currentTable:
            self.ui_initial()
        if self.currentTable == Configures.PlaylistFavorite:
            self.lovedSongs.clear() 
            self.playbackPage.favoriteButton.setIcon(QIcon(IconsHub.FavoritesNo))
    
    def ui_initial(self):
        self.stop_music()
        self.model.initial_model(self.playTable)
        self.musicTable.initial_view(self.model)
        self.allPlaySongs.clear()
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
        if not self.model.rowCount():
            return 
        self.stop_music()
        self.musicTable.selectRow(row)
        if self.playTable == self.managePage.listsFrame.model.tableName():
            self.managePage.listsFrame.musicTable.selectRow(row)
        sourcePath = self.model.get_record_paths(row)
        title = self.model.get_record_title(row)
        musicName = get_full_music_name_from_title(title)
        musicPathO = os.path.join(Configures.MusicsDir, musicName)
        musicPath = os.path.join(self.downloadDir, musicName)
        isAnUrl = False
        errorType = Configures.NoError
        isAnUrl = False
        if  os.path.exists(musicPath):
            sourcePath = musicPath
        elif os.path.exists(musicPathO):
            sourcePath = musicPathO
        elif self.playTable == Configures.PlaylistOnline:
            if sourcePath == Configures.NoLink:
                musicId = self.model.get_record_musicId(row)
                sourcePath = SearchOnline.get_song_link(musicId)
                if sourcePath:
                    self.model.setData(self.model.index(row, 4), sourcePath)
                    self.model.submitAll()
                    self.model.initial_model(self.playTable)
                    self.musicTable.selectRow(row)
                    self.managePage.listsFrame.model.initial_model(self.playTable)
                    self.managePage.listsFrame.musicTable.setModel(self.managePage.listsFrame.model)
                    self.managePage.listsFrame.musicTable.selectRow(row)
                else:
                    errorType = Configures.UrlError
            isAnUrl = True
        else:
            if os.path.exists(self.model.get_record_paths(row)):
                sourcePath=self.model.get_record_paths(row)
            else:
                self.noError = 0
                errorType = Configures.PathError
                sourcePath = "/usr/share/sounds/error_happened.ogg"
        if errorType != Configures.NoError:       
            if self.isHidden():
                self.show()
            if errorType == Configures.DisnetError:
                QMessageBox.critical(self, "错误", "联网出错！\n无法联网播放歌曲'%s'！\n您最好在网络畅通时下载该曲目！"%self.model.get_record_title(row))
            elif errorType == Configures.PathError:
                QMessageBox.information(self, "提示", "路径'%s'无效，请尝试重新下载并添加对应歌曲！"%self.model.get_record_paths(row))
            self.noError = 1 
            return
        if isAnUrl:
            url = QUrl(sourcePath)
        else:
            url = QUrl.fromLocalFile(sourcePath)
#        print(url)
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
        if not self.model.rowCount():
            return
        self.stop_music()
        nextRow = 0
        if self.playbackPage.playmode == Configures.PlaymodeRandom:
            nextSongPath = self.random_a_song()
            nextRow = self.allPlaySongs.index(nextSongPath)
        elif self.playbackPage.playmode == Configures.PlaymodeOrder:
            if self.currentSourceRow - 1 >= 0:
                nextRow = self.currentSourceRow - 1
            else:
                nextRow = self.model.rowCount() - 1
        elif self.playbackPage.playmode == Configures.PlaymodeSingle:
            nextRow = self.currentSourceRow
            if nextRow < 0:
                nextRow = 0
        self.set_media_source_at_row(nextRow)
        if self.playTable == self.managePage.listsFrame.model.tableName():
            self.managePage.listsFrame.musicTable.selectRow(self.musicTable.currentIndex().row())

    def random_a_song(self):
        listTemp = list(set(self.allPlaySongs)-set(self.nearPlayedSongs))
        ran = random.randint(0, len(listTemp)-1)
        return listTemp[ran]

    def next_song(self):
        if not self.model.rowCount():
            return
        self.stop_music()
        nextRow = 0
        if self.playbackPage.playmode == Configures.PlaymodeRandom:
            nextSongPath = self.random_a_song()
            nextRow = self.allPlaySongs.index(nextSongPath)
        elif self.playbackPage.playmode == Configures.PlaymodeOrder:
            if  self.currentSourceRow + 1 < self.model.rowCount():
                nextRow = self.currentSourceRow + 1
            else:
                nextRow = 0
        elif self.playbackPage.playmode == Configures.PlaymodeSingle:
            nextRow = self.currentSourceRow
            if nextRow < 0:
                nextRow = 0
        self.set_media_source_at_row(nextRow)
        if self.playTable == self.managePage.listsFrame.model.tableName():
            self.managePage.listsFrame.musicTable.selectRow(self.musicTable.currentIndex().row())

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
            self.settingFrame.close()
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




import os, time, random
from http.client import HTTPConnection
from socket import gaierror
from PyQt4.QtGui import (QMessageBox, QLineEdit, QIcon, QCursor, QInputDialog, QFileDialog, QTextCursor, QPixmap, QApplication)
from PyQt4.QtCore import Qt, QTime, QUrl

try:
    from PyQt4.phonon import Phonon
except ImportError:
    import sys
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "Music Player",
            "Your Qt installation does not have Phonon support.",
            QMessageBox.Ok | QMessageBox.Default,
            QMessageBox.NoButton)
    sys.exit(1)
from xyplayer.mythreads import DownloadLrcThread
from xyplayer.urldispose import SearchOnline
from xyplayer.configure import Configures
from xyplayer.util import read_music_info, parse_lrc
from xyplayer.player_ui import PlayerUi

class Player(PlayerUi):
    def __init__(self, parent = None):
        super(Player, self).__init__(parent)
        self.create_connections()
        self.managePage.ui_initial()
        self.playbackPage.ui_initial()
    
    def create_connections(self):      
        self.settingFrame.installEventFilter(self)
        
        self.mediaObject.tick.connect(self.tick)        
        self.mediaObject.stateChanged.connect(self.state_changed)      
        self.mediaObject.currentSourceChanged.connect(self.source_changed)
        self.mediaObject.finished.connect(self.music_finished)
        
        self.desktopLyric.hideDesktopLyricSignal.connect(self.show_desktop_lyric)
        
        self.playbackPage.seekSlider.valueChanged.connect(self.slider_value_changed)
        self.playbackPage.seekSlider.sliderPressed.connect(self.slider_pressed)
        self.playbackPage.seekSlider.sliderReleased.connect(self.seek)
        self.playbackPage.desktopLyricButton.clicked.connect(self.show_desktop_lyric)
        self.playbackPage.lyric_offset_changed_signal.connect(self.lyric_offset_changed)
        
        self.managePage.current_table_changed_signal.connect(self.current_table_changed)
        self.managePage.show_lists_manage_frame_signal.connect(self.show_current_table)
        self.managePage.listsFrame.titleLabel.clicked.connect(self.lists_frame_title_label_clicked)
        self.managePage.add_a_list_signal.connect(self.add_tables)
        self.managePage.randomOneButton.clicked.connect(self.listen_random_one)
        self.managePage.listsFrame.musicTable.addMusicAction.triggered.connect(self.add_files)
        self.managePage.listsFrame.musicTable.markSelectedAsFavoriteAction.triggered.connect(self.mark_selected_as_favorite)
        self.managePage.listsFrame.musicTable.deleteAction.triggered.connect(self.delete_localfile)
        self.managePage.listsFrame.musicTable.deleteSelectedsAction.triggered.connect(self.delete_selecteds)
        self.managePage.listsFrame.musicTable.clearTheListAction.triggered.connect(self.music_table_cleared)
        self.managePage.listsFrame.musicTable.downloadAction.triggered.connect(self.online_list_song_download)
        self.managePage.listsFrame.musicTable.songSpecAction.triggered.connect(self.song_spec)
        self.managePage.listsFrame.musicTable.switchToSearchPageAction.triggered.connect(self.managePage.show_search_frame)
        self.managePage.listsFrame.musicTable.doubleClicked.connect(self.music_table_clicked)

        self.managePage.listsFrame.manageTable.addTableAction.triggered.connect(self.add_tables)
        self.managePage.listsFrame.manageTable.addMusicHereAction.triggered.connect(self.add_files)
        self.managePage.listsFrame.manageTable.renameTableAction.triggered.connect(self.rename_tables)
        self.managePage.listsFrame.manageTable.deleteTableAction.triggered.connect(self.delete_tables)
        self.managePage.listsFrame.manageTable.pressed.connect(self.manage_table_clicked)
        
        self.managePage.downloadPage.listen_online_signal.connect(self.begin_to_listen)
        self.managePage.downloadPage.listen_local_signal.connect(self.listen_local)
        
        self.managePage.searchFrame.switch_to_online_list.connect(self.switch_to_online_list)
        self.managePage.searchFrame.listen_online_signal.connect(self.begin_to_listen)
        self.managePage.searchFrame.listen_local_signal.connect(self.listen_local)
        self.managePage.searchFrame.add_to_download_signal.connect(self.add_to_download)
        self.managePage.searchFrame.add_bunch_to_list_succeed.connect(self.fresh_online_list)
        self.managePage.frameBottomWidget.clicked.connect(self.show_mainstack_1)
        self.managePage.lyricLabel.clicked.connect(self.show_mainstack_1)
        
        self.pathsetFrame.downloadDirChanged.connect(self.set_new_downloaddir)
        
        self.playbackPage.playmodeButton.clicked.connect(self.playmode_changed)
        self.playbackPage.favoriteButton.clicked.connect(self.mark_as_favorite)
        self.playbackPage.backButton.clicked.connect(self.show_mainstack_0)
#        self.playbackPage.playButton.clicked.connect(self.play_music)
#        self.playbackPage.nextButton.clicked.connect(self.next_song)
#        self.playbackPage.previousButton.clicked.connect(self.previous_song)

        self.settingFrame.mountoutExitButton.clicked.connect(self.show_mountout_dialog)
        self.settingFrame.timeoutExitButton.clicked.connect(self.show_timeout_dialog)
        self.settingFrame.downloadPathButton.clicked.connect(self.show_pathset_frame)
        self.settingFrame.aboutButton.clicked.connect(self.about)

        self.timeoutDialog.time_out_signal.connect(self.close)

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
        try:
            artist = title.split('._.')[0]
            musicName = title.split('._.')[1]
        except:
            artist = '未知'
            musicName = title
        if musicName:
            information = "歌手：%s\n曲名：%s\n时长：%s\n专辑：%s\n路径：%s"%(artist, musicName, timeLength, album, path)
        else:
            information = "标题：%s\n时长：%s\n专辑：%s\n路径：%s"%(title, timeLength, album, path)
        QMessageBox.information(self, "歌曲详细信息", information)
    
    def fresh_online_list(self):
        if self.playTable == '在线试听':
            self.model.initial_model('在线试听')
            self.musicTable.initial_view(self.model)
            for item in self.managePage.searchFrame.added_items:
                self.playback_musictable_add_widget(item[0])
    
    def set_new_downloaddir(self, newDir):
        self.downloadDir = newDir
    
    def slider_pressed(self):
        self.mediaObject.tick.disconnect(self.tick)
    
    def seek(self):
        if self.mediaObject.state() == Phonon.StoppedState:
            self.mediaObject.play()
            self.mediaObject.seek(self.playbackPage.seekSlider.value())
        else:
            self.mediaObject.seek(self.playbackPage.seekSlider.value())
            self.mediaObject.play()
        self.mediaObject.tick.connect(self.tick)

#删除选中项 
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
                if self.deleteLocalfilePermit:
                    self.managePage.listsFrame.model.delete_localfiles(selecteds)
                self.managePage.listsFrame.model.delete_selecteds(selecteds)
                if self.playTable == self.currentTable:
                    self.playback_page_delete_selected(selecteds)
                    self.currentSourceRow  -=  cnt1
                    self.model.initial_model(self.playTable)
                    self.musicTable.selectRow(self.currentSourceRow)
                    self.managePage.listsFrame.musicTable.selectRow(self.currentSourceRow)
            else:
                currentMusic = self.managePage.listsFrame.model.record(self.currentSourceRow).value("title")
                if self.deleteLocalfilePermit:
                    text_tmp3 = "移除并删除当前歌曲"
                    text_tmp4 = "当前播放的歌曲: %s 将会被移除并被删除！\n请确认！"%currentMusic
                else:
                    text_tmp3 = "移除当前歌曲"
                    text_tmp4 = "当前播放的歌曲: %s 将会被移除!\n您是否要移除这首歌曲？"%currentMusic
                ok = QMessageBox.warning(self, text_tmp3, text_tmp4, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
                if ok  == QMessageBox.Yes:
                    if cnt ==  self.managePage.listsFrame.model.rowCount():
                        self.ui_initial()
                        if self.deleteLocalfilePermit:
                            self.managePage.listsFrame.model.delete_localfiles(selecteds)
                        self.managePage.listsFrame.model.delete_selecteds(selecteds)
                        self.playback_page_delete_selected(selecteds)
                        self.model.initial_model(self.playTable)
                    elif cnt == selectedsSpan and selecteds[-1].row() == self.managePage.listsFrame.model.rowCount() - 1:
                        if self.deleteLocalfilePermit:
                            self.managePage.listsFrame.model.delete_localfiles(selecteds)    
                        self.managePage.listsFrame.model.delete_selecteds(selecteds)     
                        self.playback_page_delete_selected(selecteds)   
                        self.model.initial_model(self.playTable)     
                        self.media_sources_seted(0)
                        self.managePage.listsFrame.musicTable.selectRow(0)
                    else:     
                        firstDeletedRow = selecteds[0].row()
                        if self.deleteLocalfilePermit:
                            self.managePage.listsFrame.model.delete_localfiles(selecteds)
                        self.managePage.listsFrame.model.delete_selecteds(selecteds)
                        self.playback_page_delete_selected(selecteds)
                        self.model.initial_model(self.playTable)
                        self.media_sources_seted(firstDeletedRow)
                        self.managePage.listsFrame.musicTable.selectRow(firstDeletedRow)
                elif ok  == QMessageBox.No:
                    selecteds1 = []
#                    for index in selecteds:
#                        row = index.row()
#                        if index.column() == 0 and self.managePage.listsFrame.model.record(row).value("paths")!=  self.managePage.listsFrame.model.record(self.currentSourceRow).value("paths"):
#                            if self.deleteLocalfilePermit:
#                                self.managePage.listsFrame.model.delete_localfiles(index)
#                            self.managePage.listsFrame.model.removeRow(row)
                    for index in selecteds:
                        row = index.row()
                        if self.managePage.listsFrame.model.record(row).value("paths") ==  self.managePage.listsFrame.model.record(self.currentSourceRow).value("paths"):
                            continue
                        selecteds1.append(index)
                    if self.deleteLocalfilePermit:
                            self.managePage.listsFrame.model.delete_localfiles(selecteds1)    
                    self.managePage.listsFrame.model.delete_selecteds(selecteds1)     
                    self.playback_page_delete_selected(selecteds1)   
                    self.model.initial_model(self.playTable) 
                    self.currentSourceRow  -=  cnt1
                    self.managePage.listsFrame.musicTable.selectRow(self.currentSourceRow)
                    self.musicTable.selectRow(self.currentSourceRow)
            self.setCursor(QCursor(Qt.ArrowCursor))
            if self.currentTable == "喜欢歌曲":
                self.lovedSongs.clear()
                for i in range(0, self.managePage.listsFrame.model.rowCount()):
                    self.lovedSongs.append(self.managePage.listsFrame.model.record(i).value("title"))
            if self.currentTable == self.playTable:
                self.allPlaySongs.clear()
                for i in range(0, self.managePage.listsFrame.model.rowCount()):
                    self.allPlaySongs.append(self.managePage.listsFrame.model.record(i).value("paths"))                
            self.check_favorite()

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
            if index.column() == 0:
                if record.value("title") not in self.lovedSongs and os.path.exists(record.value("paths")):
                    marked.append(record.value("title"))
                    self.lovedSongs.append(record.value("title"))
                    self.model.initial_model("喜欢歌曲")
                    self.model.insertRecord(self.model.rowCount(), record)
                    self.model.submitAll()
        self.model.initial_model(self.playTable)
        self.musicTable.initial_view(self.model)
        self.check_favorite()
#        
#        if len(marked):
#            markedStr = '\n'.join(marked)
#            QMessageBox.information(self, "完成标记", "标记完成以下歌曲：\n%s，其他歌曲不存在无法标记喜欢！"%markedStr)
        self.setCursor(QCursor(Qt.ArrowCursor))
            
    def mark_as_favorite(self):   
        if self.playTable == "喜欢歌曲" or not self.model.rowCount() or self.currentSourceRow < 0:
            return
        record = self.model.record(self.currentSourceRow)
        path = record.value("paths")
        title = record.value("title")
        if self.playTable == "在线试听":
            musicName = title + '.mp3'
            musicPath = os.path.join(self.downloadDir, musicName)
            musicPathO = os.path.join(Configures.musicsDir, musicName)
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
        self.model.initial_model("喜欢歌曲")
        if title in self.lovedSongs:
            self.model.removeRow(self.lovedSongs.index(title))
            self.model.submitAll()
            self.lovedSongs.remove(title)
            self.playbackPage.favoriteButton.setIcon(QIcon(":/iconSources/icons/favorite_no.png"))
            self.playbackPage.favoriteButton.setToolTip("标记为喜欢")
        else:
            self.model.add_record(record.value('title'), record.value('length'), record.value('album'), record.value('paths'), record.value('size'))
            self.lovedSongs.append(title)
            self.playbackPage.favoriteButton.setIcon(QIcon(":/iconSources/icons/favorite.png"))
            self.playbackPage.favoriteButton.setToolTip("取消喜欢标记")
        self.model.initial_model(self.playTable)
        self.musicTable.initial_view(self.model)
        if self.currentTable == "喜欢歌曲":
            self.managePage.listsFrame.model.initial_model(self.currentTable)
            self.managePage.listsFrame.musicTable.setModel(self.managePage.listsFrame.model)
    
    def check_favorite(self):
        if self.model.record(self.currentSourceRow).value("title") in self.lovedSongs:
            self.playbackPage.favoriteButton.setIcon(QIcon(":/iconSources/icons/favorite.png"))
        else:
            self.playbackPage.favoriteButton.setIcon(QIcon(":/iconSources/icons/favorite_no.png"))
        if self.playTable == "喜欢歌曲":
            self.playbackPage.favoriteButton.setToolTip("喜欢")
        
    def listen_local(self, toListen):
        if self.currentTable != "我的下载":
            self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(3, 0))
        k = self.add_only(self.managePage.downloadPage.valid)[3]
        if self.playTable == "我的下载":
            self.model.initial_model(self.currentTable)    
            self.musicTable.initial_view(self.model)
        if toListen:
            self.music_table_clicked(self.managePage.listsFrame.model.index(k, 0))
    
    def begin_to_listen(self, title, album, songLink):
        if not songLink:
            QMessageBox.critical(self, '错误', '链接为空，无法播放！')
            return
        self.managePage.listsFrame.model.initial_model("在线试听")
        self.managePage.listsFrame.musicTable.setModel(self.managePage.listsFrame.model)
        k = -1
        for i in range(0, self.managePage.listsFrame.model.rowCount()):
            if self.managePage.listsFrame.model.record(i).value("paths") == songLink:
                k = i
                break
        if k == -1:
#            musicId = songLink.split('~')[1]
#            lrcName = title + '.lrc'
#            lrcPath = os.path.join(Configures.lrcsDir, lrcName)
#            if os.path.exists(lrcPath):
#                os.remove(lrcPath)
#            SearchOnline.get_lrc_path(title, musicId)
            self.managePage.listsFrame.model.add_record(title, '未知', album, songLink, '0M')
            self.model.initial_model("在线试听")
            self.musicTable.initial_view(self.model)
            self.music_table_clicked(self.managePage.listsFrame.model.index(self.managePage.listsFrame.model.rowCount()-1, 0))
        else:
            self.model.initial_model("在线试听")
            self.musicTable.initial_view(self.model)
            if self.playTable == "在线试听" and self.currentSourceRow == k:
                return
            self.music_table_clicked(self.managePage.listsFrame.model.index(k, 0))
    
    def add_to_download(self):
#        songInfos = json.loads(songInfos)
        for songInfoList in self.managePage.searchFrame.toBeEmited:
#            songInfoList = songInfo.split('->')
            songLink = songInfoList[0]
            musicPath = songInfoList[1]
            title = songInfoList[2]
            album = songInfoList[3]
            musicId = songInfoList[4]
            self.managePage.downloadPage.add_to_downloadtable(songLink, musicPath, title, album, musicId)
    
    def online_list_song_download(self):
        selections = self.managePage.listsFrame.musicTable.selectionModel()
        selecteds = selections.selectedIndexes()
        isExistsSongs = []
        isErrorSongs = []
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                songLinkwrap = self.managePage.listsFrame.model.record(row).value("paths").split('~')
                title = self.managePage.listsFrame.model.record(row).value("title")
                try:
                    songLink = songLinkwrap[0]
                    musicId = songLinkwrap[1]
                except:
                    isErrorSongs.append(title)
                    continue
                album = self.managePage.listsFrame.model.record(row).value("album")
                musicName = title + '.mp3'
                musicPath = os.path.join(self.downloadDir, musicName)
                musicPathO = os.path.join(Configures.musicsDir, musicName)
                if  os.path.exists(musicPath) or os.path.exists(musicPathO):
                    isExistsSongs.append(title)
                    continue
                self.managePage.downloadPage.add_to_downloadtable(songLink, musicPath, title, album, musicId)
        if len(isErrorSongs):
            errorSongs = '\n'.join(isErrorSongs)
            QMessageBox.information(self, "提示", "以下歌曲链接出错，无法下载！\n%s"%errorSongs)
        if len(isExistsSongs):
            existsSongs = '\n'.join(isExistsSongs)
            QMessageBox.information(self, "提示", "以下歌曲已在下载目录中不再进行下载，您可以在不联网的情况下点击在线列表播放！\n%s"%existsSongs)

#计数退出的两个函数    
#    def mountout_start(self, remainMount):
#        self.remainMount = remainMount
#        self.mountoutMode = 1
#        self.settingFrame.mountoutExitButton.setText("计数退出(%s)"%self.remainMount)
#    
#    def mountout_stop(self):
#        self.mountoutMode = 0
#        self.remainMount = 0
#        self.settingFrame.mountoutExitButton.setText("计数退出(×)")
#        self.mountoutDialog.close()
    
    def add_files(self):
        selected_files_list_temp = QFileDialog.getOpenFileNames(self, "选择音乐文件",
                self.downloadDir, self.tr("*.mp3"))
        self.files = selected_files_list_temp
#        selected_files_list.clear()
        print(self.files)
        self.adding()

    def add_only(self, files):
        if not len(files):
            return
        addCount = len(files)
        pathsInTable = []
        newAddedTitles = []
        for i in range(0, self.managePage.listsFrame.model.rowCount()):
            pathsInTable.append(self.managePage.listsFrame.model.record(i).value("paths"))
        newAddedCount = 0
        t1 = time.time()
        for item in files:
            if item not in pathsInTable:
                self.setCursor(QCursor(Qt.BusyCursor))
                title, album, totalTime =  read_music_info(item)
                if self.currentTable == "喜欢歌曲":
                    self.lovedSongs.append(title)
                if self.currentTable == self.playTable:
                    self.allPlaySongs.append(item)
                    self.playback_musictable_add_widget(title)
                fileLength = round(os.path.getsize(item)/Configures.FILE_LENGTH_MB, 1)
                size = '%s M'%fileLength
                t3 = time.time()
                self.managePage.listsFrame.model.add_record(title, totalTime, album, item, size)  
                t4 = time.time()
                print('Player.py Player.add_only t4-t3 = %s'%(t4-t3))
                newAddedTitles.append((title, item))
        width = self.managePage.listsFrame.musicTable.columnWidth(1)
        self.managePage.listsFrame.model.initial_model(self.currentTable)
        self.managePage.listsFrame.musicTable.initial_view(self.managePage.listsFrame.model)
        self.managePage.listsFrame.musicTable.setColumnWidth(1, width)
        t2 = time.time()
        print('Player.py Player.add_only t2-t1 = %s'%(t2-t1))
        newAddedCount = len(newAddedTitles)
        repeatCount = addCount-newAddedCount     
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
        return addCount, newAddedCount, repeatCount, index
        
    def add_and_choose_play(self, files):
        addCount, newAddedCount, repeatCount, k = self.add_only(files)
        if self.playTable == self.currentTable:
            self.model.initial_model(self.currentTable)    
            self.musicTable.selectRow(k)
            self.media_sources_seted(k)
        return addCount, newAddedCount, repeatCount

    def adding(self):  
        if not self.files:
            return
        addCount, newAddedCount, repeatCount = self.add_and_choose_play(self.files)
        QMessageBox.information(self, "添加完成", "您选择了%s首歌曲！\n新添加了%s首歌曲，有%s首歌曲已在列表中不被添加！"%(addCount, newAddedCount, repeatCount))
        
    def tick(self):
        if not self.musicTable.currentIndex():
            self.musicTable.selectRow(self.currentSourceRow)
        self.playbackPage.seekSlider.setRange(0, self.mediaObject.totalTime())
        currentTime = self.mediaObject.currentTime()
        self.syc_lyric(currentTime)
        self.playbackPage.seekSlider.setValue(currentTime)
        minutes = (currentTime / 60000) % 60
        seconds = (currentTime / 1000) % 60
        self.cTime = QTime(0, minutes, seconds ).toString('mm:ss')
        totalTimeValue = self.mediaObject.totalTime()/1000
        try:
            ratio = currentTime/1000/totalTimeValue
        except:
            ratio = 0
        self.managePage.frameBottomWidget.setGradient(ratio)
        if self.totalTime == '未知':
            hours = totalTimeValue/3600
            minutes = (totalTimeValue%3600)/60
            seconds = (totalTimeValue)%3600%60
            if totalTimeValue < 3600:
                self.totalTime = QTime(0, minutes, seconds).toString('mm:ss')
            else:
                self.totalTime = QTime(hours, minutes, seconds).toString('hh:mm:ss')
            self.model.setData(self.model.index(self.currentSourceRow, 2), self.totalTime)
            self.model.submitAll()
            self.musicTable.selectRow(self.currentSourceRow)
            if self.currentTable == self.playTable:
                self.managePage.listsFrame.model.initial_model(self.playTable)
                self.managePage.listsFrame.musicTable.setModel(self.managePage.listsFrame.model)
                self.managePage.listsFrame.musicTable.selectRow(self.currentSourceRow)
        self.managePage.timeLabel.setText(self.cTime + '/' + self.totalTime)
        self.playbackPage.timeLabel1.setText(self.cTime)
        self.playbackPage.timeLabel2.setText(self.totalTime)
    
    def syc_lyric(self, currentTime):
        if len(self.lyricDict) and self.playbackPage.document.blockCount():
            t = sorted(self.lyricDict.keys())
            if currentTime-self.lyricOffset <= t[1]:
                self.managePage.lyricLabel.setText('歌词同步显示于此！')
                return
            vscrollbar = self.playbackPage.lyricText.verticalScrollBar() 
            for i in range(1, len(t)-1):
                if t[i] < currentTime-self.lyricOffset and t[i + 1] > currentTime-self.lyricOffset and i!= self.j:
                    if self.lyricDict[t[i]]:
                        self.managePage.lyricLabel.setText(self.lyricDict[t[i]])
                        self.jump_to_line(i + 6)
                    else:
                        self.managePage.lyricLabel.setText("音乐伴奏... ...")
                    print(self.playbackPage.lyricText.height())
#                    half_line_num = self.playbackPage.lyricText.height() / (2*Configures.LINE_HEIGHT)
                    if i + 6 >= 7:
                        value = (i - 1) * Configures.LINE_HEIGHT
#                        value_offset = Configures.LINE_HEIGHT/((t[i+1] - t[i])*2)
#                        new_value = value + value_offset
                        vscrollbar.setValue(value )
                        if value + Configures.LINE_HEIGHT > vscrollbar.maximum():
                            if self.j == len(t) -8:
                                self.playbackPage.lyricText.append('The End')
                            else:
                                self.playbackPage.lyricText.append(' ')
                    self.j = i
                    break
            if currentTime > t[-1] and self.j != len(t) - 1:
                if self.lyricDict[t[-1]]:
                    self.managePage.lyricLabel.setText(self.lyricDict[t[-1]])
                    self.jump_to_line(len(t) + 5)
                    vscrollbar.setValue(vscrollbar.value()+Configures.LINE_HEIGHT)
                else:
                    self.managePage.lyricLabel.setText("音乐伴奏... ...")
                self.j = len(t) - 1
            if not self.desktopLyric.isHidden():
                self.desktopLyric.setText(self.managePage.lyricLabel.text())
                
    def jump_to_line(self, line_num):
        block = self.playbackPage.document.findBlockByNumber(line_num)
        pos = block.position()
#        print("jumpToLine_%s"%pos)
        cur = self.playbackPage.lyricText.textCursor()
        cur.setPosition(pos, QTextCursor.MoveAnchor)
        cur.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.playbackPage.lyricText.setTextCursor(cur)
    
    def state_changed(self, newState, oldState):
        self.managePage.listsFrame.manageTable.setToolTip('当前播放列表：\n    %s'%self.playTable)
        self.managePage.listsFrame.musicTable.setToolTip('当前播放列表：\n    %s\n'%self.playTable + '当前曲目：\n  %s'%self.model.record(self.currentSourceRow).value("title"))        
        if not self.model.rowCount():
            return        
        if not self.musicTable.currentIndex:
            self.musicTable.selectRow(self.currentSourceRow)
        if newState == Phonon.ErrorState:
            self.noError = 0
            sourceDispose =  Phonon.MediaSource("/usr/share/sounds/error_happened.ogg")
            self.mediaObject.setCurrentSource(sourceDispose)
            self.mediaObject.play()
            self.show()
            if self.mediaObject.errorType() == Phonon.FatalError:
                QMessageBox.warning(self, "致命错误", self.mediaObject.errorString())
            else:
                QMessageBox.warning(self, "错误", self.mediaObject.errorString())
        elif newState == Phonon.PlayingState:
            self.playAction.setIcon(QIcon(":/iconSources/icons/pause.png"))
#            self.playbackPage.playButton.setIcon(QIcon(":/iconSources/icons/pause.png"))
            try:
                self.widgets[self.currentSourceRow].playButton.setIcon(QIcon(":/iconSources/icons/pause.png"))
            except:pass
        elif newState == Phonon.StoppedState:
            self.playAction.setIcon(QIcon(":/iconSources/icons/play.png"))
#            self.playbackPage.playButton.setIcon(QIcon(":/iconSources/icons/play.png"))
            try:
                self.widgets[self.currentSourceRow].playButton.setIcon(QIcon(":/iconSources/icons/play.png"))
            except:
                pass
        elif newState == Phonon.PausedState:
            self.playAction.setIcon(QIcon(":/iconSources/icons/play.png"))
#            self.playbackPage.playButton.setIcon(QIcon(":/iconSources/icons/play.png"))
            self.widgets[self.currentSourceRow].playButton.setIcon(QIcon(":/iconSources/icons/play.png"))

    def source_changed(self):  
        if not self.model.rowCount():
            return
        self.check_mountout_state()
        self.managePage.frameBottomWidget.setGradient(0)
        self.update_parameters()
        if self.playTable == "在线试听" or os.path.exists(self.model.record(self.currentSourceRow).value("paths")) :
            self.update_artist_info()
            self.update_lyric()
        else:
            self.managePage.lyricLabel.setText('歌词同步显示于此！')
            self.lyricDict.clear()
            self.managePage.artistHeadLabel.setPixmap(QPixmap(":/iconSources/icons/anonymous.png"))
#            self.info=''
        self.update_near_played_queue()
        self.check_favorite()
    
    def check_mountout_state(self):
        if self.mountoutDialog.countoutMode:
            if not self.mountoutDialog.remainMount:
                self.close()
            self.mountoutDialog.remainMount -= 1
            self.mountoutDialog.spinBox.setValue(self.mountoutDialog.remainMount)
            
    def update_parameters(self):
        self.playTable = self.model.tableName()
        try:
            self.widgets[self.currentSourceRow].playButton.setIcon(QIcon(":/iconSources/icons/play.png"))
        except:pass
        self.currentSourceRow = self.musicTable.currentIndex().row()
        self.widgets[self.currentSourceRow].playButton.setIcon(QIcon(":/iconSources/icons/pause.png"))
        self.playbackPage.musicTable.selectRow(self.currentSourceRow)
        self.totalTime = self.model.record(self.currentSourceRow).value("length")
        title = self.model.record(self.currentSourceRow).value("title")
        try:
            artistName = title.split('._.')[0]
            musicName = title.split('._.')[1]
        except:
            artistName = '未知'
            musicName = title
        self.playbackPage.musicNameLabel.setText(musicName)
        self.managePage.artistNameLabel.setText(artistName)
        self.managePage.musicNameLabel.setText(musicName)
        self.managePage.timeLabel.setText('00:00/'+self.totalTime)
    
    def update_near_played_queue(self):
        currentSourcePath = self.model.record(self.currentSourceRow).value("paths")
        if currentSourcePath not in self.toPlaySongs:
            self.toPlaySongs.append(currentSourcePath)
        while len(self.toPlaySongs) > self.model.rowCount()*3//5:
            del self.toPlaySongs[0]
            
    def update_artist_info(self):
        title = self.model.record(self.currentSourceRow).value("title")
        pixmap = self.playbackPage.update_artist_info(title)
        self.managePage.artistHeadLabel.setPixmap(pixmap)
    
    def update_lyric(self):
        self.managePage.lyricLabel.setToolTip("正常")
        self.lyricOffset = 0     
        musicPath = self.model.record(self.currentSourceRow).value("paths")
        title = self.model.record(self.currentSourceRow).value("title")
        if musicPath[0:4] == 'http':
            musicId = musicPath.split('~')[1]
        else:
            musicId = 0
        self.lrcPath = SearchOnline.is_lrc_path_exists(title)
        if not self.lrcPath:
            self.lrcPath = SearchOnline.get_lrc_path(title, musicId)
        with open(self.lrcPath, 'r+') as f:
            lyric = f.read()
        if lyric == 'Configures.URLERROR':
            self.lrcPath = SearchOnline.get_lrc_path(title, musicId)
            with open(self.lrcPath, 'r+') as f:
                lyric = f.read()
            if lyric == 'Configures.URLERROR':
                self.managePage.lyricLabel.setText("网络出错，无法搜索歌词！")
                self.desktopLyric.setText("网络出错，无法搜索歌词！")
                self.lyricDict.clear()
                self.playbackPage.url_error_lyric()
        elif lyric == 'None':
            self.managePage.lyricLabel.setText("搜索不到匹配歌词！")
            self.desktopLyric.setText("搜索不到匹配歌词！")
            self.lyricDict.clear()
            self.playbackPage.no_matched_lyric()
        else:
            self.managePage.lyricLabel.setText("歌词同步显示于此！")
            self.lyricOffset, self.lyricDict = parse_lrc(lyric)
            self.playbackPage.set_lyric_offset(self.lyricOffset, self.lyricDict, self.lrcPath)
            self.lyricDict[-1] = '歌词同步显示于此！'
#        if not self.lyricDict:
#            self.show_music_table()
    
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
            textOld = "我的歌单%s"%j
            if textOld not in existTables:
                break
            j += 1            
        text, ok = QInputDialog.getText(self, "添加列表", "请输入列表名：", QLineEdit.Normal, textOld)
        if ok:
            if text:
                if text in existTables:
                    QMessageBox.critical(self, "注意！", "列表'%s'已存在！\n请重新添加！"%text)
                    return
                if text in ['tablesManage', 'downloadTable']:
                    QMessageBox.critical(self, "注意！", "列表名'tablesManage'与'downloadTable'为系统所用，请选择其他名称!")
                    return
                self.managePage.listsFrame.manageTable.add_tables(self.managePage.listsFrame.manageModel, "%s"%text)
            else:
                self.managePage.listsFrame.manageTable.add_tables(self.managePage.listsFrame.manageModel, "%s"%textOld)
                text = textOld
            self.sql.createTable(text)
            self.managePage.add_a_widget_to_table(text)
            self.managePage.listsFrame.manageModel.setTable("tablesManage")
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
        newName, ok = QInputDialog.getText(self, "修改列表名", "请输入新列表名：", QLineEdit.Normal, oldName)
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
                if newName in ['tablesManage', 'downloadTable']:
                    QMessageBox.critical(self, "注意！", "列表名'tablesManage'与'downloadTable'为系统所用，请选择其他名称!")
                    return
                self.sql.renameTable(oldName, newName)
                self.managePage.listsFrame.manageModel.setData(self.managePage.listsFrame.manageModel.index(selectedsRow, 1), newName)
                self.managePage.listsFrame.manageModel.submitAll()
                self.managePage.listButtons[selectedsRow].set_text(newName)
                self.managePage.listsFrame.manageModel.setTable("tablesmanage")
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
        tableDeleted = self.managePage.listsFrame.manageModel.data(self.managePage.listsFrame.manageModel.index(row, 1))
        ok = QMessageBox.warning(self, "删除列表", "列表'%s'将被删除，表中记录将被全部移除！\n您是否继续？"%tableDeleted, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok == QMessageBox.Yes:
            self.sql.dropTable(tableDeleted)
            self.managePage.myListTable.removeRow(row - 4)
            del self.managePage.listButtons[row]
            self.managePage.listsFrame.manageModel.removeRow(selecteds[0].row())
            self.managePage.listsFrame.manageModel.submitAll()
            if self.playTable!= tableDeleted:
                for i in range(0, self.managePage.listsFrame.manageModel.rowCount()):
                    if self.managePage.listsFrame.manageModel.record(i).value("tableName") == self.playTable:
                        break
                self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(i, 0))
            else:
                self.ui_initial()
#                self.playbackPage.musicTable.clear_new_music_table()
#                self.widgets.clear()
                self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(1, 0))
                self.managePage.listsFrame.musicTable.selectRow(0)
                self.music_table_clicked(self.managePage.listsFrame.musicTable.currentIndex())

    def music_table_clicked(self, index):
        self.managePage.listsFrame.musicTable.selectRow(index.row())
#        with open(Configures.settingFile, 'r') as f:
#            self.downloadDir = f.read()
        if self.managePage.listsFrame.model.tableName() == self.playTable:
            if  index.row()!= self.currentSourceRow or self.mediaObject.state() == Phonon.StoppedState:
                self.media_sources_seted(index.row())
            elif self.mediaObject.state()  == Phonon.PausedState:
                self.mediaObject.play()
            elif self.mediaObject.state() == Phonon.PlayingState:
                self.mediaObject.pause()
        else:
            playTableOld = self.playTable
            self.playTable = self.managePage.listsFrame.model.tableName()
            self.managePage.change_list_buttons_color(playTableOld, self.playTable)
            self.managePage.listsFrame.stateLabel.setText("当前播放列表：%s"%self.playTable)
            self.model.initial_model(self.managePage.listsFrame.model.tableName())
            self.musicTable.initial_view(self.model)
            self.media_sources_seted(index.row())
            self.allPlaySongs = []
            self.playbackPage.musicTable.clear_new_music_table()
            self.widgets.clear()
            for i in range(0, self.model.rowCount()):
                self.allPlaySongs.append(self.model.record(i).value("paths"))  
                title = self.model.record(i).value("title")
                self.playback_musictable_add_widget(title)
            self.playbackPage.musicTable.selectRow(index.row())
    
    def playback_page_to_listen(self, title):
        for i in range(len(self.widgets)):
            if self.widgets[i].name == title:
                break
        if  i != self.currentSourceRow or self.mediaObject.state() == Phonon.StoppedState:
            self.media_sources_seted(i)
        elif self.mediaObject.state()  == Phonon.PausedState:
            self.mediaObject.play()
        elif self.mediaObject.state() == Phonon.PlayingState:
            self.mediaObject.pause()
    
    def playback_page_music_info(self, title):
        for i in range(len(self.widgets)):
            if self.widgets[i].name == title:
                break
        self.show_music_info(self.model, i)
                
    def playback_page_delete_selected(self, selecteds):
        if len(selecteds):
            for index in selecteds[len(selecteds) : 0 : -1]:
                row = index.row()
                if index.column() == 0:
                    self.playbackPage.musicTable.removeRow(row)
                    del self.widgets[row]
            row_0 = selecteds[0].row()
            self.playbackPage.musicTable.removeRow(row_0)
            del self.widgets[row_0]

    def music_table_cleared(self):
        if not self.managePage.listsFrame.model.rowCount():
            return
        ok = QMessageBox.warning(self, "清空列表", "当前列表的所有歌曲(包括当前播放歌曲)都将被移除，请确认!", QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok  == QMessageBox.Yes:
            currentIndex = self.managePage.listsFrame.manageTable.currentIndex()
            self.sql.dropTable(self.currentTable)
            self.sql.createTable(self.currentTable)
            self.manage_table_clicked(currentIndex)
            if self.playTable == self.currentTable:
                self.playbackPage.musicTable.clear_new_music_table()
                self.widgets.clear()
                self.model.initial_model(self.playTable)
                self.musicTable.initial_view(self.model)
                self.ui_initial()
                self.allPlaySongs.clear()
                self.playbackPage.favoriteButton.setIcon(QIcon(":/iconSources/icons/favorite.png"))
                self.playbackPage.favoriteButton.setToolTip("喜欢")
            if self.currentTable == "喜欢歌曲":
                self.lovedSongs.clear()
                self.playbackPage.favoriteButton.setIcon(QIcon(":/iconSources/icons/favorite_no.png"))
        
    def slider_value_changed(self, value):
        minutes = (value / 60000) % 60
        seconds = (value / 1000) % 60
        cTime = QTime(0, minutes, seconds ).toString('mm:ss')
        self.managePage.timeLabel.setText(cTime + '/' + self.totalTime)
        self.playbackPage.timeLabel1.setText(cTime)
        self.playbackPage.timeLabel2.setText(self.totalTime)
        self.syc_lyric(value)
        
    def media_sources_seted(self, row):    
        if not self.model.rowCount():
            return 
        self.stop_music()
        self.musicTable.selectRow(row)
        if self.playTable == self.managePage.listsFrame.model.tableName():
            self.managePage.listsFrame.musicTable.selectRow(row)
        
        sourcePath = self.model.record(row).value("paths")
        title = self.model.record(row).value("title")
        
        musicName = title + '.mp3'
        musicPathO = os.path.join(Configures.musicsDir, musicName)
        musicPath = os.path.join(self.downloadDir, musicName)
        if  os.path.exists(musicPath):
            sourcePath = musicPath
        elif os.path.exists(musicPathO):
            sourcePath = musicPathO
        elif self.playTable == "在线试听":
            isErrorHappen = self.is_url_error()
            if isErrorHappen:
                self.noError = 0
                sourceDispose =  Phonon.MediaSource("/usr/share/sounds/error_happened.ogg")
                self.mediaObject.setCurrentSource(sourceDispose)
                self.mediaObject.play()
                if self.isHidden():
                    self.show()
#                    if errorType == Configures.URLERROR:
                QMessageBox.critical(self, "错误", "联网出错！\n"+"无法联网播放歌曲'"+"%s"%self.model.record(row).value("title")+"'！\n您最好在网络畅通时下载该曲目！")
            else:
                sourcePath = sourcePath.split('~')[0].strip()
                sourceDispose =  Phonon.MediaSource(QUrl(sourcePath))
                self.mediaObject.setCurrentSource(sourceDispose)
                self.mediaObject.play()
            return
        else:
            if os.path.exists(self.model.record(row).value('paths')):
                sourcePath=self.model.record(row).value('paths')
            else:
                self.noError = 0
                sourceDispose =  Phonon.MediaSource("/usr/share/sounds/error_happened.ogg")
                self.mediaObject.setCurrentSource(sourceDispose)
                self.mediaObject.play()
                self.show()
                QMessageBox.information(self, "提示", "路径'"+"%s"%self.model.record(row).value("paths")+"'无效，请尝试重新下载并添加对应歌曲！")
                return
        sourcePath = 'file://' + sourcePath
        sourceDispose =  Phonon.MediaSource(QUrl(sourcePath))
        self.mediaObject.setCurrentSource(sourceDispose)
        self.mediaObject.play()

    def is_url_error(self):
        t1 = time.time()
        try:
            conn = HTTPConnection('www.baidu.com')
            conn.request('GET', '/')
            res = conn.getresponse()
            print('Player.py Player.is_url_error %s'%(time.time() - t1))
            if res.status == 200 and res.reason == 'OK':
                return False
            return True
        except gaierror:
            return True

    def play_music(self):
        if self.mediaObject.state() == Phonon.PlayingState :
            self.mediaObject.pause()
        else:
            self.mediaObject.play()
    
    def stop_music(self):
        self.mediaObject.stop()
        self.playbackPage.seekSlider.setValue(0)
        self.syc_lyric(-0.5)

    def previous_song(self):
        if not self.model.rowCount():
            return
        self.stop_music()
        self.mediaObject.clearQueue()
        if self.playmodeIndex == 1:
            if self.currentSourceRow - 1 >= 0:
                self.media_sources_seted(self.currentSourceRow - 1)
            else:
                self.media_sources_seted(self.model.rowCount() - 1)
        if self.playmodeIndex == 2:
            listTemp = []
            for item in self.allPlaySongs:
                if item not in self.toPlaySongs:
                    listTemp.append(item)
            nextSongPath = random.sample(listTemp, 1)[0]
            nextRow = self.allPlaySongs.index(nextSongPath)
            self.media_sources_seted(nextRow)
        if self.playmodeIndex == 3:
            self.media_sources_seted(self.currentSourceRow)
        if self.playTable == self.managePage.listsFrame.model.tableName():
            self.managePage.listsFrame.musicTable.selectRow(self.musicTable.currentIndex().row())

    def next_song(self):
        if not self.model.rowCount():
            return
        self.stop_music()
        self.mediaObject.clearQueue()
        if self.playmodeIndex == 1:
            if  self.currentSourceRow + 1 < self.model.rowCount():
                self.media_sources_seted(self.currentSourceRow + 1)
            else:
                self.media_sources_seted(0)
        if self.playmodeIndex == 2:
            listTemp = []
            for item in self.allPlaySongs:
                if item not in self.toPlaySongs:
                    listTemp.append(item)
            nextSongPath = random.sample(listTemp, 1)[0]
            nextRow = self.allPlaySongs.index(nextSongPath)
            self.media_sources_seted(nextRow)
        if self.playmodeIndex == 3:
            self.media_sources_seted(self.currentSourceRow)
        if self.playTable == self.managePage.listsFrame.model.tableName():
            self.managePage.listsFrame.musicTable.selectRow(self.musicTable.currentIndex().row())
    
    def listen_random_one(self):
        playmodeTemp = self.playmodeIndex
        self.playmodeIndex = 2
        self.next_song()
        self.playmodeIndex = playmodeTemp

    def music_finished(self):
        if self.noError:
            self.next_song()
        else:
            self.noError = 1







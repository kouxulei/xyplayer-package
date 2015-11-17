import os
from PyQt5.QtWidgets import QMenu, QAction, QAbstractItemView, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from xyplayer import Configures
from xyplayer.myplaylists import Playlist
from xyplayer.mywidgets import PlaylistButton
from xyplayer.utils import trace_to_keep_time, get_artist_and_musicname_from_title, operate_after_check_thread_locked_state

class SearchTable(QTableWidget):
    def __init__(self, parent = None):
        super(SearchTable, self).__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setRowCount(0)
        self.setColumnCount(5)
        self.hideColumn(4)
        self.hideColumn(5)
        headers  =  ( "评分","歌曲", "歌手", "专辑", "musicId")  
        self.setHorizontalHeaderLabels(headers)
#        self.setShowGrid(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
#        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.create_contextmenu()
        
    def add_record(self, score, music, artist, album, musicRid):
            countRow  =  self.rowCount()
            scoreItem = QTableWidgetItem(score)
            scoreItem.setTextAlignment(Qt.AlignCenter)
            musicItem  =  QTableWidgetItem(music)
            artistItem  =  QTableWidgetItem(artist)
            albumItem =  QTableWidgetItem(album)            
            musicRidItem  =  QTableWidgetItem(musicRid)
#            totalTimeItem.setTextAlignment(Qt.AlignCenter)
#            artistIdItem  =  QTableWidgetItem(artistId)
            
            self.insertRow(countRow)
            self.setItem(countRow, 0, scoreItem)
            self.setItem(countRow, 1, musicItem)
            self.setItem(countRow, 2, artistItem)
            self.setItem(countRow, 3, albumItem)
            self.setItem(countRow, 4, musicRidItem)           
#            self.setItem(countRow, 5, artistIdItem)
            
    def clear_search_table(self):
        while self.rowCount():
            self.removeRow(0)
   
    def create_contextmenu(self):
        self.listMenu  =  QMenu()
        self.listenOnlineAction = QAction('立即试听', self)
        self.addBunchToListAction = QAction('添加到试听列表', self)
        self.downloadAction  =  QAction('下载', self)
        self.switchToOnlineListAction = QAction('切换到试听列表', self)
        self.listMenu.addAction(self.listenOnlineAction)
        self.listMenu.addAction(self.addBunchToListAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.downloadAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.switchToOnlineListAction)
        
        self.customContextMenuRequested.connect(self.music_table_menu)
                
    def music_table_menu(self, pos):
        pos += QPoint(0, 30)
        self.listMenu.exec_(self.mapToGlobal(pos))
            
class MyListTable(QTableWidget):
    """managePage主页面中我的歌单。"""
    button_in_list_clicked = pyqtSignal(str)
    operate_mode_activated = pyqtSignal()
    remove_a_playlist_signal = pyqtSignal(int)
    rename_a_playlist_signal = pyqtSignal(int)
    def __init__(self, parent=None):
        super(MyListTable, self).__init__(parent)
        self.buttons = []
        self.names = []
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRowCount(0)    
        self.setColumnCount(1)
        self.setFixedWidth(172)
        self.horizontalHeader().setFixedHeight(36)
        self.setColumnWidth(0, 172)
        
    def add_a_button(self, name, flag=True):
        self.names.append(name)
        button = PlaylistButton(name, flag)
        button.clicked.connect(self.button_in_list_clicked.emit)   
        button.long_time_clickd.connect(self.operate_mode_activated.emit)
        button.remove_me_signal.connect(self.remove_action_triggered)
        button.rename_me_signal.connect(self.rename_action_triggered)
        if flag:
            self.add_widget(button)
        self.buttons.append(button)
    
    def get_button_at(self, index):
        return self.buttons[index]
    
    def get_name_at(self, index):
        return self.names[index]
    
    def remove_action_triggered(self, name):
        self.remove_a_playlist_signal.emit(self.names.index(name))
    
    def rename_action_triggered(self, name):
        self.rename_a_playlist_signal.emit(self.names.index(name))
    
    def rename_button_at(self, index, name):
        self.buttons[index].set_name(name)
        self.names[index] = name
    
    def remove_button_at(self, index):
        self.removeRow(index-4)
        del self.buttons[index]
        del self.names[index]
    
    def get_buttons(self):
        return self.buttons
    
    def add_widget(self, widget):
        countRow  =  self.rowCount()
        self.insertRow(countRow)
        self.setRowHeight(countRow, 43)
        self.setCellWidget(countRow, 0, widget)

class WorksList(QTableWidget):
    """用于管理下载任务的列表以及playbackPage中我的歌单的列表。"""
    def __init__(self, parent=None):
        super(WorksList, self).__init__(parent)
        self.setRowCount(0)
        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.allListItems = []
        
    def add_item(self, item, rowHeight):
        countRow  =  self.rowCount()
        self.insertRow(countRow)
        self.setColumnWidth(0, 350)
        self.setRowHeight(countRow, rowHeight)
        self.setCellWidget(countRow, 0, item)
        self.allListItems.append(item)
    
    def remove_item_at_row(self, row):
        self.removeRow(row)
        del self.allListItems[row]
    
    def get_item_at_row(self, row):
        return self.allListItems[row]
    
    def clear_list(self):
        while self.rowCount():
            self.removeRow(0)
            del self.allListItems[0]

    def row_of_item(self, ident):
        i = -1
        for i in range(len(self.allListItems)):
            if self.allListItems[i].ident == ident:
                return i

class PlaylistWidgetBasic(QTableWidget):
    def __init__(self, listName=Configures.PlaylistDefault, parent=None):
        super(PlaylistWidgetBasic, self).__init__(parent)
        self.listName = ''
        self.playlist = Playlist()
    
    def get_playlist(self):
        return self.playlist.copy()
    
    def get_operating_playlist_name(self):
        return self.listName
    
    def fill_playlist_widget(self, playlist):
        self.clear_all_items()
        itemsList = playlist.get_items_queue()
        group = playlist.get_infos_group()
        for item in itemsList:
            title = group[item][0]
            time = group[item][1]
            self.add_record(title, time)
    
    def clear_all_items(self):
        while self.rowCount():
            self.removeRow(0)
    
    def add_record(self, title, time):
        countRow = self.rowCount()
        titleItem = QTableWidgetItem(title)
        timeItem = QTableWidgetItem(time)
        self.insertRow(countRow)
        self.setItem(countRow, 0, titleItem)
        self.setItem(countRow, 1, timeItem)
    
    def add_record_with_full_info(self, id, title, totalTime, album, path, size, musicId=Configures.LocalMusicId):
        self.playlist.add_record(id, title, totalTime, album, path, size, musicId)
        self.add_record(title, totalTime)
    
    def add_a_music(self, path):
        title, totalTime = self.playlist.add_item_from_path(path)
        self.add_record(title, totalTime)   

class PlaylistWidget(PlaylistWidgetBasic):
    play_music_at_row_signal = pyqtSignal(int)
    play_or_pause_signal = pyqtSignal(int)
    playlist_changed_signal = pyqtSignal(str, str)
    musics_added_signal = pyqtSignal()
    musics_removed_signal = pyqtSignal()
    musics_cleared_signal = pyqtSignal()
    musics_marked_signal = pyqtSignal()
    switch_to_search_page_signal = pyqtSignal()
    download_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(PlaylistWidget, self).__init__(parent)
        self.initial_params()
        self.set_attritutes()
        self.create_contextmenu()
        self.create_connections()
    
    def initial_params(self):
        self.lock = None
        self.downloadDir = ''
        self.deleteFlag = False
        self.isPlaying = False
        self.playingList = Playlist()
    
    def set_lock(self, lock):
        self.lock = lock
    
    def set_download_dir(self, dir):
        self.downloadDir = dir
    
    def set_playing_status(self, playlist):
        self.playingList = playlist
 
    def set_playlist_use_name(self, listName):
        self.listName = listName
        self.isPlaying = False
        if self.playingList.get_name() == listName:
            self.isPlaying = True
        if self.get_playing_used_state():
            self.playlist = self.playingList.copy()
        else:
            self.playlist.fill_list(listName)
        self.fill_playlist_widget(self.playlist)
        if self.get_playing_used_state():
            self.selectRow(self.playingList.get_current_row())
        self.check_actions_in_page(listName)
    
    def get_playing_used_state(self):
        return self.isPlaying
        
    def create_connections(self):
        self.customContextMenuRequested.connect(self.music_table_menu)   
        self.addMusicAction.triggered.connect(self.add_musics)
        self.markSelectedAsFavoriteAction.triggered.connect(self.mark_selected_as_favorite)
        self.removeAction.triggered.connect(self.remove_musics)
        self.deleteAction.triggered.connect(self.delete_musics)
        self.clearListWidgetAction.triggered.connect(self.clear_musics)
        self.songSpecAction.triggered.connect(self.show_song_spec)
        self.switchToSearchPageAction.triggered.connect(self.switch_to_search_page_signal.emit)
        self.downloadAction.triggered.connect(self.download_signal.emit)
        self.doubleClicked.connect(self.double_click_to_play)

    def set_attritutes(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalHeader().setVisible(False)
        self.setRowCount(0)
        self.setColumnCount(2)
        self.setColumnWidth(0, 270)
        self.setColumnWidth(1, 80)

    def create_contextmenu(self):
        self.listMenu  =  QMenu()
        self.addMusicAction  =  QAction("添加歌曲", self)
        self.markSelectedAsFavoriteAction  =  QAction("添加到“我的收藏”", self)
        self.downloadAction = QAction("下载", self)
        self.removeAction = QAction("移除歌曲", self)
        self.deleteAction = QAction("移除歌曲并删除本地文件", self)
        self.clearListWidgetAction  =  QAction("清空列表", self)
        self.switchToSearchPageAction = QAction("切换到搜索页面", self)
        self.songSpecAction = QAction("歌曲信息", self)
        self.listMenu.addAction(self.downloadAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.addMusicAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.markSelectedAsFavoriteAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.removeAction)
        self.listMenu.addAction(self.deleteAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.clearListWidgetAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.songSpecAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.switchToSearchPageAction)     
    
    def music_table_menu(self, pos):
        pos += QPoint(30, 30)
        self.listMenu.exec_(self.mapToGlobal(pos))
    
    def select_row(self):
        if self.get_playing_used_state():
            self.selectRow(self.playingList.get_current_row())
    
    def add_musics(self):
        self.files = QFileDialog.getOpenFileNames(self, "选择音乐文件", self.downloadDir, self.tr("*.mp3"))[0]
        if not self.files:
            return
        self.exec_add_operation(self.files)
        self.musics_added_signal.emit()
    
    @operate_after_check_thread_locked_state
    @trace_to_keep_time
    def exec_add_operation(self, files):
        self.addedIndexes = []
        for item in sorted(list(set(files)-set(self.playlist.get_items_queue()))):
            self.add_a_music(item)
            self.addedIndexes.append(self.playlist.get_item_index(item))
        if len(self.addedIndexes):
            self.playlist.commit_records()
        self.select_row()
    
    def remove_musics(self):
        self.removedIndexes = []
        selecteds = self.selectedIndexes()
        currentRow = self.playingList.get_current_row()
        if len(selecteds):
            for index in selecteds:
                row = index.row()
                if index.column() == 0:
                    self.removedIndexes.append(row)
            self.removedIndexes.sort(reverse=True)
            if self.deleteFlag:
                text_tmp1 = "移除并删除本地文件"
                text_tmp2 = "有%s首歌曲将被移出列表，并被彻底删除，请确认!"%len(self.removedIndexes)
            else:
                text_tmp1 = "移除选中项"
                text_tmp2 = "有%s首歌曲将被移出列表!"%len(self.removedIndexes)
            ok = QMessageBox.warning(self, text_tmp1, text_tmp2, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                if not (self.get_playing_used_state() and currentRow in self.removedIndexes):
                    self.exec_remove_operation(self.removedIndexes)
                else:
                    item = self.playlist.get_item_from_queue(currentRow)
                    currentRow = self.playlist.get_item_index(item)
                    currentMusic = self.playingList.get_music_title_at(currentRow)
                    if self.deleteFlag:
                        text_tmp3 = "移除并删除当前歌曲"
                        text_tmp4 = "当前播放的歌曲: %s 将会被移除并被删除！\n请确认！"%currentMusic
                    else:
                        text_tmp3 = "移除当前歌曲"
                        text_tmp4 = "当前播放的歌曲: %s 将会被移除!\n您是否要移除这首歌曲？"%currentMusic
                    ok = QMessageBox.warning(self, text_tmp3, text_tmp4, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
                    if ok == QMessageBox.Yes:
                        self.exec_remove_operation(self.removedIndexes)
                        currentRow = -1                        
                    else:
                        self.removedIndexes.remove(currentRow)
                        self.exec_remove_operation(self.removedIndexes)
                        currentRow = self.playlist.get_item_index(item)
                self.playlist.set_current_row(currentRow)
                self.musics_removed_signal.emit()
    
    @operate_after_check_thread_locked_state
    def exec_remove_operation(self, rows):
        if len(rows):
            for row in rows:
                self.removeRow(row)
                self.playlist.remove_item_at(row, self.deleteFlag)   
            self.playlist.commit_records()
        
    def delete_musics(self):
        self.deleteFlag = True
        self.remove_musics()
        self.deleteFlag = False
    
    def clear_musics(self):
        if not self.rowCount():
            return
        ok = QMessageBox.warning(self, "清空列表", "当前列表的所有歌曲(包括当前播放歌曲)都将被移除，请确认!", QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok  == QMessageBox.Yes:
            self.exec_clear_operation()
            self.musics_cleared_signal.emit()
    
    @operate_after_check_thread_locked_state
    def exec_clear_operation(self):
        self.clear_all_items()
        self.playlist.clear_list()
        self.playlist.commit_records()

#标记选中项为喜欢
    def mark_selected_as_favorite(self):
        selecteds = self.selectedIndexes()
        self.markedIndexes = []
        playlistTemp = Playlist()
        playlistTemp.fill_list(Configures.PlaylistFavorite)
        existsTitles = playlistTemp.get_titles()
        for index in selecteds:
            row = index.row()
            path = self.playlist.get_music_path_at(row)
            title = self.playlist.get_music_title_at(row)
            if index.column() == 0 and title not in existsTitles and os.path.exists(path):
                playlistTemp.add_item(self.playlist.get_item_from_queue(row), self.playlist.get_record_at(row))
                self.markedIndexes.append(row)
        if len(self.markedIndexes):
            playlistTemp.commit_records()
            self.musics_marked_signal.emit()

    def show_song_spec(self):
        row = self.currentRow()
        self.show_music_info_at_row(row)
    
    def show_music_info_at_row(self, row):
        title, totalTime, album, path, size, musicId = self.playlist.get_record_at(row)[:6]
        artist, musicName = get_artist_and_musicname_from_title(title)
        if musicName:
            information = "歌手：%s\n曲名：%s\n时长：%s\n专辑：%s\n路径：%s"%(artist, musicName, totalTime, album, path)
        else:
            information = "标题：%s\n时长：%s\n专辑：%s\n路径：%s"%(title, totalTime, album, path)
        QMessageBox.information(self, "歌曲详细信息", information)

    def check_actions_in_page(self, name):
        if name == Configures.PlaylistOnline:
            self.deleteAction.setVisible(False)
            self.addMusicAction.setVisible(False)
            self.switchToSearchPageAction.setVisible(True)
            self.downloadAction.setVisible(True)
        elif name in Configures.BasicPlaylists:
            self.deleteAction.setVisible(True)
            self.downloadAction.setVisible(False)
            self.addMusicAction.setVisible(True)
            self.switchToSearchPageAction.setVisible(False)
        else:
            self.deleteAction.setVisible(True)
            self.downloadAction.setVisible(False)
            self.addMusicAction.setVisible(True)
            self.switchToSearchPageAction.setVisible(False)
        if name in (Configures.PlaylistOnline, Configures.PlaylistFavorite):
            self.markSelectedAsFavoriteAction.setVisible(False)
        else:
            self.markSelectedAsFavoriteAction.setVisible(True)

    def double_click_to_play(self, index):
        row = index.row()
        self.double_click_to_play_with_row(row)
    
    def double_click_to_play_with_row(self, row):
        self.selectRow(row)
        self.playlist.set_current_row(row)
        if self.get_playing_used_state():
            self.play_or_pause_signal.emit(row)
        else:
            self.isPlaying = True
            self.playlist_changed_signal.emit(self.playingList.get_name(), self.listName)

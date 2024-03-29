import os
from PyQt5.QtWidgets import (QMenu, QAction, QAbstractItemView, QFileDialog, QMessageBox, QTableWidget, 
    QTableWidgetItem, QTableWidgetSelectionRange, QWidget, QVBoxLayout, QPushButton)
from PyQt5.QtGui import QIcon
from xyplayer.myicons import IconsHub
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from xyplayer import Configures
from xyplayer.myplaylists import Playlist
from xyplayer.mywidgets import PlaylistOperator, SongOperator
from xyplayer.utils import (trace_to_keep_time, get_artist_and_musicname_from_title, 
    operate_after_check_thread_locked_state, rename_lyric_file_use_title)

class SearchTable(QTableWidget):
    def __init__(self, parent = None):
        super(SearchTable, self).__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setRowCount(0)
        self.setColumnCount(5)
        self.hideColumn(4)
        headers  =  ( "评分","歌曲", "歌手", "专辑", "musicId")  
        self.setHorizontalHeaderLabels(headers)
        self.setShowGrid(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setFixedHeight(31)
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
            
            self.insertRow(countRow)
            self.setRowHeight(countRow, 32)
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
        self.listMenu.addAction(self.listenOnlineAction)
        self.listMenu.addAction(self.addBunchToListAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.downloadAction)
        self.listMenu.addSeparator()
        self.customContextMenuRequested.connect(self.music_table_menu)
                
    def music_table_menu(self, pos):
        pos += QPoint(0, 30)
        self.listMenu.exec_(self.mapToGlobal(pos))

class PlaylistsTable(QTableWidget):
    switch_to_this_playlist_signal = pyqtSignal(int)
    add_a_playlist_signal = pyqtSignal()
    rename_a_playlist_signal = pyqtSignal(int)
    delete_a_playlist_signal = pyqtSignal(int)
    def __init__(self, parent=None):
        super(PlaylistsTable, self).__init__(parent)
        self.set_attritutes()
        self.playlistOperator = PlaylistOperator(self)
        self.playlistOperator.setGeometry(0, 40, 270, 40)
        self.create_connections()  
        
    def set_attritutes(self):
        self.setMouseTracking(True)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRowCount(0)    
        self.setColumnCount(1)
        self.setColumnWidth(0, 270)
    
    def create_connections(self):
        self.cellEntered.connect(self.cell_entered)
        self.playlistOperator.clicked_signal.connect(self.switch_to_this_playlist_signal.emit)
        self.playlistOperator.add_button_clicked_signal.connect(self.add_a_playlist_signal.emit)
        self.playlistOperator.rename_button_clicked_signal.connect(self.rename_a_playlist_signal.emit)
        self.playlistOperator.delete_button_clicked_signal.connect(self.delete_a_playlist_signal.emit)
        self.playlistOperator.wheel_event_triggered_signal.connect(self.wheelEvent)
    
    def cell_entered(self, row, column):
        self.playlistOperator.set_row(row)
        scrollBar = self.verticalScrollBar()
        scrolledValue = scrollBar.value()
#        if scrolledValue and scrolledValue == scrollBar.maximum():
#            scrolledValue -= 1
        self.playlistOperator.setGeometry(0, (row - scrolledValue)*self.rowHeight(row), 270, 40)

    def add_item(self, playlistName):
        countRow = self.rowCount()
        playlistItem = QTableWidgetItem(QIcon(IconsHub.PlaylistFold), playlistName)
        self.insertRow(countRow)
        self.setRowHeight(countRow, 40)
        self.setItem(countRow, 0, playlistItem)
    
    def get_name_at(self, row):
        return self.item(row, 0).text()
    
    def rename_an_item(self, row, newName):
        self.item(row, 0).setText(newName)
    
    def remove_item_at(self, row):
        if row == self.rowCount() - 1:
            self.cell_entered(row - 1, 0)
        self.removeRow(row)

class PlaylistsTableUnfold(QWidget):
    fold_all_signal = pyqtSignal()
    unfold_next_signal = pyqtSignal()
    def __init__(self, playlistWidget, parent=None):
        super(PlaylistsTableUnfold, self).__init__(parent)
        self.setup_ui(playlistWidget)
        
    def setup_ui(self, playlistWidget):
        self.playlistWidget = playlistWidget
        self.itemUnfold = QPushButton(QIcon(IconsHub.PlaylistUnfold), '默认列表', clicked = self.fold_all_signal.emit)
        self.itemUnfold.setFixedHeight(37)
        self.itemUnfold.setObjectName('playlistButton1')
        self.itemUnfold.setFocusPolicy(Qt.NoFocus)
        self.itemFold = QPushButton(QIcon(IconsHub.PlaylistFold), '我的收藏', clicked = self.unfold_next_signal.emit)
        self.itemFold.setFixedHeight(37)
        self.itemFold.setObjectName('playlistButton2')
        self.itemFold.setFocusPolicy(Qt.NoFocus)
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.itemUnfold)
        mainLayout.addWidget(self.playlistWidget)
        mainLayout.addStretch()
        mainLayout.addWidget(self.itemFold)
    
    def set_two_item_names(self, name1, name2):
        self.itemUnfold.setText(name1)
        self.itemFold.setText(name2)

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
    def __init__(self, listName, parent=None):
        super(PlaylistWidgetBasic, self).__init__(parent)
        self.listName = ''
        self.playlist = Playlist()
    
    def get_playlist(self):
        return self.playlist.copy()
    
    def get_operating_playlist_name(self):
        """获取正在被操作的列表名"""
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
        self.insertRow(countRow)
        self.setItem(countRow, 0, titleItem)
        self.setRowHeight(countRow, 31)
    
    def add_record_with_full_info(self, id, title, totalTime, album, path, size, musicId=Configures.LocalMusicId):
        self.playlist.add_record(id, title, totalTime, album, path, size, musicId)
        self.add_record(title, totalTime)
    
    def add_a_music(self, path):
        title, totalTime = self.playlist.add_item_from_path(path)
        self.add_record(title, totalTime)   

class PlaylistWidget(PlaylistWidgetBasic):
    play_music_at_row_signal = pyqtSignal(int)
    play_or_pause_signal = pyqtSignal(int)
    playing_list_changed_signal = pyqtSignal(str, str)
    musics_added_signal = pyqtSignal(bool)
    musics_removed_signal = pyqtSignal()
    musics_cleared_signal = pyqtSignal()
    musics_marked_signal = pyqtSignal()
    download_signal = pyqtSignal()
    show_artist_info_signal = pyqtSignal(str)
    show_song_info_signal = pyqtSignal(int)
    tag_values_changed_signal = pyqtSignal(int, str, str, str)
    playlist_changed_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(PlaylistWidget, self).__init__(parent)
        self.songOperator = SongOperator(self)
        self.initial_params()
        self.set_attritutes()
        self.create_menu_items()
        self.create_connections()

    def create_connections(self):
        self.cellEntered.connect(self.cell_entered)
        self.customContextMenuRequested.connect(self.music_table_menu)  
        self.selectAllAction.triggered.connect(self.select_all_rows)
        self.selectInvertAction.triggered.connect(self.select_invert_rows)
        self.selectNoneAction.triggered.connect(self.select_none_rows)
        self.copytoMenu.triggered.connect(self.copy_to_other_playlist)
        self.movetoMenu.triggered.connect(self.move_to_other_playlist)
        self.addMusicAction.triggered.connect(self.add_musics)
        self.markSelectedAsFavoriteAction.triggered.connect(self.mark_selected_as_favorite)
        self.removeAction.triggered.connect(self.remove_musics)
        self.deleteAction.triggered.connect(self.delete_musics)
        self.clearListWidgetAction.triggered.connect(self.clear_musics)
        self.songSpecAction.triggered.connect(self.show_song_spec)
        self.artistSpecAction.triggered.connect(self.show_artist_info)
        self.downloadAction.triggered.connect(self.download_signal.emit)
        self.doubleClicked.connect(self.double_click_to_play)
        self.songOperator.wheel_event_triggered_signal.connect(self.wheelEvent)
        self.songOperator.double_clicked_signal.connect(self.double_click_to_play_with_row)
        self.songOperator.right_mouse_button_clicked_signal.connect(self.music_table_menu)
        self.songOperator.left_mouse_button_clicked_signal.connect(self.selectRow)
        self.songOperator.left_mouse_button_dragged_signal.connect(self.select_multi_rows)

    def cell_entered(self, row, column):
        if self.songOperator.isHidden():
            self.songOperator.set_contents(row, self.item(row, column).text())
            self.songOperator.show()
        oldRow = self.songOperator.get_row()
        if self.item(oldRow, column):
            self.item(oldRow, column).setText(self.playlist.get_music_title_at(oldRow))
        self.songOperator.set_contents(row, self.playlist.get_music_title_at(row))
        self.item(row, column).setText('')
        scrollBar = self.verticalScrollBar()
        scrolledValue = scrollBar.value()
#        if scrolledValue and scrolledValue == scrollBar.maximum():
#            scrolledValue -= 1
        self.songOperator.setGeometry(0, (row - scrolledValue)*self.rowHeight(row), 270, 31)
    
    def leaveEvent(self, event=None):
        self.hide_song_operator()
    
    def select_multi_rows(self, pos):
        exactPos = pos + self.songOperator.pos()
        item = self.itemAt(exactPos)
        if item:
            self.cell_entered(item.row(), 0)
            if not item.isSelected():  
                item.setSelected(True)
    
    def hide_song_operator(self):
        if not self.songOperator.isHidden():
            oldRow = self.songOperator.get_row()
            item = self.item(oldRow, 0)
            if item:
                item.setText(self.playlist.get_music_title_at(oldRow))
            self.songOperator.hide()
    
    def initial_params(self):
        self.files = []
        self.lock = None
        self.downloadDir = ''
        self.deleteFlag = False
        self.isPlaying = False
        self.playingList = Playlist()
        self.allPlaylistNames = []
        self.mode = 0
    
    def set_playlist_names(self, listNames):
        self.allPlaylistNames = listNames
    
    def set_lock(self, lock):
        self.lock = lock
    
    def set_download_dir(self, dir):
        self.downloadDir = dir
    
    def set_playing_status(self, playlist):
        self.playingList = playlist
 
    def set_playlist_use_name(self, listName):
        if self.listName != listName:
            self.listName = listName
            self.playlist_changed_signal.emit()
        self.isPlaying = False
        if self.playingList.get_name() == listName:
            self.isPlaying = True
        if self.get_playing_used_state():
            self.playlist = self.playingList.copy()
        else:
            self.playlist.fill_list(listName)
        self.fill_playlist_widget(self.playlist)
        self.select_row()
        self.pick_actions_into_menu()

    def get_playing_used_state(self):
        return self.isPlaying
    
    def get_playlist_length(self):
        return self.playlist.length()
    
    def get_playing_list_name(self):
        return self.playingList.get_name()

    def set_attritutes(self):
        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setRowCount(0)
        self.setColumnCount(1)
        self.setColumnWidth(0, 270)
        self.setColumnWidth(1, 80)

    def pick_actions_into_menu(self):
        self.listMenu.clear()
        if self.listName == Configures.PlaylistOnline:
            self.create_online_playlist_menu()
        elif self.listName == Configures.PlaylistFavorite:
            self.create_favor_playlist_menu()
        else:
            self.create_other_playlist_menu()

    def create_menu_items(self):
        self.listMenu  =  QMenu()
        self.addMusicAction  =  QAction("添加歌曲", self)
        self.selectAllAction = QAction("全选", self)
        self.selectInvertAction = QAction("反选", self)
        self.selectNoneAction = QAction("取消选择", self)
        self.markSelectedAsFavoriteAction  =  QAction("添加到“我的收藏”", self)
        self.copytoMenu = QMenu('复制到...')
        self.movetoMenu = QMenu('移动到...')
        self.downloadAction = QAction("下载", self)
        self.removeAction = QAction("移除歌曲", self)
        self.deleteAction = QAction("移除歌曲并删除本地文件", self)
        self.clearListWidgetAction  =  QAction("清空列表", self)
        self.songSpecAction = QAction("歌曲信息", self)
        self.artistSpecAction = QAction("歌手信息", self)
    
    def create_online_playlist_menu(self):
        self.listMenu.addAction(self.downloadAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.selectAllAction)
        self.listMenu.addAction(self.selectInvertAction)
        self.listMenu.addAction(self.selectNoneAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.removeAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.clearListWidgetAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.songSpecAction)
        self.listMenu.addAction(self.artistSpecAction)
    
    def create_favor_playlist_menu(self):
        self.listMenu.addAction(self.addMusicAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.selectAllAction)
        self.listMenu.addAction(self.selectInvertAction)
        self.listMenu.addAction(self.selectNoneAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.removeAction)
        self.listMenu.addAction(self.deleteAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.clearListWidgetAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.songSpecAction)
        self.listMenu.addAction(self.artistSpecAction)
    
    def fill_copyto_and_moveto_menu(self):
        self.copytoMenu.clear()
        self.movetoMenu.clear()
        if self.listName == Configures.PlaylistDefault:
            if len(self.allPlaylistNames) > 4:
                for i, name in enumerate(self.allPlaylistNames):
                    if i >= 4:
                        self.add_action(name)
                return True
        elif self.listName == Configures.PlaylistDownloaded:
            if len(self.allPlaylistNames) > 3:
                for i, name in enumerate(self.allPlaylistNames):
                    if i >= 4 or i == 1:
                        self.add_action(name)
                return True
        else:
            for i, name in enumerate(self.allPlaylistNames):
                if i == 1 or i >= 4 and name!=self.listName:
                    self.add_action(name)
            return True
        return False
    
    def add_action(self, name):
        action1 = QAction(name, self)
        self.copytoMenu.addAction(action1)
        action2 = QAction(name, self)
        self.movetoMenu.addAction(action2)
    
    def create_other_playlist_menu(self):
        self.listMenu.addAction(self.addMusicAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.selectAllAction)
        self.listMenu.addAction(self.selectInvertAction)
        self.listMenu.addAction(self.selectNoneAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.markSelectedAsFavoriteAction)
        self.listMenu.addSeparator()
        if self.fill_copyto_and_moveto_menu():
            self.listMenu.addMenu(self.copytoMenu)
            self.listMenu.addMenu(self.movetoMenu)
            self.listMenu.addSeparator()
        self.listMenu.addAction(self.removeAction)
        self.listMenu.addAction(self.deleteAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.clearListWidgetAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.songSpecAction)
        self.listMenu.addAction(self.artistSpecAction)
    
    def music_table_menu(self, pos):
        pos += QPoint(10, 0)
        self.listMenu.exec_(self.mapToGlobal(pos))
    
    def select_row(self):
        row = self.playingList.get_current_row()
        if self.get_playing_used_state() and row>=0:
            self.selectRow(row)
    
    def add_musics(self):
        self.files = QFileDialog.getOpenFileNames(self, "选择音乐文件", self.downloadDir, self.tr("*.mp3"))[0]
        if not self.files:
            return
        self.exec_add_operation(self.files)
        self.musics_added_signal.emit(True)
        for item in self.files:
            row = self.playlist.get_item_index(item)
            self.setRangeSelected(QTableWidgetSelectionRange(row, 0, row, self.columnCount()-1), True)
    
    @operate_after_check_thread_locked_state
    @trace_to_keep_time
    def exec_add_operation(self, files):
        self.addedIndexes = []
        for item in sorted(list(set(files)-set(self.playlist.get_items_queue()))):
            self.add_a_music(item)
            self.addedIndexes.append(self.playlist.get_item_index(item))
        if self.addedIndexes:
            self.playlist.commit_records()
    
    def remove_musics(self):
        self.removedIndexes = []
        selecteds = self.selectedIndexes()
        currentRow = self.playingList.get_current_row() % self.playingList.length()
        if selecteds:
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
                text_tmp2 = "有%s首歌曲将被移出列表，请确认!"%len(self.removedIndexes)
            ok = QMessageBox.warning(self, text_tmp1, text_tmp2, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                self.hide_song_operator()
                item = self.playingList.get_item_from_queue(currentRow)
                if not (self.get_playing_used_state() and currentRow in self.removedIndexes):
                    self.exec_remove_operation(self.removedIndexes)
                    if self.get_playing_used_state():
                        currentRow = self.playlist.get_item_index(item)
                else:
                    currentMusic = self.playingList.get_music_title_at(currentRow)
                    if self.deleteFlag:
                        text_tmp3 = "移除并删除当前歌曲"
                        text_tmp4 = "当前播放的歌曲: %s 将会被移除并被删除，请确认！"%currentMusic
                    else:
                        text_tmp3 = "移除当前歌曲"
                        text_tmp4 = "当前播放的歌曲: %s 将会被移除，请确认！"%currentMusic
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
    
    def remove_without_check(self, selecteds):
        self.hide_song_operator()
        self.removedIndexes = []
        currentRow = self.playingList.get_current_row() % self.playingList.length()
        if len(selecteds):
            for index in selecteds:
                row = index.row()
                if index.column() == 0:
                    self.removedIndexes.append(row)
            self.removedIndexes.sort(reverse=True)
            item = self.playingList.get_item_from_queue(currentRow)
            if not (self.get_playing_used_state() and currentRow in self.removedIndexes):
                self.exec_remove_operation(self.removedIndexes)
                if self.get_playing_used_state():
                    currentRow = self.playlist.get_item_index(item)
            else:
                self.exec_remove_operation(self.removedIndexes)
                currentRow = -1                        
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
            self.hide_song_operator()
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

    def copy_to_other_playlist(self, action):
        selecteds = self.selectedIndexes()
        self.add_items_to_new_playlist(action.text(), selecteds)
        self.select_range_rows(selecteds)
    
    def move_to_other_playlist(self, action):
        selecteds = self.selectedIndexes()
        self.add_items_to_new_playlist(action.text(), selecteds)
        self.remove_without_check(selecteds)

    def add_items_to_new_playlist(self, name, selecteds):
        currentListName = self.listName
        if not selecteds:
            return
        playlistTemp = Playlist()
        for index in selecteds:
            row = index.row()
            if index.column() == 0:
                playlistTemp.add_item(self.playlist.get_item_from_queue(row), self.playlist.get_infos_at(row))
        self.set_playlist_use_name(name)
        self.add_musics_from_other_playlist(playlistTemp)
        self.set_playlist_use_name(currentListName)
    
    def add_musics_from_other_playlist(self, playlistTemp):
        self.addedIndexes = []
        for item in sorted(list(playlistTemp.get_ids()-self.playlist.get_ids())):
            self.playlist.add_item(item, playlistTemp.get_info_use_id(item))
            self.addedIndexes.append(self.playlist.get_item_index(item))
        if self.addedIndexes:
            self.playlist.commit_records()
            self.musics_added_signal.emit(False)
        
    def select_range_rows(self, selecteds, flag=True):
        for index in selecteds:
            if index.column() == 0:
                self.select_a_row(index.row(), flag)
    
    def select_a_row(self, row, flag=True):
        self.setRangeSelected(QTableWidgetSelectionRange(row, 0, row, self.columnCount() - 1), flag)
    
    def select_invert_rows(self):
        selecteds = self.selectedIndexes()
        self.select_all_rows()
        self.select_range_rows(selecteds, False)
        
    def select_all_rows(self):
        self.setRangeSelected(QTableWidgetSelectionRange(0, 0, self.rowCount()-1, self.columnCount()-1), True)
        
    def select_none_rows(self):
        self.setRangeSelected(QTableWidgetSelectionRange(0, 0, self.rowCount()-1, self.columnCount()-1), False)

    def show_song_spec(self):
        row = self.currentRow()
        self.show_song_info_signal.emit(row)
    
    def show_artist_info(self):
        row = self.currentRow()
        artist, musicName = get_artist_and_musicname_from_title(self.playlist.get_music_title_at(row))
        self.show_artist_info_signal.emit(artist)

    def change_tag_value(self, row, title, album, modifiedTime):
        oldTitle = self.playlist.get_music_title_at(row)
        self.playlist.set_music_title_at(row, title, False)
        self.playlist.set_music_album_at(row, album, False)
        self.playlist.set_modified_time_at(row, modifiedTime, False)
        self.playlist.commit_records()
        if oldTitle != title:
            widgetItem = self.item(row, 0)
            widgetItem.setText(title)
            rename_lyric_file_use_title(oldTitle, title)
        self.tag_values_changed_signal.emit(row, oldTitle, title, album)

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
            self.playing_list_changed_signal.emit(self.playingList.get_name(), self.listName)

import os
from PyQt5.QtWidgets import (QMenu, QAction, QAbstractItemView, 
            QTableView, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtSql import QSqlTableModel
from xyplayer import Configures

class TableModel(QSqlTableModel):
    def __init__(self, parent = None):
        super(TableModel, self).__init__(parent)
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)

    def initial_model(self, tableName):
        self.setTable(tableName)
        self.select()
    
    def add_record(self, title, length, album, paths, size, musicId=Configures.LocalMusicId):
        rowNum = self.rowCount()
        self.insertRow(rowNum)
        self.setData(self.index(rowNum, 0), paths) 
        self.setData(self.index(rowNum, 1), title)
        self.setData(self.index(rowNum, 2), length)
        self.setData(self.index(rowNum, 3), album)
        self.setData(self.index(rowNum, 4), size)
        self.setData(self.index(rowNum, 5), 0)
        self.setData(self.index(rowNum, 6), musicId)
        self.submitAll()      
    
    def get_record_paths(self, row):
        return self.record(row).value("paths")
    
    def get_record_musicId(self, row):
        return self.record(row).value('musicId')
    
    def get_record_title(self, row):
        return self.record(row).value('title')

    def get_record_album(self, row):
        return self.record(row).value('album')

    def get_record_length(self, row):
        return self.record(row).value('length')
    
    def delete_selecteds(self, selecteds):
        for index in selecteds:
            row = index.row()
            if index.column() == 0:
                self.removeRow(row)
        self.submitAll()
    
    def delete_localfiles(self, selecteds):
        for index in selecteds:
            row = index.row()
            if index.column() == 0:
                path = self.record(row).value("paths")
                if os.path.exists(path):
                    os.remove(path)
            
    
class TableView(QTableView):
    def __init__(self, parent = None):
        super(TableView, self).__init__(parent)
        self.set_attritutes()
        self.create_contextmenu()
        self.create_connections()
    
    def set_attritutes(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        #self.setShowGrid(False)
#        self.setAttribute(Qt.WA_TranslucentBackground)
#        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
#        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalHeader().setVisible(False)
        self.rowSelected = 0
        self.defaultRowHeight = 30

    def create_connections(self):
        self.customContextMenuRequested.connect(self.music_table_menu)   
        #self.clicked.connect(self.change_row_height)

    def initial_view(self, model):
        self.setModel(model)    
        self.hideColumn(0)
        for i in range(3, 12):
            self.hideColumn(i)
        self.setColumnWidth(1, 270)
        self.setColumnWidth(2, 80)
        
    def create_contextmenu(self):
        self.listMenu  =  QMenu()
        self.addMusicAction  =  QAction("添加歌曲", self)
        self.markSelectedAsFavoriteAction  =  QAction("添加到“我的收藏”", self)
        self.downloadAction = QAction("下载", self)
        self.deleteSelectedsAction = QAction("移除歌曲", self)
        self.deleteAction = QAction("移除歌曲并删除本地文件", self)
        self.clearTheListAction  =  QAction("清空列表", self)
        self.switchToSearchPageAction = QAction("切换到搜索页面", self)
        self.songSpecAction = QAction("歌曲信息", self)
        self.listMenu.addAction(self.downloadAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.addMusicAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.markSelectedAsFavoriteAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.deleteSelectedsAction)
        self.listMenu.addAction(self.deleteAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.clearTheListAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.songSpecAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.switchToSearchPageAction)     
    
    def music_table_menu(self, pos):
        pos += QPoint(30, 30)
        self.listMenu.exec_(self.mapToGlobal(pos))

    def change_row_height(self, index):
        oldSelected = self.rowSelected
        self.rowSelected = index.row()
        self.setRowHeight(oldSelected, 30)
        self.setRowHeight(self.rowSelected, 60)

class ManageTableView(QTableView):
    def __init__(self, parent = None):
        super(ManageTableView, self).__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.create_contextmenu()
        self.offsetPoint = QPoint(0, 5)
        
    def initial_view(self, model):
        self.setModel(model)    
        self.hideColumn(0)
        self.hideColumn(2)
        self.hideColumn(3)
        self.hideColumn(4)
        self.hideColumn(5)
        self.hideColumn(6)
        self.hideColumn(7)
        self.setColumnWidth(0, 91)
    
    def create_contextmenu(self):
        self.manageMenu = QMenu()
        self.addTableAction = QAction("添加列表", self)
        self.addMusicHereAction = QAction("添加歌曲到此列表", self)
        self.renameTableAction = QAction("重命名列表", self)
        self.deleteTableAction = QAction("删除列表", self)
        self.switchToSearchPageAction = QAction("切换到搜索页面", self)
        self.manageMenu.addAction(self.addTableAction)
        self.manageMenu.addAction(self.addMusicHereAction)
        self.manageMenu.addSeparator()
        self.manageMenu.addAction(self.renameTableAction)
        self.manageMenu.addSeparator()
        self.manageMenu.addAction(self.deleteTableAction)
        self.manageMenu.addSeparator()
        self.manageMenu.addAction(self.switchToSearchPageAction)
#        self.switchToSearchPageAction.setVisible(False)
        self.customContextMenuRequested.connect(self.manage_menu_event)
        
    def manage_menu_event(self, pos):    
        pos += self.offsetPoint
        self.manageMenu.exec_(self.mapToGlobal(pos))
    
    def add_tables(self, model, tableName):
        rowNum = model.rowCount()
        model.insertRow(rowNum)
        model.setData(model.index(rowNum, 1), tableName)
        model.submitAll()       

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

class DownloadWorksModel(QSqlTableModel):
    def __init__(self, parent = None):
        super(DownloadWorksModel, self).__init__(parent)
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.initial_model()
        self.columnNames = ['title', 'downloadedsize', 'size', 'album', 'songLink', 'musicPath', 'musicId', 'status']
        self.workInfoContains = ['songLink', 'musicPath', 'title', 'album', 'musicId', 'size']

    def initial_model(self):
        self.setTable(Configures.DownloadWorksTable)
        self.select()
    
    def add_record(self, title, downloadedsize, size, album, songLink, musicPath, musicId, status=Configures.DownloadPaused):
        rowNum = self.rowCount()
        self.insertRow(rowNum)
        self.setData(self.index(rowNum, 1), title)
        self.setData(self.index(rowNum, 2), downloadedsize)
        self.setData(self.index(rowNum, 3), size)
        self.setData(self.index(rowNum, 4), album)
        self.setData(self.index(rowNum, 5), songLink)
        self.setData(self.index(rowNum, 6), musicPath)
        self.setData(self.index(rowNum, 7), musicId)
        self.setData(self.index(rowNum, 8), status) 
        self.submitAll()      
    
    def get_a_record_at_row(self, row):
        values = []
        for name in self.columnNames:
            values.append(self.get_value(row, name))
        return values
    
    def get_work_info_at_row(self, row):
        workInfoList = []
        for name in self.workInfoContains:
            value = self.get_value(row, name)
            if name == 'size':
                value = int(value)
            workInfoList.append(value)
        return workInfoList
    
    def get_value(self, row, name):
        return self.record(row).value(name)
    
    def clear_table(self):
        self.removeRows(0, self.rowCount())
        self.submitAll()
    
    def delete_selecteds(self, selecteds):
        for index in selecteds:
            row = index.row()
            if index.column() == 0:
                self.removeRow(row)
        self.submitAll()
            
class MyListTable(QTableWidget):
    """managePage主页面中我的歌单。"""
    def __init__(self, parent=None):
        super(MyListTable, self).__init__(parent)
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
            
    def clear_list(self):
        while self.rowCount():
            self.removeRow(0)
            del self.allListItems[0]

    def row_of_item(self, ident):
        i = -1
        for i in range(len(self.allListItems)):
            if self.allListItems[i].ident == ident:
                return i





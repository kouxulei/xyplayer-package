import os
from PyQt4.QtGui import (QApplication, QMenu, QAction, QAbstractItemView, QStyle, 
            QTableView, QTableWidget, QTableWidgetItem, QItemDelegate, QStyleOptionProgressBarV2)
from PyQt4.QtCore import QPoint, Qt
from PyQt4.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from xyplayer.configure import Configures
#from xyplayer.mywidgets import NewListWidget

class SqlOperate():
    def __init__(self):
        self.createConnection()
        self.createTables()
        self.createTable("在线试听")
        self.createTable("默认列表")
        self.createTable("喜欢歌曲")
        self.createTable("我的下载")
        
    def createConnection(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(Configures.db)
        db.open()
#        query = QSqlQuery()
#        query.exec_("%s, 'PRAGMA synchronous = OFF;', 0, 0, 0"%Configures.db)
#        if not db.open():
#            QMessageBox.warning(0, "连接数据库错误!", db.lastError().text())
        
    def createTable(self, tableName):
        query = QSqlQuery()
        query.exec_("create table %s (id integer primary key autoincrement, title varchar(50), length varchar(10), album varchar(40), paths varchar(65), size varchar(20), \
        frequency integer, spare1 varchar, spare2 varchar, spare3 varchar, spare4 varchar, spare5 varchar)"%tableName)
        query.exec_("commit")
    
    def renameTable(self, oldName, newName):
        query = QSqlQuery()
        query.exec_("alter table %s rename to %s"%(oldName, newName))
        query.exec_("commit")
    
    def dropTable(self, tableDeleted):
        query = QSqlQuery()
        query.exec_("drop table %s"%tableDeleted)
        query.exec_("commit")
    
    def createTables(self):
        query = QSqlQuery()
        query.exec_("create table tablesManage (id integer primary key autoincrement, tableName varchar(50), spare1 varchar, spare2 varchar, spare3 varchar, spare4 varchar, spare5 varchar, spare6 varchar)")
        query.exec_("create table downloadTable (id integer primary key autoincrement, title varchar(50), progress varchar(20), size varchar(20), remain varchar(20), album varchar(20), songLink varchar(30), musicPath varchar(30),netSpeed varchar(30),\
        musicId varchar(10), spare1 varchar, spare2 varchar, spare3 varchar, spare4 varchar, spare5 varchar)" )
        query.exec_("insert into tablesManage values(0, '在线试听', Null, Null, Null, Null, Null, Null)")
        query.exec_("insert into tablesManage values(1, '默认列表', Null, Null, Null, Null, Null, Null)")
        query.exec_("insert into tablesManage values(2, '喜欢歌曲', Null, Null, Null, Null, Null, Null)")
        query.exec_("insert into tablesManage values(3, '我的下载', Null, Null, Null, Null, Null, Null)")
        query.exec_("commit")

    
class TableModel(QSqlTableModel):
    def __init__(self, parent = None):
        super(TableModel, self).__init__(parent)
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)

    def initial_model(self, tableName):
        self.setTable(tableName)
#        self.setHeaderData(1, Qt.Horizontal, "歌手._.曲目")
#        self.setHeaderData(2, Qt.Horizontal, "时长")
#        self.setHeaderData(3, Qt.Horizontal, "专辑")
#        self.setHeaderData(4, Qt.Horizontal, "路径")
        self.select()
    
    def add_record(self, title, length, album, paths, size):
        rowNum = self.rowCount()
        self.insertRow(rowNum)
        self.setData(self.index(rowNum, 1), title)
        self.setData(self.index(rowNum, 2), length)
        self.setData(self.index(rowNum, 3), album)
        self.setData(self.index(rowNum, 4), paths) 
        self.setData(self.index(rowNum, 5), size)
        self.setData(self.index(rowNum, 6), 0)
        self.submitAll()      
    
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
#        self.setStyleSheet("QTableView{background-color:rgb(250,250,115)}")
#        font = QFont()
#        font.setFamily("微软雅黑")
#        self.setFont(font)
        self.create_contextmenu()
        
    def initial_view(self, model):
        self.setModel(model)    
#        self.setColumnWidth(0, 240)
#        self.setColumnWidth(1, 80)
#        self.setColumnWidth(2, 160)
        for i in range(12):
            if i != 1:
                self.hideColumn(i)
#        self.hideColumn(2)
#        self.hideColumn(3)
#        self.hideColumn(4)
        self.setColumnWidth(1, 300)
        
    def create_contextmenu(self):
        self.listMenu  =  QMenu()
        self.addMusicAction  =  QAction("添加歌曲", self)
        self.markSelectedAsFavoriteAction  =  QAction("标记选中项为喜欢", self)
        self.downloadAction = QAction("下载", self)
        self.deleteSelectedsAction = QAction("移除选中项", self)
        self.deleteAction = QAction("移除并删除文件", self)
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
        self.listMenu.addAction(self.clearTheListAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.songSpecAction)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.switchToSearchPageAction)
        self.customContextMenuRequested.connect(self.music_table_menu)        
    
    def music_table_menu(self, pos):
        pos += QPoint(30, 30)
        self.listMenu.exec_(self.mapToGlobal(pos))

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
#        self.addTableAction.setIcon(QIcon(":/iconSources/icons/playmode.png"))
        self.renameTableAction = QAction("修改列表名", self)
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
        self.listenOnlineAction = QAction('试听', self)
        self.addBunchToListAction = QAction('添加到‘在线试听’', self)
        self.downloadAction  =  QAction('下载', self)
        self.switchToOnlineListAction = QAction("切换到试听列表", self)
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

class DownloadModel(QSqlTableModel):
    def __init__(self, parent = None):
        super(DownloadModel, self).__init__(parent)
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)

    def initial_model(self):
        self.setTable('downloadTable')
        self.setHeaderData(1, Qt.Horizontal, "下载曲目")
        self.setHeaderData(2, Qt.Horizontal, "进度")
        self.setHeaderData(3, Qt.Horizontal, "大小")
        self.setHeaderData(4, Qt.Horizontal, "剩余")
        self.setHeaderData(5, Qt.Horizontal, "专辑")
        self.setHeaderData(6, Qt.Horizontal, "网址")
        self.setHeaderData(7, Qt.Horizontal, "路径")
        self.setHeaderData(8, Qt.Horizontal, "网速")
        self.setHeaderData(9, Qt.Horizontal, "musicId")
        self.select()
    
    def add_record(self, title, progress, size, remain, album, songLink, musicPath, musicId):
        rowNum = self.rowCount()
        self.insertRow(rowNum)
        self.setData(self.index(rowNum, 1), title)
        self.setData(self.index(rowNum, 2), progress)
        self.setData(self.index(rowNum, 3), size)
        self.setData(self.index(rowNum, 4), remain) 
        self.setData(self.index(rowNum, 5), album)
        self.setData(self.index(rowNum, 6), songLink)
        self.setData(self.index(rowNum, 7), musicPath)
        self.setData(self.index(rowNum, 8), 0)
        self.setData(self.index(rowNum, 9), musicId)
        self.submitAll()      
        
    def clear_table(self):
        self.removeRows(0, self.rowCount())
        self.submitAll()
    
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
                title = self.record(row).value("title")
                with open(Configures.settingFile, 'r') as f:
                    downloadDir = f.read()
                path = downloadDir + '/' + title + '.mp3'
                if os.path.exists(path):
                    os.remove(path)

class DownloadTable(QTableView):
    def __init__(self, parent = None):
        super(DownloadTable, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
#        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
#        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
#        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setVisible(False)
        self.create_contextmenu()
    
    def initial_view(self, model):
        self.setModel(model)
        self.hideColumn(0)
        self.hideColumn(3)
        for i in range(5, 15):
            self.hideColumn(i)
        self.setColumnWidth(1, 170)
        self.setColumnWidth(2, 100)
        
    def create_contextmenu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listMenu = QMenu()
        self.listMenu1 = QMenu("下载控制")
        self.playAction = QAction("添加到“我的下载”", self)
#        self.addBunchAction = QAction("添加到“我的下载”", self)
        self.pauseDownloadAction = QAction("暂停", self)
        self.stopDownloadAction = QAction("取消下载", self)
        self.startDownloadAction = QAction("开始", self)
        self.pauseAllAction = QAction("暂停全部", self)
        self.startAllAction = QAction("开始全部", self)
        self.stopAllAction = QAction("取消全部", self)
        self.removeRowsAction = QAction("移除选中项", self)
        self.deleteAction = QAction("移除并删除文件", self)
        self.clearTableAction = QAction("清空列表", self)
        self.listMenu1.addAction(self.startDownloadAction)
        self.listMenu1.addAction(self.startAllAction)
        self.listMenu1.addSeparator()
        self.listMenu1.addAction(self.pauseDownloadAction)
        self.listMenu1.addAction(self.pauseAllAction)
        self.listMenu1.addSeparator()
        self.listMenu1.addAction(self.stopDownloadAction)
#        self.listMenu.addAction(self.stopAllAction)
        self.listMenu.addAction(self.playAction)
#        self.listMenu.addAction(self.addBunchAction)
        self.listMenu.addSeparator()
        self.listMenu.addMenu(self.listMenu1)
        self.listMenu.addSeparator()
        self.listMenu.addAction(self.removeRowsAction)
        self.listMenu.addAction(self.deleteAction)
        self.listMenu.addAction(self.clearTableAction)
        

class MyDelegate(QItemDelegate):
    def paint(self,painter,option,index):
        if index.column() == 2:
            progress = int(index.model().data(index, Qt.DisplayRole))
            progressBarOption = QStyleOptionProgressBarV2()
            progressBarOption.state = QStyle.State_Enabled
            progressBarOption.direction = QApplication.layoutDirection()
            progressBarOption.rect = option.rect
            progressBarOption.fontMetrics = QApplication.fontMetrics()
            progressBarOption.textVisible = True
            progressBarOption.textAlignment = Qt.AlignCenter
            progressBarOption.minimum = 0
            row = index.row()
            maximum = index.model().record(row).value('size')
            if maximum == '未知':
                progressBarOption.maximum = 10000000
                progressBarOption.text = '0%'
                progressBarOption.progress = 0
            else:
                progressBarOption.maximum = int(maximum)
                progressBarOption.progress = progress
                ratio = int(progress*100/int(maximum))
                progressBarOption.text = '%s'%ratio+'%'
            QApplication.style().drawControl(QStyle.CE_ProgressBar,progressBarOption,painter)
        elif index.column() == 3:
            if index.model().data(index) != '未知':
                length = int(index.model().data(index, Qt.EditRole))
                lengthMB = length/(1024*1024)
                size = round(lengthMB, 1)
                text = '%s'%size+'M'
                QApplication.style().drawItemText(painter, option.rect, Qt.AlignLeft and Qt.AlignVCenter, QApplication.palette(), True, text)
            else:
                return QItemDelegate.paint(self,painter,option,index)
        elif index.column() == 4 :
            if index.model().data(index) not in ["已完成", "已取消", "等待", "已暂停", "出错"]:
                remainSeconds = float(index.model().data(index))
                hours = int(remainSeconds/3600)
                minutes = int((remainSeconds%3600)/60)
                seconds = round((remainSeconds)%3600%60, 1)
                if remainSeconds >= 3600:
                    remainTime = '%sh%sm%ss'%(hours, minutes, int(seconds))
                elif  remainSeconds < 3600 and remainSeconds >= 60:
                    remainTime = '%sm%ss'%(minutes, int(seconds))
                else:
                    remainTime = '%ss'%seconds
                text = remainTime
                QApplication.style().drawItemText(painter, option.rect, Qt.AlignLeft and Qt.AlignVCenter, QApplication.palette(), True, text)
            else:
                return QItemDelegate.paint(self,painter,option,index)
        else:
            return QItemDelegate.paint(self,painter,option,index)

    
        
  #playback_page页面的歌单
class NewMusicTable(QTableWidget):
    def __init__(self, parent = None):
        super(NewMusicTable, self).__init__(parent)
        self.setStyleSheet("QHeaderView{background:transparent;font-family:'微软雅黑';font-size:16px;color:white;}")
        self.setRowCount(0)
        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    def add_widget(self, widget):
            countRow  =  self.rowCount()
            self.insertRow(countRow)
            self.setColumnWidth(0, 340)
            self.setRowHeight(countRow, 85)
            self.setCellWidget(countRow, 0, widget)
        
    def clear_new_music_table(self):
        while self.rowCount():
            self.removeRow(0)
            
#managePage主页面中我的歌单
class MyListTable(QTableWidget):
    def __init__(self, parent = None):
        super(MyListTable, self).__init__(parent)
        self.horizontalHeader().setVisible(False)
#        self.verticalHeader().setStyleSheet("QHeaderView::section{background:transparent}")
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRowCount(0)    
        self.setColumnCount(1)
#        header = ("我的歌单", "")
#        self.setHorizontalHeaderLabels(header)
        self.setFixedWidth(170)
        self.horizontalHeader().setFixedHeight(36)
        self.setColumnWidth(0, 170)
    
    def add_widget(self, widget):
        countRow  =  self.rowCount()
        self.insertRow(countRow)
        self.setRowHeight(countRow, 43)
        self.setCellWidget(countRow, 0, widget)







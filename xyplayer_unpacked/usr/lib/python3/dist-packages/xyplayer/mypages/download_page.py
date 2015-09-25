import os
import threading
from PyQt5.QtWidgets import QWidget, QMessageBox, QHBoxLayout, QPushButton,QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon, QCursor, QDesktopServices
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint, QUrl, QSize
from PyQt5 import QtSql
from xyplayer import Configures
from xyplayer.mywidgets import LabelButton
from xyplayer.mytables import DownloadTable, DownloadModel, MyDelegate
from xyplayer.mythreads import DownloadThread, DownloadLrcThread

class DownloadPage(QWidget):
    back_to_main_signal = pyqtSignal()
    listen_online_signal = pyqtSignal(str, str, str)
    listen_local_signal = pyqtSignal(bool)
    def __init__(self, parent = None):
        super(DownloadPage, self).__init__(parent)
        self.setup_ui()
        self.create_connections()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datas)
        self.deletePermit = False
        
    def setup_ui(self):
#返回按键
        self.backButton = QPushButton(clicked = self.back_to_main_signal.emit)
        self.backButton.setStyleSheet("font-size:15px")
        self.backButton.setFixedSize(25, 33)
        self.backButton.setIcon(QIcon(":/iconSources/icons/back.png"))
        self.backButton.setIconSize(QSize(20, 20))
        
        self.titleLabel = LabelButton("下载任务")
        self.titleLabel.setFixedWidth(70)
        self.titleLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
#        self.openDir = QPushButton("下载目录")
#        self.openDir.setIcon(QIcon(":/iconSources/icons/openDir.png"))
#        self.openDir.setStyleSheet("font-size:15px")
#        self.openDir.setFixedHeight(33)
#        self.openDir.setIconSize(QSize(20, 20))
        
        self.netSpeedInfo = QLabel("当前网速：0.0 kB/s")
#        self.netSpeedInfo.setFixedWidth(135)
        self.netSpeedInfo.setStyleSheet("background:transparent;color:white")
        self.netSpeedInfo.setAlignment(Qt.AlignRight and Qt.AlignVCenter)
        self.downloadModel = DownloadModel()
        self.downloadModel.initial_model()
        
        self.downloadTable = DownloadTable()
        self.downloadTable.initial_view(self.downloadModel)
        self.downloadTable.selectRow(0)
        self.myDelegate = MyDelegate()
        self.downloadTable.setItemDelegate(self.myDelegate)
        
#        spacerItem  =  QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        firstLayout = QHBoxLayout()
        firstLayout.addWidget(self.backButton)
        firstLayout.addWidget(self.titleLabel)
        firstLayout.addStretch()
#        firstLayout.addItem(spacerItem)
        firstLayout.addWidget(self.netSpeedInfo)
#        firstLayout.addWidget(self.openDir)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
#        mainLayout.setSpacing(4)
        mainLayout.addLayout(firstLayout)
        mainLayout.addWidget(self.downloadTable)
        
    def create_connections(self):
        self.downloadTable.installEventFilter(self)

        self.titleLabel.clicked.connect(self.open_downloaddir)
        self.downloadTable.playAction.triggered.connect(self.add_to_my_downloads)
        self.downloadTable.startDownloadAction.triggered.connect(self.start_download)
        self.downloadTable.startAllAction.triggered.connect(self.start_all)
        self.downloadTable.pauseDownloadAction.triggered.connect(self.pause_download)
        self.downloadTable.stopDownloadAction.triggered.connect(self.stop_download)
        self.downloadTable.pauseAllAction.triggered.connect(self.pause_all)
        self.downloadTable.removeRowsAction.triggered.connect(self.remove_these_rows)
        self.downloadTable.deleteAction.triggered.connect(self.delete_localfiles)
        self.downloadTable.clearTableAction.triggered.connect(self.clear_table)
        
        self.downloadTable.clicked.connect(self.show_title)
        self.downloadTable.doubleClicked.connect(self.begin_to_listen)
        self.downloadTable.customContextMenuRequested.connect(self.music_table_menu)
    
    def show_title(self, index):
        tips = self.downloadModel.record(index.row()).value("title")
        self.downloadTable.setToolTip(tips)
    
    def music_table_menu(self, pos):
        pos  += QPoint(20, 33)
        self.downloadTable.listMenu.exec_(self.mapToGlobal(pos))
    
    def add_to_my_downloads(self):
        if not self.downloadModel.rowCount():
            return
        selections = self.downloadTable.selectionModel()
        selecteds = selections.selectedIndexes()
        self.valid = []
        for index in selecteds:
            if index.column() == 0:
                state = self.downloadModel.record(index.row()).value("remain")
                musicPath = self.downloadModel.record(index.row()).value("musicPath")
                if state == "已完成" and os.path.exists(musicPath):
                    self.valid.append(musicPath)
        cnt = len(self.valid)
        if cnt:
            self.listen_local_signal.emit(False)
            QMessageBox.information(self, "提示", "已添加%s首歌曲到我的下载，其他歌曲未完成下载，建议您在线播放（双击即可）！"%cnt)
        else:
            QMessageBox.information(self, "提示", "选中歌曲均未完成下载，建议您在线播放（双击即可）！")
            
    def begin_to_listen(self, index):
        musicPath = self.downloadModel.record(index.row()).value("musicPath")
        if self.downloadModel.record(index.row()).value("remain") != "已完成":
            ok = QMessageBox.question(self, '注意', '下载未完成，您是否要在线试听？', QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                title = self.downloadModel.record(index.row()).value("title")
                album = self.downloadModel.record(index.row()).value("album")
                musicId = self.downloadModel.record(index.row()).value("musicId")
                songLink = self.downloadModel.record(index.row()).value("songLink")
                songLinkwrap = songLink + '~' + '~' + musicId
                self.listen_online_signal.emit(title, album, songLinkwrap)
        elif not os.path.exists(musicPath):
            ok = QMessageBox.warning(self, '注意', '歌曲不存在，您是否要重新下载？', QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                self.start_one(index.row())
        else:
            self.valid = [musicPath]
            self.listen_local_signal.emit(True)
    
    def add_to_downloadtable(self, songLink, musicPath, title, album, musicId):
        for t in threading.enumerate():
            if t.name == musicPath:
                return
        k = -1
        for i in range(self.downloadModel.rowCount()):
            if musicPath == self.downloadModel.record(i).value("musicPath"):
                k = i
                break
        if k != -1:
            self.downloadTable.selectRow(k)
            self.start_download()
        else:
            self.downloadModel.add_record(title, 0, '未知', '等待', album, songLink, musicPath, musicId)
            row = self.downloadModel.rowCount()-1
            self.downloadTable.selectRow(row)
            downloadThread1 = DownloadThread(self.downloadModel, row)
            downloadThread1.setDaemon(True)
            downloadThread1.setName(musicPath)
            downloadThread1.start()
            
            lrcName = title + '.lrc'
            lrcPath = os.path.join(Configures.lrcsDir, lrcName)
            if os.path.exists(lrcPath):
                os.remove(lrcPath)
            path_item_temp = songLink + '~' + musicId
            list_temp = [(title, path_item_temp)]
            thread = DownloadLrcThread(list_temp)
            thread.setDaemon(True)
            thread.setName('downloadLrc')
            thread.start()
            
            if not self.timer.isActive():
                self.timer.start(700)
    
    def update_datas(self):
        totalSpeed = 0
        for i in range(self.downloadModel.rowCount()):
            temp = float(self.downloadModel.record(i).value("netSpeed"))
            totalSpeed  += temp
        totalSpeed = round(totalSpeed, 2)
        self.netSpeedInfo.setText('当前网速：%s kB/s'%totalSpeed)
        i = 0
        for t in threading.enumerate():
            if t.name == "downloadLrc" or t.name == "volumeThread" or t == threading.main_thread():
                continue
            i  += 1
        if i == 0:
            self.netSpeedInfo.setText('当前网速：0.0 kB/s')
            row = self.downloadTable.currentIndex().row()
            self.downloadModel.submitAll()
            self.downloadTable.selectRow(row)
            self.timer.stop()
    
    def open_downloaddir(self):
        with open(Configures.settingFile, 'r') as f:
            downloadDir = f.read()
        QDesktopServices.openUrl(QUrl('file://'+downloadDir))
    
    def start_download(self):
        selections = self.downloadTable.selectionModel()
        selecteds = selections.selectedIndexes()
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                self.start_one(row)
    
    def start_all(self):
        for i in range(self.downloadModel.rowCount()):
#            if self.downloadModel.data(self.downloadModel.index(i, 3)) in ["已取消", "已暂停"]:
            self.start_one(i)
    
    def start_one(self, row):
        if not self.downloadModel.rowCount():
            return
        state = self.downloadModel.data(self.downloadModel.index(row, 4))
        musicPath = self.downloadModel.data(self.downloadModel.index(row, 7))
#        tempfile = musicPath + '.temp'
        if state in ["已取消", "已暂停", '等待'] or not os.path.exists(self.downloadModel.data(self.downloadModel.index(row, 7))):
            for t in threading.enumerate():
                if t.name == musicPath:
                    return
            downloadThread1 = DownloadThread(self.downloadModel, row)
            downloadThread1.setDaemon(True)
            downloadThread1.setName(self.downloadModel.data(self.downloadModel.index(row, 7)))
            downloadThread1.start()
            if not self.timer.isActive():
                self.timer.start(700)
            
    def pause_download(self):
        selections = self.downloadTable.selectionModel()
        selecteds = selections.selectedIndexes()
        if not len(selecteds):
            return
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                downloadState = self.downloadModel.record(row).value("remain")
                if downloadState not in ["已完成", "已取消", "已暂停"]:
                    musicPath = self.downloadModel.record(row).value("musicPath")
                    for t in threading.enumerate():
                        if t.name == musicPath:
                            t.pause()
                            break
    
    def stop_download(self):
        selections = self.downloadTable.selectionModel()
        selecteds = selections.selectedIndexes()
        if not len(selecteds):
            return
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                downloadState = self.downloadModel.record(row).value("remain")
                if downloadState not in ["已完成", "已取消"]:
                    musicPath = self.downloadModel.record(row).value("musicPath")
                    tempfileName = musicPath + '.temp'
                    if os.path.exists(tempfileName):
                        os.remove(tempfileName)
                    self.downloadModel.setData(self.downloadModel.index(row, 4), "已取消")
                    self.downloadModel.setData(self.downloadModel.index(row, 2), 0)
                    for t in threading.enumerate():
                        if t.name == musicPath:
                            t.stop()
                            break
        self.downloadModel.submitAll()
        self.downloadTable.selectRow(selecteds[0].row())

    def pause_all(self):
        if threading.active_count() == 1:
            return
#        ok = QMessageBox.question(self, '注意', '所有正在下载任务将被暂停，您是否继续？', QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
#        if ok == QMessageBox.Yes:
        for t in threading.enumerate():
            if t.name == "downloadLrc" or t.name == "volumeThread" or t == threading.main_thread():
                continue
            t.pause()
    
#    def stopAll(self):
#        if threading.active_count() == 1:
#            return
#        ok = QMessageBox.question(self, '注意', '所有正在下载任务将被取消，您是否继续？', QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
#        if ok == QMessageBox.Yes:
#            for t in threading.enumerate():
#                if t != threading.main_thread():
#                    t.stop()

    def delete_localfiles(self):
        self.deletePermit = True
        self.remove_these_rows()
        self.deletePermit = False
    
    def remove_these_rows(self):
        if not self.downloadModel.rowCount():
            return
        selections = self.downloadTable.selectionModel()
        selecteds = selections.selectedIndexes()
        if not len(selecteds):
            return
        if self.deletePermit:
            text_tmp = "选中项将被移除列表，同时会删除对应的本地文件，请确认！"
        else:
            text_tmp = "您确定要移除选中项？"
        ok = QMessageBox.warning(self, '注意', text_tmp, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok == QMessageBox.Yes:
            self.setCursor(QCursor(Qt.BusyCursor))
            if self.deletePermit:
                self.downloadModel.delete_localfiles(selecteds)
            self.downloadModel.delete_selecteds(selecteds)
            self.setCursor(QCursor(Qt.ArrowCursor))
            
    def clear_table(self):
        if not self.downloadModel.rowCount():
            return
        ok = QMessageBox.warning(self, '注意', '当前列表将被清空，当前下载也将被取消！\n您是否继续？', QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok == QMessageBox.Yes:
            self.setCursor(QCursor(Qt.BusyCursor))
            self.netSpeedInfo.setText('当前网速：0.0 kB/s')
            for t in threading.enumerate():
                if t != threading.main_thread():
                    t.stop()
#            os.system("rm -f *.temp")
            self.timer.stop()
            q = QtSql.QSqlQuery()
            q.exec_("drop table downloadTable")
            q.exec_("commit")
            q.exec_("create table downloadTable (title varchar(50), progress varchar(20), size varchar(20), remain varchar(20), album varchar(20), songLink varchar(30), musicPath varchar(30),netSpeed varchar(30),musicId varchar(10))")
            q.exec_("commit")
            self.downloadModel.initial_model()
            self.downloadTable.initial_view(self.downloadModel)
            self.setCursor(QCursor(Qt.ArrowCursor))
        
    def eventFilter(self, target, event):
        if target == self.downloadTable:
            if threading.active_count() == 1:
#                self.downloadTable.setSelectionMode(QAbstractItemView.ExtendedSelection)     
                self.downloadTable.removeRowsAction.setVisible(True)
                self.downloadTable.deleteAction.setVisible(True)
            else:
                self.downloadTable.removeRowsAction.setVisible(False)
                self.downloadTable.deleteAction.setVisible(False)
#                self.downloadTable.setSelectionMode(QAbstractItemView.SingleSelection)
        return False

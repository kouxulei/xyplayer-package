import time, os, threading
from PyQt4.QtGui import (QWidget, QIcon, QCursor, QMessageBox,QHBoxLayout, QComboBox, QPushButton, 
                                        QVBoxLayout, QLineEdit,QToolButton, QLabel)
from PyQt4.QtCore import Qt, pyqtSignal, QSize
from xyplayer.mytables import SearchTable, TableModel
from xyplayer.mythreads import DownloadLrcThread
from xyplayer.urldispose import SearchOnline
from xyplayer.configure import Configures

class SearchFrame(QWidget):
    switch_to_online_list = pyqtSignal()
    add_bunch_to_list_succeed = pyqtSignal()
    listen_online_signal = pyqtSignal(str, str, str)
    listen_local_signal = pyqtSignal(str)
    add_to_download_signal = pyqtSignal()
    back_to_main_signal = pyqtSignal()

    def  __init__(self, parent = None):
        super(SearchFrame, self).__init__(parent)
        self.setup_ui()
        self.create_connections()
        self.jumpPageFlag = 0
    
    def setup_ui(self):
        self.searchTable = SearchTable()
        self.searchTable.setColumnWidth(0, 39)
        self.searchTable.setColumnWidth(1, 110)
        self.searchTable.setColumnWidth(2, 100)
        self.searchTable.setColumnWidth(3, 100)
        self.searchButton = QPushButton(clicked = self.search_musics)
        self.searchButton.setFixedSize(QSize(33, 33))
        self.searchButton.setIconSize(QSize(20, 20))
        self.searchButton.setIcon(QIcon(":/iconSources/icons/search.png"))

#返回按键
        self.backButton = QPushButton(clicked = self.back_to_main_signal.emit)
        self.backButton.setStyleSheet("font-size:15px")
        self.backButton.setFixedSize(25, 33)
        self.backButton.setIcon(QIcon(":/iconSources/icons/back.png"))
        self.backButton.setIconSize(QSize(20, 20))

#搜索框的3个部件
        self.lineEdit = QLineEdit()                
#        self.lineEdit.setStyleSheet("font-size:16px")
        self.lineEdit.setFixedHeight(33)
        self.lineEdit.setFocusPolicy(Qt.ClickFocus)
        self.clearButton = QToolButton(clicked = self.lineEdit.clear)
        self.clearButton.setCursor(Qt.ArrowCursor)
        self.clearButton.setFixedSize(32, 32)
        self.clearButton.setIcon(QIcon(":/iconSources/icons/delete.png"))
        self.clearButton.setIconSize(QSize(20, 20))
        self.clearButton.hide()
        
        self.searchComboBox = QComboBox()
        musicIcon = QIcon(":/iconSources/icons/music.png")
        artistIcon = QIcon(":/iconSources/icons/artist.png")
        albumIcon = QIcon(":/iconSources/icons/album.png")       
        self.searchComboBox.setIconSize(QSize(20,20))
        self.searchComboBox.insertItem(0, musicIcon, "歌曲")
        self.searchComboBox.insertItem(1, artistIcon, "歌手")
        self.searchComboBox.insertItem(2, albumIcon, "专辑")
        self.searchComboBox.setFixedSize(78, 33)
        self.searchComboBox.setCursor(Qt.ArrowCursor)
        
        self.firstPageButton = QPushButton("首页", clicked = self.jump_to_first_page)
        self.firstPageButton.setFixedHeight(31)
        self.lastPageButton = QPushButton("末页", clicked = self.jump_to_last_page)
        self.lastPageButton.setFixedHeight(31)
        
        self.previousPageButton = QPushButton("上一页")
        self.previousPageButton.setFixedHeight(31)
        
        self.nextPageButton = QPushButton('下一页')
        self.nextPageButton.setFixedHeight(31)
        
        self.jumpNum = QLineEdit('0')
        self.jumpNum.setStyleSheet("font-size:16px")
        self.jumpNum.setFixedSize(84, 31)
        self.jumpNum.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.pageNum = QLabel("/ 0")
        self.pageNum.setFixedSize(45, 31)
        self.pageNum.setAlignment(Qt.AlignLeft | Qt.AlignVCenter )

#页码栏布局
        pageNumLayout = QHBoxLayout(self.jumpNum)
        pageNumLayout.addStretch()
        pageNumLayout.addWidget(self.pageNum)
        pageNumLayout.setMargin(0)
        pageNumLayout.setSpacing(0)
        pageNumLayout.setContentsMargins(0, 0, 0, 0)
        self.jumpNum.setTextMargins(0, 0, self.pageNum.width(), 0)

#搜索框self.lineEdit的布局
        searchLayout = QHBoxLayout(self.lineEdit)
        searchLayout.addWidget(self.searchComboBox)
        searchLayout.addStretch()
        searchLayout.addWidget(self.clearButton)
        searchLayout.setMargin(1)
        searchLayout.setSpacing(0)
        searchLayout.setContentsMargins(0, 0, 0, 0)
#        self.lineEdit.setLayout(searchLayout)
        self.lineEdit.setTextMargins(self.searchComboBox.width(), 0, self.clearButton.width(), 0)

#搜索栏的布局
        hbox_sch = QHBoxLayout()
        hbox_sch.addWidget(self.backButton)
        hbox_sch.addWidget(self.lineEdit)
        hbox_sch.addWidget(self.searchButton)

#综合布局
        self.controlWidget = QWidget()
        controlLayout = QHBoxLayout(self.controlWidget)
        controlLayout.setMargin(0)
        controlLayout.setSpacing(6)
#        spacerItem  =  QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
#        controlLayout.addItem(spacerItem)
        controlLayout.addWidget(self.firstPageButton)
        controlLayout.addWidget(self.previousPageButton)
        controlLayout.addWidget(self.jumpNum)
#        controlLayout.addWidget(self.pageNum)
        controlLayout.addWidget(self.nextPageButton)
        controlLayout.addWidget(self.lastPageButton)
#        controlLayout.addItem(spacerItem)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setMargin(0)
#        mainLayout.addSpacing(6)
        mainLayout.addLayout(hbox_sch)
        mainLayout.addSpacing(2)
        mainLayout.addWidget(self.searchTable)
        mainLayout.addSpacing(2)
        mainLayout.addWidget(self.controlWidget)
        mainLayout.addSpacing(2)
        
        self.currentPage = 0
        self.pages = 0
        self.currentKeyword = ''
        self.searchByType = 'all'
        self.searchComboBox.setCurrentIndex(0)
    
    def create_connections(self):
        self.lineEdit.textChanged.connect(self.clrbutton_show)
        
        self.previousPageButton.clicked.connect(self.previous_page)
        self.nextPageButton.clicked.connect(self.next_page)
        self.jumpNum.returnPressed.connect(self.return_pressed_go_to_page)
        
        self.lineEdit.returnPressed.connect(self.return_pressed_search_musics)
        self.searchComboBox.currentIndexChanged.connect(self.searchtype_changed)

        self.searchTable.switchToOnlineListAction.triggered.connect(self.switch_to_online_list)
        self.searchTable.cellDoubleClicked.connect(self.searchtable_clicked)
        self.searchTable.cellClicked.connect(self.show_tooltip)
        self.searchTable.listenOnlineAction.triggered.connect(self.listen_online)
        self.searchTable.downloadAction.triggered.connect(self.download)
        self.searchTable.addBunchToListAction.triggered.connect(self.add_bunch_to_list)
    
#    def eventFilter(self, target, event):
#        if target == self.searchTable:
#            if event.type() == QEvent.Resize:
#                width = self.searchTable.width()
#                widthTemp = (width-35)/3
#                self.searchTable.setColumnWidth(0, 35)
#                self.searchTable.setColumnWidth(1, widthTemp)
#                self.searchTable.setColumnWidth(2, widthTemp)
#                self.searchTable.setColumnWidth(3, widthTemp)
#        return False
    
    def show_tooltip(self, row):
        mark = self.searchTable.item(row, 0).text()
        songName = self.searchTable.item(row, 1).text()
        artist = self.searchTable.item(row, 2).text()
        album = self.searchTable.item(row, 3).text()
        self.searchTable.setToolTip("评分：%s\n 歌曲：%s\n歌手：%s\n专辑：%s"%(mark, songName, artist, album))
    
    def switch_to_list(self):
        self.switchToOnlineList.emit()    
    
    def listen_online(self):
        if not self.searchTable.rowCount():
            return
        self.searchtable_clicked(self.searchTable.currentRow())
            
    def searchtable_clicked(self, row):
        musicName = self.searchTable.item(row, 1).text()
        artist = self.searchTable.item(row, 2).text()
        title = artist + '._.' + musicName
        album = self.searchTable.item(row, 3).text()
        musicId = self.searchTable.item(row, 4).text()
        songLink = SearchOnline.get_song_link(musicId)
        if not songLink:
            return
        songLinkWrap = songLink + '~' + musicId
        thread = DownloadLrcThread([title, songLinkWrap])
        thread.setDaemon(True)
        thread.setName('downloadLrc')
        thread.start()
        self.listen_online_signal.emit(title, album, songLinkWrap)
    
    def add_bunch_to_list(self):
        selections = self.searchTable.selectionModel()
        selecteds = selections.selectedIndexes()
        if not len(selecteds):
            return
        model = TableModel()
        model.initial_model("在线试听")
        songsInOnlineList = []
        self.added_items = []
        t1 = time.time()
        for i in range(model.rowCount()):
            songsInOnlineList.append(model.record(i).value("paths"))
        t2 = time.time()
        print(t2-t1)
        self.setCursor(QCursor(Qt.BusyCursor))
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                musicId = self.searchTable.item(row, 4).text()
                songLink = SearchOnline.get_song_link(musicId)
                if not songLink:
                    continue
                songLinkWrap = songLink + '~' + musicId
                if songLinkWrap  not in songsInOnlineList:
                    musicName = self.searchTable.item(row, 1).text()
                    artist = self.searchTable.item(row, 2).text()
                    title = artist + '._.' + musicName
                    album = self.searchTable.item(row, 3).text()
                    lrcName = title + '.lrc'
                    lrcPath = os.path.join(Configures.lrcsDir, lrcName)
                    if os.path.exists(lrcPath):
                        os.remove(lrcPath)
                    self.added_items.append([title, songLinkWrap])
#                    SearchOnline.get_lrc_path(title, musicId)
                    model.add_record(title, '未知', album, songLinkWrap, '0M')
        if len(self.added_items):
            thread = DownloadLrcThread(self.added_items)
            thread.setDaemon(True)
            thread.setName("downloadLrc")
            thread.start()
            self.add_bunch_to_list_succeed.emit()
        self.setCursor(QCursor(Qt.ArrowCursor))
        print(time.time()-t2)
        print("Success")
            
    def download(self):
        if not self.searchTable.rowCount():
            return
#        t1 = time.time()
        hasExisted = []
        linkError = []
        self.toBeEmited = []
        selections = self.searchTable.selectionModel()
        selecteds = selections.selectedIndexes()
        if  not len(selecteds):
            return
        with open(Configures.settingFile,  'r') as f:
            downloadDir = f.read()
        self.setCursor(QCursor(Qt.BusyCursor))
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                songName = self.searchTable.item(row, 1).text()
                artist = self.searchTable.item(row, 2).text()
                title = artist + '._.' + songName
                musicName = title + '.mp3'
                musicPath = os.path.join(downloadDir, musicName)
                if os.path.exists(musicPath):
                    hasExisted.append(title)
                    continue
                for t in threading.enumerate():
                    if t.name == musicPath:
                        continue
                album = self.searchTable.item(row, 3).text()
                musicId = self.searchTable.item(row, 4).text()
                songLink = SearchOnline.get_song_link(musicId)
                if not songLink:
                    linkError.append(title)
                    continue
        #            QMessageBox.critical(self, '错误','链接错误，无法下载该歌曲！')
        #            return
#                songInfo = '->'.join([songLink, musicPath, title , album, musicId])
                self.toBeEmited.append([songLink, musicPath, title , album, musicId])
#        songInfos = json.dumps(toBeEmited)
        self.add_to_download_signal.emit()
        self.setCursor(QCursor(Qt.ArrowCursor))
#        print('searchPageWidget.py searchFrame.download timecost = %s'%(time.time()-t1))
        if len(hasExisted):
            hasExistFiles = '\n'.join(hasExisted)
            self.show()
            QMessageBox.information(self, '提示','以下歌曲已在下载目录中，将不再进行下载！\n%s'%hasExistFiles)
        if len(linkError):
            linkErrorFiles = '\n'.join(linkError)
            self.show()
            QMessageBox.critical(self, '错误','以下歌曲链接出错，无法下载！\n%s'%linkErrorFiles)
    
    def searchtype_changed(self, index):
        if index == 0:
            self.searchByType = 'all'
        elif index == 1:
            self.searchByType = 'artist'
        else:
            self.searchByType = 'album'
        self.search_musics()
        
    
    def go_to_page(self):
        if not self.currentKeyword:
            self.jumpNum.setText('%s'%self.currentPage)
            self.pageNum.setFocus()
            return
        page = self.jumpNum.text()
        try:
            page = int(page)
            if page == (self.currentPage + 1):
                self.pageNum.setFocus()
                self.jumpNum.setText('%i'%page)
                return
            if page > self.pages or page < 1:
                self.jumpNum.setText('%s'%(self.currentPage + 1))
                QMessageBox.information(None, "提示", "页码范围1~%s"%self.pages)
                return
            self.jumpNum.setText('%i'%page)
        except ValueError :
            self.jumpNum.setText('%s'%(self.currentPage + 1))
            QMessageBox.information(None, "提示", "请输入1~%s内的整数！"%self.pages)
            return
        self.show_musics(self.searchByType, self.currentKeyword, page - 1)    
        self.currentPage = page - 1
        print("hahahhahahhahahahahh")
        self.pageNum.setFocus()
    
    def return_pressed_search_musics(self):
        self.searchButton.setFocus()
    
    def return_pressed_go_to_page(self):
        self.jumpPageFlag = 1
        self.nextPageButton.setFocus()
    
    def search_musics(self):
        keyword = self.lineEdit.text()
        if not keyword:
            QMessageBox.information(self, '提示', '请输入搜索关键词！')
            return
        self.currentKeyword = keyword
        self.hit  =  self.show_musics(self.searchByType, self.currentKeyword, 0)
        if self.hit == Configures.URLERROR:
            return
        self.currentPage = 0
        if self.hit:
            self.pages = self.hit//15 + 1
            self.jumpNum.setText('1')
            self.pageNum.setText('/ %s'%self.pages)
        else:
            self.jumpNum.setText('0')
            self.pageNum.setText('/ 0')
    
    def previous_page(self):
        if not self.currentPage:
            return
        self.currentPage -= 1
        self.show_musics(self.searchByType, self.currentKeyword, self.currentPage)
        self.jumpNum.setText('%s'%(self.currentPage + 1))
        
    def next_page(self):
        if not self.jumpPageFlag:
            if self.currentPage  +  1 >= self.pages:
                return
            self.currentPage  += 1
            self.show_musics(self.searchByType, self.currentKeyword, self.currentPage)
            self.jumpNum.setText('%s'%(self.currentPage + 1))
        else:
            self.go_to_page()
            self.jumpPageFlag = 0
            
    def show_musics(self, searchByType, keyword, page):    
        self.searchTable.clear_search_table()
        songs, hit = SearchOnline.search_songs(searchByType, keyword, page)
        if hit == Configures.URLERROR:
            QMessageBox.critical(None, "错误", "联网出错！\n请检查网络连接是否正常！")     
            return Configures.URLERROR
        if not songs or hit == 0:
            return hit
        for song in songs:
            music = song[0]
            artist = song[1]
            album = song[2] 
            if not album:
                album = '未知专辑'
            music_id = song[3]
#            artistId = song['ARTISTID']
            score = song[4]
            self.searchTable.add_record(score, music, artist, album, music_id)
            self.searchTable.sortItems(0, Qt.DescendingOrder)
        return hit

    def clrbutton_show(self):
        if self.lineEdit.text():
            self.clearButton.show()
        else:
            self.clearButton.hide()
        
    def jump_to_first_page(self):
        if not self.pages or self.currentPage ==0:
            return
        self.currentPage = 0
        self.show_musics(self.searchByType, self.currentKeyword, self.currentPage)
        self.jumpNum.setText('%s'%(self.currentPage + 1))
    
    def jump_to_last_page(self):
        if not self.pages or self.currentPage == self.pages - 1:
            return
        self.currentPage = self.pages - 1
        self.show_musics(self.searchByType, self.currentKeyword, self.currentPage)
        self.jumpNum.setText('%s'%(self.currentPage + 1))
        
        
        
        
        

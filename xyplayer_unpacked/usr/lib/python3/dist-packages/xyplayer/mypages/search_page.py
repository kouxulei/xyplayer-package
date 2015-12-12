import os
import threading
from PyQt5.QtWidgets import (
    QWidget, QMessageBox,QHBoxLayout, QComboBox, QPushButton, 
    QVBoxLayout, QLineEdit,QToolButton, QLabel)
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from xyplayer import Configures
from xyplayer.mysettings import globalSettings
from xyplayer.myicons import IconsHub
from xyplayer.mytables import SearchTable
from xyplayer.myplaylists import Playlist
from xyplayer.mythreads import DownloadLrcThread
from xyplayer.urlhandle import SearchOnline
from xyplayer.utils import connect_as_title, get_full_music_name_from_title, composite_lyric_path_use_title

class SearchBox(QLineEdit):
    search_musics_signal = pyqtSignal(str)
    searchtype_changed_signal = pyqtSignal(int)
    def __init__(self, parent=None):
        super(SearchBox, self).__init__(parent)
        self.setup_ui()
        self.create_connections()
    
    def create_connections(self):
        self.returnPressed.connect(self.search_musics)
        self.searchCombo.currentIndexChanged.connect(self.searchtype_changed_signal.emit)
    
    def setup_ui(self):
        self.searchButton = QToolButton(clicked = self.search_musics)
        self.searchButton.setFocusPolicy(Qt.NoFocus)
        self.searchButton.setIconSize(QSize(20, 20))
        self.searchButton.setIcon(QIcon(IconsHub.Search))
        self.searchCombo = QComboBox()
        musicIcon = QIcon(IconsHub.SearchMusictitle)
        artistIcon = QIcon(IconsHub.SearchArtist)
        albumIcon = QIcon(IconsHub.SearchAlbum)       
        self.searchCombo.setIconSize(QSize(20, 20))
        self.searchCombo.insertItem(0, musicIcon, "歌曲")
        self.searchCombo.insertItem(1, artistIcon, "歌手")
        self.searchCombo.insertItem(2, albumIcon, "专辑")
        self.searchCombo.setFixedSize(80, 28)
        self.searchCombo.setCursor(Qt.ArrowCursor)
        self.searchCombo.setCurrentIndex(0)
        searchLayout = QHBoxLayout(self)
        searchLayout.addWidget(self.searchCombo)
        searchLayout.addStretch()
        searchLayout.addWidget(self.searchButton)
        searchLayout.setSpacing(0)
        searchLayout.setContentsMargins(1, 1, 1, 1)
        self.setTextMargins(83, 0, 23, 0)  
    
    def search_musics(self):
        self.search_musics_signal.emit(self.text())
        
class SearchFrame(QWidget):
    switch_to_online_list = pyqtSignal()
    add_bunch_to_list_succeed = pyqtSignal()
    listen_online_signal = pyqtSignal(str, str, str, str)
    add_to_download_signal = pyqtSignal()
    back_to_main_signal = pyqtSignal()

    def  __init__(self, parent = None):
        super(SearchFrame, self).__init__(parent)
        self.init_params()
        self.setup_ui()
        self.create_connections()
    
    def setup_ui(self):
        self.searchTable = SearchTable()
        self.searchTable.setColumnWidth(0, 39)
        self.searchTable.setColumnWidth(1, 205)
        self.searchTable.setColumnWidth(2, 180)
        self.searchTable.setColumnWidth(3, 180)
        
        self.firstPageButton = QPushButton("首页", clicked = self.jump_to_first_page)
        self.firstPageButton.setFocusPolicy(Qt.NoFocus)
        self.firstPageButton.setFixedHeight(31)
        self.lastPageButton = QPushButton("末页", clicked = self.jump_to_last_page)
        self.lastPageButton.setFocusPolicy(Qt.NoFocus)
        self.lastPageButton.setFixedHeight(31)
        
        self.previousPageButton = QPushButton("上一页")
        self.previousPageButton.setFocusPolicy(Qt.NoFocus)
        self.previousPageButton.setFixedHeight(31)
        
        self.nextPageButton = QPushButton('下一页')
        self.nextPageButton.setFocusPolicy(Qt.NoFocus)
        self.nextPageButton.setFixedHeight(31)
        
        self.jumpNum = QLineEdit('0')
        self.jumpNum.setFocusPolicy(Qt.StrongFocus)
        self.jumpNum.setFixedSize(84, 31)
        self.jumpNum.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.pageNum = QLabel("/ 0")
        self.pageNum.setFixedSize(45, 31)
        self.pageNum.setAlignment(Qt.AlignLeft | Qt.AlignVCenter )

#页码栏布局
        pageNumLayout = QHBoxLayout(self.jumpNum)
        pageNumLayout.addStretch()
        pageNumLayout.addWidget(self.pageNum)
        pageNumLayout.setContentsMargins(0, 0, 0, 0)
        pageNumLayout.setSpacing(0)
        pageNumLayout.setContentsMargins(0, 0, 0, 0)
        self.jumpNum.setTextMargins(0, 0, self.pageNum.width(), 0)

#综合布局
        self.controlWidget = QWidget()
        controlLayout = QHBoxLayout(self.controlWidget)
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.setSpacing(6)
        controlLayout.addWidget(self.firstPageButton)
        controlLayout.addWidget(self.previousPageButton)
        controlLayout.addWidget(self.jumpNum)
        controlLayout.addWidget(self.nextPageButton)
        controlLayout.addWidget(self.lastPageButton)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(7)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.searchTable)
        mainLayout.addWidget(self.controlWidget)
        
        self.currentPage = 0
        self.pages = 0
        self.currentKeyword = ''
        self.searchByType = 'all'
    
    def create_connections(self):
        self.previousPageButton.clicked.connect(self.previous_page)
        self.nextPageButton.clicked.connect(self.next_page)
        self.jumpNum.returnPressed.connect(self.go_to_page)

        self.searchTable.switchToOnlineListAction.triggered.connect(self.switch_to_online_list)
        self.searchTable.cellDoubleClicked.connect(self.searchtable_clicked)
        self.searchTable.cellClicked.connect(self.show_tooltip)
        self.searchTable.listenOnlineAction.triggered.connect(self.listen_online)
        self.searchTable.downloadAction.triggered.connect(self.download)
        self.searchTable.addBunchToListAction.triggered.connect(self.add_bunch_to_list)
    
    def init_params(self):
        self.downloadDir = globalSettings.DownloadfilesPath
    
    def set_download_dir(self, path):
        self.downloadDir = path
    
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
        selections = self.searchTable.selectionModel()
        selecteds = selections.selectedIndexes()
        if not len(selecteds):
            return
        row = selecteds[0].row()
        self.searchtable_clicked(row)
            
    def searchtable_clicked(self, row):
        musicName = self.searchTable.item(row, 1).text()
        artist = self.searchTable.item(row, 2).text()
        title = connect_as_title(artist, musicName)
        album = self.searchTable.item(row, 3).text()
        musicId = self.searchTable.item(row, 4).text()
        songLink = SearchOnline.get_song_link(musicId)
        if not songLink:
            return
        thread = DownloadLrcThread([(title, musicId)])
        thread.setDaemon(True)
        thread.setName('downloadLrc')
        thread.start()
        self.listen_online_signal.emit(title, album, songLink, musicId)
    
    def add_bunch_to_list(self):
        """向“在线试听”列表批量添加歌曲。"""
        selecteds = self.searchTable.selectedIndexes()
        if not len(selecteds):
            return
        self.added_items = []
        playlistTemp = Playlist()
        playlistTemp.fill_list(Configures.PlaylistOnline)
        musicIdsInOnlineList = playlistTemp.get_items_queue()
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                musicId = self.searchTable.item(row, 4).text()
                if musicId  not in musicIdsInOnlineList:
                    musicName = self.searchTable.item(row, 1).text()
                    artist = self.searchTable.item(row, 2).text()
                    title = connect_as_title(artist, musicName)
                    album = self.searchTable.item(row, 3).text()
                    lrcPath = composite_lyric_path_use_title(title)
                    if os.path.exists(lrcPath):
                        os.remove(lrcPath)
                    self.added_items.append([title, musicId])
                    playlistTemp.add_record(musicId, title, Configures.ZeroTime, album, Configures.NoLink, 0, musicId)
        if len(self.added_items):
            playlistTemp.commit_records()
            thread = DownloadLrcThread(self.added_items)
            thread.setDaemon(True)
            thread.setName("downloadLrc")
            thread.start()
            self.add_bunch_to_list_succeed.emit()
            
    def download(self):
        if not self.searchTable.rowCount():
            return
        hasExisted = []
        self.readyToDownloadSongs = []
        selections = self.searchTable.selectionModel()
        selecteds = selections.selectedIndexes()
        if  not len(selecteds):
            return
        self.setCursor(QCursor(Qt.BusyCursor))
        for index in selecteds:
            if index.column() == 0:
                row = index.row()
                songName = self.searchTable.item(row, 1).text()
                artist = self.searchTable.item(row, 2).text()
                title = connect_as_title(artist, songName)
                musicName = get_full_music_name_from_title(title)
                musicPath = os.path.join(self.downloadDir, musicName)
                if os.path.exists(musicPath):
                    hasExisted.append(title)
                    continue
                for t in threading.enumerate():
                    if t.name == musicPath:
                        continue
                album = self.searchTable.item(row, 3).text()
                musicId = self.searchTable.item(row, 4).text()
                songLink = Configures.NoLink
                self.readyToDownloadSongs.append([songLink, musicPath, title , album, musicId])
        self.add_to_download_signal.emit()
        self.setCursor(QCursor(Qt.ArrowCursor))
        if len(hasExisted):
            hasExistFiles = '\n'.join(hasExisted)
            self.show()
            QMessageBox.information(self, '提示','以下歌曲已在下载目录中，将不再进行下载！\n%s'%hasExistFiles)
    
    def searchtype_changed(self, index):
        if index == 0:
            self.searchByType = 'all'
        elif index == 1:
            self.searchByType = 'artist'
        else:
            self.searchByType = 'album'
        
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
        self.pageNum.setFocus()
    
    def search_musics(self, keyword):
        if not keyword:
            QMessageBox.information(self, '提示', '请输入搜索关键词！')
            return False
        self.currentKeyword = keyword
        self.hit  =  self.show_musics(self.searchByType, self.currentKeyword, 0)
        if self.hit == Configures.UrlError:
            QMessageBox.critical(None, "错误", "联网出错！\n请检查网络连接是否正常！")     
            return False
        self.currentPage = 0
        if not self.hit:
            self.jumpNum.setText('0')
            self.pageNum.setText('/ 0')
            QMessageBox.warning(None, "错误", "未找到任何结果！")     
            return False
        self.pages = self.hit//Configures.NumSearchOneTime + 1
        self.jumpNum.setText('1')
        self.pageNum.setText('/ %s'%self.pages)
        return True
    
    def previous_page(self):
        if not self.currentPage:
            return
        self.currentPage -= 1
        self.show_musics(self.searchByType, self.currentKeyword, self.currentPage)
        self.jumpNum.setText('%s'%(self.currentPage + 1))
        
    def next_page(self):
        if self.currentPage  +  1 >= self.pages:
            return
        self.currentPage  += 1
        self.show_musics(self.searchByType, self.currentKeyword, self.currentPage)
        self.jumpNum.setText('%s'%(self.currentPage + 1))
            
    def show_musics(self, searchByType, keyword, page):    
        self.searchTable.clear_search_table()
        songs, hit = SearchOnline.search_songs(searchByType, keyword, page)
        if hit == Configures.UrlError:
            return Configures.UrlError
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
        
        
        
        
        

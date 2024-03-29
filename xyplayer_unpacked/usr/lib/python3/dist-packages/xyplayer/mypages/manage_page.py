import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from xyplayer import Configures
from xyplayer.myicons import IconsHub
from xyplayer.mywidgets import MyLyricText
from xyplayer.mypages import  search_page, download_page
from xyplayer.myplaylists import playlistsManager
from xyplayer.mysettings import globalSettings
from xyplayer.mytables import PlaylistWidget, PlaylistsTableUnfold, PlaylistsTable
from xyplayer.mypages import (exitmode_panel, settings_frame, about_page, update_panel, 
    artist_info_page, song_info_page)

class ManagePage(QWidget):
    changeVolume = pyqtSignal(int)
    changeMuting = pyqtSignal(bool)
    current_table_changed_signal = pyqtSignal(str)
    add_a_list_signal = pyqtSignal()
    playlist_removed_signal = pyqtSignal(str)
    playlist_renamed_signal = pyqtSignal(str, str)
    def __init__(self):
        super(ManagePage, self).__init__()
        self.initial_parameters()
        self.setup_ui()
        self.create_connections()
        self.set_threading_lock_on_playlistwidget()
        self.reload_download_works()
    
    def set_threading_lock_on_playlistwidget(self):
        self.lock = threading.Lock()    #设置一个线程锁，为了防止下载任务完成后向“我的下载”添加记录时与当前在此表上的其他操作产生冲突。
        self.playlistWidget.set_lock(self.lock)
    
    def get_threading_lock(self):
        return self.lock
    
    def get_download_dir(self):
        return self.settingsFrame.get_download_dir()
    
    def reload_download_works(self):
        self.downloadPage.reload_works_from_database(self.lock)      
    
    def handle_before_app_exit(self):
        self.record_volume()
        self.downloadPage.record_works_into_database()
        
    def set_download_dir(self, dir):
        self.searchFrame.set_download_dir(dir)
        self.playlistWidget.set_download_dir(dir)
    
    def setup_ui(self):
        self.setObjectName('managePage')
        self.setFixedHeight(520)
        self.settingsFrame = settings_frame.SettingsFrame()
        self.aboutPage = about_page.AboutPage()
        self.updatePanel = update_panel.UpdatePanel()
        self.exitmodePanel = exitmode_panel.ExitmodePanel()
        self.lyricText = MyLyricText()

        self.playlistWidget = PlaylistWidget()
        self.playlistWidget.setFixedHeight(435)
        self.playlistWidget.set_playlist_names(playlistsManager.get_play_list_names())
        self.playlistWidget.set_playlist_use_name(Configures.PlaylistDefault)
        
        self.playlistTableUnfold = PlaylistsTableUnfold(self.playlistWidget)
        self.playlistTableUnfold.hide()
        self.playlistsTable = PlaylistsTable()
        for i, tableName in enumerate(playlistsManager.get_play_list_names()):
            self.playlistsTable.add_item(tableName)  
        self.playlistsTable.selectRow(1)
        
        plWidgets = QWidget()
        hbox = QHBoxLayout(plWidgets)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.playlistsTable)
        hbox.addWidget(self.playlistTableUnfold)
        
#搜索页面
        self.searchFrame = search_page.SearchFrame()
#下载页面
        self.downloadPage = download_page.DownloadPage()

#歌手信息
        self.artistInfoPage = artist_info_page.ArtistInfoPage()

#歌曲信息
        self.songInfoPage = song_info_page.SongInfoPage()

#中间的stackedWidget
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.setObjectName('stackleft')
        self.stackedWidget.setFixedWidth(270)
        self.stackedWidget.addWidget(plWidgets)
        self.stackedWidget.addWidget(self.downloadPage)
        self.stackedWidget.addWidget(self.exitmodePanel)
        self.stackedWidget.addWidget(self.updatePanel)
    
        self.muteButton = QToolButton(clicked=self.mute_clicked)
        self.muteButton.setFocusPolicy(Qt.NoFocus)
        self.muteButton.setIcon(QIcon(IconsHub.Volume))
        self.muteButton.setIconSize(QSize(25, 25))
        self.volumeSlider = QSlider(Qt.Vertical, valueChanged=self.changeVolume)
        self.volumeSlider.setObjectName('volumeSlider')
        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setFixedHeight(120)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(globalSettings.Volume)
        self.toolBar = QToolBar()
        self.toolBar.setIconSize(QSize(36, 36))
        self.toolBar.setObjectName('toolBar')
        self.toolBar.setOrientation(Qt.Vertical)
        self.toolBar.addAction(QIcon(IconsHub.Musics), self.tr('musics'))
        self.toolBar.addAction(QIcon(IconsHub.Download), self.tr('download'))
        self.toolBar.addAction(QIcon(IconsHub.Exitmode), self.tr('exitmode'))
        self.toolBar.addAction(QIcon(IconsHub.Update), self.tr('update'))
        volumeLayout = QVBoxLayout()
        volumeLayout.setContentsMargins(6, 0, 0, 0)
        volumeLayout.addWidget(self.volumeSlider)
        volumeLayout.addWidget(self.muteButton)
        toolsLayout = QVBoxLayout()
        toolsLayout.setContentsMargins(0, 0, 0, 0)
        toolsLayout.addWidget(self.toolBar)
        toolsLayout.addLayout(volumeLayout)

        functionsLayout = QHBoxLayout()
        functionsLayout.setSpacing(0)
        functionsLayout.setContentsMargins(0, 0, 0, 0)
        functionsLayout.addLayout(toolsLayout)
        functionsLayout.addWidget(self.stackedWidget)
        
        self.windowsStack = QStackedWidget()    #歌词、搜索、关于等合用的一个堆栈
        self.windowsStack.setFixedWidth(600)
        self.windowsStack.addWidget(self.lyricText)
        self.windowsStack.addWidget(self.settingsFrame)
        self.windowsStack.addWidget(self.aboutPage)
        self.windowsStack.addWidget(self.searchFrame)
        self.windowsStack.addWidget(self.artistInfoPage)
        self.windowsStack.addWidget(self.songInfoPage)
        
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(functionsLayout)
        mainLayout.addWidget(self.windowsStack)
        
    def initial_parameters(self):
        self.playerMuted  = False
        self.currentRow = 1
        self.pageDescriptions = ['歌词', '选项', '关于', '搜索', '歌手', '歌曲']
        self.certainPageDescription = self.pageDescriptions[0]

    def create_connections(self):
        self.toolBar.actionTriggered.connect(self.action_in_toolbar_triggered)
        self.playlistTableUnfold.fold_all_signal.connect(self.fold_all_playlists)
        self.playlistTableUnfold.unfold_next_signal.connect(self.unfold_next_playlist)
        self.playlistsTable.switch_to_this_playlist_signal.connect(self.unfold_a_playlist)
        self.playlistsTable.add_a_playlist_signal.connect(self.add_a_playlist)
        self.playlistsTable.rename_a_playlist_signal.connect(self.rename_a_playlist)
        self.playlistsTable.delete_a_playlist_signal.connect(self.delete_a_playlist)
        self.songInfoPage.tag_values_changed_signal.connect(self.playlistWidget.change_tag_value)
        self.songInfoPage.refresh_infos_on_page_signal.connect(self.fill_data_on_song_info_page)
        
    def ui_initial(self):
        self.lyricText.initial_contents()
    
    def unfold_a_playlist(self, row):
        self.currentRow = row % self.playlistsTable.rowCount()
        nextRow = (row + 1) % self.playlistsTable.rowCount()
        unfoldedName = self.playlistsTable.item(self.currentRow, 0).text()
        nextName = self.playlistsTable.item(nextRow, 0).text()
        self.playlistsTable.hide()
        self.playlistWidget.set_playlist_use_name(unfoldedName)
        self.playlistTableUnfold.set_two_item_names(unfoldedName, nextName)
        self.current_table_changed_signal.emit(unfoldedName)
        self.playlistTableUnfold.show()
        
    def fold_all_playlists(self):
        self.playlistsTable.show()
        self.select_current_playlist_on_table()
        self.playlistTableUnfold.hide()
        
    def unfold_next_playlist(self):
        self.unfold_a_playlist(self.currentRow+1)
    
    def select_current_playlist_on_table(self):
        if not self.playlistsTable.isHidden():
            self.playlistsTable.selectRow(playlistsManager.get_play_list_names().index(self.playlistWidget.get_playing_list_name()))
    
    def add_a_playlist(self):
        j = 1
        while True:            
            textOld = "我的列表%s"%j
            if textOld not in playlistsManager.get_play_list_names():
                break
            j += 1            
        text, ok = QInputDialog.getText(self, "添加列表", "请输入列表名：", QLineEdit.Normal, textOld)
        if ok:
            if text:
                if text in playlistsManager.get_play_list_names():
                    QMessageBox.critical(self, "注意！", "列表'%s'已存在！\n请重新添加！"%text)
                    return
            else:
                QMessageBox.critical(self, "注意！", "列表名不能为空！")
                return
            playlistsManager.create_a_playlist(text)
            self.playlistsTable.add_item(text)

    def rename_a_playlist(self, index):
        name = self.playlistsTable.get_name_at(index)
        newName, ok = QInputDialog.getText(self, "重命名列表", "请输入新列表名：", QLineEdit.Normal, name)
        if ok:
            if newName and newName != name:
                if newName in playlistsManager.get_play_list_names():
                    QMessageBox.critical(self, "注意！", "列表'%s'已存在！\n请重新修改！"%newName)
                else:
                    playlistsManager.rename_a_playlist(name, newName)
                    self.playlistsTable.rename_an_item(index, newName)
                    self.playlist_renamed_signal.emit(name, newName)
                
    def delete_a_playlist(self, index):    
        name = self.playlistsTable.get_name_at(index)
        ok = QMessageBox.warning(self, "删除列表", "列表'%s'将被删除，请确认！"%name, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok == QMessageBox.Yes:
            playlistsManager.remove_a_playlist(name)
            self.playlistsTable.remove_item_at(index)
            self.playlist_removed_signal.emit(name)

    def action_in_toolbar_triggered(self, action):
        text = action.text()
        pages = ('musics', 'download', 'exitmode', 'update')
        pageNum = pages.index(text)
        self.stackedWidget.setCurrentIndex(pageNum)
        if pageNum == 0:
            self.fold_all_playlists()
       
    def show_main_stack_window(self):
        self.show_certain_page(0)
   
    def show_settings_frame(self):
        self.show_certain_page(1)
    
    def show_about_page(self):
        self.show_certain_page(2)
    
    def show_search_frame(self):
        self.show_certain_page(3)
    
    def show_artist_info(self, name):
        self.artistInfoPage.set_artist_info(name)
        self.show_certain_page(4)
    
    def show_song_info(self, row):
        self.fill_data_on_song_info_page(row)
        self.show_certain_page(5)

    def show_certain_page(self, pageNum):
        self.certainPageDescription = self.pageDescriptions[pageNum]
        self.windowsStack.setCurrentIndex(pageNum)

    def get_page_description(self):
        return self.certainPageDescription

    def set_loved_songs(self, lovedSongs):
        self.songInfoPage.set_loved_songs(lovedSongs)
    
    def set_songinfos_manager(self, sim):
        self.songInfoPage.set_songinfos_manager(sim)
        
    def fill_data_on_song_info_page(self, row):
        playlistName = self.playlistWidget.get_operating_playlist_name()
        playlistLength = self.playlistWidget.get_playlist_length()
        editable = True
        if playlistName == Configures.PlaylistOnline:
            editable = False
        self.songInfoPage.set_editable(editable)
        playlist = self.playlistWidget.get_playlist()
        title, totalTime, album, path, size, musicId, addedTime, modifiedTime = playlist.get_record_at(row)[:8]
        self.songInfoPage.set_playlist_infos(playlistName, playlistLength, row)
        self.songInfoPage.set_basic_infos(title, totalTime, album, path, size, musicId)
        self.songInfoPage.set_time_infos(addedTime, modifiedTime)
        
    def set_muted(self, muted):
        if muted != self.playerMuted:
            self.playerMuted = muted
            self.muteButton.setIcon(QIcon(IconsHub.VolumeMuted if muted else IconsHub.Volume))
    
    def mute_clicked(self):
        self.changeMuting.emit(not self.playerMuted)
    
    def record_volume(self):
        print('Recording: volume ...')
        globalSettings.__setattr__(globalSettings.optionsHub.Volume, self.volumeSlider.value())


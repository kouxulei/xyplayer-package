from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal, Qt
from xyplayer import Configures
from xyplayer.mywidgets import NewLabel
from xyplayer.utils import (convert_B_to_MB, write_tags, connect_as_title, get_time_of_now, import_a_lyric, 
    get_artist_and_musicname_from_title, format_time_str_with_weekday, get_base_name_from_path)

class SongInfoPage(QWidget):
    tag_values_changed_signal = pyqtSignal(int, str, str, str)
    refresh_infos_on_page_signal = pyqtSignal(int)
    def __init__(self, parent=None):
        super(SongInfoPage, self).__init__(parent)
        self.row = 0
        self.artist = ''
        self.musicName = ''
        self.album = ''
        self.title = ''
        self.path = ''
        self.lovedSongs = None
        self.songinfosManager = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle('歌曲信息')
        label1 = QLabel('歌手：')
        label2 = QLabel('曲名：')
        label3 = QLabel('专辑：')
        label4 = QLabel('路径：')
        label4.setFixedWidth(40)
        self.artistEdit = QLineEdit()
        self.musicEdit = QLineEdit()
        self.albumEdit = QLineEdit()
        self.timeLabel = QLabel('时长： 00:00')
        self.sizeLabel = QLabel('大小： 0.00 MB')
        self.pathLabel = NewLabel()
        self.playlistInfoLabel = QLabel('位置： 默认列表  ( 1 / 100 )')
        self.countInfoLabel = QLabel('播放次数： n次')
        self.addTimeLabel = QLabel('添加时间： 2015年12月30日')
        self.modifyTimeLabel = QLabel('修改时间： 2015年12月31日')
        self.favorInfoLabel = QLabel('收藏情况： 未收藏')
        self.traceInfoLabel = QLabel('歌曲来源： 本地添加') 
        self.nearPlaylistLabel = QLabel('最近播放位置： 默认列表')
        self.nearPlayedDateLabel = QLabel('最近播放时间： 2016年1月1日')
        self.applyButton = QPushButton('应用', clicked=self.apply)
        self.applyButton.setFocusPolicy(Qt.NoFocus)
        self.cancelButton = QPushButton('取消', clicked=self.cancel)
        self.cancelButton.setFocusPolicy(Qt.NoFocus)
        self.refreshButton = QPushButton('刷新', clicked=self.refresh_infos_on_page)
        self.refreshButton.setFocusPolicy(Qt.NoFocus)
        self.importlyricButton = QPushButton('导入歌词', clicked=self.import_lyric)
        self.importlyricButton.setFocusPolicy(Qt.NoFocus)
        hbox0 = QHBoxLayout()
        hbox0.addWidget(label4)
        hbox0.addWidget(self.pathLabel)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label1)
        hbox1.addWidget(self.artistEdit)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(label2)
        hbox2.addWidget(self.musicEdit)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(label3)
        hbox3.addWidget(self.albumEdit)
        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.importlyricButton)
        hbox4.addStretch()
        hbox4.addWidget(self.applyButton)
        hbox4.addWidget(self.cancelButton)
        hbox4.addWidget(self.refreshButton)
        hbox5 = QHBoxLayout()
        hbox5.addWidget(self.timeLabel)
        hbox5.addWidget(self.sizeLabel)
        hbox5.addWidget(self.traceInfoLabel)
        hbox6 = QHBoxLayout()
        hbox6.setContentsMargins(0, 0, 20, 0)
        hbox6.addWidget(self.playlistInfoLabel)
        hbox6.addStretch()
        hbox6.addWidget(self.favorInfoLabel)
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(10)
        mainLayout.addLayout(hbox0)
        mainLayout.addLayout(hbox6)
        mainLayout.addLayout(hbox1)
        mainLayout.addLayout(hbox2)
        mainLayout.addLayout(hbox3)
        mainLayout.addLayout(hbox5)
        mainLayout.addWidget(self.countInfoLabel)
        mainLayout.addWidget(self.nearPlaylistLabel)
        mainLayout.addWidget(self.nearPlayedDateLabel)
        mainLayout.addWidget(self.addTimeLabel)
        mainLayout.addWidget(self.modifyTimeLabel)
        mainLayout.addLayout(hbox4)
    
    def set_editable(self, editable):
        self.artistEdit.setReadOnly(not editable)
        self.musicEdit.setReadOnly(not editable)
        self.albumEdit.setReadOnly(not editable)
        self.applyButton.setEnabled(editable)
        self.cancelButton.setEnabled(editable)
    
    def set_basic_infos(self, title, totalTime, album, path, size, musicId):
        artist, musicName = get_artist_and_musicname_from_title(title)
        self.title = title
        self.artist = artist
        self.musicName = musicName
        self.album = album
        self.path = path
        self.artistEdit.setText(artist)
        self.musicEdit.setText(musicName)
        self.albumEdit.setText(album)
        self.timeLabel.setText('时长： %s'%totalTime)
        self.sizeLabel.setText('大小： %.2f MB'%convert_B_to_MB(size))
        self.pathLabel.setText(path)
        trace = '线上资源'
        if musicId == Configures.LocalMusicId:
            trace = '本地资源'
        self.traceInfoLabel.setText('歌曲来源： %s'%trace)
        self.set_favorite_info(title in self.lovedSongs)
        item = get_base_name_from_path(path)
        freq, totalSpan, spanMax, nearPlaylistName, nearPlayedDate, nearPlayedTime = self.songinfosManager.get_statistic_infos_of_item(item)
        if freq:
            countInfos = '播放次数： %i 次#平均播放时长： %.1f 秒#最长播放时长： %.1f 秒'%(freq, totalSpan/freq, spanMax)
            nearPlaylistInfo = '最近播放位置： %s#最近播放时长： %.1f 秒'%(nearPlaylistName,nearPlayedTime)
            nearPlayedDateInfo = '最近播放： %s'%format_time_str_with_weekday(nearPlayedDate)
        else:
            countInfos = '播放次数： 0 次'
            nearPlaylistInfo = '最近播放位置： 未曾播放'
            nearPlayedDateInfo = '最近播放： 未曾播放'
        self.countInfoLabel.setText(countInfos.replace('#', ' '*15))
        self.nearPlaylistLabel.setText(nearPlaylistInfo.replace('#', ' '*15))
        self.nearPlayedDateLabel.setText(nearPlayedDateInfo)
    
    def set_playlist_infos(self, playlistName, playlistLength, row):
        self.row = row
        self.playlistInfoLabel.setText('位置： %s    ( 第%i首 / 共%i首 )'%(playlistName, row+1, playlistLength))
    
    def set_loved_songs(self, lovedSongs):
        self.lovedSongs = lovedSongs
    
    def set_songinfos_manager(self, sim):
        self.songinfosManager = sim
    
    def set_favorite_info(self, loved):
        text = '未收藏'
        if loved:
            text = '已收藏'
        self.favorInfoLabel.setText('收藏情况： %s'%text)
        
    def set_time_infos(self, addedTime, modifiedTime):
        self.addTimeLabel.setText('添加时间： %s'%format_time_str_with_weekday(addedTime))
        self.modifyTimeLabel.setText('修改时间： %s'%format_time_str_with_weekday(modifiedTime))
        
    def apply(self):
        if  self.check_validity() and (self.artist, self.musicName, self.album) != (self.artistEdit.text(), self.musicEdit.text(), self.albumEdit.text()):
            self.artist, self.musicName, self.album = self.artistEdit.text(), self.musicEdit.text(), self.albumEdit.text()
            self.title = connect_as_title(self.artist, self.musicName)
            write_tags(self.path, self.title, self.album)
            modifiedTime = get_time_of_now()
            self.modifyTimeLabel.setText('修改时间： %s'%format_time_str_with_weekday(modifiedTime))
            self.tag_values_changed_signal.emit(self.row, self.title, self.album, modifiedTime)
    
    def cancel(self):
        if (self.artist, self.musicName, self.album) != (self.artistEdit.text(), self.musicEdit.text(), self.albumEdit.text()):
            self.artistEdit.setText(self.artist)
            self.musicEdit.setText(self.musicName)
            self.albumEdit.setText(self.album)

    def check_validity(self):
        text = ''
        valid = False
        if not self.artistEdit.text(): 
            text = self.tr('歌手名')
            self.artistEdit.setText(self.artist)
        elif not self.musicEdit.text():
            text = self.tr('歌曲名')
            self.musicEdit.setText(self.musicName)
        elif not self.albumEdit.text():
            text = self.tr('专辑')
            self.albumEdit.setText(self.album)
        else:
            valid = True
        if not valid:
            QMessageBox.information(self, "歌曲详细信息", '%s不能为空！'%text)
        return valid

    def import_lyric(self):
        lrcFile = QFileDialog.getOpenFileName(self, "选择音乐文件", Configures.HomeDir, self.tr("*.lrc"))[0]
        if lrcFile:
            import_a_lyric(lrcFile, self.title)

    def refresh_infos_on_page(self):
        self.refresh_infos_on_page_signal.emit(self.row)

import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from xyplayer.myicons import IconsHub
from xyplayer.urlhandle import SearchOnline
from xyplayer.mywidgets import NewLabel, MyTextEdit
from xyplayer.utils import get_artist_and_musicname_from_title, parse_artist_info

class ArtistInfoPage(QWidget):
    def __init__(self, parent=None):
        super(ArtistInfoPage, self).__init__(parent)
        self.setup_ui()
        self.create_connections()
    
    def setup_ui(self):
        self.setObjectName('playbackPage')

        #歌手信息页
        self.artistHeadLabel = QLabel(self)
        self.artistHeadLabel.setFixedSize(QSize(90, 90))
        self.artistHeadLabel.setScaledContents(True)
        self.artistName = NewLabel(self, True)
        self.artistName.setFixedSize(QSize(90, 30))
        self.artistGender = QLabel("性别：未知", self)
        self.artistBirthday = QLabel("生日：未知", self)
        self.artistConstellation = QLabel("星座：未知", self)
        self.artistLanguage = QLabel("语言：未知", self)
        self.artistBirthplace = QLabel("出生地：未知", self)
        self.artistDetail = MyTextEdit(self)
        
        #刷新歌手信息缓存按键
        self.refreshBtn = QPushButton(self)
        self.refreshBtn.setFocusPolicy(Qt.NoFocus)
        self.refreshBtn.setIcon(QIcon(IconsHub.Refresh))
        self.refreshBtn.setText('刷新')
        self.refreshBtn.setToolTip("刷新歌手信息")
        self.refreshBtn.setFixedSize(QSize(70, 30))
        
        vbox1 = QVBoxLayout()
        vbox1.setSpacing(10)
        vbox1.addWidget(self.artistHeadLabel)
        vbox1.addWidget(self.artistName)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.artistGender)
        hbox1.addWidget(self.artistBirthday)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.artistConstellation)
        hbox2.addWidget(self.artistLanguage)
        
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.artistBirthplace)
        hbox3.addWidget(self.refreshBtn)
        vbox2 = QVBoxLayout()
        vbox2.addLayout(hbox1)
        vbox2.addLayout(hbox2)
        vbox2.addLayout(hbox3)
        hbox4 = QHBoxLayout()
        hbox4.setSpacing(30)
        hbox4.addLayout(vbox1)
        hbox4.addLayout(vbox2)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(hbox4)
        mainLayout.addWidget(self.artistDetail)
    
    def create_connections(self):
        self.refreshBtn.clicked.connect(self.update_infofile_cached)
    
    def set_artist_info(self, artist):
        if artist == 'Zheng-Yejian':
            self.ui_initial()
        elif artist != self.artistName.text():
            infoPath = SearchOnline.get_artist_info_path(artist)
            infoDict = parse_artist_info(infoPath)
            self.artistName.setText(artist)
            self.artistBirthday.setText('生日：%s'%infoDict['birthday'])
            self.artistBirthplace.setText('出生地：%s'%infoDict['birthplace'])
            self.artistLanguage.setText('语言：%s'%infoDict['language'])
            self.artistGender.setText('性别：%s'%infoDict['gender'])
            self.artistConstellation.setText('星座：%s'%infoDict['constellation'])
            self.artistDetail.clear()
            self.artistDetail.setAlignment(Qt.AlignHCenter)
            self.artistDetail.setHtml(self.get_artist_detail_style_text(infoDict['info']))
            imagePath = SearchOnline.get_artist_image_path(artist)
            if imagePath:
                pixmap = QPixmap(imagePath)
            else:
                pixmap = QPixmap(IconsHub.Anonymous)
            self.artistHeadLabel.setPixmap(pixmap)
    
    def update_artist_info(self, title):
        artist, musicName = get_artist_and_musicname_from_title(title)
        return self.set_artist_info(artist)
    
    def update_infofile_cached(self):
        artist = self.artistName.text()
        if artist != '未知':
            infoPath = SearchOnline.get_local_artist_info_path(artist)
            if os.path.exists(infoPath):
                os.remove(infoPath)
                self.set_artist_info(artist)
    
    def ui_initial(self):
        self.artistHeadLabel.setPixmap(QPixmap(IconsHub.Anonymous))
        self.artistName.setText("Zheng-Yejian")
        self.artistBirthday.setText("生日：1992.10.18")
        self.artistBirthplace.setText("出生地：福建")
        self.artistLanguage.setText("语言：国语")
        self.artistGender.setText("性别：男")
        self.artistConstellation.setText("星座：天秤座")
        self.artistDetail.setHtml(self.get_artist_detail_style_text('大家好，我是作者！！！'))
    
    def get_artist_detail_style_text(self, text):
        return "<p style='color:black;font-size:16px;'>%s</p>"%text
            

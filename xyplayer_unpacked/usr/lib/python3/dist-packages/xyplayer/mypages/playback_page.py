import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from xyplayer import Configures, app_version
from xyplayer.myicons import IconsHub
from xyplayer.urlhandle import SearchOnline
from xyplayer.mytables import WorksList
from xyplayer.mywidgets import NewLabel, MyTextEdit
from xyplayer.mypages import desktop_lyric
from xyplayer.utils import get_artist_and_musicname_from_title, change_lyric_offset_in_file, parse_artist_info
from xyplayer.mysettings import globalSettings

class PlaybackPage(QWidget):
    lyric_offset_changed_signal = pyqtSignal(int)
    desktop_lyric_state_changed_signal = pyqtSignal(bool)
    select_current_row_signal = pyqtSignal()
    playmode_changed_signal = pyqtSignal(int, int)
    def __init__(self):
        super(PlaybackPage, self).__init__()
        self.setup_ui()
        self.create_connections()
        self.initial_params()
    
    def initial_params(self):
        self.playmode = Configures.PlaymodeRandom    #播放模式指示器
        self.lyricRunSize = globalSettings.WindowlyricRunFontSize
        self.lyricRunColor = globalSettings.WindowlyricRunFontColor
        self.lyricReadySize = globalSettings.WindowlyricReadyFontSize
        self.lyricReadyColor = globalSettings.WindowlyricReadyFontColor
    
    def setup_ui(self):
        self.setStyleSheet(
            "QStackedWidget,QTextEdit,QTableView,QTableWidget{background:transparent}"
            "QLabel{color:yellow;}"
            )

#桌面歌词标签
        self.desktopLyric = desktop_lyric.DesktopLyric()
        self.desktopLyric.set_color(globalSettings.DesktoplyricColors)
        
#歌单
        self.musicList = WorksList()
        self.musicList.setFixedHeight(420)
        self.musicList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
#spacerItem
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
#五个基本按键
        self.playmodeButton = QToolButton(self, clicked=self.change_playmode)
        self.playmodeButton.setFocusPolicy(Qt.NoFocus)
        self.playmodeButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:0px solid yellow;border-radius:30px;background:yellow}")
        self.playmodeButton.setIcon(QIcon(IconsHub.PlaymodeRandom))
        self.playmodeButton.setIconSize(QSize(28, 28))
        self.playmodeButton.setToolTip('随机播放')
        
        self.favoriteButton = QToolButton(self)
        self.favoriteButton.setFocusPolicy(Qt.NoFocus)
        self.favoriteButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:0px solid yellow;border-radius:30px;background:yellow}")
        self.favoriteButton.setToolTip('收藏')
        
        self.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
        self.favoriteButton.setIconSize(QSize(25, 25))

        self.previousButton = QToolButton(self)
        self.previousButton.setFocusPolicy(Qt.NoFocus)
        self.previousButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:0px solid yellow;border-radius:35px;background:yellow}")
        self.previousButton.setIconSize(QSize(45, 45))
        self.previousButton.setShortcut(QKeySequence("Ctrl + Left"))

        self.playButton = QToolButton(self)
        self.playButton.setFocusPolicy(Qt.NoFocus)
        self.playButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:0px solid yellow;border-radius:40px;background:yellow}")

        self.playButton.setIconSize(QSize(64, 64))
        self.playButton.setShortcut(QKeySequence("Ctrl + Down"))

        self.nextButton = QToolButton(self)
        self.nextButton.setFocusPolicy(Qt.NoFocus)
        self.nextButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:0px solid yellow;border-radius:35px;background:yellow}")
        self.nextButton.setIconSize(QSize(45, 45))
        self.nextButton.setFocusPolicy(Qt.NoFocus)
        self.nextButton.setShortcut(QKeySequence("Ctrl + Right"))
        
        self.seekSlider = QSlider(Qt.Horizontal, self)
        self.seekSlider.setFocusPolicy(Qt.NoFocus)
        self.seekSlider.setRange(0, 0)
        
        #时间标签
        self.timeLabel1 = QLabel(Configures.ZeroTime, self)
        self.timeLabel2 = QLabel(Configures.ZeroTime, self)
        self.timeLabel1.setAlignment(Qt.AlignRight and Qt.AlignVCenter)
        self.timeLabel2.setAlignment(Qt.AlignLeft and Qt.AlignVCenter)
        self.timeLabel1.setFixedSize(QSize(40, 25))
        self.timeLabel2.setFixedSize(QSize(40, 25)) 
        self.timeLabel1.setStyleSheet("font-family:'微软雅黑';font-size:15px;color: white")
        self.timeLabel2.setStyleSheet("font-family:'微软雅黑';font-size:15px;color: white")
        
        self.backButton = QPushButton(self)
        self.backButton.setFocusPolicy(Qt.NoFocus)
        self.backButton.setIcon(QIcon(IconsHub.Back))
        self.backButton.setFixedSize(35, 28)
        self.backButton.setIconSize(QSize(25, 25))
        self.backButton.setStyleSheet("QPushButton:hover{border:2px solid lightgray;border-color:white;background:rgb(210,240,240)}"
                                                            "QPushButton{border:2px;background:transparent}"
                                                        )
        
        self.musicNameLabel = NewLabel(self)
        self.musicNameLabel.setFixedSize(QSize(220, 30))
        self.musicNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:28px;color: cyan")
        
        self.buttonList = []
        for text in ["歌词", "歌手", "歌单"]:
            button = QPushButton(text, self)
            button.setFocusPolicy(Qt.NoFocus)
            button.setFixedSize(30, 25)
            button.setStyleSheet("font-family:'微软雅黑'; font-size:15px;color:white")
            self.buttonList.append(button)
        self.buttonList[0].setStyleSheet("border:0px solid lightgray;background:rgb(210,240,240);color:blue")
        self.buttonList[1].setStyleSheet("border:0px;background:transparent;color:white")
        self.buttonList[2].setStyleSheet("border:0px;background:transparent;color:white")

        #歌手信息页
        artistInfoFrame = QFrame()
        self.artistHeadLabel = QLabel(artistInfoFrame)
        self.artistHeadLabel.setGeometry(0, 0, 90, 90)
        self.artistHeadLabel.setScaledContents(True)
        self.artistName = NewLabel(artistInfoFrame, True)
        self.artistName.setGeometry(0, 90, 90, 30)
        self.artistGender = QLabel("性别：未知", artistInfoFrame)
        self.artistGender.setGeometry(100, 0, 110, 30)
        self.artistBirthday = QLabel("生日：未知", artistInfoFrame)
        self.artistBirthday.setGeometry(210, 0, 140, 30)
        self.artistConstellation = QLabel("星座：未知", artistInfoFrame)
        self.artistConstellation.setGeometry(100, 45, 110, 30)
        self.artistLanguage = QLabel("语言：未知", artistInfoFrame)
        self.artistLanguage.setGeometry(210, 45, 140, 30)
        self.artistBirthplace = QLabel("出生地：未知", artistInfoFrame)
        self.artistBirthplace.setGeometry(100, 90, 210, 30)
        self.artistDetail = MyTextEdit(artistInfoFrame)
        self.artistDetail.setGeometry(0, 120, 352, 300)
        self.artistDetail.setStyleSheet("font-family:微软雅黑;font-size:18px;color:black;")
        
        #刷新歌手信息缓存按键
        self.refreshBtn = QToolButton(artistInfoFrame)
        self.refreshBtn.setFocusPolicy(Qt.NoFocus)
        self.refreshBtn.setIcon(QIcon(IconsHub.Refresh))
        self.refreshBtn.setIconSize(QSize(40, 40))
        self.refreshBtn.setToolTip("刷新歌手信息")
        self.refreshBtn.setStyleSheet("background:transparent;")
        self.refreshBtn.setGeometry(315, 80, 40, 40)
        
#歌词各控件
        self.lyricOperateButton = QPushButton(clicked = self.show_lyric_operate_widget)
        self.lyricOperateButton.setStyleSheet("QPushButton:hover{border:2px solid lightgray;border-color:white;background:rgb(210,240,240)}"
                                                            "QPushButton{border:2px;background:transparent}")
        self.lyricOperateButton.setIcon(QIcon(IconsHub.Settings))
        self.lyricOperateButton.setFocusPolicy(Qt.NoFocus)
        self.lyricOperateButton.setIconSize(QSize(25, 25))
        
        self.desktopLyricButton = QPushButton(clicked = self.show_desktop_lyric)
        self.desktopLyricButton.setFocusPolicy(Qt.NoFocus)
        self.desktopLyricButton.setStyleSheet("QPushButton:hover{border:2px solid lightgray;border-color:white;background:rgb(210,240,240)}"
                                                            "QPushButton{border:2px;background:transparent}")
        self.desktopLyricButton.setIcon(QIcon(IconsHub.DesktopLyric))
        self.desktopLyricButton.setIconSize(QSize(25, 25))

        self.lyricOffsetSButton = QPushButton()
        self.lyricOffsetSButton.setFocusPolicy(Qt.NoFocus)
        self.lyricOffsetSButton.setFixedSize(25, 25)
        self.lyricOffsetSButton.setText('S')
        
        self.lyricOffsetCombo = QComboBox()
        self.lyricOffsetCombo.setFocusPolicy(Qt.NoFocus)
#        self.lyricOffsetCombo.setStyleSheet("font-size:15px;color:blue")
        self.lyricOffsetCombo.setFixedSize(70, 25)
        self.lyricOffsetCombo.insertItem(0, '提前')
        self.lyricOffsetCombo.insertItem(1, '延迟')
        self.lyricOffsetCombo.insertItem(2, '正常')
        self.lyricOffsetCombo.setCurrentIndex(2)
        
        self.lyricOffsetSlider = QSlider(Qt.Horizontal)
        self.lyricOffsetSlider.setFocusPolicy(Qt.NoFocus)
        self.lyricOffsetSlider.setMinimumWidth(130)
        self.lyricOffsetSlider.setPageStep(1)
        self.lyricOffsetSlider.setRange(0, 0)
        
        self.lyricOffsetLabel = QLineEdit("0.0秒")
        self.lyricOffsetLabel.setFixedSize(60, 25)
        self.lyricOffsetLabel.setReadOnly(True)
        
#歌词文本框
        self.lyricText = MyTextEdit()
        self.lyricText.setFixedHeight(420)
        self.document = self.lyricText.document()
        self.lyricText.setAlignment(Qt.AlignHCenter)
        self.lyricText.setStyleSheet("font-family:'微软雅黑';font-size:23px;")
        self.lyricOperateWidget = QWidget()
        self.lyricOperateWidget.setStyleSheet("background:rgb(210,240,240);font-size:15px;color:blue;")
        self.lyricOperateWidget.hide()
        lyricOffsetLayout = QHBoxLayout(self.lyricOperateWidget)
        lyricOffsetLayout.setSpacing(2)
        lyricOffsetLayout.setContentsMargins(0, 0, 0, 0)
        lyricOffsetLayout.addWidget(self.lyricOffsetCombo)
        lyricOffsetLayout.addWidget(self.lyricOffsetSlider)
        lyricOffsetLayout.addWidget(self.lyricOffsetLabel)
        lyricOffsetLayout.addWidget(self.lyricOffsetSButton)
        
        hbox_lyric = QHBoxLayout()
        hbox_lyric.addWidget(self.lyricOperateWidget)
        hbox_lyric.addStretch()
        hbox_lyric.addWidget(self.lyricOperateButton)
        hbox_lyric1 = QHBoxLayout()
        hbox_lyric1.addStretch()
        hbox_lyric1.addWidget(self.desktopLyricButton)
        vbox_lyric = QVBoxLayout(self.lyricText)
        vbox_lyric.addStretch()
        vbox_lyric.addLayout(hbox_lyric1)
        vbox_lyric.addLayout(hbox_lyric)

#堆栈窗口
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.addWidget(self.lyricText)
        self.stackedWidget.addWidget(artistInfoFrame)
        self.stackedWidget.addWidget(self.musicList)

#综合布局
        hbox2 = QHBoxLayout()
        hbox2.setContentsMargins(13, 0, 13, 11)
        hbox2.addWidget(self.timeLabel1)
        hbox2.addSpacing(3)
        hbox2.addWidget(self.seekSlider)
        hbox2.addSpacing(6)
        hbox2.addWidget(self.timeLabel2)
        
        widget1 = QWidget(self)
        hbox3 = QGridLayout()
        hbox3.setContentsMargins(0, 0, 0, 0)
        hbox3.addWidget(self.backButton, 0, 0, 2, 1)
        hbox3.addWidget(self.musicNameLabel, 0, 1, 2, 2)
        hbox3.addItem(spacerItem, 0, 3, 2, 5)
        hbox3.addWidget(self.buttonList[0], 1, 9)
        hbox3.addWidget(self.buttonList[1], 1, 10)
        hbox3.addWidget(self.buttonList[2], 1, 8)
        
        mainLayout = QVBoxLayout(widget1)
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(hbox3)
        mainLayout.addWidget(self.stackedWidget)
        mainLayout.addLayout(hbox2)

        widget1.setGeometry(6, 0, 352, 503)
        self.playmodeButton.setGeometry(0, 507, 60, 60)
        self.previousButton.setGeometry(65, 502, 70, 70)
        self.playButton.setGeometry(140, 497, 80, 80)
        self.nextButton.setGeometry(225, 502, 70, 70)
        self.favoriteButton.setGeometry(300, 507, 60, 60)
    
    def create_connections(self):
        self.desktopLyric.hide_desktop_lyric_signal.connect(self.show_desktop_lyric)
        self.buttonList[0].clicked.connect(self.show_lyric_text)
        self.buttonList[1].clicked.connect(self.show_artist_info)
        self.buttonList[2].clicked.connect(self.show_music_table)
        self.lyricOffsetSButton.clicked.connect(self.lyric_offset_save)
        self.lyricOffsetCombo.currentIndexChanged.connect(self.lyric_offset_type)
        self.lyricOffsetSlider.valueChanged.connect(self.lyric_offset_changed)
        self.refreshBtn.clicked.connect(self.update_infofile_cached)
    
    def set_artist_info(self, artist):
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
        return pixmap
    
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
        
    def set_lyric_offset(self, lyricOffset, lyricDict, lrcPath):
        self.lrcPath = lrcPath
        k = 2
        if lyricOffset > 0:
            k = 0
        elif lyricOffset < 0:
            k = 1
        self.lyricOffsetCombo.setCurrentIndex(k)
        self.lyricOffsetSlider.setValue(abs(lyricOffset)//100)
        self.lyricOffsetLabel.setText('%.1f秒'%(abs(lyricOffset)/1000))
        self.lyricText.clear()
        self.lyricText.setAlignment(Qt.AlignHCenter)
        t = sorted(lyricDict.keys())
        self.set_html(1, lyricDict, t)
    
    def set_html(self, index, lyricDict, t, extraBlocks=10):
        htmlList = ['<body><center>']
        for k in range(extraBlocks):
            htmlList.append("<br></br>")
        for i in range(len(t)):
            if i == index:
                size = self.lyricRunSize
                color = self.lyricRunColor
            else:
                size = self.lyricReadySize
                color = self.lyricReadyColor
            htmlList.append("<p style = 'color:%s;font-size:%spx;'>%s</p>"%(color, size, lyricDict[t[i]]))
        for i in range(6):
            htmlList.append("<br></br>")
        htmlList.append('</body></center>')
        html = ''.join(htmlList)
        self.lyricText.setHtml(html)
        self.jump_to_line(index)
        
    def jump_to_line(self, index):
        block = self.document.findBlockByLineNumber(index)
        #print('%s %i'%(block.text(), block.blockNumber()))
        lines =  (block.layout().lineCount() - 1) / 2
        pos = block.position()
        cur = self.lyricText.textCursor()
        cur.setPosition(pos, QTextCursor.MoveAnchor)
#        cur.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.lyricText.setTextCursor(cur)
        vscrollbar = self.lyricText.verticalScrollBar()
#        print('scrollbar %i'%vscrollbar.value())
        vscrollbar.setValue(vscrollbar.value() + 49 * (4 + lines))
    
    def no_matched_lyric(self):
        self.lyricText.clear()
        self.lyricText.setHtml(self.get_lyric_style_text('搜索不到匹配的歌词！'))
        self.lyricText.setAlignment(Qt.AlignHCenter)        
    
    def url_error_lyric(self):
        self.lyricText.clear()
        self.lyricText.setHtml(self.get_lyric_style_text('网络连接错误！'))
        self.lyricText.setAlignment(Qt.AlignHCenter)
    
    def get_lyric_style_text(self, text):
        return "<p style = 'color:white;font-size:20px;'><br><br><br><br><br><br><br>%s</p>"%text
            
    def lyric_offset_type(self, index):
        self.lyricOffset = 0
        self.lyricOffsetSlider.setValue(0)
        self.lyricOffsetLabel.setText('0.0秒')
        if index == 0 or index == 1:
            self.lyricOffsetSlider.setRange(0, 200)        
        else:
            self.lyricOffsetSlider.setRange(0, 0)
        self.lyric_offset_changed_signal.emit(0)
    
    def lyric_offset_changed(self, value):
        if self.lyricOffsetCombo.currentIndex() == 0:
            self.lyricOffset = value*100
        elif self.lyricOffsetCombo.currentIndex() == 1:
            self.lyricOffset = - value*100
        self.lyricOffsetLabel.setText('%.1f秒'%(value/10))
        self.lyric_offset_changed_signal.emit(self.lyricOffset)
    
    def lyric_offset_save(self):
        change_lyric_offset_in_file(self.lrcPath, self.lyricOffset)
    
    def show_lyric_text(self):
        self.stacked_widget_change_index(0)
    
    def show_artist_info(self):
        self.stacked_widget_change_index(1)
    
    def show_music_table(self):
        self.stacked_widget_change_index(2)
        self.select_current_row_signal.emit()
    
    def stacked_widget_change_index(self, givenIndex):
        if self.stackedWidget.currentIndex() != givenIndex:
            oldIndex = self.stackedWidget.currentIndex()
            self.change_button_stylesheet(oldIndex,  givenIndex)
            self.stackedWidget.setCurrentIndex(givenIndex)
    
    def change_button_stylesheet(self,  from_,  to_):
        self.buttonList[from_].setStyleSheet("border:0px;background:transparent;color:white")
        self.buttonList[to_].setStyleSheet("border:0px solid lightgray;background:rgb(210,240,240);color:blue")
    
    def show_lyric_operate_widget(self):
        if self.lyricOperateWidget.isHidden():
            self.lyricOperateWidget.show()
        else:
            self.lyricOperateWidget.hide()
    
    def ui_initial(self):
        self.musicNameLabel.setText("XYPLAYER")
        self.artistHeadLabel.setPixmap(QPixmap(IconsHub.HeadIcon))
        self.artistName.setText("Zheng-Yejian")
        self.artistBirthday.setText("生日：1992.10.18")
        self.artistBirthplace.setText("出生地：福建")
        self.artistLanguage.setText("语言：国语")
        self.artistGender.setText("性别：男")
        self.artistConstellation.setText("星座：天秤座")
        self.artistDetail.setHtml(self.get_artist_detail_style_text('大家好，我是作者！！！'))
        authorInfo = ("<p style='color:white;font-size:20px;'>作者：Zheng-Yejian"
                            "<br /><br />"
                            "邮箱： 1035766515@qq.com"
                            "<br /><br />"
                            "声明：Use of this source code is governed by GPLv3 license that can be found in the LICENSE file. "
                            "<br /><br />"
                            "版本: v%s "
                            "<br /><br />"
                            "简介: This is a simple musicplayer that can search, play, download musics from the Internet.</p>"%app_version)
        self.lyricText.clear()
        self.musicList.clear_list()
        self.lyricText.setHtml(authorInfo)
        cur = self.lyricText.textCursor()
        cur.setPosition(0, QTextCursor.MoveAnchor)
        self.lyricText.setTextCursor(cur)
        self.seekSlider.setRange(0, 0)
        self.favoriteButton.setIcon(QIcon(IconsHub.Favorites))
        self.favoriteButton.setToolTip('收藏')
    
    def get_artist_detail_style_text(self, text):
        return "<p style='color:white;font-size:16px;'>%s</p>"%text
        
    def show_desktop_lyric(self):
        if self.desktopLyric.isHidden():
            beToOff = True
            self.desktopLyric.show()
            self.desktopLyric.original_place()
        else:
            beToOff = False
            self.desktopLyric.hide()  
        self.desktop_lyric_state_changed_signal.emit(beToOff)
    
    def change_playmode(self):
        oldPlaymode = self.playmode
        if self.playmode == Configures.PlaymodeRandom:
            self.set_new_playmode(Configures.PlaymodeOrder)
        elif self.playmode == Configures.PlaymodeOrder:
            self.set_new_playmode(Configures.PlaymodeSingle)
        elif self.playmode == Configures.PlaymodeSingle:
            self.set_new_playmode(Configures.PlaymodeRandom)
        self.playmode_changed_signal.emit(oldPlaymode, self.playmode)

    def set_new_playmode(self, playmode):
        self.playmode = playmode
        if playmode == Configures.PlaymodeRandom:
            iconPath = IconsHub.PlaymodeRandom
            toolTip = Configures.PlaymodeRandomText
        elif playmode == Configures.PlaymodeOrder:
            iconPath = IconsHub.PlaymodeOrder
            toolTip = Configures.PlaymodeOrderText
        else:
            iconPath = IconsHub.PlaymodeSingle
            toolTip = Configures.PlaymodeSingleText
        self.playmodeButton.setIcon(QIcon(iconPath))
        self.playmodeButton.setToolTip(toolTip)
            
    def set_new_window_lyric_style(self, params):
        self.lyricRunSize, self.lyricRunColor, self.lyricReadySize, self.lyricReadyColor = params
            
            
            

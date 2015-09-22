import json, re
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from xyplayer.urldispose import SearchOnline
from xyplayer.mytables import NewMusicTable
from xyplayer.mywidgets import NewLabel, MyTextEdit
from xyplayer.mypages import desktop_lyric
from xyplayer import __version__

class PlaybackPage(QWidget):
    lyric_offset_changed_signal = pyqtSignal(int)
    desktop_lyric_state_changed_signal = pyqtSignal(bool)
    def __init__(self):
        super(PlaybackPage, self).__init__()
        self.setup_ui()
        self.create_connections()
    
    def setup_ui(self):
        self.setStyleSheet(
            "QStackedWidget,QTextEdit,QTableView,QTableWidget{background:transparent}"
            "QPushButton:hover{border:2px solid lightgray;border-color:white;background:transparent}"
            "QPushButton{border-color:green;background:transparent}")

#桌面歌词标签
        self.desktopLyric = desktop_lyric.DesktopLyric()
        
#歌单
        self.musicTable = NewMusicTable()
        self.musicTable.setFixedHeight(425)
        
#spacerItem
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
#五个基本按键
        self.playmodeButton = QToolButton()
        self.playmodeButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:4px solid yellow;border-radius:17px;background:yellow}")
#        self.playmodeButton.setFixedSize(QSize(36, 36))
        self.playmodeButton.setIcon(QIcon(":/iconSources/icons/playmode1.png"))
        self.playmodeButton.setIconSize(QSize(28, 28))
        
        self.favoriteButton = QToolButton()
        self.favoriteButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:4px solid yellow;border-radius:17px;background:yellow}")
#        self.favoriteButton.setFixedSize(QSize(36, 36))
        self.favoriteButton.setIcon(QIcon(":/iconSources/icons/favorite.png"))
        self.favoriteButton.setIconSize(QSize(25, 25))
#        self.favoriteButton.setEnabled(False)

        self.previousButton = QToolButton()
        self.previousButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:4px solid yellow;border-radius:25px;background:yellow}")
        self.previousButton.setIconSize(QSize(45, 45))
        self.previousButton.setShortcut(QKeySequence("Ctrl + Left"))

        self.playButton = QToolButton()
        self.playButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:4px solid yellow;border-radius:33px;background:yellow}")
#        self.playButton.setIcon(QIcon(":/iconSources/icons/play.png"))
        self.playButton.setIconSize(QSize(64, 64))
        self.playButton.setShortcut(QKeySequence("Ctrl + Down"))

        self.nextButton = QToolButton()
        self.nextButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:4px solid yellow;border-radius:25px;background:yellow}")
        self.nextButton.setIconSize(QSize(45, 45))
        self.nextButton.setShortcut(QKeySequence("Ctrl + Right"))
        
        self.seekSlider = QSlider(Qt.Horizontal)
        self.seekSlider.setRange(0, 0)
        
#时间标签
        self.timeLabel1 = QLabel("00:00")
        self.timeLabel2 = QLabel("00:00")
        
        self.timeLabel1.setAlignment(Qt.AlignLeft and Qt.AlignVCenter)
        self.timeLabel2.setAlignment(Qt.AlignRight and Qt.AlignVCenter)
        
        self.timeLabel1.setFixedSize(QSize(40, 25))
        self.timeLabel2.setFixedSize(QSize(40, 25))
        
        self.timeLabel1.setStyleSheet("font-family:'微软雅黑';font-size:13px;color: white")
        self.timeLabel2.setStyleSheet("font-family:'微软雅黑';font-size:13px;color: white")
        
#歌曲信息按键
        self.backButton = QPushButton()
        self.backButton.setIcon(QIcon(":/iconSources/icons/back.png"))
        self.backButton.setFixedSize(35, 30)
        self.backButton.setIconSize(QSize(25, 25))
        self.backButton.setStyleSheet("QPushButton:hover{background:rgb(210,240,240)}")
        
        self.musicNameLabel = NewLabel()
        self.musicNameLabel.setMinimumWidth(230)
        self.musicNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:28px;color: white")
#        self.musicNameLabel.setParameters(300, 50, 100)
        
        self.buttonList = []
        for text in ["歌词", "歌手", "歌单"]:
            button = QPushButton(text)
            button.setFixedSize(30, 25)
            button.setStyleSheet("font-family:'微软雅黑'; font-size:15px;color:white")
            self.buttonList.append(button)
        self.buttonList[0].setStyleSheet("border:0px solid lightgray;background:rgb(210,240,240);color:blue")

#歌手信息
        self.artistHeadLabel = QLabel()
        self.artistHeadLabel.setFixedSize(85, 85)
        self.artistHeadLabel.setScaledContents(True)
        self.artistName = QLabel("歌手：未知")
        self.artistName.setFixedHeight(35)
        self.artistBirthday = QLabel("生日：未知")
        self.artistBirthday.setFixedHeight(35)
        self.artistBirthplace = QLabel("出生地：未知")
        self.artistBirthplace.setFixedHeight(35)
        self.artistLanguage = QLabel("语言：未知")
        self.artistLanguage.setFixedHeight(35)
        self.artistGender = QLabel("性别：未知")
        self.artistGender.setFixedHeight(35)
        self.artistConstellation = QLabel("星座：未知")
        self.artistConstellation.setFixedHeight(35)
        self.artistDetail = MyTextEdit()
        self.artistDetail.setFixedWidth(360)
        self.artistDetail.setStyleSheet("font-family:微软雅黑;font-size:18px;color:black;")
        
        artistInfoFrame = QFrame()
        artistInfoFrame.setStyleSheet("font-family:'微软雅黑';font-size:14px;")
        artistInfoLayout = QGridLayout(artistInfoFrame)
        artistInfoLayout.setSpacing(4)
        artistInfoLayout.setRowMinimumHeight(0, 45)
        artistInfoLayout.setColumnMinimumWidth(0, 105)
        artistInfoLayout.setSpacing(2)
        artistInfoLayout.setMargin(0)
        artistInfoLayout.addWidget(self.artistHeadLabel, 0, 0, 2, 1)
        artistInfoLayout.addWidget(self.artistGender, 0, 1)
        artistInfoLayout.addWidget(self.artistBirthday, 0, 2)
        artistInfoLayout.addWidget(self.artistConstellation, 1, 1)
        artistInfoLayout.addWidget(self.artistLanguage, 1, 2)
        artistInfoLayout.addWidget(self.artistName, 2, 0)
        artistInfoLayout.addWidget(self.artistBirthplace, 2, 1, 1, 2)
        artistInfoLayout.addWidget(self.artistDetail, 3, 0, 3, 3)
        
#歌词各控件
        self.lyricOperateButton = QPushButton(clicked = self.show_lyric_operate_widget)
        self.lyricOperateButton.setStyleSheet("QPushButton:hover{background:rgb(210,240,240)}")
        self.lyricOperateButton.setIcon(QIcon(":/iconSources/icons/setting.png"))
        self.lyricOperateButton.setIconSize(QSize(25, 25))
        
        self.desktopLyricButton = QPushButton(clicked = self.show_desktop_lyric)
        self.desktopLyricButton.setStyleSheet("QPushButton:hover{background:rgb(210,240,240)}")
        self.desktopLyricButton.setIcon(QIcon(":/iconSources/icons/desktopLyric.png"))
        self.desktopLyricButton.setIconSize(QSize(25, 25))

        self.lyricOffsetSButton = QPushButton()
        self.lyricOffsetSButton.setFixedSize(25, 25)
        self.lyricOffsetSButton.setText('S')
        
        self.lyricOffsetCombo = QComboBox()
#        self.lyricOffsetCombo.setStyleSheet("font-size:15px;color:blue")
        self.lyricOffsetCombo.setFixedSize(70, 25)
        self.lyricOffsetCombo.insertItem(0, '提前')
        self.lyricOffsetCombo.insertItem(1, '延迟')
        self.lyricOffsetCombo.insertItem(2, '正常')
        self.lyricOffsetCombo.setCurrentIndex(2)
        
        self.lyricOffsetSlider = QSlider(Qt.Horizontal)
        self.lyricOffsetSlider.setMinimumWidth(130)
        self.lyricOffsetSlider.setPageStep(1)
        self.lyricOffsetSlider.setRange(0, 0)
        
        self.lyricOffsetLabel = QLineEdit("0.0秒")
        self.lyricOffsetLabel.setFixedSize(60, 25)
        self.lyricOffsetLabel.setReadOnly(True)

#歌词颜色
        label_t = QLabel("桌面歌词颜色")
        label_t.setFixedWidth(90)
        label_r = QLabel("r")
        label_g = QLabel("g")
        label_b = QLabel("b")
        self.colorSpins = []
        for i in range(3):
            spinBox = QSpinBox()
            spinBox.setRange(0, 255)
            if i == 0:
                spinBox.setValue(20)
            elif i == 1:
                spinBox.setValue(190)
            else:
                spinBox.setValue(240)
            spinBox.valueChanged.connect(self.desktop_lyric_color_changed)
            self.colorSpins.append(spinBox)
        
        self.dtcWidget = QWidget()
        self.dtcWidget.hide()
        self.dtcWidget.setFixedHeight(50)
        self.dtcWidget.setStyleSheet("font-size:12px;background:rgb(210,230,230);")
        hbox_dtc = QHBoxLayout(self.dtcWidget)
        hbox_dtc.addWidget(label_t)
        hbox_dtc.addSpacing(10)
        hbox_dtc.addWidget(label_r)
        hbox_dtc.addWidget(self.colorSpins[0])
        hbox_dtc.addWidget(label_g)
        hbox_dtc.addWidget(self.colorSpins[1])
        hbox_dtc.addWidget(label_b)
        hbox_dtc.addWidget(self.colorSpins[2])
        
        

#歌词文本框
#        self.lyricText = QTextEdit()
##        self.lyricText.setLineWrapMode(QTextEdit.FixedPixelWidth)
##        self.lyricText.setLineWrapColumnOrWidth(358)
#        self.lyricText.setContextMenuPolicy(Qt.NoContextMenu)
        self.lyricText = MyTextEdit()
        self.lyricText.setFixedSize(360, 427)
        self.document = self.lyricText.document()
        self.lyricText.setAlignment(Qt.AlignHCenter)
        self.lyricText.setStyleSheet("font-family:'微软雅黑';font-size:23px;color:black;")
        
        self.lyricOperateWidget = QWidget()
        self.lyricOperateWidget.setStyleSheet("background:rgb(210,240,240);font-size:15px;color:blue;")
        self.lyricOperateWidget.hide()
        lyricOffsetLayout = QHBoxLayout(self.lyricOperateWidget)
        lyricOffsetLayout.setSpacing(2)
        lyricOffsetLayout.setMargin(0)
        lyricOffsetLayout.addWidget(self.lyricOffsetCombo)
        lyricOffsetLayout.addWidget(self.lyricOffsetSlider)
        lyricOffsetLayout.addWidget(self.lyricOffsetLabel)
        lyricOffsetLayout.addWidget(self.lyricOffsetSButton)
        
        hbox_lyric = QHBoxLayout()
        hbox_lyric.addWidget(self.lyricOperateWidget)
        hbox_lyric.addStretch()
        hbox_lyric.addWidget(self.lyricOperateButton)
        hbox_lyric1 = QHBoxLayout()
        hbox_lyric1.addWidget(self.dtcWidget)
        hbox_lyric1.addStretch()
        hbox_lyric1.addWidget(self.desktopLyricButton)
        vbox_lyric = QVBoxLayout(self.lyricText)
        vbox_lyric.addStretch()
        vbox_lyric.addLayout(hbox_lyric1)
        vbox_lyric.addLayout(hbox_lyric)

#堆栈窗口
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.lyricText)
        self.stackedWidget.addWidget(artistInfoFrame)
        self.stackedWidget.addWidget(self.musicTable)

#综合布局
        controlWidget = QWidget()
        controlWidget.setFixedSize(360, 70)
        hbox1 = QHBoxLayout(controlWidget)
        hbox1.setMargin(0)
        hbox1.addWidget(self.playmodeButton)
        hbox1.addWidget(self.previousButton)
        hbox1.addWidget(self.playButton)
        hbox1.addWidget(self.nextButton)
        hbox1.addWidget(self.favoriteButton)
        
        hbox2 = QHBoxLayout()
        hbox2.setMargin(13)
        hbox2.addWidget(self.timeLabel1)
        hbox2.addWidget(self.seekSlider)
        hbox2.addWidget(self.timeLabel2)
        
        hbox3 = QGridLayout()
        hbox3.addWidget(self.backButton, 0, 0, 2, 1)
        hbox3.addWidget(self.musicNameLabel, 0, 1, 2, 2)
        hbox3.addItem(spacerItem, 0, 3, 2, 5)
        hbox3.addWidget(self.buttonList[0], 1, 9)
        hbox3.addWidget(self.buttonList[1], 1, 10)
        hbox3.addWidget(self.buttonList[2], 1, 8)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.setMargin(2)
        mainLayout.addLayout(hbox3)
        mainLayout.addWidget(self.stackedWidget)
        mainLayout.addLayout(hbox2)
#        mainLayout.addLayout(hbox1)
        mainLayout.addWidget(controlWidget)
    
    def create_connections(self):
        self.desktopLyric.hide_desktop_lyric_signal.connect(self.show_desktop_lyric)
        self.buttonList[0].clicked.connect(self.show_lyric_text)
        self.buttonList[1].clicked.connect(self.show_artist_info)
        self.buttonList[2].clicked.connect(self.show_music_table)
        self.lyricOffsetSButton.clicked.connect(self.lyric_offset_save)
        self.lyricOffsetCombo.currentIndexChanged.connect(self.lyric_offset_type)
        self.lyricOffsetSlider.valueChanged.connect(self.lyric_offset_changed)
    
    def desktop_lyric_color_changed(self, value):
        self.desktopLyric.set_color(self.colorSpins[0].value(), self.colorSpins[1].value(), self.colorSpins[2].value())
    
    def update_artist_info(self, title):
        try:
            try:
                artist = title.split('._.')[0].strip()
                title.split('._.')[1].strip()
            except:
                artist = '未知'
            infoPath = SearchOnline.get_artist_info_path(artist)
            if infoPath:
                with open(infoPath, 'r+') as f:
                    info = f.read()
                infoList = json.loads(info)
                name = infoList['name']
                birthday = infoList['birthday']
                if not birthday:
                    birthday = '不是今天'
                birthplace = infoList['birthplace']
                if not birthplace:
                    birthplace = '地球'
#                country = infoList['country']
#                if not country:
#                    country = '全球'
                language = infoList['language']
                if not language:
                    language = '地球语'
                gender = infoList['gender']
                if not gender:
                    gender = '男/女'
                constellation = infoList['constellation']
                if not constellation:
                    constellation = '神马座'
                info = infoList['info']
                infos = info.split('<br>')
                self.artistName.setText('歌手：' + name)
                self.artistBirthday.setText('生日：' + birthday)
                self.artistBirthplace.setText('出生地：' + birthplace)
#                self.artistCountry.setText('国籍：' + country)
                self.artistLanguage.setText('语言：' + language)
                self.artistGender.setText('性别：' + gender)
                self.artistConstellation.setText('星座：' + constellation)
                self.artistDetail.clear()
                if infos:
                    for line in infos:
                        self.artistDetail.append(line)
                else:
                    self.artistDetail.setText("未找到歌手的详细信息")
                cur = self.artistDetail.textCursor()
                cur.setPosition(0, QTextCursor.MoveAnchor)
                self.artistDetail.setTextCursor(cur)
            else:
                self.artistName.setText('歌手：' + aritist)
                self.artistBirthday.setText('生日：' + '不是今天')
                self.artistBirthplace.setText('出生地：' + '地球')
#                self.artistCountry.setText('国籍：' + country)
                self.artistLanguage.setText('语言：' + '地球语')
                self.artistGender.setText('性别：' + '男/女')
                self.artistConstellation.setText('星座：' + '神马座')
                self.artistDetail.clear()
                self.artistDetail.setText("未找到歌手的详细信息")
                self.artistDetail.setAlignment(Qt.AlignHCenter)
            imagePath = SearchOnline.get_artist_image_path(artist)
            if imagePath:
                pixmap = QPixmap(imagePath)
            else:
                pixmap = QPixmap(":/iconSources/icons/anonymous.png")
        except:
            pixmap = QPixmap(":/iconSources/icons/anonymous.png")
        self.artistHeadLabel.setPixmap(pixmap)
        return pixmap
    
    def set_lyric_offset(self, lyricOffset, lyricDict, lrcPath):
        self.lrcPath = lrcPath
        if lyricOffset < 0:
            k = 0
            self.lyricOffsetSlider.setRange(0, 50)
        elif lyricOffset > 0:
            k = 1
            self.lyricOffsetSlider.setRange(0, 50)
        else:
            k = 2
            self.lyricOffsetSlider.setRange(0, 0)
        self.lyricOffsetIndex = k
        self.lyricOffsetCombo.setCurrentIndex(k)
        self.lyricOffsetSlider.setValue(abs(lyricOffset)//100)
        self.lyricOffsetLabel.setText('%s秒'%round(abs(lyricOffset)/1000, 1))
        self.lyricText.clear()
        self.lyricText.setAlignment(Qt.AlignHCenter)
        t = sorted(lyricDict.keys())
        self.set_html(1, lyricDict, t)
#        cur = self.lyricText.textCursor()
#        cur.setPosition(0, QTextCursor.MoveAnchor)
#        self.lyricText.setTextCursor(cur)
        self.lyricOffset = lyricOffset
        self.lyric_offset_changed_signal.emit(self.lyricOffset)
    
#    def fill_lyricText(self, lyricDict):
#        for k in range(7):
#            if k == 4:
#                self.lyricText.append("欢迎使用xyplayer！")
#                continue
#            self.lyricText.append(' ')
#        print("playback_page fill_lyricText %s %s"%(self.lyricText.width(), self.lyricText.height()))
#        
#        for k in sorted(lyricDict.keys()):
#            line = lyricDict[k]
#            self.lyricText.append(line)  
    
    def set_html(self, index, lyricDict, t):
        htmlList = ['<body><center>']
        for k in range(7):
#            if k == 5:
#                htmlList.append("<p style = 'color:green;font-size:25px;'>欢迎使用xyplayer！</p>")
#            else:
            htmlList.append("<br></br>")
        for i in range(len(t)):
            if i == index:
                size = '36'
                color = 'yellow'
            else:
                size = '23'
                color = 'black'
            htmlList.append("<p style = 'color:%s;font-size:%spx;'>%s</p>"%(color, size, lyricDict[t[i]]))
        for i in range(3):
            htmlList.append("<br></br>")
        htmlList.append('</body></center>')
        html = "".join(htmlList)
        self.lyricText.setHtml(html)
#        print('blockcount %i'%self.playbackPage.document.textWidth())
        self.jump_to_line(index)
        
    def jump_to_line(self, index):
        block = self.document.findBlockByLineNumber(index)
        print('%s %i'%(block.text(), block.blockNumber()))
        lines =  (block.layout().lineCount() - 1) / 2
        pos = block.position()
        cur = self.lyricText.textCursor()
        cur.setPosition(pos, QTextCursor.MoveAnchor)
#        cur.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.lyricText.setTextCursor(cur)
        vscrollbar = self.lyricText.verticalScrollBar()
#        print('scrollbar %i'%vscrollbar.value())
        vscrollbar.setValue(vscrollbar.value() + 48 * (4 + lines))
    
    def no_matched_lyric(self):
        self.lyricText.clear()
        self.lyricText.setAlignment(Qt.AlignHCenter)
        for k in range(7):
            if k == 3:
                self.lyricText.append('搜索不到匹配的歌词！')
            else:
                self.lyricText.append(' ')
        
    
    def url_error_lyric(self):
        self.lyricText.clear()
        self.lyricText.setAlignment(Qt.AlignHCenter)
        for k in range(7):
            if k == 3:
                self.lyricText.append('网络连接错误！')
            else:
                self.lyricText.append(' ')
        
            
    def lyric_offset_type(self, index):
        self.lyricOffsetIndex = index
        self.lyricOffset = 0
        self.lyricOffsetSlider.setValue(0)
        self.lyricOffsetLabel.setText('0.0秒')
        if index == 0 or index == 1:
            self.lyricOffsetSlider.setRange(0, 200)        
        else:
            self.lyricOffsetSlider.setRange(0, 0)
        self.lyric_offset_changed_signal.emit(0)
    
    def lyric_offset_changed(self, value):
        if self.lyricOffsetIndex == 0:
            self.lyricOffset = (0 - value*100)
        elif self.lyricOffsetIndex == 1:
            self.lyricOffset = value*100
        self.lyricOffsetLabel.setText('%s秒'%(value/10))
        self.lyric_offset_changed_signal.emit(self.lyricOffset)
    
    def lyric_offset_save(self):
        with open(self.lrcPath, 'r') as f:
           originalText = f.read() 
        m = re.search('offset\=',originalText,re.MULTILINE)
        if m:
            pos = m.end()
            lyricOffsetTemp = int(originalText[pos:])
            print('Player.py lyric_offset_save %s'%lyricOffsetTemp)
            if lyricOffsetTemp!= self.lyricOffset:
                newText = originalText[:pos] + '%s'%self.lyricOffset
                with open(self.lrcPath, 'w+') as f:
                    f.write(newText)
        else:
            with open(self.lrcPath, 'a+') as f:
                f.write('\noffset=%s'%self.lyricOffset)
        self.lyricOffsetSButton.setFocus()
    
    def show_lyric_text(self):
        self.stackedWidget.setCurrentIndex(0)
        for i in range(3):
            if i != 0: 
                self.buttonList[i].setStyleSheet("border-color:white;background:transparent;color:white")
            else:
                self.buttonList[i].setStyleSheet("border:0px solid lightgray;background:rgb(210,240,240);color:blue")
    
    def show_artist_info(self):
        self.stackedWidget.setCurrentIndex(1)
        for i in range(3):
            if i != 1: 
                self.buttonList[i].setStyleSheet("border-color:white;background:transparent;color:white")
            else:
                self.buttonList[i].setStyleSheet("border:0px solid lightgray;background:rgb(210,240,240);color:blue")
    
    def show_music_table(self):
        self.stackedWidget.setCurrentIndex(2)
        for i in range(3):
            if i != 2: 
                self.buttonList[i].setStyleSheet("border-color:white;background:transparent;color:white")
            else:
                self.buttonList[i].setStyleSheet("border:0px solid lightgray;background:rgb(210,240,240);color:blue")
                
    def show_lyric_operate_widget(self):
        if self.lyricOperateWidget.isHidden():
            self.lyricOperateWidget.show()
            self.dtcWidget.show()
            
        else:
            self.lyricOperateWidget.hide()
            self.dtcWidget.hide()
    
    def ui_initial(self):
        self.musicNameLabel.setText("未知")
        self.artistHeadLabel.setPixmap(QPixmap(":/iconSources/icons/anonymous.png"))
        self.artistName.setText("歌手：Zheng-Yejian")
        self.artistBirthday.setText("生日：1992.10.18")
        self.artistBirthplace.setText("出生地：福建")
        self.artistLanguage.setText("语言：国语")
        self.artistGender.setText("性别：男")
        self.artistConstellation.setText("星座：天秤座")
        self.artistDetail.setText("大家好，我是作者！！！")
        textsList = ["作者：Zheng-Yejian",
                            " ",
                            "电联： <1035766515@qq.com>",
                            " ",
                            "声明：Use of this source code is governed by GPLv3 license that can be found in the LICENSE file. ",
                            " ", 
                            "版本: %s "%__version__,
                            " ", 
                            "简介: This is a simple musicplayer that can search, play, download musics from the Internet."]
        self.lyricText.clear()
        for line in textsList:
            self.lyricText.append(line)
        cur = self.lyricText.textCursor()
        cur.setPosition(0, QTextCursor.MoveAnchor)
        self.lyricText.setTextCursor(cur)
        self.seekSlider.setRange(0, 0)
        self.favoriteButton.setIcon(QIcon(":/iconSources/icons/favorite.png"))
        
    def show_desktop_lyric(self):
        if self.desktopLyric.isHidden():
            beToOff = True
#            self.desktopLyricButton.setToolTip('关闭桌面歌词')
            self.desktopLyric.show()
            self.desktopLyric.original_place()
        else:
            beToOff = False
            self.desktopLyric.hide()
#            self.desktopLyricButton.setToolTip('开启桌面歌词')        
        self.desktop_lyric_state_changed_signal.emit(beToOff)
        

import threading
from PyQt4.QtGui import (QMessageBox, QDialog, QIcon, QCursor,QPixmap, QStackedWidget, QSystemTrayIcon, 
                                          QHBoxLayout, QLabel, QVBoxLayout, QFrame, QMenu, QPushButton, QAction)
from PyQt4.QtCore import Qt, QEvent, QPoint, QSize
from PyQt4.phonon import Phonon
from xyplayer.mypages import manage_page, playback_page, setting_frame
from xyplayer.mytables import SqlOperate, TableModel, TableView
from xyplayer.configure import Configures
from xyplayer.mywidgets import PushButton, NewListWidget

import xyplayer.allIcons_rc

class PlayerUi(QDialog):
    def __init__(self, parent = None):
        super(PlayerUi, self).__init__(parent)
        self.sql = SqlOperate()
        Configures().check_dirs()
        self.initial_phonon()
        self.create_actions()
        self.setup_ui()
        self.initial_parameters()
        
    def initial_phonon(self):
        self.mediaObject = Phonon.MediaObject(self)
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        Phonon.createPath(self.mediaObject, self.audioOutput)
        self.mediaObject.setTickInterval(500)     
        self.volume = self.audioOutput.volume()/2
        self.audioOutput.setVolume(self.volume)
    
    def initial_parameters(self):
        self.widgets = []
        self.widgetIndex = 0
        self.dragPosition = QPoint(0, 0)
        self.lyricOffset = 0
        self.playmodeIndex = 2
        self.currentSourceRow = -1
        self.totalTime = '00:00'
        self.cTime = '00:00'
        self.playTable =  "默认列表"
        self.currentTable = "默认列表"
        self.noError = 1
        self.allPlaySongs = []
        self.files = []
        self.toPlaySongs = []
        self.lyricDict = {}
#        self.info = ''
        self.j = -5
        self.deleteLocalfilePermit = False
        try:
            with open(Configures.settingFile, 'r') as f:
                self.downloadDir = f.read()
        except:
            self.downloadDir = Configures.musicsDir
        
        self.model.initial_model("喜欢歌曲")
        self.lovedSongs = []  
        for i in range(0, self.model.rowCount()):
            self.lovedSongs.append(self.model.record(i).value("title"))     
            print(self.lovedSongs[i])
        
        self.model.initial_model("默认列表")
        self.musicTable.initial_view(self.model)
        for i in range(0, self.model.rowCount()):
            self.allPlaySongs.append(self.model.record(i).value("paths"))  
            title = self.model.record(i).value("title")
            self.playback_musictable_add_widget(title)
    
    def playback_musictable_add_widget(self, title):
        widget = NewListWidget(title)
        self.widgets.append(widget)
        widget.play_button_clicked_signal.connect(self.playback_page_to_listen)
        widget.info_button_clicked_signal.connect(self.playback_page_music_info)
        self.playbackPage.musicTable.add_widget(widget)
            
    def setup_ui(self):        
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon(":/iconSources/icons/musicface.png"))
        self.setObjectName('xyplayer')
        self.setStyleSheet("#xyplayer{border-image: url(:/iconSources/icons/player_background.png);background:transparent}")
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
#        self.setWindowFlags(Qt.WindowMinhideButtonsHint)
#        self.setWindowFlags(Qt.WindowStaysOnTopHint)
#        self.setAttribute(Qt.WA_TranslucentBackground)
#        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setFixedWidth(370)
        self.setAttribute(Qt.WA_QuitOnClose,True)
        
#        desktop = QApplication.desktop()
#        screenRec = desktop.screenGeometry()
#        desktopWidth = screenRec.width()
#        self.setGeometry((self.playbackPage.desktopLyric.desktopWidth - 370)//2, 40, 370, 660)       
#        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

#title_widgets
        self.titleIconLabel = QLabel()
        pixmap = QPixmap(":/iconSources/icons/xy_logo_little.png")
        self.titleIconLabel.setFixedSize(15, 15)
        self.titleIconLabel.setScaledContents(True)
        self.titleIconLabel.setPixmap(pixmap)
        self.titleLabel = QLabel("xyplayer")
        self.titleLabel.setStyleSheet("font-family:'微软雅黑';font-size:13px;color: white")
        self.minButton = PushButton()
        self.hideButton = PushButton()
        self.closeButton = PushButton()
        self.minButton.loadPixmap(":/iconSources/icons/min_button.png")
        self.hideButton.loadPixmap(":/iconSources/icons/hide_button.png")
        self.closeButton.loadPixmap(":/iconSources/icons/close_button.png")
        self.hideButton.clicked.connect(self.show_mainwindow)
        self.minButton.clicked.connect(self.show_minimized)
        self.closeButton.clicked.connect(self.close)

#播放页面
        self.playbackPage = playback_page.PlaybackPage()
        self.playbackPage.previousButton.setDefaultAction(self.previousAction)
        self.playbackPage.playButton.setDefaultAction(self.playAction)
        self.playbackPage.nextButton.setDefaultAction(self.nextAction)
        self.setGeometry((self.playbackPage.desktopLyric.desktopWidth - 370)//2, 40, 370, 660)
        
#管理页面
        self.managePage = manage_page.ManagePage()
        self.managePage.playButton.setDefaultAction(self.playAction)
        self.managePage.nextButton.setDefaultAction(self.nextAction)

#设置菜单页面
        self.settingFrame = setting_frame.SettingFrame()
        self.settingFrame.volumeSlider.setAudioOutput(self.audioOutput)
#        self.audioOutput.setVolume(0)

##spacerItem
#        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

#3个主按键
        self.globalBackButton = QPushButton(clicked = self.global_back)
        self.globalHomeButton = QPushButton(clicked = self.global_home)
        self.globalSettingButton = QPushButton(clicked = self.show_global_setting_frame)
        self.globalBackButton.setIcon(QIcon(":/iconSources/icons/global_back.png"))
        self.globalHomeButton.setIcon(QIcon(":/iconSources/icons/showMainWindow.png"))
        self.globalSettingButton.setIcon(QIcon(":/iconSources/icons/preference.png"))
        self.globalBackButton.setFixedHeight(30)
        self.globalBackButton.setIconSize(QSize(25, 25))
        self.globalHomeButton.setFixedHeight(30)
        self.globalHomeButton.setIconSize(QSize(25, 25))
        self.globalSettingButton.setFixedHeight(30)
        self.globalSettingButton.setIconSize(QSize(25, 25))

#管理列表的model
        self.model = TableModel()      
        self.model.initial_model("默认列表")
        
        self.musicTable = TableView()
        self.musicTable.initial_view(self.model)

#综合布局 
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(self.titleIconLabel)
        titleLayout.addSpacing(3)
        titleLayout.addWidget(self.titleLabel)
#        titleLayout.addStretch()
        titleLayout.addWidget(self.hideButton)
        titleLayout.addWidget(self.minButton)
        titleLayout.addWidget(self.closeButton)
        
        self.globalFrame = QFrame()
        self.globalFrame.setStyleSheet("QPushButton{border:2px solid lightgray;border-radius:10px;}")
        hbox4 = QHBoxLayout(self.globalFrame)
#        hbox4.setMargin(2)
        hbox4.addWidget(self.globalBackButton)
        hbox4.addWidget(self.globalHomeButton)
        hbox4.addWidget(self.globalSettingButton)

#主堆栈框
        self.mainStack = QStackedWidget()
        self.mainStack.addWidget(self.managePage)
        self.mainStack.addWidget(self.playbackPage)
        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(titleLayout)
        mainLayout.setSpacing(0)
        mainLayout.setMargin(3)
        mainLayout.addWidget(self.mainStack)
        mainLayout.addWidget(self.globalFrame)
#        mainLayout.addWidget(self.settingFrame)
        self.show_mainstack_0()

#创建托盘图标
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(":/iconSources/icons/musicface.png"))
        self.showDesktopLyricAction = QAction(
             QIcon(":/iconSources/icons/desktopLyric.png"), "开启桌面歌词", 
                self,  triggered = self.playbackPage.show_desktop_lyric )
        trayMenu = QMenu()
        trayMenu.addAction(self.showMainWindowAction)
        trayMenu.addAction(self.showDesktopLyricAction)
        trayMenu.addSeparator()
        trayMenu.addAction(self.previousAction)
        trayMenu.addAction(self.playAction)
        trayMenu.addAction(self.nextAction)
        trayMenu.addAction(self.stopAction)
        trayMenu.addSeparator()
        trayMenu.addAction(self.seqPlaymodeAction)
        trayMenu.addAction(self.rdnPlaymodeAction)
        trayMenu.addAction(self.onePlaymodeAction)
        trayMenu.addSeparator()
        trayMenu.addAction(self.exitNowAction)
        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.show()

    def create_actions(self):
        self.showMainWindowAction = QAction(
             QIcon(":/iconSources/icons/showMainWindow.png"), "隐藏主界面", 
                self,  triggered = self.show_mainwindow )
                
        self.stopAction = QAction(
                QIcon(":/iconSources/icons/stop.png"), "停止",
                self, enabled = True,
                triggered = self.stop_music)
        
        self.nextAction = QAction(
        QIcon(":/iconSources/icons/next.png"), "下一首", 
                self, enabled = True,
                triggered = self.next_song)
        
        self.playAction = QAction(
        QIcon(":/iconSources/icons/play.png"), "播放/暂停",
                self, enabled = True,
                triggered = self.play_music)
        
        self.previousAction = QAction(
        QIcon(":/iconSources/icons/previous.png"), "上一首", 
                self, enabled = True,
                triggered = self.previous_song)
        
        self.seqPlaymodeAction = QAction(
            QIcon(":/iconSources/icons/playmode_select.png"),  "顺序循环", 
                self, triggered = self.seq_playmode_seted)
                
        self.rdnPlaymodeAction = QAction(
            QIcon(":/iconSources/icons/playmode_select_no.png"),  "随机播放", 
                self, triggered = self.rdn_playmode_seted)
        
        self.onePlaymodeAction = QAction(
            QIcon(":/iconSources/icons/playmode_select_no.png"),  "单曲循环", 
                self, triggered = self.one_playmode_seted)
        
        self.exitNowAction = QAction(
            QIcon(":/iconSources/icons/shutdown.png"),  "立即退出", 
                self, triggered = self.close)
        
        self.hideAction  = QAction(
            QIcon(":/iconSources/icons/minimum.png"),  "隐藏到托盘", 
                self, triggered = self.show_mainwindow)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
        self.settingFrame.close()
        event.accept()
    
    def mouseReleaseEvent(self, event):
        self.setCursor(QCursor(Qt.ArrowCursor))
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.RightButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()
    
    def eventFilter(self, target, event):
        if target == self.settingFrame:
            if event.type() == QEvent.Leave:
                self.settingFrame.close()
        return False
    
    def closeEvent(self, event):
        if not self.settingFrame.isHidden():
            self.settingFrame.hide()
        if self.settingFrame.mountoutDialog.countoutMode and not self.settingFrame.mountoutDialog.remainMount or self.settingFrame.timeoutDialog.timeoutFlag:
            self.dispose_before_close()
            event.accept()
        else:
            self.show()
            if threading.active_count() == 1:
                ok = QMessageBox.question(self, '退出', '您确定退出？',QMessageBox.Cancel|QMessageBox.Ok, QMessageBox.Cancel )
                if ok == QMessageBox.Ok:
                    self.trayIcon.hide()
                    self.managePage.downloadPage.downloadModel.submitAll()
                    event.accept()
                else:
                    event.ignore()
            else:
                ok = QMessageBox.question(self, '退出', '当前有下载任务正在进行，您是否要挂起全部下载任务并退出？',QMessageBox.Cancel|QMessageBox.Ok, QMessageBox.Cancel )
                if ok == QMessageBox.Ok:
                    self.dispose_before_close()
                    event.accept()
                else:
                    event.ignore()

    def dispose_before_close(self):
        self.hide()
        self.trayIcon.hide()
#        from xyplayer.urldispose.SearchOnline import reqCache
#        contents = json.dumps(reqCache)
#        with open(Configures.urlCache, 'w') as f:
#            f.write(contents)
        for t in threading.enumerate():
            if t.name == 'downloadLrc':
                t.stop()
            elif t!= threading.main_thread():
                t.pause()
                t.join()
        self.managePage.downloadPage.downloadModel.submitAll()

# ###   播放模式设置  #######################################
    def seq_playmode_seted(self):
        self.playmodeIndex = 1      
        self.playmode_check()
    
    def rdn_playmode_seted(self):
        self.playmodeIndex = 2
        self.playmode_check()
    
    def one_playmode_seted(self):
        self.playmodeIndex = 3
        self.playmode_check()
    
    def playmode_changed(self):
        self.playmodeIndex += 1
        if self.playmodeIndex > 3:
            self.playmodeIndex = 1
        self.playmode_check()
    
    def playmode_check(self):
        if self.playmodeIndex == 1:
            self.playbackPage.playmodeButton.setToolTip("顺序循环")
            icon_path = ":/iconSources/icons/playmode1.png"
            icon_path1 = ":/iconSources/icons/playmode_select.png"
            icon_path2 = icon_path3 = ":/iconSources/icons/playmode_select_no.png"
        elif self.playmodeIndex == 2:
            self.playbackPage.playmodeButton.setToolTip("随机播放")
            icon_path = ":/iconSources/icons/playmode2.png"
            icon_path2 = ":/iconSources/icons/playmode_select.png"
            icon_path1 = icon_path3 = ":/iconSources/icons/playmode_select_no.png"
        elif self.playmodeIndex == 3:
            self.playbackPage.playmodeButton.setToolTip("单曲循环")
            icon_path = ":/iconSources/icons/playmode3.png"
            icon_path3 = ":/iconSources/icons/playmode_select.png"
            icon_path1 = icon_path2 = ":/iconSources/icons/playmode_select_no.png"
        self.playbackPage.playmodeButton.setIcon(QIcon(icon_path))
        self.seqPlaymodeAction.setIcon(QIcon(icon_path1))
        self.rdnPlaymodeAction.setIcon(QIcon(icon_path2))
        self.onePlaymodeAction.setIcon(QIcon(icon_path3))
# ############## 播放模式  ###################################
    
    def show_minimized(self):
        if not self.settingFrame.isHidden():
            self.settingFrame.hide()
        self.showMinimized()

    def show_mainstack_1(self):
        self.playbackPage.show_lyric_text()
        self.mainStack.setCurrentIndex(1)
        self.globalFrame.setStyleSheet(  "QPushButton:hover{border:2px solid lightgray;border-radius:10px;background:rgb(210,240,240)}"
                                    "QPushButton{border:2px solid lightgray;border-radius:10px;background:transparent}")
        
    def show_mainstack_0(self):
        self.mainStack.setCurrentIndex(0)
        self.globalFrame.setStyleSheet("QPushButton{border:2px solid lightgray;border-radius:10px;background:rgb(210,240,240)}"
                                                        "QPushButton:hover{border:2px solid lightgray;border-radius:10px;background:white}")

    def show_mainwindow(self):
        if self.isHidden():
            self.show()
            self.showMainWindowAction.setText('隐藏主界面')
        else:
            if not self.settingFrame.isHidden():
                self.settingFrame.close()
            self.hide()
            self.showMainWindowAction.setText('显示主界面')
    
    def show_global_setting_frame(self):
        if self.settingFrame.isHidden():
            self.x= self.geometry().x()
            self.y = self.geometry().y()
#            x_offset = (self.width() - self.settingFrame.width()) / 2
#            y_offset = (self.height() - self.settingFrame.height()) / 2
            self.settingFrame.move(self.x + 11, self.y + 245)
            pixmap = QPixmap(":/iconSources/icons/functions.png")
#            pixmap = QPixmap("/home/zyj/图片/function2.png")
            self.settingFrame.setPixmap(pixmap)
            self.settingFrame.setMask(pixmap.mask())
            self.settingFrame.show()  
            self.settingFrame.show_main()
        else:
            self.settingFrame.hide()
    
    def desktop_lyric_state_changed(self, be_to_off):
        if be_to_off:
            self.showDesktopLyricAction.setText('关闭桌面歌词')
        else:
            self.showDesktopLyricAction.setText('开启桌面歌词')
    
    def switch_to_online_list(self):
        self.managePage.show_lists_frame()
        self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(0, 0))
    
    def current_table_changed(self, i):
        self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(i, 1))
        
    def show_current_table(self):
        for i in range(0, self.managePage.listsFrame.manageModel.rowCount()):
            if self.managePage.listsFrame.manageModel.record(i).value("tableName") == self.playTable:
                break
        self.manage_table_clicked(self.managePage.listsFrame.manageModel.index(i, 0))
    
    def lists_frame_title_label_clicked(self):
        text = self.managePage.listsFrame.titleLabel.text()
        if text == '列表管理':
            self.show_current_table()
        else:
            if text == self.playTable:
                self.managePage.listsFrame.musicTable.selectRow(self.currentSourceRow)
    
    def ui_initial(self):
        self.mediaObject.stop()
        self.mediaObject.clear()
        self.totalTime = '00:00'
        self.playAction.setIcon(QIcon(":/iconSources/icons/play.png"))
        self.managePage.ui_initial()
        self.playbackPage.ui_initial()

    def global_back(self):
        if self.mainStack.currentIndex() == 0:
            if self.managePage.stackedWidget.currentIndex() != 0:
                self.managePage.back_to_main()
        elif self.mainStack.currentIndex() == 1:
            if self.playbackPage.stackedWidget.currentIndex() !=0:
                self.playbackPage.show_lyric_text()
            else:
                self.show_mainstack_0()
    
    def global_home(self):
        if self.mainStack.currentIndex or self.managePage.stackedWidget.currentIndex: 
            self.show_mainstack_0()
            self.managePage.back_to_main()

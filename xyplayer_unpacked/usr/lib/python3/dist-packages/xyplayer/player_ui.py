import threading
from PyQt5.QtWidgets import (
    QMessageBox, QDialog, QStackedWidget, QSystemTrayIcon, QAction, 
    QHBoxLayout, QLabel, QVBoxLayout, QFrame, QMenu, QPushButton)
from PyQt5.QtGui import QIcon, QCursor,QPixmap
from PyQt5.QtCore import Qt, QSize
from xyplayer import Configures, desktopSize
from xyplayer.iconshub import IconsHub
from xyplayer.mypages import manage_page, playback_page, setting_frame
from xyplayer.mytables import TableModel, TableView
from xyplayer.mywidgets import PushButton, NewListWidget

class PlayerUi(QDialog):
    def __init__(self, parent = None):
        super(PlayerUi, self).__init__(parent)
        self.create_actions()
        self.setup_ui()
        self.managePage.ui_initial()
        self.playbackPage.ui_initial()
    
    def playback_musictable_add_widget(self, ident, title):
        widget = NewListWidget(ident, title)
        widget.play_button_clicked_signal.connect(self.playback_page_to_listen)
        widget.info_button_clicked_signal.connect(self.playback_page_music_info)
        self.playbackPage.musicList.add_item(widget, 85)
        self.allPlaySongs.append(ident) 
            
    def setup_ui(self):        
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon(IconsHub.Xyplayer))
        self.setFocusPolicy(Qt.NoFocus)
        self.setObjectName('xyplayer')
        self.setStyleSheet("#xyplayer{border-image: url(%s);background:transparent}"%IconsHub.Background)
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint | Qt.FramelessWindowHint)
        self.setFixedSize(370, 660)
        self.setGeometry((desktopSize.width() - 370)//2, 40, 370, 660)
        self.setAttribute(Qt.WA_QuitOnClose,True)

#title_widgets
        self.titleIconLabel = QLabel()
        pixmap = QPixmap(IconsHub.Xyplayer)
        self.titleIconLabel.setFixedSize(17, 17)
        self.titleIconLabel.setScaledContents(True)
        self.titleIconLabel.setPixmap(pixmap)
        self.titleLabel = QLabel("xyplayer")
        self.titleLabel.setStyleSheet("font-family:'微软雅黑';font-size:14px;color: white")
        self.minButton = PushButton()
        self.minButton.setFocusPolicy(Qt.NoFocus)
        self.hideButton = PushButton()
        self.hideButton.setFocusPolicy(Qt.NoFocus)
        self.closeButton = PushButton()
        self.closeButton.setFocusPolicy(Qt.NoFocus)
        self.minButton.loadPixmap(IconsHub.MinButton)
        self.hideButton.loadPixmap(IconsHub.HideButton)
        self.closeButton.loadPixmap(IconsHub.CloseButton)
        self.hideButton.clicked.connect(self.show_mainwindow)
        self.minButton.clicked.connect(self.show_minimized)
        self.closeButton.clicked.connect(self.close)

#播放页面
        self.playbackPage = playback_page.PlaybackPage()
        self.playbackPage.previousButton.setDefaultAction(self.previousAction)
        self.playbackPage.playButton.setDefaultAction(self.playAction)
        self.playbackPage.nextButton.setDefaultAction(self.nextAction)
        
#管理页面
        self.managePage = manage_page.ManagePage()
        self.managePage.playButton.setDefaultAction(self.playAction)
        self.managePage.nextButton.setDefaultAction(self.nextAction)

#3个主按键
        self.globalBackButton = QPushButton(clicked = self.global_back)
        self.globalBackButton.setFocusPolicy(Qt.NoFocus)
        self.globalHomeButton = QPushButton(clicked = self.global_home)
        self.globalHomeButton.setFocusPolicy(Qt.NoFocus)
        self.globalSettingButton = QPushButton(clicked = self.show_global_setting_frame)
        self.globalSettingButton.setFocusPolicy(Qt.NoFocus)
        self.globalBackButton.setIcon(QIcon(IconsHub.GlobalBack))
        self.globalHomeButton.setIcon(QIcon(IconsHub.GlobalMainpage))
        self.globalSettingButton.setIcon(QIcon(IconsHub.GlobalFunctions))
        self.globalBackButton.setFixedHeight(30)
        self.globalBackButton.setIconSize(QSize(25, 25))
        self.globalHomeButton.setFixedHeight(30)
        self.globalHomeButton.setIconSize(QSize(25, 25))
        self.globalSettingButton.setFixedHeight(30)
        self.globalSettingButton.setIconSize(QSize(25, 25))

#管理列表的model
        self.model = TableModel()      
        self.model.initial_model(Configures.PlaylistDefault)
        
        self.musicTable = TableView()
        self.musicTable.initial_view(self.model)

#综合布局 
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(self.titleIconLabel)
        titleLayout.addSpacing(3)
        titleLayout.addWidget(self.titleLabel)
        titleLayout.addWidget(self.hideButton)
        titleLayout.addWidget(self.minButton)
        titleLayout.addWidget(self.closeButton)
        
        self.globalFrame = QFrame()
        self.globalFrame.setStyleSheet("QPushButton{border:2px solid lightgray;border-radius:10px;}")
        hbox4 = QHBoxLayout(self.globalFrame)
        hbox4.setContentsMargins(4, 2, 4, 2)
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
        mainLayout.setContentsMargins(3, 6, 3, 8)
        mainLayout.addWidget(self.mainStack)
        mainLayout.addWidget(self.globalFrame)
        self.show_mainstack_1()
#        self.show_mainstack_0()

#设置菜单页面
        self.settingFrame = setting_frame.SettingFrame(self)
        self.settingFrame.setGeometry(9, 246, 352, 390)
        pixmap = QPixmap(IconsHub.Functions)
        self.settingFrame.setPixmap(pixmap)
        self.settingFrame.setMask(pixmap.mask())
        self.settingFrame.hide()

#创建托盘图标
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(IconsHub.Xyplayer))
        self.showDesktopLyricAction = QAction(
             QIcon(IconsHub.DesktopLyric), "开启桌面歌词", 
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
        trayMenu.addAction(self.playmodeRandomAction)
        trayMenu.addAction(self.playmodeOrderAction)
        trayMenu.addAction(self.playmodeSingleAction)
        trayMenu.addSeparator()
        trayMenu.addAction(self.exitNowAction)
        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.show()

    def create_actions(self):
        self.showMainWindowAction = QAction(
             QIcon(IconsHub.ShowMainWindow), "隐藏主界面", 
                self,  triggered = self.show_mainwindow )
                
        self.stopAction = QAction(
                QIcon(IconsHub.ControlStop), "停止",
                self, enabled = True,
                triggered = self.stop_music)
        
        self.nextAction = QAction(
        QIcon(IconsHub.ControlNext), "下一首", 
                self, enabled = True,
                triggered = self.next_song)
        
        self.playAction = QAction(
        QIcon(IconsHub.ControlPlay), "播放/暂停",
                self, enabled = True,
                triggered = self.play_music)
        
        self.previousAction = QAction(
        QIcon(IconsHub.ControlPrevious), "上一首", 
                self, enabled = True,
                triggered = self.previous_song)
        
        self.playmodeOrderAction = QAction(
            QIcon(IconsHub.PlaymodeSelectedNo),  Configures.PlaymodeOrderText, 
                self, triggered = self.playmode_order_seted)
                
        self.playmodeRandomAction = QAction(
            QIcon(IconsHub.PlaymodeSelected),  Configures.PlaymodeRandomText, 
                self, triggered = self.playmode_random_seted)
        
        self.playmodeSingleAction = QAction(
            QIcon(IconsHub.PlaymodeSelectedNo),  Configures.PlaymodeSingleText, 
                self, triggered = self.playmode_single_seted)
        
        self.exitNowAction = QAction(
            QIcon(IconsHub.Close),  "立即退出", 
                self, triggered = self.close)
                
        self.playmodeActions = [self.playmodeRandomAction, self.playmodeOrderAction, self.playmodeSingleAction]
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()
    
    def mouseReleaseEvent(self, event):
        self.setCursor(QCursor(Qt.ArrowCursor))
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.RightButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()
    
    def force_close(self):
        """用于程序成功更新之后跳过确认窗口强制关闭。"""
        self.forceCloseFlag = True
        self.close()

    def closeEvent(self, event):
        if not self.settingFrame.isHidden():
            self.settingFrame.hide()
        if self.settingFrame.mountoutDialog.countoutMode and not self.settingFrame.mountoutDialog.remainMount or self.settingFrame.timeoutDialog.timeoutFlag or self.forceCloseFlag:
            self.handle_before_close()
            event.accept()
        else:
            self.show()
            if threading.active_count() == 1:
                ok = QMessageBox.question(self, '退出', '您确定退出？',QMessageBox.Cancel|QMessageBox.Ok, QMessageBox.Cancel )
                if ok == QMessageBox.Ok:
                    self.trayIcon.hide()
                    if self.managePage.downloadPage.allWorksCount:
                        self.mediaPlayer.stop()
                        self.hide()
                        self.managePage.downloadPage.record_works_into_database()
                    event.accept()
                else:
                    event.ignore()
            else:
                ok = QMessageBox.question(self, '退出', '当前有下载任务正在进行，您是否要挂起全部下载任务并退出？',QMessageBox.Cancel|QMessageBox.Ok, QMessageBox.Cancel )
                if ok == QMessageBox.Ok:
                    self.handle_before_close()
                    event.accept()
                else:
                    event.ignore()

    def handle_before_close(self):
        self.mediaPlayer.stop()
        self.hide()
        self.trayIcon.hide()
        for t in threading.enumerate():
            if t.name == 'downloadLrc':
                t.stop()
#                t.join()
            elif t!= threading.main_thread():
                t.pause()
                t.join()
        self.managePage.downloadPage.record_works_into_database()

    def playmode_changed(self, oldPlaymode, newPlaymode):
        self.playmodeActions[oldPlaymode].setIcon(QIcon(IconsHub.PlaymodeSelectedNo))
        self.playmodeActions[newPlaymode].setIcon(QIcon(IconsHub.PlaymodeSelected))
    
    def playmode_order_seted(self):
        if self.playbackPage.playmode != Configures.PlaymodeOrder:
            self.playmode_changed(self.playbackPage.playmode, Configures.PlaymodeOrder)
            self.playbackPage.set_new_playmode(Configures.PlaymodeOrder)
    
    def playmode_random_seted(self):
        if self.playbackPage.playmode != Configures.PlaymodeRandom:
            self.playmode_changed(self.playbackPage.playmode, Configures.PlaymodeRandom)
            self.playbackPage.set_new_playmode(Configures.PlaymodeRandom)
    
    def playmode_single_seted(self):
        if self.playbackPage.playmode != Configures.PlaymodeSingle:
            self.playmode_changed(self.playbackPage.playmode, Configures.PlaymodeSingle)
            self.playbackPage.set_new_playmode(Configures.PlaymodeSingle)
    
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
            self.showMainWindowAction.setText('隐藏主界面')
            self.show()
        else:
            if not self.settingFrame.isHidden():
                self.settingFrame.hide()
            self.hide()
            self.showMainWindowAction.setText('显示主界面')
    
    def show_global_setting_frame(self):
        if self.settingFrame.isHidden():
            self.settingFrame.show_main()
            self.settingFrame.show()  
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
        self.totalTime = '00:00'
        self.playAction.setIcon(QIcon(IconsHub.ControlPlay))
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

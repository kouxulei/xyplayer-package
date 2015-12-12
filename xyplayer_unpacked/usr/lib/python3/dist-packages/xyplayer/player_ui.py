import threading
from PyQt5.QtWidgets import (
    QMessageBox, QDialog, QStackedWidget, QSystemTrayIcon, QAction, QApplication, 
    QHBoxLayout, QLabel, QVBoxLayout, QMenu, QPushButton)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QFile, QPoint
from xyplayer import Configures, app_name
from xyplayer.myicons import IconsHub
from xyplayer.mypages import manage_page, search_page, artist_info_dialog
from xyplayer.mywidgets import PushButton
from xyplayer.playbackpanel import PlaybackPanel

class PlayerUi(QDialog):
    def __init__(self, parent = None):
        super(PlayerUi, self).__init__(parent)
        self.create_actions()
        self.setup_ui()
        self.managePage.ui_initial()
        self.load_style_sheet(Configures.QssFileDefault, Configures.IconsDir)
    
    def load_style_sheet(self, sheetName, iconsDir):
        """load qss file"""
        print('Using qss file: %s'%sheetName)
        qss = QFile(sheetName)
        qss.open(QFile.ReadOnly)
        styleSheet = str(qss.readAll(), encoding='utf8').replace(':PathPrefix', iconsDir)
        QApplication.instance().setStyleSheet(styleSheet)
        qss.close()
    
    def create_connections(self):
        self.searchBox.search_musics_signal.connect(self.search_musics_online)
        self.searchBox.searchtype_changed_signal.connect(self.managePage.searchFrame.searchtype_changed)
        self.aboutButton.clicked.connect(self.show_about_page)
        self.preferenceButton.clicked.connect(self.show_settings_frame)
        self.minButton.clicked.connect(self.show_minimized)
        self.closeButton.clicked.connect(self.close_button_acted)
        self.playbackPanel.desktop_lyric_state_changed_signal.connect(self.desktop_lyric_state_changed)
        self.playbackPanel.show_artist_info_signal.connect(self.show_artist_info)
        self.managePage.playlistWidget.show_artist_info_signal.connect(self.show_artist_info)

    def setup_ui(self):        
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon(IconsHub.Xyplayer))
        self.setFocusPolicy(Qt.NoFocus)
        self.setObjectName(app_name)
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint | Qt.FramelessWindowHint)
        self.setMaximumSize(QSize(Configures.WindowWidth, Configures.WindowHeight))
        self.setGeometry((Configures.DesktopSize.width() - Configures.WindowWidth)//2, (Configures.DesktopSize.height() - Configures.WindowHeight)//2, Configures.WindowWidth, Configures.WindowHeight)
        self.setAttribute(Qt.WA_QuitOnClose,True)
        self.dragPosition = QPoint(0, 0)

#title_widgets
        self.titleIconLabel = QLabel()
        pixmap = QPixmap(IconsHub.Xyplayer)
        self.titleIconLabel.setFixedSize(18, 18)
        self.titleIconLabel.setScaledContents(True)
        self.titleIconLabel.setPixmap(pixmap)
        self.titleLabel = QLabel("XYPLAYER")
        self.titleLabel.setFixedHeight(30)
        self.titleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setObjectName('titleLabel')
        self.minButton = PushButton()
        self.minButton.setFocusPolicy(Qt.NoFocus)
        self.closeButton = PushButton()
        self.closeButton.setFocusPolicy(Qt.NoFocus)
        self.aboutButton = PushButton()
        self.aboutButton.setFocusPolicy(Qt.NoFocus)
        self.preferenceButton = PushButton()
        self.preferenceButton.setFocusPolicy(Qt.NoFocus)
        self.minButton.loadPixmap(IconsHub.MinButton)
        self.closeButton.loadPixmap(IconsHub.CloseButton)
        self.aboutButton.loadPixmap(IconsHub.AboutButton)
        self.preferenceButton.loadPixmap(IconsHub.PreferenceButton)
        
#管理页面
        self.managePage = manage_page.ManagePage()

#播放器
        self.playbackPanel = PlaybackPanel()

#歌手信息
        self.artistInfoDialog = artist_info_dialog.ArtistInfoDialog()

        self.mainPageButton = QPushButton(self, clicked = self.global_home)
        self.mainPageButton.hide()
        self.mainPageButton.setGeometry(620, 3, 60, 30)
        self.mainPageButton.setObjectName('globalHomeButton')
        self.mainPageButton.setFocusPolicy(Qt.NoFocus)
        self.mainPageButton.setIcon(QIcon(IconsHub.GlobalMainpage))
        self.mainPageButton.setIconSize(QSize(20, 20))
        self.pageLabel = QLabel(self)
        self.pageLabel.hide()
        self.pageLabel.setGeometry(685, 3, 100, 30)
        self.searchBox = search_page.SearchBox(self)
        self.searchBox.setGeometry(180, 3, 290, 30)

#综合布局 
        titleLayout = QHBoxLayout()
        titleLayout.setContentsMargins(3, 0, 0, 0)
        titleLayout.setSpacing(0)
        titleLayout.addWidget(self.titleIconLabel)
        titleLayout.addWidget(self.titleLabel)
        titleLayout.addStretch()
        titleLayout.addWidget(self.aboutButton)
        titleLayout.addWidget(self.preferenceButton)
        titleLayout.addWidget(self.minButton)
        titleLayout.addWidget(self.closeButton)

#主堆栈框
        self.mainStack = QStackedWidget()
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(2)
        mainLayout.setContentsMargins(3, 0, 3, 0)
        mainLayout.addLayout(titleLayout)
        mainLayout.addWidget(self.managePage)
        mainLayout.addWidget(self.playbackPanel)

#创建托盘图标
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(IconsHub.Xyplayer))
        self.showDesktopLyricAction = QAction(
             QIcon(IconsHub.DesktopLyric), "开启桌面歌词", 
                self,  triggered = self.playbackPanel.show_desktop_lyric )
        trayMenu = QMenu()
        trayMenu.addAction(self.showMainWindowAction)
        trayMenu.addAction(self.showDesktopLyricAction)
        trayMenu.addSeparator()
        trayMenu.addAction(self.playbackPanel.get_previous_button_action())
        trayMenu.addAction(self.playbackPanel.get_play_button_action())
        trayMenu.addAction(self.playbackPanel.get_next_button_action())
        trayMenu.addAction(self.playbackPanel.get_stop_button_action())
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
        self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()
#    
#    def mouseReleaseEvent(self, event):
#        self.setCursor(QCursor(Qt.ArrowCursor))
    
    def mouseMoveEvent(self, event):
        if event.buttons():
#            self.setCursor(QCursor(Qt.ClosedHandCursor))
            self.move(event.globalPos() - self.dragPosition)
            event.accept()
    
    def force_close(self):
        """用于程序成功更新之后跳过确认窗口强制关闭。"""
        self.forceCloseFlag = True
        self.close()

    def closeEvent(self, event):
        self.artistInfoDialog.close()
        if self.managePage.exitmodePanel.mountoutDialog.countoutMode and not self.managePage.exitmodePanel.mountoutDialog.remainMount or self.managePage.exitmodePanel.timeoutDialog.timeoutFlag or self.forceCloseFlag:
            self.handle_before_close()
            event.accept()
        else:
            if threading.active_count() == 1:
                if self.managePage.downloadPage.allWorksCount:
                    self.playbackPanel.mediaPlayer.stop()
                    self.hide()
                    self.trayIcon.hide()
                    self.managePage.downloadPage.record_works_into_database()
                event.accept()
            else:
                self.show()
                ok = QMessageBox.question(self, '退出', '当前有下载任务正在进行，您是否要挂起全部下载任务并退出？',QMessageBox.Cancel|QMessageBox.Ok, QMessageBox.Cancel )
                if ok == QMessageBox.Ok:
                    self.handle_before_close()
                    event.accept()
                else:
                    event.ignore()

    def handle_before_close(self):
        self.playbackPanel.mediaPlayer.stop()
        self.hide()
        self.trayIcon.hide()
        for t in threading.enumerate():
            if t.name == 'downloadLrc':
                t.stop()
            elif t!= threading.main_thread():
                t.pause()
                t.join()
        self.managePage.downloadPage.record_works_into_database()

    def playmode_changed(self, oldPlaymode, newPlaymode):
        self.playmodeActions[oldPlaymode].setIcon(QIcon(IconsHub.PlaymodeSelectedNo))
        self.playmodeActions[newPlaymode].setIcon(QIcon(IconsHub.PlaymodeSelected))
    
    def playmode_order_seted(self):
        if self.playbackPanel.playmode != Configures.PlaymodeOrder:
            self.playmode_changed(self.playbackPanel.playmode, Configures.PlaymodeOrder)
            self.playbackPanel.set_new_playmode(Configures.PlaymodeOrder)
    
    def playmode_random_seted(self):
        if self.playbackPanel.playmode != Configures.PlaymodeRandom:
            self.playmode_changed(self.playbackPanel.playmode, Configures.PlaymodeRandom)
            self.playbackPanel.set_new_playmode(Configures.PlaymodeRandom)
    
    def playmode_single_seted(self):
        if self.playbackPanel.playmode != Configures.PlaymodeSingle:
            self.playmode_changed(self.playbackPanel.playmode, Configures.PlaymodeSingle)
            self.playbackPanel.set_new_playmode(Configures.PlaymodeSingle)
    
    def show_minimized(self):
        self.showMinimized()

    def show_mainwindow(self):
        if self.isHidden():
            self.showMainWindowAction.setText('隐藏主界面')
            self.show()
        else:
            self.artistInfoDialog.close()
            self.showMainWindowAction.setText('显示主界面')
            self.hide()
    
    def desktop_lyric_state_changed(self, be_to_off):
        if be_to_off:
            self.showDesktopLyricAction.setText('关闭桌面歌词')
        else:
            self.showDesktopLyricAction.setText('开启桌面歌词')
    
    def ui_initial(self):
        self.playbackPanel.ui_initial()
        self.managePage.ui_initial()
    
    def global_home(self):
        self.pageLabel.hide()
        self.mainPageButton.hide()
        self.managePage.show_main_stack_window()
    
    def show_about_page(self):
        self.pageLabel.setText(self.tr('关于'))
        self.mainPageButton.show()
        self.pageLabel.show()
        self.managePage.show_about_page()
    
    def show_settings_frame(self):
        self.pageLabel.setText(self.tr('选项'))
        self.mainPageButton.show()
        self.pageLabel.show()
        self.managePage.show_settings_frame()
    
    def search_musics_online(self, keyword):
        if self.managePage.searchFrame.search_musics(keyword):
            self.pageLabel.setText(self.tr('搜索'))
            self.mainPageButton.show()
            self.pageLabel.show()
            self.managePage.show_search_frame()
    
    def close_button_acted(self):
        if self.closeButtonAct == Configures.SettingsHide:
            self.show_mainwindow()
        else:
            self.close()

    def show_artist_info(self, name):
        if name == 'Zheng-Yejian':
            self.artistInfoDialog.ui_initial()
        else:
            self.artistInfoDialog.set_artist_info(name)
        self.artistInfoDialog.exec()

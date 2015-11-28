from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from xyplayer import Configures
from xyplayer.myicons import IconsHub
from xyplayer.mywidgets import LabelButton, SpecialLabel, NewLabel
from xyplayer.mypages import  search_page, download_page
from xyplayer.mytables import MyListTable
from xyplayer.myplaylists import playlistsManager
from xyplayer.mytables import PlaylistWidget

class ManagePage(QWidget):
    current_table_changed_signal = pyqtSignal(str)
    add_a_list_signal = pyqtSignal()
    playlist_removed_signal = pyqtSignal(str)
    playlist_renamed_signal = pyqtSignal(str, str)
    show_playback_page_signal = pyqtSignal()
    def __init__(self):
        super(ManagePage, self).__init__()
        self.setup_ui()
        self.create_connections()
        self.set_normal_mode()
    
    def setup_ui(self):
        self.setStyleSheet("QToolButton{background:transparent}"
                                    "QTableWidget, QTableView, QHeaderView:hover{color:green;font-size:15px}" 
                                    "QTableWidget, QTableView, QHeaderView{background:rgb(210,240,240);color:blue;font-size:15px}"
                                    "QPushButton{border:0px solid lightgray;color:blue;background:rgb(210,240,240)}"
                                    "QPushButton:hover{border:0px solid lightgray;color:green;background:white}"
                                    "QComboBox,QLineEdit:hover{background:white;color:green;border:0px solid lightgray;}" 
                                    "QComboBox,QLineEdit{background:rgb(210,240,240);color:blue;border:0px solid lightgray;}")
                                    
#管理歌曲的列表
        self.playlistWidget = PlaylistWidget()
        self.playlistWidget.set_playlist_names(playlistsManager.get_play_list_names())
#搜索页面
        self.searchFrame = search_page.SearchFrame()
#下载页面
        self.downloadPage = download_page.DownloadPage()
        
        self.searchButton = QPushButton(clicked = self.show_search_frame)
        self.searchButton.setFocusPolicy(Qt.NoFocus)
        self.searchButton.setFixedSize(QSize(33, 33))
        self.searchButton.setIconSize(QSize(20, 20))
        self.searchButton.setIcon(QIcon(IconsHub.Search))
        
        self.lyricLabel = LabelButton("歌词同步显示", 33)
        self.lyricLabel.setFixedWidth(312)

        self.frameBottomWidget = SpecialLabel()    
        self.frameBottomWidget.setFixedSize(QSize(352, 93))
#3个标签
        self.artistHeadLabel = QLabel(self.frameBottomWidget)
        self.artistHeadLabel.setScaledContents(True)
        self.artistHeadLabel.setPixmap(QPixmap(IconsHub.Anonymous))

        self.musicNameLabel = NewLabel(self.frameBottomWidget)
        self.musicNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:18px;color: blue;background:transparent")

        self.artistNameLabel = NewLabel(self.frameBottomWidget)
        self.artistNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:15px;color: blue;background:transparent")

        self.timeLabel = QLabel("00:00/00:00", self.frameBottomWidget)
        self.timeLabel.setAlignment(Qt.AlignRight and Qt.AlignVCenter)
        self.timeLabel.setStyleSheet("font-family:'微软雅黑';font-size:13px;color: blue;background:transparent")

        self.playButton = QToolButton(self.frameBottomWidget)
        self.playButton.setFocusPolicy(Qt.NoFocus)
        self.playButton.setIconSize(QSize(70, 70))
        self.playButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:0px solid blue;border-radius:35px;background:blue}")
        self.nextButton = QToolButton(self.frameBottomWidget)
        self.nextButton.setIconSize(QSize(70, 70))
        self.nextButton.setFocusPolicy(Qt.NoFocus)
        self.nextButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:0px solid blue;border-radius:35px;background:blue}")

        self.artistHeadLabel.setGeometry(9, 14, 65, 65)
        self.musicNameLabel.setGeometry(79, 8, 120, 28)
        self.artistNameLabel.setGeometry(79, 38, 120, 23)
        self.timeLabel.setGeometry(79, 66, 120, 15)
        self.playButton.setGeometry(204, 11, 70, 70)
        self.nextButton.setGeometry(274, 11, 70, 70)
        
        self.allListButton = LabelButton("列表管理")
        self.downloadPageButton = LabelButton("下载任务")
        
        self.myListTable = MyListTable()
        self.myListTable.setStyleSheet("background:transparent")
        for i, tableName in enumerate(playlistsManager.get_play_list_names()):
            flag = False
            if i >= 4:
                flag = True
            self.myListTable.add_a_button( tableName, flag)
        self.myListTable.get_button_at(1).setStyleSheet("QLabel{background:rgb(50, 255, 50);color:blue;}"
                                            "QLabel:hover{background:white;color:green;}")
        self.randomOneButton = LabelButton("随机切歌", 271)
        self.addListButton = LabelButton("添加列表")
        
        listsFrame = QWidget()
#返回按键
        self.backButton = QPushButton(clicked = self.back_to_main)
        self.backButton.setFocusPolicy(Qt.NoFocus)
        self.backButton.setStyleSheet("font-size:15px")
        self.backButton.setFixedSize(25, 33)
        self.backButton.setIcon(QIcon(IconsHub.Back))
        self.backButton.setIconSize(QSize(20, 20))
 #标签 
        self.titleLabel = LabelButton("列表管理")
        self.titleLabel.setFixedSize(100, 33)
        self.titleLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
#管理歌曲列表页面的布局
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.backButton)
        hbox1.addWidget(self.titleLabel)
        hbox1.addStretch()
        listFrameLayout = QVBoxLayout(listsFrame)
        listFrameLayout.setContentsMargins(0, 0, 0, 0)
        listFrameLayout.addLayout(hbox1)
        listFrameLayout.addWidget(self.playlistWidget)

#综合布局            
        hbox_sch = QHBoxLayout()
        hbox_sch.setSpacing(7)
        hbox_sch.addWidget(self.lyricLabel)
        hbox_sch.addWidget(self.searchButton)
        
        hbox_om = QHBoxLayout()
        hbox_om.setSpacing(7)
        hbox_om.addWidget(self.myListTable.get_button_at(0))
        hbox_om.addWidget(self.myListTable.get_button_at(2))
        
        hbox_fd = QHBoxLayout()
        hbox_fd.setSpacing(7)
        hbox_fd.addWidget(self.myListTable.get_button_at(1))
        hbox_fd.addWidget(self.myListTable.get_button_at(3))
        
        vbox_no = QVBoxLayout()
        vbox_no.setSpacing(7)
        vbox_no.addWidget(self.downloadPageButton)
        vbox_no.addWidget(self.randomOneButton)
        
        vbox_mar = QVBoxLayout()
        vbox_mar.setSpacing(7)
        vbox_mar.addWidget(self.myListTable)
        vbox_mar.addWidget(self.addListButton)
        
        hbox_nh = QHBoxLayout()
        hbox_nh.setSpacing(7)
        hbox_nh.addLayout(vbox_mar)
        hbox_nh.addLayout(vbox_no)
        
        listsLayout = QVBoxLayout()
        listsLayout.setSpacing(7)
        listsLayout.addWidget(self.allListButton)
        listsLayout.addLayout(hbox_om)
        listsLayout.addLayout(hbox_fd)
        listsLayout.addLayout(hbox_nh)
        
        homeWidget = QWidget()
        layout_list = QVBoxLayout(homeWidget)
        layout_list.setSpacing(7)
        layout_list.setContentsMargins(0, 0, 0, 0)
        layout_list.addLayout(hbox_sch)
        layout_list.addLayout(listsLayout)

#中间的stackedWidget
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(homeWidget)
        self.stackedWidget.addWidget(listsFrame)
        self.stackedWidget.addWidget(self.searchFrame)
        self.stackedWidget.addWidget(self.downloadPage)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(6, 0, 6, 4)
        mainLayout.setSpacing(7)
        mainLayout.addWidget(self.stackedWidget)
        mainLayout.addWidget(self.frameBottomWidget)
    
    def create_connections(self):
        self.searchFrame.back_to_main_signal.connect(self.back_to_main)
        self.downloadPage.back_to_main_signal.connect(self.back_to_main)
        self.downloadPageButton.clicked.connect(self.show_download_page)
        self.addListButton.clicked.connect(self.add_a_playlist)
        self.frameBottomWidget.clicked.connect(self.show_playback_page_signal.emit)
        self.lyricLabel.clicked.connect(self.show_playback_page_signal.emit)
        self.myListTable.button_in_list_clicked.connect(self.switch_to_certain_page)
        self.myListTable.operate_mode_activated.connect(self.set_operate_mode)
        self.myListTable.remove_a_playlist_signal.connect(self.remove_a_playlist)
        self.myListTable.rename_a_playlist_signal.connect(self.rename_a_playlist)
        
        #新连接
        self.playlistWidget.playlist_changed_signal.connect(self.change_list_buttons_color)
    
    def back_to_main(self):
        self.stackedWidget.setCurrentIndex(0)
    
    def show_search_frame(self):
        self.stackedWidget.setCurrentIndex(2)
    
    def show_download_page(self):
        self.stackedWidget.setCurrentIndex(3)
        
    def ui_initial(self):
        self.artistHeadLabel.setPixmap(QPixmap(IconsHub.HeadIcon))
        self.lyricLabel.setText('歌词同步显示')
        self.timeLabel.setText("00:00/00:00")
        self.frameBottomWidget.setGradient(0)
        self.musicNameLabel.setText("XYPLAYER")
        self.artistNameLabel.setText("Zheng-Yejian")
    
    def switch_to_certain_page(self, text):
        self.titleLabel.setText(text)
        self.stackedWidget.setCurrentIndex(1)
        self.playlistWidget.set_playlist_use_name(text)
        self.current_table_changed_signal.emit(text)
        if self.playlistWidget.get_playing_used_state():
            self.titleLabel.setStyleSheet("QLabel{background: rgb(50, 255, 50);color:blue;}"
                                                    "QLabel:hover{background:white;color:green;}")
        else:
            self.titleLabel.setStyleSheet("QLabel{background: rgb(210,240,240);color:blue;}"
                                                    "QLabel:hover{background:white;color:green;}")

    def change_list_buttons_color(self, playTableOld, playTable):
        self.titleLabel.setStyleSheet("QLabel{background: rgb(50, 255, 50);color:blue;}"
                                                    "QLabel:hover{background:white;color:green;}")
        for button in self.myListTable.get_buttons():
            if button.name == playTableOld:
                button.setStyleSheet("QLabel{background: rgb(210,240,240);color:blue;}"
                                                    "QLabel:hover{background:white;color:green;}")
            if button.name == playTable:
                button.setStyleSheet("QLabel{background: rgb(50, 255, 50);color:blue;}"
                                                    "QLabel:hover{background:white;color:green;}")

    def set_operate_mode(self):
        self.playlistMode = Configures.OperateMode
        self.addListButton.set_text('完成操作')
        for button in self.myListTable.buttons:
            button.set_remove_mode()
    
    def set_normal_mode(self):
        self.playlistMode = Configures.NormalMode
        self.addListButton.set_text('添加列表')
        for button in self.myListTable.buttons:
            button.set_normal_mode()
    
    def add_a_playlist(self):
        if self.playlistMode == Configures.NormalMode:
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
                self.myListTable.add_a_button(text)
        else:
            self.set_normal_mode()

    def rename_a_playlist(self, index):
        name = self.myListTable.get_name_at(index)
        newName, ok = QInputDialog.getText(self, "重命名列表", "请输入新列表名：", QLineEdit.Normal, name)
        if ok:
            if newName and newName != name:
                if newName in playlistsManager.get_play_list_names():
                    QMessageBox.critical(self, "注意！", "列表'%s'已存在！\n请重新修改！"%newName)
                else:
                    playlistsManager.rename_a_playlist(name, newName)
                    self.myListTable.rename_button_at(index, newName)
                    self.playlist_renamed_signal.emit(name, newName)
        self.myListTable.get_button_at(index).set_normal_style_sheet()
                
    def remove_a_playlist(self, index):    
        name = self.myListTable.get_name_at(index)
        ok = QMessageBox.warning(self, "删除列表", "列表'%s'将被删除，请确认！"%name, QMessageBox.No|QMessageBox.Yes, QMessageBox.No)
        if ok == QMessageBox.Yes:
            playlistsManager.remove_a_playlist(name)
            self.myListTable.remove_button_at(index)
            self.playlist_removed_signal.emit(name)
        else:
            self.myListTable.get_button_at(index).set_normal_style_sheet()

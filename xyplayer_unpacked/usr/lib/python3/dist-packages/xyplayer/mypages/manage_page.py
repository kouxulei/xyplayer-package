from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from xyplayer import Configures
from xyplayer.iconshub import IconsHub
from xyplayer.mywidgets import LabelButton, SpecialLabel, NewLabel
from xyplayer.mypages import  search_page, download_page, lists_frame
from xyplayer.mytables import MyListTable

class ManagePage(QWidget):
    show_lists_manage_frame_signal = pyqtSignal()
    current_table_changed_signal = pyqtSignal(int)
    add_a_list_signal = pyqtSignal()
    def __init__(self):
        super(ManagePage, self).__init__()
        self.setup_ui()
        self.create_connections()
    
    def setup_ui(self):
        self.setStyleSheet("QToolButton{background:transparent}"
                                    "QTableWidget, QTableView, QHeaderView:hover{color:green;font-size:15px}" 
                                    "QTableWidget, QTableView, QHeaderView{background:rgb(210,240,240);color:blue;font-size:15px}"
                                    "QPushButton{border:0px solid lightgray;color:blue;background:rgb(210,240,240)}"
                                    "QPushButton:hover{border:0px solid lightgray;color:green;background:white}"
                                    "QComboBox,QLineEdit:hover{background:white;color:green;border:0px solid lightgray;}" 
                                    "QComboBox,QLineEdit{background:rgb(210,240,240);color:blue;border:0px solid lightgray;}")
#搜索页面
        self.searchFrame = search_page.SearchFrame()

#下载页面
        self.downloadPage = download_page.DownloadPage()

#列表管理页面
        self.listsFrame = lists_frame.ListsFrame()
        
        self.searchButton = QPushButton(clicked = self.show_search_frame)
        self.searchButton.setFocusPolicy(Qt.NoFocus)
        self.searchButton.setFixedSize(QSize(33, 33))
        self.searchButton.setIconSize(QSize(20, 20))
        self.searchButton.setIcon(QIcon(IconsHub.Search))
        
        self.lyricLabel = LabelButton("歌词同步显示", 33)


        self.frameBottomWidget = SpecialLabel('', 93)    
#3个标签
        self.artistHeadLabel = QLabel(self.frameBottomWidget)
        self.artistHeadLabel.setScaledContents(True)
        self.artistHeadLabel.setPixmap(QPixmap(IconsHub.Anonymous))

#        self.musicNameLabel = QLabel("xyplayer")
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
        
        self.listButtons = []
        for text in [Configures.PlaylistOnline, Configures.PlaylistDefault, Configures.PlaylistFavorite, Configures.PlaylistDownloaded]:
            button = LabelButton(text)
            button.clicked.connect(self.switch_to_certain_page)
            self.listButtons.append(button)
        self.listButtons[1].setStyleSheet("QLabel{background:rgb(50, 255, 50);color:blue;}"
                                            "QLabel:hover{background:white;color:green;}")
        
        self.myListTable = MyListTable()
        self.myListTable.setStyleSheet("background:transparent")
        for i in range(4, self.listsFrame.manageModel.rowCount()):
            text = self.listsFrame.manageModel.record(i).value('tableName')
            self.add_a_widget_to_table(text)
        
        self.randomOneButton = LabelButton("随机切歌", 260)
        
        self.addListButton = LabelButton("添加列表")
        self.deleteListButton = LabelButton("删除列表")

#综合布局            
        hbox_sch = QHBoxLayout()
        hbox_sch.setSpacing(7)
        hbox_sch.addWidget(self.lyricLabel)
        hbox_sch.addWidget(self.searchButton)
        
        hbox_om = QHBoxLayout()
        hbox_om.setSpacing(7)
        hbox_om.addWidget(self.listButtons[0])
        hbox_om.addWidget(self.listButtons[1])
        
        hbox_fd = QHBoxLayout()
        hbox_fd.setSpacing(7)
        hbox_fd.addWidget(self.listButtons[2])
        hbox_fd.addWidget(self.listButtons[3])
        
        vbox_no = QVBoxLayout()
        vbox_no.setSpacing(7)
        vbox_no.addWidget(self.downloadPageButton)
        vbox_no.addWidget(self.randomOneButton)
        
        hbox_ar = QHBoxLayout()
        hbox_ar.setSpacing(7)
        hbox_ar.addWidget(self.addListButton)
        
        vbox_mar = QVBoxLayout()
        vbox_mar.setSpacing(7)
        vbox_mar.addWidget(self.myListTable)
        vbox_mar.addLayout(hbox_ar)
        
        hbox_nh = QHBoxLayout()
        hbox_nh.setSpacing(7)
        hbox_nh.addLayout(vbox_mar)
        hbox_nh.addLayout(vbox_no)
        
        listsLayout = QVBoxLayout()
        listsLayout.setSpacing(8)
        listsLayout.addWidget(self.allListButton)
        listsLayout.addLayout(hbox_om)
        listsLayout.addLayout(hbox_fd)
        listsLayout.addLayout(hbox_nh)
        
        homeWidget = QWidget()
        layout_list = QVBoxLayout(homeWidget)
        layout_list.setSpacing(8)
        layout_list.setContentsMargins(0, 0, 0, 0)
        layout_list.addLayout(hbox_sch)
        layout_list.addLayout(listsLayout)

#中间的stackedWidget
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(homeWidget)
        self.stackedWidget.addWidget(self.listsFrame)
        self.stackedWidget.addWidget(self.searchFrame)
        self.stackedWidget.addWidget(self.downloadPage)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(6, 6, 7, 7)
        mainLayout.setSpacing(8)
        mainLayout.addWidget(self.stackedWidget)
        mainLayout.addWidget(self.frameBottomWidget)
    
    def create_connections(self):
        self.searchFrame.back_to_main_signal.connect(self.back_to_main)
        self.downloadPage.back_to_main_signal.connect(self.back_to_main)
        self.listsFrame.back_to_main_signal.connect(self.back_to_main)
        self.downloadPageButton.clicked.connect(self.show_download_page)
        self.allListButton.clicked.connect(self.show_lists_frame)
        self.addListButton.clicked.connect(self.add_a_list_signal.emit)
    
    def back_to_main(self):
        self.stackedWidget.setCurrentIndex(0)
    
    def show_lists_frame(self):
        self.listsFrame.titleLabel.setText("列表管理")
#        self.listsFrame.stateLabel.show()
        self.listsFrame.manageTable.show()
        self.listsFrame.musicTable.setColumnWidth(1, 300)
        self.show_lists_manage_frame_signal.emit()
        self.stackedWidget.setCurrentIndex(1)
    
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
        for i in range(0, self.listsFrame.manageModel.rowCount()):
            if self.listsFrame.manageModel.record(i).value("tableName") == text:
                break
        self.listsFrame.titleLabel.setText(text)
        self.listsFrame.stateLabel.hide()
        self.listsFrame.manageTable.hide()
        self.listsFrame.musicTable.setColumnWidth(1, 270)
        self.listsFrame.musicTable.setColumnWidth(2, 80)
        self.stackedWidget.setCurrentIndex(1)
        self.current_table_changed_signal.emit(i)

    def change_list_buttons_color(self, playTableOld, playTable):
        for button in self.listButtons:
            if button.name == playTableOld:
                button.setStyleSheet("QLabel{background: rgb(210,240,240);color:blue;}"
                                                    "QLabel:hover{background:white;color:green;}")
            if button.name == playTable:
                button.setStyleSheet("QLabel{background: rgb(50, 255, 50);color:blue;}"
                                                    "QLabel:hover{background:white;color:green;}")
  
    
    def add_a_widget_to_table(self, text):
            button = LabelButton(text)
            button.clicked.connect(self.switch_to_certain_page)
            button.setStyleSheet("QLabel:hover{background:white;color:green;font-size:15px}" 
                                    "QLabel{background:rgb(210,240,240);color:blue;font-size:15px}")
            self.listButtons.append(button)
            self.myListTable.add_widget(button)
 
    
        

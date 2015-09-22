from PyQt4.QtGui import *
from PyQt4.QtCore import *
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
                                    "QTableWidget, QTableView, QHeaderView,QLabel:hover{background:white;color:green;font-size:15px}" 
                                    "QTableWidget, QTableView, QHeaderView,QLabel{background:rgb(210,240,240);color:blue;font-size:15px}"
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
        
#spacerItem
#        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.searchButton = QPushButton(clicked = self.show_search_frame)
        self.searchButton.setFixedSize(QSize(33, 33))
        self.searchButton.setIconSize(QSize(20, 20))
        self.searchButton.setIcon(QIcon(":/iconSources/icons/search.png"))
        
        self.lyricLabel = LabelButton("歌词同步显示于此！", 33)


        self.frameBottomWidget = SpecialLabel('', 93)    
#3个标签
        self.artistHeadLabel = QLabel(self.frameBottomWidget)
        self.artistHeadLabel.setScaledContents(True)
        self.artistHeadLabel.setPixmap(QPixmap(":/iconSources/icons/anonymous.png"))
        self.artistHeadLabel.setGeometry(10, 14, 65, 65)

#        self.musicNameLabel = QLabel("xyplayer")
        self.musicNameLabel = NewLabel(self.frameBottomWidget)
        self.musicNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:18px;color: blue;background:transparent")
        self.musicNameLabel.setGeometry(80, 12, 120, 27)

        self.artistNameLabel = NewLabel(self.frameBottomWidget)
        self.artistNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:15px;color: blue;background:transparent")
        self.artistNameLabel.setGeometry(80, 41, 120, 23)

        self.timeLabel = QLabel("00:00/00:00", self.frameBottomWidget)
        self.timeLabel.setAlignment(Qt.AlignRight and Qt.AlignVCenter)
        self.timeLabel.setStyleSheet("font-family:'微软雅黑';font-size:13px;color: blue;background:transparent")
        self.timeLabel.setGeometry(80, 67, 120, 15)

        self.playButton = QToolButton(self.frameBottomWidget)
        self.playButton.setIconSize(QSize(70, 70))
        self.playButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:0px solid blue;border-radius:35px;background:blue}")
        self.playButton.setGeometry(205, 11, 70, 70)
        self.nextButton = QToolButton(self.frameBottomWidget)
        self.nextButton.setIconSize(QSize(70, 70))
        self.nextButton.setStyleSheet("QToolButton{background:transparent}"
                                                        "QToolButton:hover{border:0px solid blue;border-radius:35px;background:blue}")
        self.nextButton.setGeometry(275, 11, 70, 70)

        self.allListButton = LabelButton("列表管理")
        self.downloadPageButton = LabelButton("下载任务")
        
        self.listButtons = []
        for text in ["在线试听", "默认列表", "喜欢歌曲", "我的下载"]:
            button = LabelButton(text)
            button.clicked.connect(self.switch_to_certain_page)
            self.listButtons.append(button)
        self.listButtons[1].setStyleSheet("QLabel{background: rgb(50, 255, 50)}"
                                            "QLabel:hover{background:white}")
        
        self.myListTable = MyListTable()
        self.myListTable.setStyleSheet("background:transparent")
#        self.myListTable.horizontalHeader().setStyleSheet("QHeaderView::section{background:transparent}")
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
#        hbox_ar.addWidget(self.deleteListButton)
        
        vbox_mar = QVBoxLayout()
        vbox_mar.setSpacing(7)
        vbox_mar.addWidget(self.myListTable)
        vbox_mar.addLayout(hbox_ar)
        
        hbox_nh = QHBoxLayout()
        hbox_nh.setSpacing(7)
        hbox_nh.setMargin(0)
        hbox_nh.addLayout(vbox_mar)
        hbox_nh.addLayout(vbox_no)
        
        listsLayout = QVBoxLayout()
        listsLayout.setSpacing(8)
        listsLayout.addWidget(self.allListButton)
        listsLayout.addLayout(hbox_om)
        listsLayout.addLayout(hbox_fd)
        listsLayout.addLayout(hbox_nh)

#         frame_bottom_gbox = QGridLayout(self.frameBottomWidget)
#         frame_bottom_gbox.setMargin(7)
#         frame_bottom_gbox.addWidget(self.artistHeadLabel, 0, 0, 3, 1)
#         frame_bottom_gbox.addWidget(self.musicNameLabel, 0, 1, 1, 2)
#         frame_bottom_gbox.addWidget(self.artistNameLabel, 1, 1, 1, 2)
#         frame_bottom_gbox.addWidget(self.timeLabel, 2, 1, 1, 2)
# #        frame_bottom_gbox.addItem(spacerItem, 0, 2, 1, 5)
#         frame_bottom_gbox.addWidget(self.playButton, 0, 6, 3, 1)
#         frame_bottom_gbox.addWidget(self.nextButton, 0, 7, 3, 1)
        
        homeWidget = QWidget()
        layout_list = QVBoxLayout(homeWidget)
        layout_list.setSpacing(8)
        layout_list.setMargin(0)
        layout_list.addLayout(hbox_sch)
        layout_list.addLayout(listsLayout)
#        layout_list.addWidget(self.randomOneButton)
#        layout_list.addLayout(listsLayout)

#中间的stackedWidget
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(homeWidget)
        self.stackedWidget.addWidget(self.listsFrame)
        self.stackedWidget.addWidget(self.searchFrame)
        self.stackedWidget.addWidget(self.downloadPage)

        mainLayout = QVBoxLayout(self)
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
#        for button in self.listButtons:
#            button.clicked.connect(self.switch_to_certain_page)
#        self.onlineListButton.clicked.connect(self.switch_to_certain_page)
#        self.favoriteListButton.clicked.connect(self.switch_to_certain_page)
##        self.nearplayedListButton.clicked.connect(self.switch_to_certain_page)
#        self.defaultListButton.clicked.connect(self.switch_to_certain_page)
    
    def back_to_main(self):
        self.stackedWidget.setCurrentIndex(0)
    
    def show_lists_frame(self):
        self.listsFrame.titleLabel.setText("列表管理")
        self.listsFrame.stateLabel.show()
        self.listsFrame.manageTable.show()
        self.listsFrame.musicTable.setColumnWidth(1, 300)
        self.show_lists_manage_frame_signal.emit()
        self.stackedWidget.setCurrentIndex(1)
    
    def show_search_frame(self):
        self.stackedWidget.setCurrentIndex(2)
    
    def show_download_page(self):
        self.stackedWidget.setCurrentIndex(3)
        
    def ui_initial(self):
        self.artistHeadLabel.setPixmap(QPixmap(":/iconSources/icons/anonymous.png"))
        self.lyricLabel.setText('歌词同步显示于此！')
        self.timeLabel.setText("00:00/00:00")
        self.musicNameLabel.setText("xyplayer")
        self.artistNameLabel.setText("Zheng-Yejian")
    
    def switch_to_certain_page(self, text):
        for i in range(0, self.listsFrame.manageModel.rowCount()):
            if self.listsFrame.manageModel.record(i).value("tableName") == text:
                break
#        self.listsFrame.check_actions_in_page(i)
        self.listsFrame.titleLabel.setText(text)
        self.listsFrame.stateLabel.hide()
        self.listsFrame.manageTable.hide()
        self.listsFrame.musicTable.setColumnWidth(1, 350)
#        self.listsFrame.model.initial_model(text)
#        self.listsFrame.musicTable.setModel(self.listsFrame.model)
        self.stackedWidget.setCurrentIndex(1)
        self.current_table_changed_signal.emit(i)

    def change_list_buttons_color(self, playTableOld, playTable):
        for button in self.listButtons:
            if button.name == playTableOld:
                button.setStyleSheet("QLabel{background: rgb(210,240,240)}"
                                                    "QLabel:hover{background:white}")
            if button.name == playTable:
                button.setStyleSheet("QLabel{background: rgb(50, 255, 50)}"
                                                    "QLabel:hover{background:white}")
  
    
    def add_a_widget_to_table(self, text):
            button = LabelButton(text)
            button.clicked.connect(self.switch_to_certain_page)
            button.setStyleSheet("QLabel:hover{background:white;color:green;font-size:15px}" 
                                    "QLabel{background:rgb(210,240,240);color:blue;font-size:15px}")
            self.listButtons.append(button)
            self.myListTable.add_widget(button)
 
    
        

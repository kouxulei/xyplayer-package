from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSql import QSqlTableModel
from xyplayer import Configures
from xyplayer.iconshub import IconsHub
from xyplayer.mywidgets import LabelButton
from xyplayer.mytables import TableModel, TableView, ManageTableView

class ListsFrame(QWidget):
    back_to_main_signal = pyqtSignal()
    def __init__(self, parent = None):
        super(ListsFrame, self).__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
#返回按键
        self.backButton = QPushButton(clicked = self.back_to_main_signal.emit)
        self.backButton.setFocusPolicy(Qt.NoFocus)
        self.backButton.setStyleSheet("font-size:15px")
        self.backButton.setFixedSize(25, 33)
        self.backButton.setIcon(QIcon(IconsHub.Back))
        self.backButton.setIconSize(QSize(20, 20))
 #标签 
        self.titleLabel = LabelButton("列表管理")
        self.titleLabel.setFixedSize(100, 33)
        self.titleLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.stateLabel = QLabel( "当前播放列表：默认列表")
        self.stateLabel.setStyleSheet("background:transparent;color:white")
 
        self.manageModel = QSqlTableModel()
        self.manageModel.setTable(Configures.PlaylistsManageTable)
        self.manageModel.setHeaderData(1, Qt.Horizontal, "*所有列表*")
        self.manageModel.select()
        
        self.manageTable = ManageTableView()
        self.manageTable.initial_view(self.manageModel)
        self.manageTable.setFixedWidth(90)
        
        self.model = TableModel()
        self.model.initial_model(Configures.PlaylistDefault)
        self.musicTable = TableView()
        self.musicTable.initial_view(self.model)

        self.manageTable.selectRow(1)
        self.musicTable.addMusicAction.setVisible(True)
        self.musicTable.switchToSearchPageAction.setVisible(False)
        self.manageTable.addMusicHereAction.setVisible(True)
        self.manageTable.renameTableAction.setVisible(False)
        self.manageTable.deleteTableAction.setVisible(False)
        self.manageTable.switchToSearchPageAction.setVisible(False)
        self.musicTable.downloadAction.setVisible(False)

#综合布局
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.backButton)
        hbox1.addWidget(self.titleLabel)
        hbox1.addStretch()
#        hbox1.addWidget(self.stateLabel)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.manageTable)
        hbox2.addWidget(self.musicTable)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(hbox1)
        mainLayout.addLayout(hbox2)
    
    def manage_model_remove_row(self, row):
        self.manageModel.removeRow(row)
        self.manageModel.submitAll()
        self.manageModel.select()    # this statement can't be omitted, or it's view  couldn't update 

    def check_actions_in_page(self, row):
        if row == 0:
            self.musicTable.deleteAction.setVisible(False)
            self.musicTable.addMusicAction.setVisible(False)
            self.musicTable.switchToSearchPageAction.setVisible(True)
            self.musicTable.downloadAction.setVisible(True)
            self.manageTable.addMusicHereAction.setVisible(False)
            self.manageTable.renameTableAction.setVisible(False)
            self.manageTable.deleteTableAction.setVisible(False)
            self.manageTable.switchToSearchPageAction.setVisible(True)
        elif row == 1 or row == 2 or row == 3:
            self.musicTable.deleteAction.setVisible(True)
            self.musicTable.downloadAction.setVisible(False)
            self.musicTable.addMusicAction.setVisible(True)
            self.musicTable.switchToSearchPageAction.setVisible(False)
            self.manageTable.addMusicHereAction.setVisible(True)
            self.manageTable.renameTableAction.setVisible(False)
            self.manageTable.deleteTableAction.setVisible(False)
            self.manageTable.switchToSearchPageAction.setVisible(False)
        else:
            self.musicTable.deleteAction.setVisible(True)
            self.musicTable.downloadAction.setVisible(False)
            self.musicTable.addMusicAction.setVisible(True)
            self.musicTable.switchToSearchPageAction.setVisible(False)
            self.manageTable.addMusicHereAction.setVisible(True)
            self.manageTable.renameTableAction.setVisible(True)
            self.manageTable.deleteTableAction.setVisible(True)
            self.manageTable.switchToSearchPageAction.setVisible(False)
        if row == 0 or row == 2:
            self.musicTable.markSelectedAsFavoriteAction.setVisible(False)
        else:
            self.musicTable.markSelectedAsFavoriteAction.setVisible(True)

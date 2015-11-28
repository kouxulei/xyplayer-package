from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  
from PyQt5.QtCore import *  
from xyplayer.myicons import IconsHub
from xyplayer.mypages import time_out, mount_out, settings_frame, about_page
from xyplayer.mywidgets import ToolButton, LabelButton
  
class FunctionsFrame(QLabel):  
    changeVolume = pyqtSignal(int)
    changeMuting = pyqtSignal(bool)
    def __init__(self, parent = None):  
        super(FunctionsFrame, self).__init__(parent)  
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setup_ui()
        self.create_connections()
        self.dragPosition=None  
    
    def setup_ui(self):
#        self.setStyleSheet("QLabel,QPushButton{font-family:'微软雅黑';font-size:15px;}")
        
#定时退出页面
        self.timeoutDialog = time_out.TimeoutDialog()

#计数退出页面
        self.mountoutDialog = mount_out.MountoutDialog()

#下载路径设置框
        self.settingsFrame = settings_frame.SettingsFrame()
        
#关于信息
        self.aboutPage = about_page.AboutPage()

#音量条
        self.playerMuted  = False
        self.muteButton = QToolButton(clicked=self.mute_clicked)
        self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.volumeSlider = QSlider(Qt.Horizontal, valueChanged=self.changeVolume)
        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(75)
        self.volumeSlider.setFixedSize(QSize(270, 25))
         
        self.downloadPathButton = ToolButton(IconsHub.Preference, "选项")
        self.mountoutExitButton = ToolButton(IconsHub.ExitmodeCountout, "计数退出")
        self.timeoutExitButton = ToolButton(IconsHub.ExitmodeTimeout, "定时退出")
        self.aboutButton = ToolButton(IconsHub.Info, "关于")

#标题栏标签
        self.titleLabel = QLabel('更多功能')
        self.titleLabel.setFixedWidth(70)
        self.titleLabel.setStyleSheet('color:cyan;')
        self.titlePic = LabelButton()
        self.titlePic.setStyleSheet('background:transparent')
        pixmap = QPixmap(IconsHub.Xyplayer)
        self.titlePic.setFixedSize(16, 16)
        self.titlePic.setScaledContents(True)
        self.titlePic.setPixmap(pixmap)

#返回按键
        self.backButton = QPushButton('关闭', clicked=self.show_main)
        self.backButton.setFocusPolicy(Qt.NoFocus)
        self.backButton.setStyleSheet('background:transparent;color:yellow;')
        self.backButton.setFixedWidth(60)
        
#综合布局
        titleLayout = QHBoxLayout()
        titleLayout.addSpacing(3)
        titleLayout.addWidget(self.titlePic)
        titleLayout.addWidget(self.titleLabel)
        titleLayout.addStretch()
        titleLayout.addWidget(self.backButton)

        buttonWidget = QWidget()
        buttonsLayout = QGridLayout(buttonWidget)
        buttonsLayout.addWidget(self.mountoutExitButton, 0, 0)
        buttonsLayout.addWidget(self.timeoutExitButton, 0, 1)
        buttonsLayout.addWidget(self.downloadPathButton, 1, 0)
        buttonsLayout.addWidget(self.aboutButton, 1, 1)
        
        hbox_vlmsld = QHBoxLayout()
        hbox_vlmsld.addStretch()
        hbox_vlmsld.addWidget(self.muteButton)
        hbox_vlmsld.addWidget(self.volumeSlider)
        hbox_vlmsld.addStretch()
        
#主堆栈窗口
        self.mainStack = QStackedWidget()
        self.mainStack.setFixedWidth(354)
        self.mainStack.addWidget(buttonWidget)
        self.mainStack.addWidget(self.mountoutDialog)
        self.mainStack.addWidget(self.timeoutDialog)
        self.mainStack.addWidget(self.settingsFrame)
        self.mainStack.addWidget(self.aboutPage)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 5, 0, 0)
        mainLayout.addLayout(titleLayout)
        mainLayout.addWidget(self.mainStack)
        mainLayout.addLayout(hbox_vlmsld)
        mainLayout.addSpacing(18)
    
    def create_connections(self):
        self.mountoutExitButton.clicked.connect(self.show_mountout_dialog)
        self.timeoutExitButton.clicked.connect(self.show_timeout_dialog)
        self.downloadPathButton.clicked.connect(self.show_pathset_frame)
        self.aboutButton.clicked.connect(self.show_about_page)
        self.timeoutDialog.state_message_signal.connect(self.remain_time_changed)
        self.mountoutDialog.state_message_signal.connect(self.remain_mount_changed)
    
    def remain_time_changed(self, remainTime):
        if not remainTime:
            remainTime = '定时退出'
        self.timeoutExitButton.setText(remainTime)
    
    def remain_mount_changed(self, mount):
        text = '剩下%s首'%mount
        if mount == -1:
            text = '计数退出'
        elif mount == 0:
            text = '最后１首'
        self.mountoutExitButton.setText(text)
    
    def mousePressEvent(self,event):  
        if event.button()==Qt.RightButton:  
            self.go_back()
    
    def go_back(self):
        self.show_main() 

    def show_main(self):
        if self.mainStack.currentIndex() != 0:
            self.mainStack.setCurrentIndex(0)
            self.titleLabel.setText("更多功能")
            self.backButton.setText("关闭")
        else:
            self.hide()
        
    def show_mountout_dialog(self):
        self.switch_to_page(1, "计数退出")
    
    def show_timeout_dialog(self):
        self.switch_to_page(2, "定时退出")
    
    def show_pathset_frame(self):
        self.switch_to_page(3, "选项")
    
    def show_about_page(self):
        self.switch_to_page(4, "关于")
    
    def switch_to_page(self, num, text):
        self.mainStack.setCurrentIndex(num)
        self.titleLabel.setText(text)      
        self.backButton.setText("返回")  
  
    def set_muted(self, muted):
        if muted != self.playerMuted:
            self.playerMuted = muted
            self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted if muted else QStyle.SP_MediaVolume))
    
    def mute_clicked(self):
        self.changeMuting.emit(not self.playerMuted)

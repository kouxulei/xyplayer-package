from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.phonon import Phonon
from xyplayer.mypages import time_out, mount_out, pathset_frame, about_page
from xyplayer.mywidgets import ToolButton, LabelButton
  
class SettingFrame(QLabel):  
    def __init__(self, parent = None):  
        super(SettingFrame, self).__init__(parent)  
        self.setAttribute(Qt.WA_QuitOnClose,False)
        self.setup_ui()
        self.create_connections()
        self.dragPosition=None  
    
    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("QTabWidget{background:transparent;}"
                                        "QLabel{font-family:'微软雅黑';font-size:15px;color:white;}")
        
#定时退出页面
        self.timeoutDialog = time_out.TimeoutDialog()

#计数退出页面
        self.mountoutDialog = mount_out.MountoutDialog()

#下载路径设置框
        self.pathsetFrame = pathset_frame.PathsetFrame()
        
#关于信息
        self.aboutPage = about_page.AboutPage()

#音量条
        self.volumeSlider = Phonon.VolumeSlider(self)
        self.volumeSlider.setFixedSize(QSize(270, 25))
         
        self.downloadPathButton = ToolButton(":/iconSources/icons/download_path.png", "下载路径")
        self.mountoutExitButton = ToolButton(":/iconSources/icons/mountout_exit.png", "计数退出")
        self.timeoutExitButton = ToolButton(":/iconSources/icons/timeout_exit.png", "定时退出")
        self.aboutButton = ToolButton(":/iconSources/icons/info.png", "关于")

#标题栏标签
        self.titleLabel = QLabel('个人设置')
        self.titleLabel.setFixedWidth(60)
        self.titlePic = LabelButton()
        pixmap = QPixmap(":/iconSources/icons/more_functions.png")
        self.titlePic.setFixedSize(15, 15)
        self.titlePic.setScaledContents(True)
        self.titlePic.setPixmap(pixmap)

#状态栏标签
        self.stateLabel = QLabel()
        self.stateLabel.setFixedHeight(25)
#        self.stateLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.stateLabel.setStyleSheet("font-family:'微软雅黑';font-size:14px;color:red")
#        self.stateLabel.setStyleSheet("background:transparent")

#返回按键
        self.backButton = QPushButton()
        self.backButton.setFixedSize(50, 30)
        
        
#综合布局
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(self.titlePic)
        titleLayout.addWidget(self.titleLabel)
        titleLayout.addSpacing(6)
        titleLayout.addWidget(self.stateLabel)

        buttonWidget = QWidget()
        buttonsLayout = QGridLayout(buttonWidget)
        buttonsLayout.addWidget(self.mountoutExitButton, 0, 0)
        buttonsLayout.addWidget(self.timeoutExitButton, 0, 1)
        buttonsLayout.addWidget(self.downloadPathButton, 1, 0)
        buttonsLayout.addWidget(self.aboutButton, 1, 1)
        
        hbox_vlmsld = QHBoxLayout()
        hbox_vlmsld.addSpacing(0)
        hbox_vlmsld.addWidget(self.volumeSlider)
        
#主堆栈窗口
        self.mainStack = QStackedWidget()
        self.mainStack.setFixedWidth(345)
        self.mainStack.addWidget(buttonWidget)
#        self.mainStack.setStyleSheet('background:black')
        self.mainStack.addWidget(self.mountoutDialog)
        self.mainStack.addWidget(self.timeoutDialog)
        self.mainStack.addWidget(self.pathsetFrame)
        self.mainStack.addWidget(self.aboutPage)

        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(5)
        mainLayout.setMargin(5)
        mainLayout.addLayout(titleLayout)
#        mainLayout.addWidget(self.stateLabel)
        mainLayout.addSpacing(3)
        mainLayout.addWidget(self.mainStack)
        mainLayout.addSpacing(5)
        mainLayout.addLayout(hbox_vlmsld)
        mainLayout.addSpacing(25)
    
    def create_connections(self):
        self.titlePic.clicked.connect(self.show_main)
        self.mountoutExitButton.clicked.connect(self.show_mountout_dialog)
        self.timeoutExitButton.clicked.connect(self.show_timeout_dialog)
        self.downloadPathButton.clicked.connect(self.show_pathset_frame)
        self.aboutButton.clicked.connect(self.show_about_page)
        self.timeoutDialog.state_message_signal.connect(self.state_message_changed)
        self.mountoutDialog.state_message_signal.connect(self.state_message_changed)
    
    def state_message_changed(self, message, flag):
        messageList = self.stateLabel.text().split('  ')
        timeMessage = messageList[0]
        try:
            countMessage = messageList[1]
        except:
            countMessage = ''
        if flag == 1:
            timeMessage = message
        if flag == 0:
            countMessage = message
        self.stateLabel.setText(timeMessage + '  ' + countMessage )
    
    def mousePressEvent(self,event):  
        if event.button()==Qt.RightButton:  
            if self.mainStack.currentIndex() != 0:
                self.show_main()
            else:
                self.close()  

    def show_main(self):
        if self.mainStack.currentIndex() != 0:
            self.mainStack.setCurrentIndex(0)
            self.titleLabel.setText("个人设置")
        
    def show_mountout_dialog(self):
        self.mainStack.setCurrentIndex(1)
        self.titleLabel.setText("计数退出")
    
    def show_timeout_dialog(self):
        self.mainStack.setCurrentIndex(2)
        self.titleLabel.setText("定时退出")
    
    def show_pathset_frame(self):
        self.mainStack.setCurrentIndex(3)
        self.titleLabel.setText("下载路径")
    
    def show_about_page(self):
        self.mainStack.setCurrentIndex(4)
        self.titleLabel.setText("关于")
    

from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.phonon import Phonon
from xyplayer.mywidgets import ToolButton
  
class SettingFrame(QLabel):  
    def __init__(self, parent = None):  
        super(SettingFrame, self).__init__(parent)  
        self.setAttribute(Qt.WA_QuitOnClose,False)
        self.setup_ui()
        self.dragPosition=None  
    
    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
#        self.titleLabel = QLabel("sdfadfasf")
#音量条
        self.volumeSlider = Phonon.VolumeSlider(self)
        self.volumeSlider.setFixedSize(QSize(270, 25))
#        self.volumeSlider.setIconSize(QSize(25, 25))
#        self.volumeSlider.setStyleSheet("background:transparent")
         
        self.downloadPathButton = ToolButton(":/iconSources/icons/download_path.png", "下载路径")
        self.mountoutExitButton = ToolButton(":/iconSources/icons/mountout_exit.png", "计数退出")
        self.timeoutExitButton = ToolButton(":/iconSources/icons/timeout_exit.png", "定时退出")
        self.aboutButton = ToolButton(":/iconSources/icons/info.png", "关于播放器")
        
#综合布局
        buttonsLayout = QGridLayout()
        buttonsLayout.addWidget(self.mountoutExitButton, 0, 0)
        buttonsLayout.addWidget(self.timeoutExitButton, 0, 1)
        buttonsLayout.addWidget(self.downloadPathButton, 1, 0)
        buttonsLayout.addWidget(self.aboutButton, 1, 1)
#        buttonsLayout.addWidget(self.volumeSlider, 2, 0, 1, 2)
        
        hbox_vlmsld = QHBoxLayout()
        hbox_vlmsld.addSpacing(0)
        hbox_vlmsld.addWidget(self.volumeSlider)
        vbox_vlmsld = QVBoxLayout()
        vbox_vlmsld.addSpacing(40)
        vbox_vlmsld.addLayout(hbox_vlmsld)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setMargin(0)
        mainLayout.addSpacing(25)
        mainLayout.addLayout(buttonsLayout)
        mainLayout.addLayout(vbox_vlmsld)
#        mainLayout.addWidget(self.volumeSlider)
#        mainLayout.addSpacing(0)
    
    def mousePressEvent(self,event):  
#        if event.button()==Qt.LeftButton:  
#            self.dragPosition=event.globalPos()-self.frameGeometry().topLeft()  
#            event.accept()  
        if event.button()==Qt.RightButton:  
            self.close()  
#  
#    def mouseMoveEvent(self,event):  
#        if event.buttons() & Qt.LeftButton:  
#            moveVector = event.globalPos()-self.dragPosition
#            self.move(moveVector)  
#            event.accept()  

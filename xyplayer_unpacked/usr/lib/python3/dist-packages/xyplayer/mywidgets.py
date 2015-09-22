import os
from PyQt4.QtGui import (QPushButton, QPixmap, QPainter, QLabel, QToolButton, QLinearGradient, 
                                        QColor, QIcon, QPalette, QFont, QVBoxLayout, QHBoxLayout)
from PyQt4.QtCore import pyqtSignal, Qt, QSize
from xyplayer.configure import Configures

class PushButton(QPushButton):
    def __init__(self,parent = None):
        super(PushButton,self).__init__(parent)
        self.status = 0 
        
    def loadPixmap(self, pic_name):	
        self.pixmap = QPixmap(pic_name)
        self.btn_width = self.pixmap.width()/4
        self.btn_height = self.pixmap.height()
        self.setFixedSize(self.btn_width, self.btn_height)
        
        
    def enterEvent(self,event):	
        self.status = 1 
        self.update()
        
        
    def mousePressEvent(self,event):	
#        if(event.button() == Qt.LeftButton):		
        self.mouse_press = True
        self.status = 2 
        self.update()		
            
    def mouseReleaseEvent(self,event):	
        if(self.mouse_press):		
            self.mouse_press = False
            self.status = 3 
            self.update()
            self.clicked.emit(True)		
            
    def leaveEvent(self,event):	
        self.status = 0 
        self.update()
        
        
    def paintEvent(self,event):	
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.drawPixmap(self.rect(), self.pixmap.copy(self.btn_width * self.status, 0, self.btn_width, self.btn_height))
        self.painter.end()
            
class ToolButton(QToolButton):
    def __init__(self,pic_name, text = '', parent = None):
        super(ToolButton,self).__init__(parent)
        
        #设置图标
        self.pixmap= QPixmap(pic_name) 
        self.setIcon(QIcon(self.pixmap))
        self.setIconSize(self.pixmap.size())
        #设置大小
        self.setFixedSize(self.pixmap.width()+25, self.pixmap.height()+27)
        self.setAutoRaise(True)
        
        #设置文本颜色
        self.text_palette = QPalette()
        self.text_palette.setColor(self.text_palette.ButtonText, QColor(230, 230, 230))
        self.setPalette(self.text_palette)
        
        #设置文本粗体
        self.setText(text)
        self.text_font = QFont()
        self.text_font.setWeight(QFont.Bold)
        
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.setStyleSheet("background:transparent")
        self.mouse_over  = False#鼠标是否移过
        self.mouse_press = False#鼠标是否按下
        
    def enterEvent(self,event):
        self.mouse_over = True
        self.update()
        
    def leaveEvent(self,event):
        self.mouse_over = False
        self.update()
        
    def mousePressEvent(self,event):
        if(event.button() == Qt.LeftButton):		
            self.clicked.emit(True)
    
    def setMousePress(self, mouse_press):
        self.mouse_press = mouse_press
        self.update()
        
    def paintEvent(self,event):
        if(self.mouse_over):
            #绘制鼠标移到按钮上的按钮效果
            self.painterInfo(0, 100, 150)
        else:
            if(self.mouse_press):
                self.painterInfo(0, 100, 150)
        QToolButton.paintEvent(self,event)
    
    def painterInfo(self,top_color,middle_color,bottom_color):
        self.painter = QPainter()
        self.painter.begin(self)
        #self.pen = QPen()
        #self.pen.setWidth(0)
        self.painter.setPen(Qt.NoPen)
        
        self.linear = QLinearGradient(self.rect().topLeft(),self.rect().bottomLeft())
#        self.linear = QLinearGradient(self.rect().topLeft(),self.rect().topRight())
        #self.linear.start()
        self.linear.setColorAt(0.2, QColor(230, 230, 230, top_color))
        self.linear.setColorAt(0.5, QColor(230, 230, 230, middle_color))
        self.linear.setColorAt(1, QColor(230, 230, 230, bottom_color))
        #self.linear.finalStop()
        
        self.painter.setBrush(self.linear)
        #self.painter.fillRect(self.rect(),Qt.LinearGradientPattern)
        self.painter.drawRect(self.rect()) #
        self.painter.end()      

class LabelButton(QLabel):
    clicked = pyqtSignal(str)
    def __init__(self, text = None, height = 36, icon = None):
        super(LabelButton, self).__init__()
        self.setFixedHeight(height)
        self.setText(text)
        self.name = text
        self.setAlignment(Qt.AlignHCenter| Qt.AlignVCenter)
        self.setStyleSheet("font-family:'微软雅黑';font-size:15px;")
        self.setScaledContents(True)
        if icon:
            self.setPixmap(QPixmap(icon))
    
    def set_text(self, text):
        self.setText(text)
        self.name = text
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.name)
            
class SpecialLabel(LabelButton):
    def __init__(self, text = None, height = 36, icon = None):
        super(SpecialLabel, self).__init__(text, height, icon)
        self.ratio = 0
    
    def setGradient(self, ratio):
        self.ratio = ratio
        self.update()
    
    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setPen(Qt.NoPen)

        self.linear = QLinearGradient(self.rect().topLeft(),self.rect().topRight())
        self.linear.setColorAt(1, QColor(50, 255, 50))
        
        self.painter.setBrush(self.linear)
        self.painter.drawRect(0, 0, self.ratio * self.rect().width(), self.rect().height())
        self.painter.end()      

class NewListWidget(QLabel):
    play_button_clicked_signal = pyqtSignal(str)
    info_button_clicked_signal = pyqtSignal(str)
    def __init__(self, title):
        super(NewListWidget, self).__init__()
        self.setFixedSize(335, 85)
        self.name = title
        self.setStyleSheet("QToolButton{background:transparent}"
                                    "QToolButton:hover{border:1px solid yellow;border-radius:16px;background:yellow}")
        try:
            artistName = title.split('._.')[0]
            musicName = title.split('._.')[1]
        except:
            artistName = '未知'
            musicName = title
        imageName = artistName + '.jpg'
        imagePath = os.path.join(Configures.imagesDir, imageName)
        if not os.path.exists(imagePath):
            imagePath = ":/iconSources/icons/anonymous.png"
        self.artistPicture = QLabel()
        self.artistPicture.setFixedSize(60, 60)
        self.artistPicture.setScaledContents(True)
        self.artistPicture.setPixmap(QPixmap(imagePath))
        self.musicNameLabel = QLabel(musicName)
        self.artistNameLabel = QLabel(artistName)
        self.musicNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:20px;color: white;")
        self.artistNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:14px;color: white;")
        
        self.infoButton = QToolButton(clicked = self.info_button_clicked)
        self.infoButton.setIcon(QIcon(":/iconSources/icons/info.png"))
        self.infoButton.setIconSize(QSize(25, 25))
        self.playButton = QToolButton(clicked = self.play_button_clicked)
        self.playButton.setIcon(QIcon(":/iconSources/icons/play.png"))
        self.playButton.setIconSize(QSize(25, 25))
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.musicNameLabel)
        vbox.addWidget(self.artistNameLabel)
        
        mainLayout = QHBoxLayout(self)
        mainLayout.addWidget(self.artistPicture)
        mainLayout.addLayout(vbox)
        mainLayout.addWidget(self.playButton)
        mainLayout.addWidget(self.infoButton)
    
    def play_button_clicked(self):
        self.play_button_clicked_signal.emit(self.name)
    
    def info_button_clicked(self):
        self.info_button_clicked_signal.emit(self.name)

    def mousePressEvent(self, event):
        pass
         
    
    
    
    
    

import os
import random
from PyQt5.QtWidgets import QPushButton, QLabel, QToolButton, QWidget, QTextEdit, QProgressBar
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QCursor,  QColor, QIcon, QPalette, QFont
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from xyplayer import Configures
from xyplayer.iconshub import IconsHub
from xyplayer.utils import convert_B_to_MB

class MyTextEdit(QTextEdit):
    def __init__(self, parent = None):
        super(MyTextEdit, self).__init__(parent)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton or event.button() == Qt.LeftButton:
            self.setCursor(QCursor(Qt.ArrowCursor))
            event.accept()
        
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

        self.setStyleSheet("background:transparent;color:black;")
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
            self.painterInfo(0, 150, 255)
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
        self.linear.setColorAt(0.2, QColor(0, 255, 0, top_color))
        self.linear.setColorAt(0.5, QColor(0, 255, 0, middle_color))
        self.linear.setColorAt(1, QColor(0, 255, 0, bottom_color))
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
        self.setStyleSheet("QLabel{background:rgb(210,240,240);color:blue;font-family:'微软雅黑';font-size:15px;}"
            "QLabel:hover{background:white;color:green;font-family:'微软雅黑';font-size:15px}")
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
        self.cl = [50, 255, 50]
        self.color1 = QColor(255, 50, 50)
        self.color2 = QColor(50, 255, 50)

    def setGradient(self, ratio):
        self.ratio = ratio
        self.change_color(ratio)
        self.update()

    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setPen(Qt.NoPen)

        self.linear = QLinearGradient(self.rect().topLeft(),self.rect().topRight())
        self.linear.setColorAt(1, self.color1)

        self.painter.setBrush(self.linear)
        self.painter.drawRect(1, 1, self.ratio * self.rect().width(), 5)
        self.linear.setColorAt(1, self.color2)
        self.painter.setBrush(self.linear)
        self.painter.drawRect(1, self.rect().height()-6, self.ratio * self.rect().width(), 5)
        self.painter.end()      
    
    def change_color(self, ratio):
        self.cl[0] = random.randint(0, 255)
        self.cl[1] = 255
        self.cl[2] = 0
        q = self.cl[0] % 3
        self.color1 = QColor(self.cl[q], self.cl[q-1], self.cl[q-2])
        self.color2 = QColor(self.cl[q-1], self.cl[q-2], self.cl[q])

class NewListWidget(QWidget):
    """playbackPage的“我的歌单”的列表项"""
    play_button_clicked_signal = pyqtSignal(str)
    info_button_clicked_signal = pyqtSignal(str)
    def __init__(self, ident, title):
        super(NewListWidget, self).__init__()
        self.setFixedSize(334, 84)
        self.ident = ident
        self.isPaused = True
        self.artistHeadIconSetted = False
        self.setStyleSheet("QToolButton{background:transparent}"
                                    "QToolButton:hover{border:0px solid yellow;border-radius:18px;background:yellow}")
        self.setFocusPolicy(Qt.NoFocus)
        try:
            artistName = title.split('._.')[0]
            musicName = title.split('._.')[1]
        except:
            artistName = '未知'
            musicName = title
        imageName = artistName + '.jpg'
        self.imagePath = os.path.join(Configures.imagesDir, imageName)
        self.artistPicture = QLabel(self)
        self.artistPicture.setScaledContents(True)
        if os.path.exists(self.imagePath):
            self.artistPicture.setPixmap(QPixmap(self.imagePath))
            self.artistHeadIconSetted = True
        else:
            self.artistPicture.setPixmap(QPixmap(IconsHub.Anonymous))
        self.musicNameLabel = QLabel(musicName, self)
        self.artistNameLabel = QLabel(artistName, self)
        self.musicNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:20px;color: white;")
        self.artistNameLabel.setStyleSheet("font-family:'微软雅黑';font-size:14px;color: white;")
        self.infoButton = QToolButton(self, clicked = self.info_button_clicked)
        self.infoButton.setIcon(QIcon(IconsHub.Info))
        self.infoButton.setIconSize(QSize(36, 36))
        self.playButton = QToolButton(self, clicked = self.play_button_clicked)
        self.playButton.setIcon(QIcon(IconsHub.ControlPlay))
        self.playButton.setIconSize(QSize(36, 36))

        self.artistPicture.setGeometry(10,  10,  64, 64)
        self.musicNameLabel.setGeometry(84, 10, 154, 30)
        self.artistNameLabel.setGeometry(84, 54, 154, 20)
        self.playButton.setGeometry(250, 22, 36, 36) 
        self.infoButton.setGeometry(295, 22, 36, 36)

    def set_pause_state(self, isPaused):
        self.isPaused = isPaused
        if isPaused:
            self.playButton.setIcon(QIcon(IconsHub.ControlPlay))
        else:
            self.playButton.setIcon(QIcon(IconsHub.ControlPause))
        self.check_artist_headicon_seted()
    
    def play_button_clicked(self):
        self.isPaused = not self.isPaused
        iconPath = IconsHub.ControlPlay
        if self.isPaused:
            iconPath = IconsHub.ControlPause
        self.playButton.setIcon(QIcon(iconPath))
        self.play_button_clicked_signal.emit(self.ident)
        self.check_artist_headicon_seted()

    def info_button_clicked(self):
        self.info_button_clicked_signal.emit(self.ident)
        self.check_artist_headicon_seted()

    def check_artist_headicon_seted(self):
        if not self.artistHeadIconSetted and os.path.exists(self.imagePath):
            self.artistPicture.setPixmap(QPixmap(self.imagePath))
            self.artistHeadIconSetted = True

class NewLabel(QLabel):
    """可以以跑马灯显示超出本事长度文字的标签"""
    def __init__(self, parent = None, drawCenter=False):
        super(NewLabel, self).__init__(parent)
        self.myTimerId = 0
        self.timer_interval = 300
        self.step = 3
        self.init_pos = 15
        self.setText('')
        self.drawCenter = drawCenter

    def setText(self, text):
        self.myText = text
        self.textWidth = self.fontMetrics().width(text)
        self.initial_timer()
        self.update()
    
    def initial_timer(self):
        if self.textWidth < self.width():
            self.offset = 0
#            self.kill_timer()
        else:
            self.offset = -self.init_pos
            self.start_timer()
    
    def setParameters(self, timer_interval, step, init_pos):
        self.timer_interval = timer_interval
        self.step = step
        self.init_pos = init_pos

    def text(self):
        return self.myText

    def timerEvent(self, event):
        if event.timerId() == self.myTimerId:
            self.offset += self.step
        if self.offset >= (self.textWidth - self.width() + self.init_pos):
            self.offset = -self.init_pos
        self.update()

    def paintEvent(self, event):
        if self.textWidth < 1:
            return
        self.painter = QPainter()
        self.painter.begin(self)
        if self.textWidth < self.width():
            x = 0
            if self.drawCenter:
                x = 0.5*(self.width() - self.textWidth)
        else:
            x = -self.offset
        self.painter.drawText(x, 0, self.textWidth, self.height(), Qt.AlignLeft | Qt.AlignVCenter, self.text())
        self.painter.end()
        
#    def showEvent(self, event):
#        self.initial_timer()
    
#    def hideEvent(self, event):
#        self.kill_timer()
#
#    def kill_timer(self):
#        self.killTimer(self.myTimerId) 
    
    def start_timer(self):
        self.myTimerId = self.startTimer(self.timer_interval)

class DownloadListItem(QLabel):
    """下载任务列表项"""
    downloadStatusChanged = pyqtSignal(str, bool)
    killWork = pyqtSignal(str)
    def __init__(self, ident, title, timeSpan=1, parent=None):
        super(DownloadListItem, self).__init__(parent)
        self.ident = ident
        self.title = title
        self.timeSpan = timeSpan / 1000    #计算网速的时间间隔
        self.netSpeed = 0
        self.isPaused = False
        self.setup_ui()
    
    def setup_ui(self):
        self.setObjectName('downloadlistitem')
        self.setStyleSheet('color:green;')
        self.setFixedSize(340, 85)
        self.pauseButton = QToolButton(self, clicked=self.pause_button_clicked)
        self.pauseButton.setIcon(QIcon(IconsHub.DownloadPause))
        self.pauseButton.setIconSize(QSize(45, 45))
        self.killButton = QToolButton(self, clicked=self.kill_button_clicked)
        self.killButton.setIcon(QIcon(IconsHub.DownloadKill))
        self.killButton.setIconSize(QSize(23, 23))
        self.titleLabel = QLabel(self.title, self)
        self.titleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.progressBar = QProgressBar(self)
        self.progressBar.setValue(0)
        self.progressBar.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.sizeProgressLabel = QLabel('0.0MB / 0.0MB', self)
        self.sizeProgressLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.statusLabel = QLabel('准备下载', self)
        self.statusLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.pauseButton.setGeometry(3, 16, 52, 52)
        self.killButton.setGeometry(312, 8, 23, 23)
        self.titleLabel.setGeometry(58, 12, 252, 18)
        self.progressBar.setGeometry(58, 37, 276, 15)
        self.sizeProgressLabel.setGeometry(58, 51, 160, 30)
        self.statusLabel.setGeometry(235, 51, 100, 30)
    
    def set_pause_state(self, state, statusInfo='已暂停'):
        """当发现线程暂停时，对 应修改任务列表项的暂停状态。"""
        self.isPaused = state
        self.pauseButton.setIcon(QIcon(IconsHub.DownloadStart))
        self.statusLabel.setText(statusInfo)
    
    def download_completed(self):
        self.progressBar.setValue(self.progressBar.maximum())
        self.progressBar.update()
        self.statusLabel.setText('已完成')
        self.pauseButton.setIcon(QIcon(IconsHub.DownloadCompleted))
    
    def set_timespan(self, t):
        if t <= 0:
            t = 1
        self.timeSpan = t / 1000
    
    def update_progress(self, currentLength, totalLength):
        currentLength = int(currentLength)
        totalLength = int(totalLength)
        if self.progressBar.maximum() != totalLength:
            self.progressBar.setRange(0, totalLength)
        oldLength = self.progressBar.value()
        self.progressBar.setValue(currentLength)
        self.progressBar.update()
        self.sizeProgressLabel.setText('%.1fMB / %.1fMB'%(convert_B_to_MB(currentLength), convert_B_to_MB(totalLength)))
        self.netSpeed = (currentLength - oldLength) / (1024 * self.timeSpan)
        self.statusLabel.setText('%.2f KB/s'%self.netSpeed)
    
    def get_net_speed(self):
        return self.netSpeed
    
    def pause_button_clicked(self):
        self.isPaused = not self.isPaused
        iconPath = IconsHub.DownloadStart
        statusInfo = '已暂停'
        if not self.isPaused:
            iconPath = IconsHub.DownloadPause
            statusInfo = '0.00 KB/s'
        self.pauseButton.setIcon(QIcon(iconPath))
        self.statusLabel.setText(statusInfo)
        self.downloadStatusChanged.emit(self.ident, self.isPaused)
    
    def kill_button_clicked(self):
        self.killWork.emit(self.ident)




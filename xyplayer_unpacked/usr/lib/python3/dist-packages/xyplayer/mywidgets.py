import os
import random
import time
from PyQt5.QtWidgets import (QPushButton, QLabel, QToolButton, QWidget, QTextEdit, QProgressBar, 
    QColorDialog, QComboBox, QHBoxLayout, QVBoxLayout, QGroupBox, QRadioButton, QLineEdit, QFileDialog)
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QCursor,  QColor, QIcon, QPalette, QFont
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QTimer
from xyplayer import Configures
from xyplayer.myicons import IconsHub
from xyplayer.mysettings import globalSettings, configOptions
from xyplayer.utils import convert_B_to_MB, get_artist_and_musicname_from_title, system_fonts

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
    
    def start_timer(self):
        self.myTimerId = self.startTimer(self.timer_interval)

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
        self.pixmap= QPixmap(pic_name) 
        self.setIcon(QIcon(self.pixmap))
        self.setIconSize(self.pixmap.size())
        self.setFixedSize(self.pixmap.width()+25, self.pixmap.height()+27)
        self.setAutoRaise(True)
        self.text_palette = QPalette()
        self.text_palette.setColor(self.text_palette.ButtonText, QColor(230, 230, 230))
        self.setPalette(self.text_palette)
        self.setText(text)
        self.text_font = QFont()
        self.text_font.setWeight(QFont.Bold)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setStyleSheet("background:transparent;color:black;font-size:16px")
        self.mouse_over  = False
        self.mouse_press = False

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
            self.painterInfo(0, 150, 255)
        else:
            if(self.mouse_press):
                self.painterInfo(0, 100, 150)
        QToolButton.paintEvent(self,event)

    def painterInfo(self,top_color,middle_color,bottom_color):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setPen(Qt.NoPen)

        self.linear = QLinearGradient(self.rect().topLeft(),self.rect().bottomLeft())
        self.linear.setColorAt(0.2, QColor(0, 255, 0, top_color))
        self.linear.setColorAt(0.5, QColor(0, 255, 0, middle_color))
        self.linear.setColorAt(1, QColor(0, 255, 0, bottom_color))

        self.painter.setBrush(self.linear)
        self.painter.drawRect(self.rect()) #
        self.painter.end()      

class ColorButton(QWidget):
    """选择桌面歌词颜色的按键"""
    new_color_signal = pyqtSignal()
    def __init__(self, index=0, color=QColor(255, 255, 0)):
        super(ColorButton, self).__init__()
        self.setMinimumHeight(10)
        self.color = color
        self.index = index
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            color = QColorDialog.getColor(initial=self.color, title='颜色选择 #%i'%(self.index+1))
            if color.isValid() and color != self.color:
                self.set_color(color)
    
    def set_color(self, color):
        self.color = color
        self.update()
        self.new_color_signal.emit()
    
    def get_color(self):
        return self.color
    
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.fillRect(self.rect(), self.color)
        painter.end()

class LabelButtonBasic(QLabel):
    clicked = pyqtSignal(str)
    def __init__(self, text='', parent=None):
        super(LabelButtonBasic, self).__init__(parent)
        self.name = text
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.name)

class LabelButton(LabelButtonBasic):
    def __init__(self, text = None, height = 36, icon = None):
        super(LabelButton, self).__init__(text)
        self.setFixedHeight(height)
        self.setText(self.name)
        self.setAlignment(Qt.AlignHCenter| Qt.AlignVCenter)
        self.setStyleSheet("QLabel{background:rgb(210,240,240);color:blue;font-family:'微软雅黑';font-size:15px;}"
            "QLabel:hover{background:white;color:green;font-family:'微软雅黑';font-size:15px}")
        self.setScaledContents(True)
        if icon:
            self.setPixmap(QPixmap(icon))

    def set_text(self, text):
        self.setText(text)
        self.name = text

class PlaylistButton(QLabel):
    clicked = pyqtSignal(str)
    long_time_clickd = pyqtSignal()
    remove_me_signal = pyqtSignal(str)
    rename_me_signal = pyqtSignal(str)
    def __init__(self, name = '', removable=False):
        super(PlaylistButton, self).__init__()
        self.setFixedSize(QSize(172, 36))
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.name = name
        self.setText(name)
        self.removable = removable
        self.operateState = False
        self.setup_ui()
        self.setStyleSheet("QLabel{background:rgb(210,240,240);color:blue;font-family:'微软雅黑';font-size:15px;}"
            "QLabel:hover{background:white;color:green;font-family:'微软雅黑';font-size:15px}")
        self.timerFlag = False
        self.startTime = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_press_time)
    
    def setup_ui(self):
        self.nameLabel = LabelButtonBasic()
        self.nameLabel.setVisible(False)
        self.nameLabel.clicked.connect(self.rename_button_clicked)
        self.nameLabel.setStyleSheet("background:transparent;")
        self.nameLabel.setText(self.name)
        self.nameLabel.setFixedSize(140, 30)
        self.killLabel = LabelButtonBasic()
        self.killLabel.setVisible(False)
        self.killLabel.clicked.connect(self.remove_button_clicked)
        self.killLabel.setFixedSize(QSize(25, 25))
        self.killLabel.setScaledContents(True)
        self.killLabel.setPixmap(QPixmap(IconsHub.RemovePlaylist))
        self.nameLabel.setAlignment(Qt.AlignHCenter| Qt.AlignVCenter)
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(5, 0, 5, 0)
        mainLayout.addWidget(self.killLabel)
        mainLayout.addStretch()
        mainLayout.addWidget(self.nameLabel)
    
    def set_remove_mode(self):
        if self.removable:
            self.setText('')
            self.nameLabel.setVisible(True)
            self.killLabel.setVisible(True)
        self.operateState = True
    
    def set_normal_mode(self):
        if self.removable:
            self.setText(self.name)
            self.nameLabel.setVisible(False)
            self.killLabel.setVisible(False)
        self.operateState = False
    
    def set_name(self, text):
        self.name = text
        if self.operateState:
            self.nameLabel.setText(self.name)
        else:
            self.setText(self.name)

    def get_name(self):
        return self.name
    
    def rename_button_clicked(self):
        self.styleDesc = self.styleSheet()
        self.setStyleSheet("background:rgb(255,0,255);")
        self.rename_me_signal.emit(self.name)
    
    def set_normal_style_sheet(self):
        self.setStyleSheet(self.styleDesc)       
    
    def remove_button_clicked(self):
        self.styleDesc = self.styleSheet()
        self.setStyleSheet("background:rgb(255,0,255);")
        self.remove_me_signal.emit(self.name)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.operateState:
                self.timerFlag = True
                self.startTime = time.time()
                self.timer.start(50)
    
    def mouseReleaseEvent(self, event):
        if not self.operateState and time.time() - self.startTime < 0.6:
            self.timer.stop()
            self.clicked.emit(self.name)          
    
    def check_press_time(self):
        if self.timerFlag:
            if time.time() - self.startTime >= 0.6:
                self.timer.stop()
                self.long_time_clickd.emit()
        
class SpecialLabel(QLabel):
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super(SpecialLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignHCenter| Qt.AlignVCenter)
        self.setStyleSheet("QLabel{background:rgb(210,240,240);color:blue;font-family:'微软雅黑';font-size:15px;}"
            "QLabel:hover{background:white;color:green;font-family:'微软雅黑';font-size:15px}")
        self.setScaledContents(True)
        self.ratio = 0
        self.cl = [50, 255, 50]
        self.color1 = QColor(255, 50, 50)
        self.color2 = QColor(50, 255, 50)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

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
        artistName, musicName = get_artist_and_musicname_from_title(title)
        imageName = artistName + '.jpg'
        self.imagePath = os.path.join(Configures.ImagesDir, imageName)
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
        self.titleLabel = NewLabel(self)
        self.titleLabel.setText(self.title)
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


#FontPanel,ColorsPanel,CloseActionsBox均在settings_frame.py中用到

class FontPanel(QWidget):
    """用来调整桌面歌词字体的板块，放在settings_frame中使用。"""
    font_style_changed = pyqtSignal(str, str)
    def __init__(self, parent=None):
        super(FontPanel, self).__init__(parent)
        self.setup_ui()
        self.create_connections()
        self.fill_family_combo()
        self.fill_size_combo()
        self.fill_form_combo()
    
    def create_connections(self):
        self.familyCombo.currentTextChanged.connect(self.family_combo_text_changed)
        self.sizeCombo.currentTextChanged.connect(self.size_combo_text_changed)
        self.formCombo.currentTextChanged.connect(self.form_combo_text_changed)
    
    def setup_ui(self):
        label1 = QLabel('字体:', self)
        label2 = QLabel('字号:', self)
        label3 = QLabel('字型:', self)
        self.familyCombo = QComboBox(self)
        self.familyCombo.setFixedWidth(95)
        self.sizeCombo = QComboBox(self)
        self.sizeCombo.setFixedWidth(50)
        self.formCombo = QComboBox(self)
        self.formCombo.setFixedWidth(60)
        
        mainLayout = QHBoxLayout(self)
        mainLayout.setSpacing(2)
        mainLayout.setContentsMargins(0, 2, 0, 4)
        mainLayout.addWidget(label1)
        mainLayout.addWidget(self.familyCombo)
        mainLayout.addStretch()
        mainLayout.addWidget(label2)
        mainLayout.addWidget(self.sizeCombo)
        mainLayout.addStretch()
        mainLayout.addWidget(label3)
        mainLayout.addWidget(self.formCombo)
    
    def fill_family_combo(self):
        self.familys = system_fonts
        self.fill_combo_common(self.familyCombo, self.familys)
    
    def fill_size_combo(self):
        self.sizes = Configures.SettingsFontSizes
        self.fill_combo_common(self.sizeCombo, self.sizes)
    
    def fill_form_combo(self):
        self.forms = Configures.SettingsFontForms
        self.fill_combo_common(self.formCombo, self.forms)
        
    def fill_combo_common(self, combo, values):
        for value in values:
            combo.addItem(str(value))
    
    def family_combo_text_changed(self, text):
        self.font_style_changed.emit(globalSettings.optionsHub.DesktoplyricFontFamily, text)
    
    def size_combo_text_changed(self, text):
        self.font_style_changed.emit(globalSettings.optionsHub.DesktoplyricFontSize, text)
    
    def form_combo_text_changed(self, text):
        self.font_style_changed.emit(globalSettings.optionsHub.DesktoplyricFontForm, text)
    
    def get_font_style(self):
        return (self.familyCombo.currentText(), int(self.sizeCombo.currentText()), self.formCombo.currentText())
    
    def set_font_style(self, family, size, form):
        self.familyCombo.setCurrentIndex(self.familys.index(family))
        self.sizeCombo.setCurrentIndex(self.sizes.index(size))
        self.formCombo.setCurrentIndex(self.forms.index(form))
    
    def restore_default_font_style(self):
        self.set_font_style(
            configOptions[globalSettings.optionsHub.DesktoplyricFontFamily], 
            configOptions[globalSettings.optionsHub.DesktoplyricFontSize], 
            configOptions[globalSettings.optionsHub.DesktoplyricFontForm]
        )

class ColorsPanel(QWidget):
    color_changed = pyqtSignal()
    def __init__(self, parent=None):
        super(ColorsPanel, self).__init__(parent)
        self.setup_ui()
        self.create_connections()
    
    def create_connections(self):
        for button in self.colorButtons:
            button.new_color_signal.connect(self.color_of_button_changed)
    
    def setup_ui(self):
        self.colorButtons = []
        colorsLayout = QVBoxLayout(self)
        colorsLayout.setContentsMargins(0, 0, 0, 0)
        colorsLayout.setSpacing(5)
        for index in range(3):
            colorButton = ColorButton(index)
            self.colorButtons.append(colorButton)
            colorsLayout.addWidget(colorButton)
    
    def color_of_button_changed(self):
        self.color_changed.emit()
    
    def get_colors(self):
        return tuple(button.get_color() for button in self.colorButtons)
    
    def set_colors(self, colors):
        for i, color in enumerate(colors):
            self.colorButtons[i].set_color(color)
    
    def restore_default_colors(self):
        self.set_colors(configOptions[globalSettings.optionsHub.DesktoplyricColors])

class CloseActionsBox(QGroupBox):
    close_act_changed = pyqtSignal(int)
    def __init__(self, parent=None):
        super(CloseActionsBox, self).__init__(parent)
        self.setup_ui()
        self.create_connections()
    
    def create_connections(self):
        self.hideItButton.pressed.connect(self.hideit_button_clicked)
        self.exitItButton.pressed.connect(self.exitit_button_clicked)
    
    def setup_ui(self):
        self.setTitle('关闭主面板时')
        self.hideItButton = QRadioButton('最小化到托盘')
        self.hideItButton.setFocusPolicy(Qt.NoFocus)
        self.exitItButton = QRadioButton('退出程序')
        self.exitItButton.setFocusPolicy(Qt.NoFocus)    
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.hideItButton)
        vbox.addWidget(self.exitItButton)
    
    def set_close_act(self, act):
        if act == Configures.SettingsHide:
            self.hideItButton.setChecked(True)
        elif act == Configures.SettingsExit:
            self.exitItButton.setChecked(True) 
        self.close_act_changed.emit(act)
    
    def hideit_button_clicked(self):
        self.close_act_changed.emit(Configures.SettingsHide)
    
    def exitit_button_clicked(self):
        self.close_act_changed.emit(Configures.SettingsExit)
    
    def restore_default_close_act(self):
        self.set_close_act(configOptions[globalSettings.optionsHub.CloseButtonAct])

class PathSelectPanel(QWidget):
    download_dir_changed = pyqtSignal(str)
    def __init__(self, parent=None):
        super(PathSelectPanel, self).__init__(parent)
        self.setup_ui()
        self.create_connections()
    
    def create_connections(self):
        self.lineEdit.textChanged.connect(self.text_changed)
    
    def setup_ui(self):
        label = QLabel("下载目录")
        self.lineEdit = QLineEdit()
        self.openDir = QToolButton(clicked = self.select_dir)
        self.openDir.setText('...')
        downloadDirLayout = QHBoxLayout(self)
        downloadDirLayout.setContentsMargins(0, 0, 0, 0)
        downloadDirLayout.setSpacing(2)
        downloadDirLayout.addWidget(label)
        downloadDirLayout.addWidget(self.lineEdit)
        downloadDirLayout.addWidget(self.openDir)
    
    def select_dir(self):
        oldDir = self.lineEdit.text()
        f = QFileDialog()
        newDir = f.getExistingDirectory(self, "选择下载文件夹", Configures.HomeDir, QFileDialog.ShowDirsOnly)
        if newDir and newDir != oldDir:
            self.lineEdit.setText(newDir)
    
    def get_download_dir(self):
        return self.lineEdit.text().strip()
    
    def set_download_dir(self, dir):
        self.lineEdit.setText(dir)
    
    def text_changed(self, text):
        self.download_dir_changed.emit(text.strip())
    
    def restore_default_download_dir(self):
        self.lineEdit.setText(configOptions[globalSettings.optionsHub.DownloadfilesPath])

class LyricPanel(QWidget):
    param_changed = pyqtSignal(str, str)
    def __init__(self, title='窗口歌词', option1='', option2='', parent=None):
        super(LyricPanel, self).__init__(parent)
        self.title = title
        self.set_option_names(option1, option2)
        self.setup_ui()
        self.create_connections()
    
    def create_connections(self):
        self.sizeCombo.currentTextChanged.connect(self.size_combo_text_changed)
        self.colorCombo.currentTextChanged.connect(self.color_combo_text_changed)
    
    def setup_ui(self):
        titleLabel = QLabel(self.title)
        font = QFont()
        font.setBold(True)
        titleLabel.setFont(font)
        label1 = QLabel('字号:')
        label2 = QLabel('颜色:')
        self.sizeCombo = QComboBox()
        self.sizeCombo.setFixedWidth(50)
        self.colorCombo = QComboBox()
        self.colorCombo.setFixedWidth(80)
        self.fill_color_combo()
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(titleLabel)
        mainLayout.addStretch()
        mainLayout.addWidget(label1)
        mainLayout.addWidget(self.sizeCombo)
        mainLayout.addStretch()
        mainLayout.addWidget(label2)
        mainLayout.addWidget(self.colorCombo)
    
    def fill_color_combo(self):
        self.colors = Configures.SettingsNormColors
        for color in self.colors:
            self.colorCombo.addItem(color)
    
    def set_combo_range(self, range):
        self.sizes = range
        for v in range:
            self.sizeCombo.addItem(str(v))
    
    def set_option_names(self, option1, option2):
        self.sizeOption = option1
        self.colorOption = option2        
    
    def set_parameters(self, size, color):
        self.sizeCombo.setCurrentIndex(self.sizes.index(size))
        self.colorCombo.setCurrentIndex(self.colors.index(color))
    
    def size_combo_text_changed(self, text):
        self.param_changed.emit(self.sizeOption, text)
    
    def color_combo_text_changed(self, text):
        self.param_changed.emit(self.colorOption, text)
        
class LyricPanelsBox(QGroupBox):
    parameters_changed = pyqtSignal(str, str)
    def __init__(self, parent=None):
        super(LyricPanelsBox, self).__init__(parent)
        self.setup_ui()
        self.create_connections()
    
    def create_connections(self):
        self.lyricPanelRun.param_changed.connect(self.parameters_changed.emit)
        self.lyricPanelReady.param_changed.connect(self.parameters_changed.emit)
    
    def setup_ui(self):
        self.setTitle('窗口歌词')
        self.lyricPanelRun = LyricPanel(title='已选中：')
        self.lyricPanelRun.set_combo_range(Configures.SettingsRange1)
        self.lyricPanelRun.set_option_names(globalSettings.optionsHub.WindowlyricRunFontSize, globalSettings.optionsHub.WindowlyricRunFontColor)
        self.lyricPanelReady = LyricPanel(title='未选中：')
        self.lyricPanelReady.set_combo_range(Configures.SettingsRange2)
        self.lyricPanelReady.set_option_names(globalSettings.optionsHub.WindowlyricReadyFontSize, globalSettings.optionsHub.WindowlyricReadyFontColor)
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.lyricPanelRun)
        vbox.addSpacing(6)
        vbox.addWidget(self.lyricPanelReady)
    
    def set_box_parameters(self, size1, color1, size2, color2):
        self.lyricPanelRun.set_parameters(size1, color1)
        self.lyricPanelReady.set_parameters(size2, color2)
    
    def restore_default_font_style(self):
        self.set_box_parameters(
            configOptions[globalSettings.optionsHub.WindowlyricRunFontSize], 
            configOptions[globalSettings.optionsHub.WindowlyricRunFontColor], 
            configOptions[globalSettings.optionsHub.WindowlyricReadyFontSize], 
            configOptions[globalSettings.optionsHub.WindowlyricReadyFontColor]
        )

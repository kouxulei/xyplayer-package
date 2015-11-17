from PyQt5.QtWidgets import QLabel, QMenu, QAction
from PyQt5.QtGui import QCursor, QFont, QPainter, QLinearGradient, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from xyplayer import desktopSize, Configures
from xyplayer.mysettings import globalSettings

class DesktopLyricBasic(QLabel):
    def __init__(self, text='桌面歌词', parent=None):
        super(DesktopLyricBasic, self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setText(text)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.set_font_style(globalSettings.DesktoplyricFontFamily, globalSettings.DesktoplyricFontSize, globalSettings.DesktoplyricFontForm)
        self.set_color(globalSettings.DesktoplyricColors)

    def set_color(self, colors):
        self.colors = colors
        self.update()
    
    def set_font_style(self, family, size, form):
        font = QFont()
        font.setFamily(family)
        font.setPointSize(size)  
        boldFlag, italicFlag = self.interprete_font_form(form)
        font.setBold(boldFlag)
        font.setItalic(italicFlag)
        self.setFont(font)
    
    def interprete_font_form(self, form):
        boldFlag = False
        italicFlag = False
        if form == Configures.SettingsFontForms[1]:
            boldFlag = True
        elif form == Configures.SettingsFontForms[2]:
            italicFlag = True
        elif form == Configures.SettingsFontForms[3]:
            boldFlag = True
            italicFlag = True
        return boldFlag, italicFlag
    
    def get_linear_gradient(self):
        fontHeight = self.fontMetrics().height()
        startPoint = QPoint(self.rect().x(), self.rect().y()+0.5*(self.rect().height()-fontHeight))
        endPoint = QPoint(startPoint.x(), startPoint.y()+fontHeight)
        linear = QLinearGradient(startPoint, endPoint)
        colorCounts = len(self.colors)
        for i in range(colorCounts):
            linear.setColorAt(0.2+i/colorCounts, self.colors[i])
        return linear
    
    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)
        linear = self.get_linear_gradient()
        self.painter.setPen(QPen(linear, 0))
        self.painter.drawText(0, 0, self.rect().width(), self.rect().height(), Qt.AlignHCenter|Qt.AlignVCenter, self.text())
        self.painter.end()      

class DesktopLyric(DesktopLyricBasic):
    hide_desktop_lyric_signal = pyqtSignal()
    def __init__(self):
        super(DesktopLyric, self).__init__()
        self.setAttribute(Qt.WA_TranslucentBackground )    #设置透明背景
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setWindowFlags(Qt.FramelessWindowHint| Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.set_text('桌面歌词显示')
        self.original_place()
        self.create_contextmenu()
    
    def create_contextmenu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listMenu = QMenu()
        self.originalPlaceAction = QAction("放回原位置", self)
        self.hideLyricAction = QAction("关闭桌面歌词", self)
        self.listMenu.addAction(self.originalPlaceAction)
        self.listMenu.addAction(self.hideLyricAction)
        self.originalPlaceAction.triggered.connect(self.original_place)
        self.hideLyricAction.triggered.connect(self.close)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def original_place(self):
        self.move(QPoint((desktopSize.width()-self.width())//2, desktopSize.height()-self.height()-20))
    
    def geometry_info(self):
        return self.geometry().x(), self.geometry().y(), self.width(), self.height()
    
    def set_text(self, text):
        x, y, old_width, height = self.geometry_info()
        width = self.fontMetrics().width(text)
        height = self.fontMetrics().height()
        self.setFixedWidth(width+10)
        self.setFixedHeight(height)
        self.setText(text)
        self.move(x + (old_width - self.width()) / 2, y)
    
    def set_font_style(self, family, size, form):
        DesktopLyricBasic.set_font_style(self, family, size, form)
        self.set_text(self.text())
    
    def show_context_menu(self, pos):
        self.listMenu.exec_(self.mapToGlobal(pos))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.setCursor(QCursor(Qt.ArrowCursor))
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()
    
    def closeEvent(self, event):
        self.hide_desktop_lyric_signal.emit()
        event.accept()

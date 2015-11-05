from PyQt5.QtWidgets import QLabel, QMenu, QAction
from PyQt5.QtGui import QCursor, QFont, QPainter, QLinearGradient, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from xyplayer import desktopSize
from xyplayer.mysettings import globalSettings

class DesktopLyricBasic(QLabel):
    def __init__(self, text='桌面歌词', parent=None):
        super(DesktopLyricBasic, self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)    #设置透明背景
        self.setText(text)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.font = QFont()
        self.font.setFamily(globalSettings.DesktoplyricFontFamily)
        self.font.setWeight(globalSettings.DesktoplyricFontWeight)
        self.font.setPointSize(globalSettings.DesktoplyricFontSize)
        self.setFont(self.font)
        self.set_color(globalSettings.DesktoplyricColors)

    def set_color(self, colors):
        self.colors = colors
        self.update()
    
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
        self.setAttribute(Qt.WA_QuitOnClose,False)
        self.desktopWidth = desktopSize.width()
        self.desktopHeight = desktopSize.height()
        self.setGeometry((self.desktopWidth - 300)//2, self.desktopHeight-90, 300, 60)
        self.setText('桌面歌词显示')
        self.create_contextmenu()
    
    def create_contextmenu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listMenu = QMenu()
        self.originalPlaceAction = QAction("放回原位置", self)
        self.hideLyricAction = QAction("关闭桌面歌词", self)
        self.listMenu.addAction(self.originalPlaceAction)
        self.listMenu.addAction(self.hideLyricAction)
        self.originalPlaceAction.triggered.connect(self.original_place)
        self.hideLyricAction.triggered.connect(self.hide_desktop_lyric)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def original_place(self):
        self.move(QPoint((self.desktopWidth - self.width())//2, self.desktopHeight - self.height()-30))
    
    def geometry_info(self):
        return self.geometry().x(), self.geometry().y(), self.width(), self.height()
    
    def set_text(self, text):
        x, y, old_width, height = self.geometry_info()
        width = self.fontMetrics().width(text)
        self.setFixedWidth(width)
        self.setText(text)
        self.setGeometry(x + (old_width - width) / 2, y, width, height)
    
    def hide_desktop_lyric(self):
        self.hide_desktop_lyric_signal.emit()
    
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
        self.hideDesktopLyricSignal.emit()
        event.ignore()

from PyQt5.QtWidgets import QApplication,  QLabel, QMenu, QAction
from PyQt5.QtGui import QCursor, QPalette, QFont, QColor, QPainter, QLinearGradient, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QPoint

class DesktopLyric(QLabel):
    hide_desktop_lyric_signal = pyqtSignal()
    
    def __init__(self):
        super(DesktopLyric, self).__init__()
        self.setAttribute(Qt.WA_QuitOnClose,False)
        desktop = QApplication.desktop()
        screenRec = desktop.screenGeometry()
        self.desktopWidth = screenRec.width()
        self.desktopHeight = screenRec.height()
        self.setGeometry((self.desktopWidth - 500)//2, self.desktopHeight-90, 500, 60)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
#        self.setWordWrap(True)
        self.setText('桌面歌词显示于此！')
        self.setAlignment(Qt.AlignCenter)
#        self.setStyleSheet("background:transparent;font-family:'楷体';font-size:45px;color:blue;")
        font = QFont()
        font.setFamily("楷体")
        font.setWeight(60)
        font.setPointSize(35)
        self.setFont(font)
        pe = QPalette()
        pe.setColor(QPalette.WindowText, QColor(0, 0, 255))
        self.setPalette(pe)
        self.create_contextmenu()
        
        self.colorR = 20
        self.colorG = 190
        self.colorB = 255
    
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
    
    def set_color(self, colorR, colorG, colorB):
        self.colorR = colorR
        self.colorG = colorG
        self.colorB = colorB
        self.update()
        
    
    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)

        self.linear = QLinearGradient(self.rect().topLeft(),self.rect().bottomLeft())
        self.linear.setColorAt(1, QColor(self.colorR, self.colorG, self.colorB));
#        self.linear.setColorAt(0.5, QColor(114, 232, 255));
#        self.linear.setColorAt(0.9, QColor(14, 179, 255));

        self.painter.setPen(QPen(self.linear, 0))
        self.painter.drawText(0, 0, self.rect().width(), self.rect().height(), Qt.AlignLeft, self.text())
        self.painter.end()      
    
    def original_place(self):
        self.move(QPoint((self.desktopWidth - self.width())//2, self.desktopHeight - self.height()-30))
    
    def geometry_info(self):
        return self.geometry().x(), self.geometry().y(), self.width(), self.height()
    
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

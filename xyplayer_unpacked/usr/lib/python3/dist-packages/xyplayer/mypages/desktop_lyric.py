from PyQt4.QtGui import QApplication,  QCursor, QPalette, QLabel, QFont, QMenu, QAction
from PyQt4.QtCore import Qt, pyqtSignal, QPoint

class DesktopLyric(QLabel):
    hideDesktopLyricSignal = pyqtSignal()
    
    def __init__(self):
        super(DesktopLyric, self).__init__()
        self.setAttribute(Qt.WA_QuitOnClose,False)
#        self.setFixedSize(700, 60)
        desktop = QApplication.desktop()
        screenRec = desktop.screenGeometry()
        self.desktopWidth = screenRec.width()
        self.desktopHeight = screenRec.height()
        self.setGeometry((self.desktopWidth - 800)//2, self.desktopHeight - 100, 800, 100)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWordWrap(True)
        self.setText('桌面歌词显示于此！')
        self.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setFamily("楷体")
        font.setWeight(60)
        font.setPointSize(28)
        self.setFont(font)
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.blue)
        self.setPalette(pe)
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
        self.move(QPoint((self.desktopWidth - 800)//2, self.desktopHeight - 100))
    
    def hide_desktop_lyric(self):
        self.hideDesktopLyricSignal.emit()
    
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

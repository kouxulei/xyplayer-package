from PyQt4.QtGui import QHBoxLayout, QPushButton, QVBoxLayout, QSpinBox, QLabel, QDialog, QMessageBox
from PyQt4.QtCore import pyqtSignal, Qt

class MountoutDialog(QDialog):
    mountSetSignal = pyqtSignal(int)
    def __init__(self, parent = None):
        super(MountoutDialog, self).__init__(parent)
        self.setFixedSize(200, 80)
        self.setAttribute(Qt.WA_QuitOnClose,False)
        self.setWindowTitle("计数退出")
        label1 = QLabel("还能再听")
        label1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label1.setFixedWidth(62)
        
        self.spinBox = QSpinBox()
        self.spinBox.setFixedWidth(35)
        label2 = QLabel("首歌曲！")
        label2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label2.setFixedWidth(68)
        
        self.startButton = QPushButton("开始", clicked = self.start_count)
        self.startButton.setFixedWidth(40)
        self.cancelButton = QPushButton("取消", clicked = self.cancel)
        self.cancelButton.setFixedWidth(40)
        self.pauseCountButton = QPushButton("暂停", clicked = self.pause_count)
        self.pauseCountButton.setFixedWidth(55)
        
        layout1 = QHBoxLayout()
        layout1.addWidget(label1)
        layout1.addWidget(self.spinBox)
        layout1.addWidget(label2)
        layout2 = QHBoxLayout()
        layout2.addWidget(self.startButton)
        layout2.addWidget(self.pauseCountButton)
        layout2.addWidget(self.cancelButton)
        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(layout1)
        mainLayout.addLayout(layout2)
        
        self.countoutMode = 0
        self.remainMount = 0
    
    def start_count(self):
        remain = self.spinBox.value()
        if not remain:
            QMessageBox.warning(self, "提示", "计数设定不能小于0！")
        else:
            self.countoutMode = 1
            self.remainMount = remain
    
    def pause_count(self):
        self.countoutMode = 0

    def cancel(self):
        self.countoutMode = 0
        self.remainMount = 0
        self.spinBox.setValue(0)
        

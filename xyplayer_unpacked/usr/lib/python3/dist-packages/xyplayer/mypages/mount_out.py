from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QSpinBox, QLabel, QDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt

class MountoutDialog(QDialog):
    mountSetSignal = pyqtSignal(int)
    state_message_signal = pyqtSignal(int)
    def __init__(self, parent = None):
        super(MountoutDialog, self).__init__(parent)
        label1 = QLabel("系统将再播放")
        label1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label1.setFixedHeight(35)
        self.stateLabel = QLabel("计数状态：未计数")
        self.stateLabel.setFixedHeight(35)
        self.stateLabel.setAlignment(Qt.AlignCenter)
        self.spinBox = QSpinBox()
        self.spinBox.valueChanged.connect(self.spinbox_value_changed)
        self.spinBox.setFixedWidth(40)
        label2 = QLabel("首歌曲退出！")
        label2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label2.setFixedHeight(35)
        
        self.startButton = QPushButton("开始", clicked = self.start_count)
        self.cancelButton = QPushButton("取消", clicked = self.cancel)
        
        layout1 = QHBoxLayout()
        layout1.addStretch()
        layout1.addWidget(label1)
        layout1.addWidget(self.spinBox)
        layout1.addWidget(label2)
        layout1.addStretch()
        layout2 = QHBoxLayout()
        layout2.addStretch()
        layout2.addWidget(self.startButton)
        layout2.addStretch()
        layout2.addWidget(self.cancelButton)
        layout2.addStretch()
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.stateLabel)
        mainLayout.addLayout(layout1)
        mainLayout.addLayout(layout2)
        
        self.countoutMode = 0
        self.remainMount = 0
    
    def start_count(self):
        if self.startButton.text() == "开始":
            remain = self.spinBox.value()
            if not remain:
                QMessageBox.warning(self, "提示", "计数设定不能小于1！")
            else:
                self.countoutMode = 1
                self.remainMount = remain
                self.startButton.setText("暂停")
                self.spinBox.setReadOnly(True)
                self.stateLabel.setText("计数状态：正在计数")
                self.state_message_signal.emit(remain)
        else:
            self.countoutMode = 0
            self.startButton.setText("开始")
            self.spinBox.setReadOnly(False)
            self.stateLabel.setText("计数状态：已暂停")
            self.state_message_signal.emit(-1)

    def cancel(self):
        self.countoutMode = 0
        self.remainMount = 0
        self.spinBox.setValue(0)
        self.startButton.setText("开始")
        self.stateLabel.setText("计数状态：已取消")
        self.spinBox.setReadOnly(False)
        self.state_message_signal.emit(-1)
    
    def spinbox_value_changed(self, value):
        if self.countoutMode == 1:
            self.state_message_signal.emit(value)
    
    

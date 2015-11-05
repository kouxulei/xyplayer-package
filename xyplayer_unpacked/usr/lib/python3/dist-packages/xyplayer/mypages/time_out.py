from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class TimeoutDialog(QDialog):
    """
    定时退出的页面。
    
    @signal time_out_signal() 定时的时间已到发射信号通知主程序强制退出
    ＠signal state_message_signal(str) 发射信号通知SettingFrame更新界面上显示的剩余时间
    """
    time_out_signal = pyqtSignal()
    state_message_signal = pyqtSignal(str)
    def __init__(self, parent = None):
        super(TimeoutDialog, self).__init__(parent)
        self.setStyleSheet("QLabel,QPushButton{font-family:'微软雅黑';font-size:16px;color:blue;}")
        self.timeoutFlag = 0
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.countDown)
        
        self.spinBoxes = []
        for i in range(3):
            spinBox = QSpinBox()
            self.spinBoxes.append(spinBox)
            if i == 0:
                spinBox.setRange(0, 23)
            else:
                spinBox.setRange(0, 59)
        
        self.stateLabel = QLabel("定时状态：未定时")
        self.stateLabel.setAlignment(Qt.AlignCenter)
        self.stateLabel.setFixedHeight(30)
        titleLabel = QLabel("剩余时间：")
        titleLabel.setStyleSheet("font-size:15px")
        
        label1 =  QLabel("时")
        label2 = QLabel("分")
        label3 = QLabel("秒")
        
        self.startButton = QPushButton("开始", clicked = self.start_timer)
        self.cancelButton = QPushButton("取消", clicked = self.cancel_timer)
        
        hbox_boxes = QHBoxLayout()
        hbox_boxes.addWidget(self.spinBoxes[0])
        hbox_boxes.addWidget(label1)
        hbox_boxes.addWidget(self.spinBoxes[1])
        hbox_boxes.addWidget(label2)
        hbox_boxes.addWidget(self.spinBoxes[2])
        hbox_boxes.addWidget(label3)
        
        mainLayout = QGridLayout(self)
        mainLayout.addWidget(self.stateLabel, 1, 0, 1, 2)
        mainLayout.addWidget(titleLabel, 4, 0)
        mainLayout.addWidget(self.startButton, 4, 1)
        mainLayout.addWidget(self.cancelButton, 5, 1)
        mainLayout.addLayout(hbox_boxes, 5, 0)
    
    def start_timer(self):
        if self.startButton.text() == "开始":
            if not self.spinBoxes[0].value() and not self.spinBoxes[1].value() and not self.spinBoxes[2].value():
                QMessageBox.warning(self, "提示", "定时时间设定不能为0！")
            else:
                self.timer.start()
                self.startButton.setText("暂停")
                self.stateLabel.setText("定时状态：正在定时")
                for i in range(3):
                    self.spinBoxes[i].setReadOnly(True)
        else:
            self.timer.stop()
            self.state_message_signal.emit('')
            self.startButton.setText("开始")
            self.stateLabel.setText("定时状态：已暂停")
            for i in range(3):
                self.spinBoxes[i].setReadOnly(False)
        
    def cancel_timer(self):
        self.timer.stop()
        self.state_message_signal.emit('')
        self.startButton.setText("开始")
        self.stateLabel.setText("定时状态：已取消")
        for i in range(3):
            self.spinBoxes[i].setValue(0)
            self.spinBoxes[i].setReadOnly(False)
    
    def countDown(self):
        a = []
        for i in range(3):
            a.append(self.spinBoxes[i].value())
        a[2] -= 1
        if a[2] < 0: 
            a[2] = 59
            a[1] -= 1
            if a[1] < 0:
                a[1] = 59
                a[0] -= 1
                if a[0] < 0:
                    a[0] -= 1
                    if a[0] < 0:
                        self.timeoutFlag = 1
                        self.time_out_signal.emit()
                        self.timer.stop()
                        for i in range(3):
                            a[i] = 0
        if not a[0]:
            remainTime = QTime(0, a[1], a[2]).toString('mm:ss')
        else:
            remainTime = QTime(a[0], a[1], a[2]).toString('hh:mm:ss')
        self.state_message_signal.emit(remainTime)
        for i in range(3):
            self.spinBoxes[i].setValue(a[i])
    
    
    
    
    
    
    
    

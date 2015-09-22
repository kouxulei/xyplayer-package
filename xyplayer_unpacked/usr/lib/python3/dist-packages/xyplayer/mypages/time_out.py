from PyQt4.QtGui import *
from PyQt4.QtCore import *

class TimeoutDialog(QDialog):
    time_out_signal = pyqtSignal()
    def __init__(self, parent = None):
        super(TimeoutDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_QuitOnClose,False)
        self.setWindowTitle("定时退出")
        self.timeoutFlag = 0
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.countDown)
        
        self.hourBox  = QSpinBox()
        self.minuteBox = QSpinBox()
        self.secondBox = QSpinBox()
        
        self.hourBox.setRange(0, 23)
        self.minuteBox.setRange(0, 59)
        self.secondBox.setRange(0, 59)
        
        titleLabel = QLabel("剩余时间：")
        titleLabel.setStyleSheet("font-size:15px")
        
        label1 =  QLabel("时")
        label2 = QLabel("分")
        label3 = QLabel("秒")
        
        self.startButton = QPushButton("开始", clicked = self.start_timer)
        self.pauseButton = QPushButton("暂停", clicked = self.pause_timer)
        self.cancelButton = QPushButton("取消", clicked = self.cancel_timer)
        
        hbox_boxes = QHBoxLayout()
        hbox_boxes.addWidget(self.hourBox)
        hbox_boxes.addWidget(label1)
        hbox_boxes.addWidget(self.minuteBox)
        hbox_boxes.addWidget(label2)
        hbox_boxes.addWidget(self.secondBox)
        hbox_boxes.addWidget(label3)
        
        vbox1 = QVBoxLayout()
        vbox1.addWidget(titleLabel)
        vbox1.addLayout(hbox_boxes)
        
        vbox_buttons = QVBoxLayout()
        vbox_buttons.addWidget(self.startButton)
        vbox_buttons.addWidget(self.pauseButton)
        vbox_buttons.addWidget(self.cancelButton)
        
        mainLayout = QHBoxLayout(self)
        mainLayout.addLayout(vbox1)
        mainLayout.addLayout(vbox_buttons)
    
    def start_timer(self):
        if not self.hourBox.value() and not self.minuteBox.value() and not self.secondBox.value():
            QMessageBox.warning(self, "提示", "定时时间设定不能为0！")
        else:
            self.timer.start()
    
    def pause_timer(self):
        self.timer.stop()
        
    def cancel_timer(self):
        self.timer.stop()
        self.hourBox.setValue(0)
        self.minuteBox.setValue(0)
        self.secondBox.setValue(0)
    
    def countDown(self):
        h = self.hourBox.value()
        m = self.minuteBox.value()
        s = self.secondBox.value()
        s -= 1
        if s < 0: 
            s = 59
            m -= 1
            if m < 0:
                m = 59
                h -= 1
                if h < 0:
                    h -= 1
                    if h < 0:
                        self.timeoutFlag = 1
                        self.time_out_signal.emit()
                        self.timer.stop()
                        h = 0
                        m = 0
                        s = 0
        self.hourBox.setValue(h)
        self.minuteBox.setValue(m)
        self.secondBox.setValue(s)
    
    
    
    
    
    
    
    

import os
from PyQt4.QtGui import (QMessageBox,QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QVBoxLayout, 
                                        QLineEdit,QToolButton, QLabel, QDialog, QFileDialog)
from PyQt4.QtCore import pyqtSignal, Qt
from xyplayer.configure import Configures

class PathsetFrame(QDialog):
    downloadDirChanged = pyqtSignal(str)
    def __init__(self, parent = None):
        super(PathsetFrame, self).__init__(parent)
        self.setAttribute(Qt.WA_QuitOnClose,False)
        self.setMinimumSize(370, 110)
        label = QLabel("歌曲下载到：")
        with open(Configures.settingFile,  'r') as f:
            self.oldDir = f.read()
        self.lineEdit = QLineEdit("%s"%self.oldDir)
        self.setWindowTitle("当前设置："+self.oldDir)
        self.openDir = QToolButton(clicked = self.select_dir)
        self.openDir.setText('...')
        self.defaultButton = QPushButton("默认值", clicked = self.default)
        self.okButton = QPushButton("确定", clicked = self.confirm)
        self.cancelButton = QPushButton("取消", clicked = self.cancel)
        
        inputLayout = QHBoxLayout()
        inputLayout.addWidget(self.lineEdit)
        inputLayout.addWidget(self.openDir)
        
        buttonsLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        buttonsLayout.addItem(spacerItem)
        buttonsLayout.addWidget(self.defaultButton)
        buttonsLayout.addWidget(self.cancelButton)
        buttonsLayout.addWidget(self.okButton)
        buttonsLayout.addItem(spacerItem)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(label)
        mainLayout.addLayout(inputLayout)
        mainLayout.addLayout(buttonsLayout)
    
    def set_place(self, x, y):
        self.setGeometry(x, y, 370, 110)
    
    def select_dir(self):
        f = QFileDialog()
        newDir = f.getExistingDirectory(self, "选择下载文件夹", Configures.homeDir, QFileDialog.ShowDirsOnly)
        if newDir:
            self.lineEdit.setText(newDir)
    
    def confirm(self):
        print('setting.py  here1')
        newDir = self.lineEdit.text()
        if not os.path.isdir(newDir):
            QMessageBox.critical(self, '错误', '您输入的不是一个文件夹！')
            self.lineEdit.setText(self.oldDir)
            return
        if newDir != self.oldDir:
            if not os.path.exists(newDir):
                os.mkdir(newDir)
            with open(Configures.settingFile, 'w') as f:
                f.write(newDir)
            self.oldDir = newDir
            self.setWindowTitle("当前设置："+newDir)
            self.downloadDirChanged.emit(newDir)
        self.close()
    
    def cancel(self):
        self.lineEdit.setText(self.oldDir)
        self.close()
    
    def default(self):
        self.lineEdit.setText(Configures.musicsDir)
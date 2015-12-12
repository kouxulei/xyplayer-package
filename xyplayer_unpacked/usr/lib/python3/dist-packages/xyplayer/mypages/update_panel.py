import os
import time
import socket
from urllib import request
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from xyplayer import app_version, app_version_num
from xyplayer import Configures
from xyplayer.utils import version_to_num

class UpdatePanel(QWidget):
    updatingStateChanged = pyqtSignal(int)
    def __init__(self, parent = None):
        super(UpdatePanel, self).__init__(parent)
        socket.setdefaulttimeout(3)
        self.setup_ui()
        self.create_connections()

    def setup_ui(self):
        currentVersion = QLabel('当前版本：v%s'%app_version)
        self.newestVersionLabel = QLabel('最新版本：未检查')
        self.checkUpdateButton = QPushButton("检查更新")
        self.checkUpdateButton.setFixedSize(70, 30)
        self.updateButton = QPushButton('在线更新')
        self.updateButton.setFixedSize(70, 30)
        self.updateButton.hide()
        self.changeLogText = QTextEdit()
        self.changeLogText.setReadOnly(True)
        self.changeLogText.setMinimumHeight(460)
        self.progressBar = QProgressBar()
        self.updateState = QLabel()
        self.updateState.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.progressBar.hide()
        self.updateState.hide()
        
        self.changelogVersionNum = 0
        if os.path.exists(Configures.Changelog):
            changelogVersion = self.fill_changelog_text()
            self.changelogVersionNum = version_to_num(changelogVersion)
            if self.changelogVersionNum > app_version_num:
                self.newestVersionLabel.setText('最新版本：存在%s或更高版本'%changelogVersion )
            else:
                self.newestVersionLabel.setText('最新版本：未检查')
        else:
            self.changeLogText.hide()
        updateLayout = QGridLayout(self)
        updateLayout.setContentsMargins(0, 5, 0, 0)
        updateLayout.addWidget(currentVersion, 0, 0)
        updateLayout.addWidget(self.checkUpdateButton, 0, 1)
        updateLayout.addWidget(self.newestVersionLabel, 1, 0)
        updateLayout.addWidget(self.updateButton, 1, 1)
        updateLayout.addWidget(self.progressBar, 2, 0)
        updateLayout.addWidget(self.updateState, 2, 1)
        updateLayout.addWidget(self.changeLogText, 3, 0, 3, 2)
    
    def create_connections(self):
        self.checkUpdateButton.clicked.connect(self.check_update)
        self.updateButton.clicked.connect(self.update)
    
    def fill_changelog_text(self):
        with open(Configures.Changelog, 'r+') as f:
            version = f.readline().strip()
            content = f.read()
        f.close()
        self.changeLogText.append(version)
        self.changeLogText.append(content)
        cur = self.changeLogText.textCursor()
        cur.setPosition(0, QTextCursor.MoveAnchor)
        self.changeLogText.setTextCursor(cur)
        return version
    
    def check_update(self):
        url = 'https://raw.githubusercontent.com/Zheng-Yejian/xyplayer-package/master/changelog'
        version, req = self.url_open(url)
        if not version:
            self.newestVersionLabel.setText('联网出错，检查新版本失败！')
            return
        try:
            versionNum = version_to_num(version)
            if versionNum != self.changelogVersionNum:
                with open(Configures.Changelog, 'w') as f:
                    content = req.read().decode()
                    content = '%s\n%s'%(version, content)
                    f.write(content)
                    f.close()
                self.changeLogText.clear()
                self.fill_changelog_text()
                if self.changeLogText.isHidden():
                    self.changeLogText.show()
            if versionNum > app_version_num :
                self.newestVersion = version[1:]
                self.newestVersionLabel.setText('最新版本：v%s' %self.newestVersion)
                self.updateButton.show()
            else:
                self.newestVersionLabel.setText('已是最新版，谢谢使用！')
        except:
            self.newestVersionLabel.setText('联网出错，检查新版本失败！')
    
    def url_open(self, url):
        retries = 4
        while retries:
            try:
                req = request.urlopen(url)
                version = req.readline().decode().strip()
                return version, req
            except:
                time.sleep(0.05)
                retries -= 1
        return None, None
    
    def update(self):
        url = 'https://github.com/Zheng-Yejian/xyplayer-package/blob/master/xyplayer_%s_all.deb?raw=true'%self.newestVersion
        debLocal =  '%s/xyplayer_%s_all.deb'%(Configures.DebsDir, self.newestVersion)
        if not os.path.exists(debLocal):
            fail = self.download_package(url, debLocal)
            if fail:
                self.updatingStateChanged.emit(Configures.UpdateFailed)
                return
        self.updatingStateChanged.emit(Configures.UpdateStarted)
        os.system('gdebi-gtk %s'%debLocal)
        from xyplayer.__init__ import app_version
        print(app_version, self.newestVersion)
        if app_version == self.newestVersion:
            self.updateButton.hide()
            self.newestVersionLabel.setText('已完成更新，请重启播放器!')
            self.updateState.setText("完成更新")
            self.updatingStateChanged.emit(Configures.UpdateSucceed)
        else:
            self.updateState.setText("放弃更新")
            self.updatingStateChanged.emit(Configures.UpdateDropped)

    def download_package(self, url, debLocal):
        try:
            self.progressBar.show()
            self.updateState.show()
            res = request.urlopen(url)
            if res.status == 200 and  res.reason == 'OK':
                totalLength = int(res.getheader('Content-Length'))
            self.progressBar.setRange(0, totalLength)
            self.updateState.setText("正在更新")
            currentLength = 0
            while currentLength < totalLength:
                currentLength += 20480
                if currentLength > totalLength:
                    currentLength = totalLength
                self.progressBar.setValue(currentLength)
                pkgContent = res.read(20480)
                with open(debLocal, 'ab+') as f:
                    f.write(pkgContent)
                    f.close()
            res.close()
            failFlag = 0
        except:
            if os.path.exists(debLocal):
                os.remove(debLocal)
            failFlag = 1
        self.progressBar.hide()
        self.updateState.hide()
        return failFlag    
        







import os
import socket
from urllib import request
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from xyplayer import app_version, app_version_num
from xyplayer import Configures
from xyplayer.utils import version_to_num

class AboutPage(QWidget):
    updatingStateChanged = pyqtSignal(int)
    def __init__(self, parent = None):
        super(AboutPage, self).__init__(parent)
        socket.setdefaulttimeout(3)
        self.setup_ui()
        self.create_connections()

    def setup_ui(self):
        self.setStyleSheet("QLabel{font-size:14px;color:white}")
        self.authorLabel = QLabel('作&nbsp;&nbsp;者：<a style="color:yellow" href=https://github.com/Zheng-Yejian>Zheng-Yejian</a>')
        self.emailLabel = QLabel('邮&nbsp;&nbsp;箱：<a style="color:yellow" href="mailto:1035766515@qq.com">1035766515@qq.com</a>')
        self.addressLabel = QLabel('链&nbsp;&nbsp;接：'
            '<a style="color:yellow;" href=https://github.com/Zheng-Yejian/xyplayer>软件源码</a>'
            '<span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
            '<a style = "color:yellow;" href=https://github.com/Zheng-Yejian/xyplayer-package>deb包下载</a>'
            '<span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
            '<a style = "color:yellow;" href="http://forum.ubuntu.org.cn/viewtopic.php?f=74&t=465335">版本说明</a>')

#使用说明
        specText = QTextEdit()
        specText.setReadOnly(True)
        specs = ("<p>xyplayer项目旨在设计一个能实现基本播放以及在线搜索播放媒体资源功能的MP3播放器。谢谢您的使用，如果发现问题，还请与我交流。</p>"
                        "<p>遵循协议： GPLv3</p>"
                        "<p>当前版本： v%s</p>"
                        "<p>特别操作说明：</p>"
                        "<p>1. 主界面右键长按拖动窗口；</p>"
                        "<p>2. “更多功能”页面右键单击返回；</p>"%app_version )
        specText.setText(specs)
            
#感谢页面   
        thanks = ("<p>谢谢<a style = 'color:green;' href=https://github.com/LiuLang/kwplayer>github.com/LiuLang/kwplayer</a>"
                        "项目的作者，程序中kuwo的网络API使用、歌词的解码解析以及项目流程的管理都是从您的项目中学来的。</p>"
                        "<p>播放器的图标大部分从网上下载来修改的，谢谢这些素材的作者。</p>")
        thanksText = QTextEdit()
        thanksText.setReadOnly(True)
        thanksText.setText(thanks)

#软件协议
        licenseText = QTextEdit()
        licenseText.setReadOnly(True)
        with open(Configures.LicenseFile, 'r') as f:
            licenseText.append(f.read())
        cur = licenseText.textCursor()
        cur.setPosition(0, QTextCursor.MoveAnchor)
        licenseText.setTextCursor(cur)

#更新页面
        currentVersion = QLabel('当前版本：v%s'%app_version)
        self.newestVersionLabel = QLabel('最新版本：未检查')
        self.checkUpdateButton = QPushButton("检查更新")
        self.checkUpdateButton.setFixedSize(70, 30)
        self.updateButton = QPushButton('在线更新')
        self.updateButton.setFixedSize(70, 30)
        self.updateButton.hide()
        self.changeLogText = QTextEdit()
        self.changeLogText.setReadOnly(True)
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
        updatePage = QWidget()
        updatePage.setStyleSheet('color:black')
        updateLayout = QGridLayout(updatePage)
        updateLayout.setContentsMargins(8, 3, 8, 2)
        updateLayout.addWidget(currentVersion, 0, 0)
        updateLayout.addWidget(self.checkUpdateButton, 0, 1)
        updateLayout.addWidget(self.newestVersionLabel, 1, 0)
        updateLayout.addWidget(self.updateButton, 1, 1)
        updateLayout.addWidget(self.progressBar, 2, 0)
        updateLayout.addWidget(self.updateState, 2, 1)
        updateLayout.addWidget(self.changeLogText, 3, 0, 3, 2)
        
#tab页
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(specText, '简介')
        self.tabWidget.addTab(thanksText, '鸣谢')
        self.tabWidget.addTab(updatePage, '更新')
        self.tabWidget.addTab(licenseText, '软件协议')
#        self.tabWidget.setStyleSheet('QTabWidget::tab-bar{alignment:center}')
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(3)
        mainLayout.setContentsMargins(2, 0, 4, 0)
        mainLayout.addWidget(self.authorLabel)
        mainLayout.addWidget(self.emailLabel)
        mainLayout.addWidget(self.addressLabel)
        mainLayout.addWidget(self.tabWidget)
    
    def create_connections(self):
        self.authorLabel.linkActivated.connect(self.open_url)
        self.emailLabel.linkActivated.connect(self.open_url)
        self.addressLabel.linkActivated.connect(self.open_url)
        self.checkUpdateButton.clicked.connect(self.check_update)
        self.updateButton.clicked.connect(self.update)
    
    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))
    
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
        try:
            req = request.urlopen(url)
            version = req.readline().decode().strip()
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
        







import os, socket
from urllib import request
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from xyplayer import __version__, __versionNum__
from xyplayer.configure import Configures

class AboutPage(QWidget):
    def __init__(self, parent = None):
        super(AboutPage, self).__init__(parent)
        socket.setdefaulttimeout(3)
        self.setup_ui()
        self.create_connections()

    def setup_ui(self):
        self.setStyleSheet("QLabel{font-size:13px;color:white}")
        authorLabel = QLabel('作  者：Zheng-Yejian')
        emailLabel = QLabel('邮  箱：1035766515@qq.com')
        self.addressLabel = QLabel("项目网址：<a style = 'color:green;'href= https://github.com/Zheng-Yejian/xyplayer>github.com/Zheng-Yejian/xyplayer</a>")
        self.debAddressLabel = QLabel("deb包网址：<a style = 'color:green;'href= https://github.com/Zheng-Yejian/xyplayer-package>github.com/Zheng-Yejian/xyplayer-package</a>")

#使用说明
        specText = QTextEdit()
        specText.setReadOnly(True)
        specList = ["xyplayer项目旨在设计一个能实现基本播放以及在线搜索播放媒体资源功能的音乐播放器。谢谢您的使用，如果发现问题，还请与我交流。", " ",  "当前版本： %s"%__version__, " ",  
                            "特别操作说明：", "1、主界面右键长按拖动窗口；", "2、设置页面右键单击返回；"]
        for line in specList:
            specText.append(line)
            
#感谢页面   
        thanksList = ["要感谢<a style = 'color:green;' href=https://github.com/LiuLang/kwplayer>github.com/LiuLang/kwplayer</a>项目的参与者们，我从他们的代码中收获了很多。", 
                            "播放器的图标大部分从网上找来的，谢谢这些素材的作者。"]   
        thanksText = QTextEdit()
        thanksText.setReadOnly(True)
        for line in thanksList:
            thanksText.append(line)

#更新页面
        
        currentVersion = QLabel('当前版本：' + __version__)
        self.newestVersionLabel = QLabel('最新版本：未检查')
        self.versionNum = __versionNum__
        self.checkUpdateButton = QPushButton("检查更新")
        self.checkUpdateButton.setFixedWidth(70)
        self.updateButton = QPushButton('在线更新')
        self.updateButton.setFixedWidth(70)
        self.updateButton.hide()
        self.changeLogText = QTextEdit()
        self.changeLogText.setReadOnly(True)
        self.progressBar = QProgressBar()
        self.updateState = QLabel()
        self.progressBar.hide()
        self.updateState.hide()
        
        if os.path.exists(Configures.changelog):
            newVersion = self.fill_changelog_text()
            newVersionNum = self.version_to_num(newVersion)
            if newVersionNum > __versionNum__:
                self.newestVersionLabel.setText('最新版本：存在%s或更高版本'%newVersion )
            else:
                self.newestVersionLabel.setText('最新版本：未检查')
        else:
            self.changeLogText.hide()
        updatePage = QWidget()
        updatePage.setStyleSheet('color:black')
        updateLayout = QGridLayout(updatePage)
        updateLayout.addWidget(currentVersion, 0, 0)
        updateLayout.addWidget(self.checkUpdateButton, 0, 1)
        updateLayout.addWidget(self.newestVersionLabel, 1, 0)
        updateLayout.addWidget(self.updateButton, 1, 1)
        updateLayout.addWidget(self.progressBar, 2, 0)
        updateLayout.addWidget(self.updateState, 2, 1)
        updateLayout.addWidget(self.changeLogText, 3, 0, 3, 2)
        
#tab页
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(specText, '说明')
        self.tabWidget.addTab(thanksText, '鸣谢')
        self.tabWidget.addTab(updatePage, '更新')
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.setMargin(3)
        mainLayout.addWidget(authorLabel)
        mainLayout.addWidget(emailLabel)
        mainLayout.addWidget(self.addressLabel)
        mainLayout.addWidget(self.debAddressLabel)
        mainLayout.addWidget(self.tabWidget)
    
    def create_connections(self):
        self.addressLabel.linkActivated.connect(self.openUrl)
        self.debAddressLabel.linkActivated.connect(self.openUrl)
        self.checkUpdateButton.clicked.connect(self.check_update)
        self.updateButton.clicked.connect(self.update)
    
    def openUrl(self, url):
        QDesktopServices.openUrl(QUrl(url))
    
    def fill_changelog_text(self):
        with open(Configures.changelog, 'r+') as f:
            version = f.read(8)
            content = f.read()
        f.close()
        self.changeLogText.append(version + content)
        cur = self.changeLogText.textCursor()
        cur.setPosition(0, QTextCursor.MoveAnchor)
        self.changeLogText.setTextCursor(cur)
        return version
    
    def version_to_num(self, version):
        m = ''
        for c in version:
            try:
                int(c)
                m += c
            except:
                continue
        if not m:
            return __versionNum__
        return int(m)
    
    def check_update(self):
        url = 'https://raw.githubusercontent.com/Zheng-Yejian/xyplayer-package/master/changelog'
        try:
            req = request.urlopen(url)
            version = req.read(8).decode()
            versionNum = self.version_to_num(version)
            if versionNum > __versionNum__ or not os.path.exists(Configures.changelog):
                with open(Configures.changelog, 'w') as f:
                    content = req.read().decode()
                    content = version + content
                    f.write(content)
                self.changeLogText.clear()
                self.fill_changelog_text()
                if self.changeLogText.isHidden():
                    self.changeLogText.show()
                f.close()
            if versionNum > __versionNum__ :
                self.newestVersionLabel.setText('最新版本：' + version)
                self.newestVersion = version[1:]
                self.updateButton.show()
            else:
                self.newestVersionLabel.setText('最新版本：已是最新版')
        except:pass
    
    def update(self):
        url = 'https://github.com/Zheng-Yejian/xyplayer-package/blob/master/xyplayer_%s_all.deb?raw=true'%self.newestVersion
        debLocal = Configures.debsDir + '/xyplayer_%s_all.deb'%self.newestVersion
        if not os.path.exists(debLocal):
            fail = self.download_package(url, debLocal)
            if fail:
                return
        os.system('gdebi-gtk %s'%debLocal)
        from xyplayer import __version__
        if __version__ == self.newestVersion:
            self.updateButton.hide()
            self.newestVersionLabel.setText('已完成更新，请重启播放器!')
            self.updateState.setText("完成更新")
        else:
            self.updateState.setText("放弃更新")

    def download_package(self, url, debLocal):
        try:
            self.progressBar.show()
            self.updateState.show()
            self.newestVersionLabel.hide()
            self.updateButton.hide()
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
            res.close()
            f.close()
            failFlag = 0
        except:
            if os.path.exists(debLocal):
                os.remove(debLocal)
            failFlag = 1
        self.progressBar.hide()
        self.updateState.hide()
        self.newestVersionLabel.show()
        self.updateButton.show()   
        return failFlag    
        







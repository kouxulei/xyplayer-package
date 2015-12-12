from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from xyplayer import app_version
from xyplayer import Configures

class AboutPage(QDialog):
    updatingStateChanged = pyqtSignal(int)
    def __init__(self, parent = None):
        super(AboutPage, self).__init__(parent)
        self.setup_ui()
        self.create_connections()

    def setup_ui(self):
#        self.setStyleSheet("QLabel{font-size:14px;color:white}")
        self.authorLabel = QLabel('作&nbsp;&nbsp;者：<a style="color:green" href=https://github.com/Zheng-Yejian>Zheng-Yejian</a>')
        self.emailLabel = QLabel('邮&nbsp;&nbsp;箱：<a style="color:green" href="mailto:1035766515@qq.com">1035766515@qq.com</a>')
        self.addressLabel = QLabel('链&nbsp;&nbsp;接：'
            '<a style="color:green;" href=https://github.com/Zheng-Yejian/xyplayer>软件源码</a>'
            '<span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
            '<a style = "color:green;" href=https://github.com/Zheng-Yejian/xyplayer-package>deb包下载</a>'
            '<span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
            '<a style = "color:green;" href="http://forum.ubuntu.org.cn/viewtopic.php?f=74&t=465335">版本说明</a>')

#使用说明
        specText = QTextEdit()
        specText.setReadOnly(True)
        specs = ("<p>xyplayer是一款简单的MP3播放器，支持本地音乐管理、在线音乐搜索试听、下载管理、在线升级等功能。</p>"
                        "<p>当前版本： v%s</p>"
                        "<p>软件协议：本软件使用GNU General Public License V3协议发布，详细内容请看”软件协议“一栏以及项目中的LICENSE文件。</p>"
                        "<p>资源版权：本项目的网络资源获取功能是基于kwplayer修改的，获取到的资源（目前主要是图片和MP3文件）同样来自kuwo.cn这个网站，"
                        "因使用本程序引起的侵权问题由使用者自己承担。</p>"%app_version )
        specText.setText(specs)
            
#感谢页面   
        thanks = ("<p>谢谢<a style = 'color:green;' href=https://github.com/LiuLang/kwplayer>github.com/LiuLang/kwplayer</a>"
                        "项目的作者，本程序中关于网络资源获取和歌词解码解析的功能是基于kwplayer的代码修改实现的，而且代码管理也是学着您的项目弄的。</p>"
                        "<p>程序的图标有一部分是从网上下载来修改的，感谢这些素材的作者。</p>"
                        "<p>感谢所有给我反馈BUG以及给我提供意见建议的朋友们。</p>")
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
        
#tab页
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(specText, '简介')
        self.tabWidget.addTab(thanksText, '鸣谢')
        self.tabWidget.addTab(licenseText, '软件协议')
#        self.tabWidget.setStyleSheet('QTabWidget::tab-bar{alignment:center}')
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(3)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.authorLabel)
        mainLayout.addWidget(self.emailLabel)
        mainLayout.addWidget(self.addressLabel)
        mainLayout.addWidget(self.tabWidget)
    
    def create_connections(self):
        self.authorLabel.linkActivated.connect(self.open_url)
        self.emailLabel.linkActivated.connect(self.open_url)
        self.addressLabel.linkActivated.connect(self.open_url)
    
    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))

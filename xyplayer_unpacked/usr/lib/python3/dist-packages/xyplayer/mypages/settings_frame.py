import os
from PyQt5.QtWidgets import (
    QMessageBox,QHBoxLayout, QPushButton, QTabWidget, QFileDialog, QLabel, QWidget, QVBoxLayout, 
    QLineEdit,QToolButton, QGroupBox, QRadioButton)
from PyQt5.QtCore import pyqtSignal, Qt
from xyplayer import Configures
from xyplayer.mypages import desktop_lyric
from xyplayer.mywidgets import ColorButton
from xyplayer.mysettings import globalSettings, configOptions

class SettingsFrame(QWidget):
    downloadDirChanged = pyqtSignal(str)
    desktop_lyric_style_changed = pyqtSignal()
    close_button_act_changed = pyqtSignal(int)
    def __init__(self, parent = None):
        super(SettingsFrame, self).__init__(parent)
        self.setStyleSheet("QPushButton{font-family:'微软雅黑';font-size:14px;}")
        self.initial_basic_tab()
        self.initial_download_tab()
        self.initial_lyric_tab()
        self.initial_main_ui()
        self.create_connections()
        self.initial_parames()
    
    def create_connections(self):
        self.lineEdit.textChanged.connect(self.check_changed_text)
        self.tabWidget.currentChanged.connect(self.tab_switched)
        for colorButton in self.colorButtons:
            colorButton.new_color_signal.connect(self.preview)
        self.hideItButton.pressed.connect(self.hideit_button_clicked)
        self.exitItButton.pressed.connect(self.exitit_button_clicked)
    
    def initial_parames(self):
        self.modifiedDict = {}
        self.modifiedDictsGroup = {}
        self.tabWidget.setCurrentIndex(0)
        self.currentIndex = self.tabWidget.currentIndex()
        for k in range(self.tabWidget.count()):
            self.modifiedDictsGroup[self.tabWidget.tabText(k)] = {}
    
    def tab_switched(self, index):
        self.modifiedDictsGroup[self.tabWidget.tabText(self.currentIndex)] = self.modifiedDict.copy()
        self.currentIndex = index
        self.modifiedDict = self.modifiedDictsGroup[self.tabWidget.tabText(self.currentIndex)].copy()
        self.check_control_buttons_state()
    
    def initial_basic_tab(self):
        self.basicTab = QWidget()
        groupBox = QGroupBox('关闭主面板时')
        self.hideItButton = QRadioButton('最小化到托盘')
        self.hideItButton.setFocusPolicy(Qt.NoFocus)
        self.exitItButton = QRadioButton('退出程序')
        self.exitItButton.setFocusPolicy(Qt.NoFocus)
        if globalSettings.CloseButtonAct == Configures.SettingsHide:
            self.hideItButton.setChecked(True)
        else:
            self.exitItButton.setChecked(True)
        vbox = QVBoxLayout(groupBox)
        vbox.addWidget(self.hideItButton)
        vbox.addWidget(self.exitItButton)
        
        mainLayout = QVBoxLayout(self.basicTab)
        mainLayout.addWidget(groupBox)
        mainLayout.addStretch()
    
    def initial_download_tab(self):
        self.downloadTab = QWidget()
        label = QLabel("下载目录")
        self.lineEdit = QLineEdit("%s"%globalSettings.DownloadfilesPath)
        self.openDir = QToolButton(clicked = self.select_dir)
        self.openDir.setText('...')
        downloadDirLayout = QHBoxLayout()
        downloadDirLayout.setSpacing(2)
        downloadDirLayout.addWidget(label)
        downloadDirLayout.addWidget(self.lineEdit)
        downloadDirLayout.addWidget(self.openDir)
        downloadTabLayout = QVBoxLayout(self.downloadTab)
        downloadTabLayout.addLayout(downloadDirLayout)
        downloadTabLayout.addStretch()
    
    def initial_lyric_tab(self):
        self.lyricTab = QWidget()
        self.colors = []
        self.colorButtons = []
        self.previewLabel = desktop_lyric.DesktopLyricBasic()
        self.previewLabel.set_color(globalSettings.DesktoplyricColors)
        label1 = QLabel('颜色：', self.lyricTab)
        label2 = QLabel('预览：', self.lyricTab)
        label1.setFixedWidth(50)
        
        colorsLayout = QVBoxLayout()
        colorsLayout.setSpacing(3)
        for index in range(3):
            colorButton = ColorButton()
            colorButton.set_index(index)
            colorButton.set_color(globalSettings.DesktoplyricColors[index])
            self.colors.append(globalSettings.DesktoplyricColors[index])
            self.colorButtons.append(colorButton)
            colorsLayout.addWidget(colorButton)
        lyricColorLayout = QHBoxLayout()
        lyricColorLayout.addWidget(label1)
        lyricColorLayout.addLayout(colorsLayout)
        
        lyricTabLayout = QVBoxLayout(self.lyricTab)
        lyricTabLayout.addLayout(lyricColorLayout)
        lyricTabLayout.addStretch()
        lyricTabLayout.addWidget(label2)
        lyricTabLayout.addWidget(self.previewLabel)
        
    
    def initial_main_ui(self):
        self.defaultButton = QPushButton("恢复本页默认配置", clicked = self.default)
        self.defaultButton.setFocusPolicy(Qt.NoFocus)
        self.okButton = QPushButton("应用", clicked = self.confirm)
        self.okButton.setFocusPolicy(Qt.NoFocus)
        self.okButton.setEnabled(False)
        self.cancelButton = QPushButton("取消", clicked = self.cancel)
        self.cancelButton.setFocusPolicy(Qt.NoFocus)
        self.cancelButton.setEnabled(False)
        self.tabWidget = QTabWidget()
        self.tabWidget.insertTab(0, self.basicTab, Configures.SettingsBasicTab)
        self.tabWidget.insertTab(1, self.downloadTab, Configures.SettingsDownloadTab)
        self.tabWidget.insertTab(2, self.lyricTab, Configures.SettingsDesktopLyricTab)
        
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(self.defaultButton)
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(self.okButton)
        buttonsLayout.addWidget(self.cancelButton)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addLayout(buttonsLayout)
        mainLayout.setContentsMargins(2, 4, 4, 4)

    def make_modified_global_settings_valid(self):
        for key, value in self.modifiedDict.items():
            globalSettings.__setattr__(key, value)
        self.modifiedDict.clear()
        self.check_control_buttons_state()

    def confirm(self):
        self.make_modified_global_settings_valid() 
        if self.tabWidget.tabText(self.currentIndex) == Configures.SettingsBasicTab:
            self.basic_tab_confirm()
        elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDownloadTab:
            self.download_tab_confirm()
        elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDesktopLyricTab:
            self.desktoplyric_tab_confirm()

    def cancel(self):
        if self.tabWidget.tabText(self.currentIndex) == Configures.SettingsBasicTab:
            self.basic_tab_cancel()
        elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDownloadTab:
            self.download_tab_cancel()
        elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDesktopLyricTab:
            self.desktoplyric_tab_cancel()

    def default(self):
        ok = QMessageBox.question(self, 'xyplayer选项管理', '确认恢复本页默认配置？',QMessageBox.Cancel|QMessageBox.Ok, QMessageBox.Cancel )
        if ok == QMessageBox.Ok:
            if self.tabWidget.tabText(self.currentIndex) == Configures.SettingsBasicTab:
                self.basic_tab_default()
            elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDownloadTab:
                self.download_tab_default()
            elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDesktopLyricTab:
                self.desktoplyric_tab_default()

    def basic_tab_confirm(self):
        self.close_button_act_changed.emit(globalSettings.CloseButtonAct)
    
    def basic_tab_cancel(self):
        if globalSettings.CloseButtonAct == Configures.SettingsHide:
            self.hideItButton.setChecked(True)
        else:
            self.exitItButton.setChecked(True)
        self.check_close_button_act()
    
    def basic_tab_default(self):
        self.hideItButton.setChecked(True)
        self.check_close_button_act()

    def download_tab_confirm(self):
        self.downloadDirChanged.emit(globalSettings.DownloadfilesPath)

    def download_tab_cancel(self):
        self.lineEdit.setText(globalSettings.DownloadfilesPath)
    
    def download_tab_default(self):
        self.lineEdit.setText(configOptions[globalSettings.optionsHub.DownloadfilesPath])
    
    def desktoplyric_tab_confirm(self):
        self.desktop_lyric_style_changed.emit()
    
    def desktoplyric_tab_cancel(self):
        for index in range(len(self.colorButtons)):
            self.colorButtons[index].set_color(globalSettings.DesktoplyricColors[index])
            
    def desktoplyric_tab_default(self):
        for index in range(len(self.colorButtons)):
            self.colorButtons[index].set_color(configOptions[globalSettings.optionsHub.DesktoplyricColors][index])

    def check_control_buttons_state(self):
        self.okButton.setEnabled(bool(len(self.modifiedDict)))
        self.cancelButton.setEnabled(bool(len(self.modifiedDict)))
    
    def select_dir(self):
        f = QFileDialog()
        newDir = f.getExistingDirectory(self, "选择下载文件夹", Configures.HomeDir, QFileDialog.ShowDirsOnly)
        if not os.path.isdir(newDir):
            QMessageBox.critical(self, '错误', '您输入的不是一个文件夹！')
            self.lineEdit.setText(globalSettings.DownloadfilesPath)
            return
        if newDir:
            self.lineEdit.setText(newDir)
    
    def check_changed_text(self, text):
        self.check_and_change_edit_state(globalSettings.optionsHub.DownloadfilesPath, globalSettings.DownloadfilesPath, text.strip())
    
    def preview(self, i, color):
        if self.colors[i] != color:
            self.colors[i] = color
        colors_tuple = tuple(self.colors)
        self.previewLabel.set_color(colors_tuple)
        self.check_and_change_edit_state(globalSettings.optionsHub.DesktoplyricColors, globalSettings.DesktoplyricColors, colors_tuple)
    
    def check_close_button_act(self):
        act = Configures.SettingsHide
        if self.exitItButton.isChecked():
            act = Configures.SettingsExit
        self.check_and_change_edit_state(globalSettings.optionsHub.CloseButtonAct, globalSettings.CloseButtonAct, act)
    
    def hideit_button_clicked(self):
        act = Configures.SettingsHide
        self.check_and_change_edit_state(globalSettings.optionsHub.CloseButtonAct, globalSettings.CloseButtonAct, act)
    
    def exitit_button_clicked(self):
        act = Configures.SettingsExit
        self.check_and_change_edit_state(globalSettings.optionsHub.CloseButtonAct, globalSettings.CloseButtonAct, act)
    
    def check_and_change_edit_state(self, option, default, new):
        if new != default:
            self.modifiedDict[option] = new
        else:
            if option in self.modifiedDict:
                del self.modifiedDict[option]
        self.check_control_buttons_state()

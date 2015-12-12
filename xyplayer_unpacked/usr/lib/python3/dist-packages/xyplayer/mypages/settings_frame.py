import os
from PyQt5.QtWidgets import QMessageBox,QHBoxLayout, QPushButton, QTabWidget, QLabel, QWidget, QVBoxLayout, QDialog
from PyQt5.QtCore import pyqtSignal, Qt
from xyplayer import Configures
from xyplayer.mypages import desktop_lyric
from xyplayer.mywidgets import FontPanel, ColorsPanel, CloseActionsBox, PathSelectPanel, LyricPanelsBox
from xyplayer.mysettings import globalSettings

class SettingsFrame(QDialog):
    download_dir_changed = pyqtSignal(str)
    desktop_lyric_style_changed = pyqtSignal()
    close_button_act_changed = pyqtSignal(int)
    window_lyric_style_changed = pyqtSignal()
    def __init__(self, parent = None):
        super(SettingsFrame, self).__init__(parent)
#        self.setStyleSheet("QPushButton{font-family:'微软雅黑';font-size:14px;}")
        self.initial_basic_tab()
        self.initial_download_tab()
        self.initial_lyric_tab()
        self.initial_main_ui()
        self.create_connections()
        self.initial_parames()
    
    def create_connections(self):
        self.tabWidget.currentChanged.connect(self.tab_switched)
        self.pathSelectPanel.download_dir_changed.connect(self.change_download_dir)
        self.fontPanel.font_style_changed.connect(self.set_new_desktoplyric_font_style)
        self.colorsPanel.color_changed.connect(self.set_new_colors)
        self.closeActionsBox.close_act_changed.connect(self.check_close_button_act)
        self.lyricPanelsBox.parameters_changed.connect(self.set_new_windowlyric_font_style)
    
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
        self.closeActionsBox = CloseActionsBox()
        self.lyricPanelsBox = LyricPanelsBox()
        self.basic_tab_revert_parameters()
        mainLayout = QVBoxLayout(self.basicTab)
        mainLayout.addWidget(self.closeActionsBox)
        mainLayout.addStretch()
        mainLayout.addWidget(self.lyricPanelsBox)
        mainLayout.addStretch()
    
    def initial_download_tab(self):
        self.downloadTab = QWidget()
        self.pathSelectPanel = PathSelectPanel()
        self.download_tab_revert_parameters()
        downloadTabLayout = QVBoxLayout(self.downloadTab)
        downloadTabLayout.addWidget(self.pathSelectPanel)
        downloadTabLayout.addStretch()
    
    def initial_lyric_tab(self):
        self.lyricTab = QWidget()
        self.previewLabel = desktop_lyric.DesktopLyricBasic()
        self.previewLabel.setFixedHeight(80)
        self.previewLabel.set_color(globalSettings.DesktoplyricColors)
        label1 = QLabel('颜色：', self.lyricTab)
        label1.setFixedWidth(50)
        label2 = QLabel('预览：', self.lyricTab)
        self.fontPanel = FontPanel()
        self.colorsPanel = ColorsPanel()
        self.desktoplyric_tab_revert_parameters()
        lyricColorLayout = QHBoxLayout()
        lyricColorLayout.addWidget(label1)
        lyricColorLayout.addWidget(self.colorsPanel)
        lyricTabLayout = QVBoxLayout(self.lyricTab)
        lyricTabLayout.setSpacing(6)
        lyricTabLayout.addWidget(self.fontPanel)
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
        mainLayout.setContentsMargins(0, 0, 0, 0)

    def check_control_buttons_state(self):
        self.okButton.setEnabled(bool(len(self.modifiedDict)))
        self.cancelButton.setEnabled(bool(len(self.modifiedDict)))

    def check_and_change_edit_state(self, option, default, new):
        if new != default:
            self.modifiedDict[option] = new
        else:
            if option in self.modifiedDict:
                del self.modifiedDict[option]
        self.check_control_buttons_state()

    def make_modified_global_settings_valid(self):
        for key, value in self.modifiedDict.items():
            if key == globalSettings.optionsHub.DownloadfilesPath:
                if not os.path.isdir(value):
                    QMessageBox.critical(self, '错误', '您输入的不是一个文件夹！')
                    return False
            globalSettings.__setattr__(key, value)
        self.modifiedDict.clear()
        self.check_control_buttons_state()
        return True

    def confirm(self):
        if not self.make_modified_global_settings_valid() :
            return
        if self.tabWidget.tabText(self.currentIndex) == Configures.SettingsBasicTab:
            self.basic_tab_confirm()
        elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDownloadTab:
            self.download_tab_confirm()
        elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDesktopLyricTab:
            self.desktoplyric_tab_confirm()

    def cancel(self):
        if self.tabWidget.tabText(self.currentIndex) == Configures.SettingsBasicTab:
            self.basic_tab_revert_parameters()
        elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDownloadTab:
            self.download_tab_revert_parameters()
        elif self.tabWidget.tabText(self.currentIndex) == Configures.SettingsDesktopLyricTab:
            self.desktoplyric_tab_revert_parameters()

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
        self.window_lyric_style_changed.emit()
    
    def basic_tab_revert_parameters(self):
        self.closeActionsBox.set_close_act(globalSettings.CloseButtonAct)
        self.lyricPanelsBox.set_box_parameters(
            globalSettings.WindowlyricRunFontSize, 
            globalSettings.WindowlyricRunFontColor, 
            globalSettings.WindowlyricReadyFontSize, 
            globalSettings.WindowlyricReadyFontColor)
        
    def basic_tab_default(self):
        self.closeActionsBox.restore_default_close_act()
        self.lyricPanelsBox.restore_default_font_style()

    def download_tab_confirm(self):
        self.download_dir_changed.emit(globalSettings.DownloadfilesPath)

    def download_tab_revert_parameters(self):
        self.pathSelectPanel.lineEdit.setText(globalSettings.DownloadfilesPath)
    
    def download_tab_default(self):
        self.pathSelectPanel.restore_default_download_dir()
    
    def desktoplyric_tab_confirm(self):
        self.desktop_lyric_style_changed.emit()
    
    def desktoplyric_tab_revert_parameters(self):
        self.fontPanel.set_font_style(globalSettings.DesktoplyricFontFamily, 
            globalSettings.DesktoplyricFontSize, globalSettings.DesktoplyricFontForm)
        self.colorsPanel.set_colors(globalSettings.DesktoplyricColors)
            
    def desktoplyric_tab_default(self):
        self.fontPanel.restore_default_font_style()
        self.colorsPanel.restore_default_colors()
    
    def change_download_dir(self, text):
        self.check_and_change_edit_state(globalSettings.optionsHub.DownloadfilesPath, globalSettings.DownloadfilesPath, str(text))
    
    def check_close_button_act(self, act):
        self.check_and_change_edit_state(globalSettings.optionsHub.CloseButtonAct, globalSettings.CloseButtonAct, act)
    
    def set_new_desktoplyric_font_style(self, option, new):
        if option == globalSettings.optionsHub.DesktoplyricFontFamily:
            default = globalSettings.DesktoplyricFontFamily
        elif option == globalSettings.optionsHub.DesktoplyricFontSize:
            default = globalSettings.DesktoplyricFontSize
            new = int(new)
        elif option == globalSettings.optionsHub.DesktoplyricFontForm:
            default = globalSettings.DesktoplyricFontForm
        self.previewLabel.set_font_style(*self.get_lyric_font_styles())
        self.check_and_change_edit_state(option, default, new)
    
    def set_new_windowlyric_font_style(self, option, new):
        if option == globalSettings.optionsHub.WindowlyricRunFontSize:
            default = globalSettings.WindowlyricRunFontSize
            new = int(new)
        elif option == globalSettings.optionsHub.WindowlyricRunFontColor:
            default = globalSettings.WindowlyricRunFontColor
        elif option == globalSettings.optionsHub.WindowlyricReadyFontSize:
            default = globalSettings.WindowlyricReadyFontSize
            new = int(new)
        elif option == globalSettings.optionsHub.WindowlyricReadyFontColor:
            default = globalSettings.WindowlyricReadyFontColor
        self.check_and_change_edit_state(option, default, new)

    def set_new_colors(self):
        colors = self.get_lyric_colors()
        self.previewLabel.set_color(colors)
        self.check_and_change_edit_state(globalSettings.optionsHub.DesktoplyricColors, globalSettings.DesktoplyricColors, colors)
    
    def get_lyric_colors(self):
        return self.colorsPanel.get_colors()
        
    def get_lyric_font_styles(self):
        return self.fontPanel.get_font_style()
    
    def get_window_lyric_params(self):
        return (
            globalSettings.WindowlyricRunFontSize, 
            globalSettings.WindowlyricRunFontColor, 
            globalSettings.WindowlyricReadyFontSize, 
            globalSettings.WindowlyricReadyFontColor)

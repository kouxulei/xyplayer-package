from PyQt5.QtGui import QColor
from xyplayer import Configures
from xyplayer.utils import system_fonts

configOptions = {
    'CloseButtonAct': Configures.SettingsHide, 
    'DownloadfilesPath': Configures.MusicsDir, 
    'DesktoplyricFontFamily': system_fonts[0],
    'DesktoplyricFontSize': 35,    #values: 20~60, step by 5
    'DesktoplyricFontForm': '常规', 
    'DesktoplyricColors': (QColor(14, 100, 255), QColor(85, 255, 127), QColor(14, 100, 255)), 
    'WindowlyricRunFontSize': 28,     #values: 18~30, step by 1
    'WindowlyricRunFontColor': 'purple', 
    'WindowlyricReadyFontSize': 15,     #values: 12~24, step by 1
    'WindowlyricReadyFontColor': 'teal'
}

def read_from_settings(key, keyType, default=None, settings=Configures.Settings):
    if not settings.contains(key):
        return default
    try:
        value = settings.value(key, type=keyType)
        if isinstance(value, keyType):
            return value
        return keyType(value)
    except TypeError as error:
        print('Warning: %s'%str(error))
        return default if default else keyType()

def write_to_settings(key, value, default, settings=Configures.Settings):
    if value == default:
        settings.remove(key)
    else:
        settings.setValue(key, value)

class SettingOptions(object):pass

class MySettings(object):
    """用来收集属性及其值的类。"""
    def __init__(self):
        object.__setattr__(self, 'optionsHub', SettingOptions())
        for option in configOptions:
            value = configOptions[option]
            object.__setattr__(self.optionsHub, option, option)
            object.__setattr__(self, option, read_from_settings(option, type(value), default=value))
    
    def __setattr__(self, option, value):
        if not option in configOptions:
            raise AttributeError('Unknown attribute %s!'%option)
        object.__setattr__(self, option, value)
        write_to_settings(option, value, configOptions[option])
    
    def check_download_path(self):
        downloadPathOrigin = Configures.clean_old_settings_file()
        if downloadPathOrigin:
            self.DownloadfilesPath = downloadPathOrigin 

globalSettings = MySettings()
globalSettings.check_download_path()

from PyQt5.QtGui import QColor
from xyplayer import Configures, settings

configOptions = {
    'CloseButtonAct': Configures.SettingsHide, 
    'DownloadfilesPath': Configures.MusicsDir, 
    'DesktoplyricFontFamily': "楷体", 
    'DesktoplyricFontWeight': 60, 
    'DesktoplyricFontSize': 35, 
    'DesktoplyricColors': (QColor(14, 100, 255), QColor(114, 150, 230), QColor(14, 100, 255))
}

def readFromSettings(key, keyType, default=None, settings=settings):
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

def writeToSettings(key, value, default, settings=settings):
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
            object.__setattr__(self, option, readFromSettings(option, type(value), default=value))
    
    def __setattr__(self, option, value):
        if not option in configOptions:
            raise AttributeError('Unknown attribute %s!'%option)
        object.__setattr__(self, option, value)
        writeToSettings(option, value, configOptions[option])

globalSettings = MySettings()
globalSettings.DownloadfilesPath = Configures.clean_old_settings_file()

from PyQt5.QtGui import QColor
from xyplayer import Configures, settings

configOptions = {
    'CloseButtonAct': Configures.SettingsHide, 
    'DownloadfilesPath': Configures.MusicsDir, 
    'DesktoplyricFontFamily': '楷体', 
    'DesktoplyricFontSize': 35,    #values: 20~60, step by 5
    'DesktoplyricFontForm': '常规', 
    'DesktoplyricColors': (QColor(14, 100, 255), QColor(85, 255, 127), QColor(14, 100, 255)), 
    'WindowlyricRunFontSize': 20,     #values: 18~30, step by 1
    'WindowlyricRunFontColor': 'white', 
    'WindowlyricReadyFontSize': 16,     #values: 12~24, step by 1
    'WindowlyricReadyFontColor': 'black'
}

def read_from_settings(key, keyType, default=None, settings=settings):
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

def write_to_settings(key, value, default, settings=settings):
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

globalSettings = MySettings()
downloadPathOrigin = Configures.clean_old_settings_file()
if downloadPathOrigin:
    globalSettings.DownloadfilesPath = downloadPathOrigin

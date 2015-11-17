import os
import re
import time
import json
import tempfile
from functools import wraps
from mutagenx.mp3 import MP3
from mutagenx.easyid3 import EasyID3
from PyQt5.QtCore import QTime
from xyplayer import app_version_num, Configures

def trace_to_keep_time(func):
    """用于计算程序运行时间的装饰器。"""
    @wraps(func)
    def _call(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        print('fuction "%s" consumes: %fs'%(func.__name__, time.time() - t1))
        return result  #Do not forget the returns
    return _call

def operate_after_check_thread_locked_state(func):
    """用于判断当前线程锁的状态的修饰器，主要用在添加、删除、清空列表几个操作。"""
    @wraps(func)
    def _call(*args, **kwargs):
        obj = args[0]
        if obj.playlist.get_name() == Configures.PlaylistDownloaded:
            if obj.lock.acquire():
                result = func(*args, **kwargs)
                obj.lock.release()
        else:
            result = func(*args, **kwargs)
        print('%s执行成功!'%func.__name__)
        return result
    return _call

def connect_as_title(artist, musicname):
    return '%s%s%s'%(artist, Configures.Hyphen, musicname)

def get_artist_and_musicname_from_title(title):
    try:
        l = title.split(Configures.Hyphen)
        artist = l[0].strip()
        musicName = l[1].strip()
    except IndexError:
        artist = '未知'
        musicName = title.strip()
    return artist, musicName

def get_full_music_name_from_title(title, musicType=Configures.MusicMp3):
    return '%s.%s'%(title, musicType)

def format_position_to_mmss(value):
    hours = value // 3600
    minutes = (value % 3600) // 60    
    seconds = value % 3600 % 60
    if hours:
        return QTime(hours, minutes, seconds).toString('hh:mm:ss')
    return QTime(0, minutes, seconds).toString('mm:ss')

def read_music_info(path):
    """读取歌曲的tag信息。"""
    audio = MP3(path)
    basepath = os.path.splitext(path)[0]
    basename = os.path.split(basepath)[-1]
    musicname = '%s'%audio.get("TIT2", basename)          
    artist = '%s'%audio.get("TPE1", "") 
    album = '%s'%audio.get("TALB", "未知专辑")
    try:
        totalTimeValue = int(audio.info.length)
        totalTime = format_position_to_mmss(totalTimeValue)
    except:
        totalTime = Configures.ZeroTime
    if not artist:
        title = musicname
    else:
        title = connect_as_title(artist, musicname)
    return title,album, totalTime

def write_tags(musicPath, title, album):
    audio = MP3(musicPath, ID3 = EasyID3)
    audio.clear()
    artist, musicname = get_artist_and_musicname_from_title(title)
    audio['title'] = musicname
    audio['artist'] = artist
    audio['album'] = album.strip()
    audio.save()

def list_to_seconds(timeTuple):
    min, sec, ms = timeTuple
    if not ms:
        currentTime = int(min)*60 + int(sec)
    else:
        currentTime = int(min)*60 + int(sec) + float(ms)
    return currentTime*1000

def get_lyric_offset_from_text(text):
    m = re.search(r'\[offset\:(\-?\d+?)\]', text, re.MULTILINE)
    offset = 0
    recordExists = False
    if m:
        offset = int(m.group(1))
        recordExists = True
    return recordExists, offset

def composite_lyric_path_use_title(title):
    lrcPath = os.path.join(Configures.LrcsDir, '%s.lrc'%title)
    return lrcPath

def change_lyric_offset_in_file(file, offset):
    with open(file, 'r') as f:
       originalText = f.read() 
       f.close()
    offsetRecord = r'[offset:%i]'%offset
    screen = r'\[offset\:(\-?\d+?)\]'
    recordExists, oldOffset = get_lyric_offset_from_text(originalText)
    newText = ''
    if recordExists:
        if offset != oldOffset:
            newText = re.sub(screen, offsetRecord, originalText)
    else:
        newText = '%s\n%s'%(offsetRecord, originalText)
    newText = re.sub(r'\noffset\=(\-?\d+)', '', newText)    #将用原来方法的部分改回来
    if newText:
        with open(file, 'w') as f:
            f.write(newText)
            f.close()       

def parse_lrc(text):
    """解析lrc歌词文件。"""
    recordExists, lrcOffset = get_lyric_offset_from_text(text)
    lines = text.split('\n')
    lrcHandled = {-2:''}
    pattern = re.compile(r'\[([0-9]{2}):([0-9]{2})(\.[0-9]{1,3})?\]')
    for line in lines:
        offset = 0
        match = pattern.search(line)
        timeTags = []
        while True:
            while match:
                currentTime = list_to_seconds(match.groups())
                timeTags.append(currentTime)
                offset = match.end()
                match = pattern.match(line, offset)
            breakFlag = True
            if len(timeTags):
                content = line[offset:].strip()
                if not content:
                    content = '... ...'
                else:
                    match = pattern.search(line, offset)
                    if match:
                        content = line[offset:match.start()].strip()
                        breakFlag = False
                for tag in timeTags:
                    lrcHandled[tag] = content
            if breakFlag:
                break
            else:
                timeTags =[]
    return lrcOffset, lrcHandled

def parse_artist_info(infoPath):
    def _parse_info_text(infoText, infoDict):
        pattern = re.compile(r'\"(\S+?)\"\:\"(.*?)\"\,')
        wraps = pattern.findall(infoText)
        for key, value in wraps:
            if key in infoDict and value:
                infoDict[key] = value
    infoDict = {
        'birthday': '不是今天', 
        'birthplace': '地球', 
        'language': '地球语', 
        'gender': '男/女', 
        'constellation': '神马座', 
        'info': '未找到歌手的详细信息'}
    if infoPath:
        with open(infoPath, 'r') as f:
            infoText = f.read()
        if infoText:
            _parse_info_text(infoText, infoDict)
    return infoDict

def get_pic_url_from_info_text(infoText):
    pattern = re.compile(r'\"pic\"\:\"(.*?)\"\,')
    m = pattern.search(infoText)
    if m:
        return m.group(1)
    return None

def version_to_num(version):
    """将版本号转化成数字序列，主要是方便比较检查是否有更高版本。"""
    m = re.search(r'v(\d+)\.(\d+)\.(\d+)\-(\d+)', version)
    if not m:
        return app_version_num
    numbers = []
    for n in m.groups():
        if len(n) == 1:
            n = '0' + n
        numbers.append(n)
    num_str = ''.join(numbers)
    return int(num_str)
    
def get_file_contents_length(filename):
    """返回一个文件内容长度。"""
    with open(filename, 'rb') as f:
        size = len(f.read())
        f.close()
        return size

def convert_B_to_MB(bytes):
    """单位转换：B转到单位MB。"""
    mb = bytes / (1024 * 1024)
    return mb

def get_usable_fonts():
    """读取系统可用的中文字体"""
    fontsListFile = tempfile.NamedTemporaryFile(prefix='xyplayer-', suffix='.fonts').name
    os.system('fc-list :lang=zh > %s'%fontsListFile)
    fonts = []
    pattern = re.compile(r'\: (.+?)\:')
    with open(fontsListFile, 'r') as f:
        for line in f.readlines():
            m = pattern.search(line)
            font = m.group(1).split(',')[0]
            if font not in fonts:
                fonts.append(font)
    fonts.sort()
    return tuple(fonts)
    
def composite_playlist_path_use_name(listName):
    return os.path.join(Configures.PlaylistsDir, '%s%s'%(listName, Configures.PlaylistsExt))

def rename_playlist(oldName, newName):
    oldPath = composite_playlist_path_use_name(oldName)
    newPath = composite_playlist_path_use_name(newName)
    os.rename(oldPath, newPath)

def remove_playlist(name):
    path = composite_playlist_path_use_name(name)
    os.remove(path)

def wrap_playlist_datas(items=[], infos={}):
        dict = {}
        dict[Configures.PlaylistKeyQueue] = items
        dict[Configures.PlaylistKeyGroup] = infos
        return json.dumps(dict)

def wrap_datas(data=Configures.BasicPlaylists):
    return json.dumps(data)

def parse_json_file(file):
    with open(file, 'r') as f:
        contents = f.read()
        f.close()
    return json.loads(contents)

def write_into_disk(file, datas):
    with open(file, 'w') as f:
        f.write(datas)
        f.close()
    

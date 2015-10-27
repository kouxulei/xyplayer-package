import os
import re
import time
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

def format_position_to_mmss(value):
    hours = value // 3600
    minutes = (value % 3600) // 60    
    seconds = value % 3600 % 60
    if hours:
        return QTime(hours, minutes, seconds).toString('hh:mm:ss')
    return QTime(0, minutes, seconds).toString('mm:ss')

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

def list_to_seconds(timeTuple):
    min, sec, ms = timeTuple
    if not ms:
        currentTime = int(min)*60 + int(sec)
    else:
        currentTime = int(min)*60 + int(sec) + float(ms)
    return currentTime*1000

def parse_lrc(text):
    """解析lrc歌词文件。"""
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
            content = line[offset:].strip()
            breakFlag = True
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
    c = re.match('offset\=(\-?\d+)',lines[-1])
    if c:
        lrcOffset = int(c.group(1))
    else:
        lrcOffset = 0
    return lrcOffset, lrcHandled
    
def write_tags(musicPath, title, album):
    audio = MP3(musicPath, ID3 = EasyID3)
    audio.clear()
    artist, musicname = get_artist_and_musicname_from_title(title)
    audio['title'] = musicname
    audio['artist'] = artist
    audio['album'] = album.strip()
    audio.save()

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

def get_full_music_name_from_title(title, musicType=Configures.MusicMp3):
    return '%s.%s'%(title, musicType)

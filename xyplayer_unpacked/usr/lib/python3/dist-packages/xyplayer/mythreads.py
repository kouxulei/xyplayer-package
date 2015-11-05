import os
import time
import socket
import threading
from urllib import request
from xyplayer import Configures
from xyplayer.utils import write_tags, get_file_contents_length, read_music_info
from xyplayer.urlhandle import SearchOnline
from xyplayer.mytables import TableModel

BufferBlock = 5120

class DownloadLrcThread(threading.Thread):
    """下载歌词、歌手信息的线程。"""
    def __init__(self, list):
        super(DownloadLrcThread, self).__init__()
        self.list = list
        self.runPermit = True
    
    def run(self):
        i = 0
        cnt = len(self.list)
        while i < cnt and self.runPermit:
            title = self.list[i][0]
            try:
                artist = title.split(Configures.Hyphen)[0].strip()
                SearchOnline.get_artist_image_path(artist)
            except:
                pass
            musicId = self.list[i][1]
            if not SearchOnline.is_lrc_path_exists(title):
                SearchOnline.get_lrc_path(title, musicId)
            i  += 1
    
    def stop(self):
        self.runPermit = False

class DownloadThread(threading.Thread):     
    """用于下载歌曲的线程。"""
    timeout = 3
    def __init__(self, title, album, songLink, musicPath, musicId, size, lock):
        super(DownloadThread, self).__init__()
        self.currentLength = 0
        self.title = title
        self.album = album
        self.songLink = songLink
        self.musicPath = musicPath
        self.musicId = musicId
        self.length = size
        self.downloadStatus = Configures.DownloadReady
        self.tempfileName = self.musicPath + '.temp'
        self.runPermit = True
        self.noPause = True
        self.lock = lock    #线程锁
        socket.setdefaulttimeout(self.timeout)
        
    def run(self):
        if self.songLink == Configures.NoLink:
            self.songLink = SearchOnline.get_song_link(self.musicId)
            if not self.songLink:
                self.errorHappend('歌曲的网络链接为空')
                return
        self.downloadStatus = Configures.Downloading
        self.print_info('开始下载')
        self.download_lrc_and_artistinfo(self.title, self.musicId)
        if self.length == 0:
            res = self.try_to_open_url(self.songLink)
            if not res:
                self.errorHappend('无法打开歌曲链接')
            else:
                if res.status == 200 and  res.reason == 'OK' and res.getheader('Content-Type') == 'audio/mpeg':
                    try:
                        self.length = int(res.getheader('Content-Length'))
                    except ValueError:
                        self.errorHappend('无法获取歌曲的大小')
                else:
                    self.errorHappend('不是音乐资源类型')
        if not self.length or self.downloadStatus == Configures.DownloadError:
            return
        self.currentLength = self.check_temp_downloaded(self.tempfileName)
        req = request.Request(self.songLink)
        req.headers['Range'] = 'bytes= %s-%s'%(self.currentLength, self.length)
        res = self.try_to_open_url(req)
        if not res or res.getheader('Content-Type') != 'audio/mpeg':
            self.errorHappend('无法定位到开始下载处的节点位置')
            return
        contentsList = []
        while self.currentLength<self.length and self.runPermit and self.noPause:
            trytimes = 10
            while(trytimes):
                try:
                    contentCache = res.read(BufferBlock)
                    contentsList.append(contentCache)
                    self.currentLength  += BufferBlock
                    if self.currentLength>self.length:
                        self.currentLength = self.length
                    break
                except:
                    time.sleep(0.1)
                    trytimes -= 1
                    continue
            if trytimes == 0:
                self.print_info('下载超时')
                self.pause()
        res.close()
        if self.currentLength == self.length:
            self.downloadStatus = Configures.DownloadCompleted
        if self.downloadStatus != Configures.DownloadCancelled:
            contentsStr = b''.join(contentsList)
            with open(self.tempfileName, 'ab+') as f:
                f.write(contentsStr)
            if self.downloadStatus == Configures.DownloadCompleted:
                if os.path.exists(self.musicPath):
                    os.remove(self.musicPath)
                os.rename(self.tempfileName, self.musicPath)
                write_tags(self.musicPath, self.title, self.album)
                self.print_info('准备添加到“%s”'%Configures.PlaylistDownloaded)
                model = TableModel()
                model.initial_model(Configures.PlaylistDownloaded)
                title, album, totalTime = read_music_info(self.musicPath)
                if self.lock.acquire():
                    model.add_record(title, totalTime, album, self.musicPath, self.length, self.musicId)
                    self.print_info("已完成下载")
                    self.lock.release()
        
    def stop(self):
        self.runPermit = False
        self.downloadStatus = Configures.DownloadCancelled
        if os.path.exists(self.tempfileName):
            os.remove(self.tempfileName)
        self.print_info("已取消下载")
    
    def pause(self):
        self.noPause = False
        self.downloadStatus = Configures.DownloadPaused
        self.print_info("已暂停下载")
    
    def errorHappend(self, error):
        self.downloadStatus = Configures.DownloadError
        self.print_info('下载出错')
        print(error)
    
    def print_info(self, info):
        print('%s : %s'%(info, self.title))
    
    def try_to_open_url(self, songLink, retries=5):
        while retries:
            try:
                res = request.urlopen(songLink, timeout=3)
                return res
            except:
                retries -= 1
                time.sleep(0.1)
                continue
        return None
    
    def check_temp_downloaded(self, tempfileName):
        """查看是否有下载一半的文件，如果有就继续下载到该临时文件。"""
        if not os.path.exists(self.tempfileName):
            currentLength = 0
            with open(self.tempfileName, 'w') as f:
                f.close()
        else:
            currentLength = get_file_contents_length(self.tempfileName)
        return currentLength
            
    def download_lrc_and_artistinfo(self, title, musicId):
        """下载歌曲的同时去下载对应的歌词、歌手信息等内容。"""
        lrcName = title + '.lrc'
        lrcPath = os.path.join(Configures.LrcsDir, lrcName)
        if os.path.exists(lrcPath):
            os.remove(lrcPath)
        list_temp = [(title, musicId)]
        thread = DownloadLrcThread(list_temp)
        thread.setDaemon(True)
        thread.setName('downloadLrc')
        thread.start()

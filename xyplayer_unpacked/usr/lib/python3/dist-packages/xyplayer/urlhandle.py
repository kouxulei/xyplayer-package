import os
import time
import socket
import re
import zlib
import base64
from urllib import request, parse
from xyplayer import Configures
from xyplayer.utils import (trace_to_keep_time, get_artist_and_musicname_from_title, 
    composite_lyric_path_use_title, get_pic_url_from_info_text)

reqCache = {}
songLinkCache = {}
    
class SearchOnline(object):
    """存放所有与获取在线信息有关的函数。"""
    @trace_to_keep_time
    def search_songs(searchByType, keyword, page, rn = 15):
        url = ''.join([
            'http://search.kuwo.cn/r.s?ft=music&rn=%s'%rn,'&newsearch=1&primitive=0&cluster=0&itemset=newkm&rformat=xml&encoding=utf8&%s='%searchByType, 
            SearchOnline.parse_quote(keyword), 
            '&pn=', 
            str(page)
        ])
        if url not in reqCache:    
            reqContent = SearchOnline.url_open(url)
            if reqContent ==  Configures.UrlError:
                return (None, Configures.UrlError)
            if not reqContent:
                return (None, 0)    
            reqCache[url] = reqContent
        songs, hit = SearchOnline.parse_songs_wrap(reqCache[url])
        return (songs, hit)
    
    def get_song_link(musicId):
        if musicId in songLinkCache:
            return songLinkCache[musicId][0]
        url = 'http://antiserver.kuwo.cn/anti.s?response=url&type=convert_url&format=%s&rid=MUSIC_%s'%(Configures.MusicMp3, musicId)
        reqContent = SearchOnline.url_open(url)
        if reqContent == Configures.UrlError:
            print('联网出错')
            return None
        if not reqContent:
            return None
        songLinkTemp = reqContent
        if len(songLinkTemp)<20:
            return None
        songLinkTemp = songLinkTemp.split('/')
        songLink = '/'.join(songLinkTemp[:3]+songLinkTemp[5:])
        return songLink
    
    def get_artist_info_path(artist):
        """获取歌手信息。"""
        infoPath = SearchOnline.get_local_artist_info_path(artist)
        if os.path.exists(infoPath):
            return infoPath
        url = ''.join([
        'http://search.kuwo.cn/r.s?', 
        'stype=artistinfo&artist=', 
        SearchOnline.parse_quote(artist)
        ])
        reqContent = SearchOnline.url_open(url)
        if reqContent ==  Configures.UrlError:
            return None
        try:
            info = reqContent.replace('"', '''\\"''').replace("'", '"').replace('\t', '').replace('\\', '')
            with open(infoPath, 'w+') as f:
                f.write(info)
            return infoPath
        except ValueError:
            return None
        if not info:
            return None
            
    def get_local_artist_info_path(artist):
        infoName = artist+'.info'
        infoPath = os.path.join(Configures.ArtistinfosDir, infoName)
        return infoPath

    def get_artist_image_path(artist):
        def _get_artist_pic_url(pic_path):
            if len(pic_path) < 5:
                return None
            if pic_path[:2] in ('55', '90'):
                pic_path = '100/%s'%pic_path[2:]
            url = ''.join(['http://img4.kwcdn.kuwo.cn/', 'star/starheads/', pic_path])
            return url
        imageName = artist+'.jpg'
        imagePath = os.path.join(Configures.ImagesDir, imageName)
        if os.path.exists(imagePath):
            return imagePath          
        infoPath = SearchOnline.get_artist_info_path(artist)
        if not infoPath:
            return None
        with open(infoPath, 'r+') as f:
            infoStr = f.read()
        picPath = get_pic_url_from_info_text(infoStr)
        picUrl = _get_artist_pic_url(picPath)
        if not picUrl or len(picUrl)<10:
            return None
        try:
            req = request.urlopen(picUrl)
        except:
            return None
        if req.status != 200 or req.reason != 'OK':
            return None
        if req.getheader('Content-Type') != 'image/jpeg':
            print(req.getheader('Content-Type'))
            return None
        image = req.read()
        with open(imagePath, 'wb+') as f:
            f.write(image)
        return imagePath
    
    def  get_lrc_contents(title, musicId):
        """获取歌词。"""
        lrcPath = composite_lyric_path_use_title(title)
        if os.path.exists(lrcPath):
            f = open(lrcPath, 'r')
            contents = f.read()
            if contents == 'None':
                return Configures.LyricNone
            if contents not in ('Configures.UrlError', 'Error'):
                return contents
        if musicId != Configures.LocalMusicId:
            lrcContent = SearchOnline.get_lrc_from_musicid(musicId)
        else:
            lrcContent = SearchOnline.get_lrc_from_title(title)
        with open(lrcPath, 'w') as f:
            if lrcContent == Configures.LyricNone:
                f.write('None')
            elif lrcContent == Configures.LyricNetError:
                f.write('Error')
            else:
                f.write(lrcContent)
            f.close()
        return lrcContent

    def get_lrc_from_musicid(musicId):
        url = ('http://newlyric.kuwo.cn/newlyric.lrc?' + 
            SearchOnline.encode_lrc_url(musicId))
        try:
            req = request.urlopen(url)
            if req.status != 200 or req.reason != 'OK':
                return Configures.LyricNetError
            reqContent = req.read()
        except:
            return Configures.LyricNetError
        if not reqContent:
            return Configures.LyricNone
        try:
            lrcContent = SearchOnline.decode_lrc_content(reqContent)
            return lrcContent if lrcContent else Configures.LyricNone
        except:
            return Configures.LyricNone

    def get_lrc_from_title(title):
        try:
            artist, songName = get_artist_and_musicname_from_title(title)
            print('searchOnline_%s'%artist)
            url = ''.join([
                'http://search.kuwo.cn/r.s?ft=music&rn=1', '&newsearch=1&primitive=0&cluster=0&itemset=newkm&rformat=xml&encoding=utf8&artist=', 
                SearchOnline.parse_quote(artist), 
                '&all=', 
                SearchOnline.parse_quote(songName), 
                '&pn=0'
            ])
            reqContent = SearchOnline.url_open(url)
            if reqContent ==  Configures.UrlError:
                return Configures.LyricNetError
            if not reqContent:
                return Configures.LyricNone
            songs, hit = SearchOnline.parse_songs_wrap(reqContent)
            if hit == 0 or  not songs:
                return Configures.LyricNone
            musicId = songs[0][3]
            if not musicId:
                return Configures.LyricNone
            lrcContent = SearchOnline.get_lrc_from_musicid(musicId)
            return lrcContent if lrcContent else Configures.LyricNone
        except:
            return Configures.LyricNone

    def parse_songs_wrap(str):
        hit = int(re.search('Hit\=(\d+)', str).group(1))
        songs_wrap = []
        str_list = str.split('\r\n\r\n')
        for i in range(1, 16):
            if str_list[i]:
                song_list = str_list[i].split('\r\n')
                songname = song_list[0][9:]
                artist = song_list[1][7:]
                album = song_list[2][6:]
                music_id = song_list[6][15:]
                score = song_list[18][9:]
                songs_wrap.append([songname, artist, album, music_id, score])
                continue
            break
        return songs_wrap, hit
    
    def parse_quote(str):
        return parse.quote(str, safe = '~@#$&()*!+=:;,.?/\'')

    def url_open(url, retries = 4):
        socket.setdefaulttimeout(3)
        while retries:
            try:
                req = request.urlopen(url, timeout=3)
                req = req.read()
                reqContent = req.decode()
                reqContent = reqContent.lstrip()
                return reqContent
            except:
                retries -= 1
                time.sleep(0.05)
                continue
        return Configures.UrlError
    
    def encode_lrc_url(musicId):
        param = ('user=12345,web,web,web&requester=localhost&req=1&rid=MUSIC_%s' %musicId)
        str_bytes = SearchOnline.xor_bytes(param.encode())
        output = base64.encodebytes(str_bytes).decode()
        return output.replace('\n', '')
        
    def decode_lrc_content(lrc, is_lrcx = False):
        if lrc[:10]  != b'tp=content':
            return None
        index = lrc.index(b'\r\n\r\n')
        lrc_bytes = lrc[index+4:]
        str_lrc = zlib.decompress(lrc_bytes)
        if not is_lrcx:
            return str_lrc.decode('gb18030')
        str_bytes = base64.decodebytes(str_lrc)
        return SearchOnline.xor_bytes(str_bytes).decode('gb18030')
    
    def xor_bytes(str_bytes, key = 'yeelion'):
        xor_bytes = key.encode('utf8')
        str_len = len(str_bytes)
        xor_len = len(xor_bytes)
        output = bytearray(str_len)
        i = 0
        while i < str_len:
            j = 0
            while j < xor_len and i < str_len:
                output[i] = str_bytes[i] ^ xor_bytes[j]
                i +=  1
                j +=  1
        return output  

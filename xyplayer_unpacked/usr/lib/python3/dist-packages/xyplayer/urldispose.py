import os, json, base64, zlib
from urllib import request
from PyQt4.QtGui import  QMessageBox
from xyplayer.util import parse_songs_wrap, parse_quote, url_open
from xyplayer.configure import Configures

if not os.path.exists(Configures.urlCache):
    f =open(Configures.urlCache, 'w') 
    f.close()

reqCache = {}
f= open(Configures.urlCache, 'r+')
contents = f.read()
if contents:
    reqCache = json.loads(contents) 
songLinkCache = {}
    
class SearchOnline():

    def search_songs(searchByType, keyword, page, rn = 15):
        url = ''.join([
            'http://search.kuwo.cn/r.s?ft=music&rn=%s'%rn,'&newsearch=1&primitive=0&cluster=0&itemset=newkm&rformat=xml&encoding=utf8&%s='%searchByType, 
            parse_quote(keyword), 
            '&pn=', 
            str(page)
        ])
        if url not in reqCache:    
            reqContent = url_open(url)
            if reqContent ==  Configures.URLERROR:
                return (None, Configures.URLERROR)
            if not reqContent:
                return (None, 0)    
            reqCache[url] = reqContent
            contents = json.dumps(reqCache)
            with open(Configures.urlCache, 'w') as f:
                f.write(contents)
        songs, hit = parse_songs_wrap(reqCache[url])
        return (songs, hit)
    
    def get_song_link(musicId):
        if musicId in songLinkCache:
            return songLinkCache[musicId][0]
        url = 'http://antiserver.kuwo.cn/anti.s?response=url&type=convert_url&format=mp3&rid=MUSIC_%s'%musicId
        reqContent = url_open(url)
        if reqContent == Configures.URLERROR:
            QMessageBox.critical(None, "错误", "联网出错！\n请检查网络连接是否正常！")     
            return None
        if not reqContent:
            return None
        songLinkTemp = reqContent
        if len(songLinkTemp)<20:
            return None
        songLinkTemp = songLinkTemp.split('/')
        songLink = '/'.join(songLinkTemp[:3]+songLinkTemp[5:])
        return songLink

#获取歌手信息
    def get_artist_info_path(artist):
        infoName = artist+'.info'
        infoPath = os.path.join(Configures.artistInfosDir, infoName)
        if os.path.exists(infoPath):
            return infoPath
        url = ''.join([
        'http://search.kuwo.cn/r.s?', 
        'stype=artistinfo&artist=', 
        parse_quote(artist)
        ])
        reqContent = url_open(url)
        if reqContent ==  Configures.URLERROR:
            return None
#        if not reqContent:
#            return None
        try:
            info = reqContent.replace('"', '''\\"''').replace("'", '"').replace('\t', '')
            with open(infoPath, 'w+') as f:
                f.write(info)
            return infoPath
        except ValueError:
            return None
        if not info:
            return None

    def get_artist_image_path(artist):
        imageName = artist+'.jpg'
        imagePath = os.path.join(Configures.imagesDir, imageName)
        if os.path.exists(imagePath):
            return imagePath          
        infoPath = SearchOnline.get_artist_info_path(artist)
        if not infoPath:
            return None
        with open(infoPath, 'r+') as f:
            infoStr = f.read()
        infoList = json.loads(infoStr)
        try:
            picPath = infoList['pic']
        except:
            return None
        picUrl = SearchOnline.get_artist_pic_url(picPath)
        if not picUrl or len(picUrl)<10:
            return None
        try:
            req = request.urlopen(picUrl)
        except:
            return None
        if req.status != 200 or req.reason != 'OK':
            return None
        print('here6')
        if req.getheader('Content-Type') != 'image/jpeg':
            print(req.getheader('Content-Type'))
            return None
        image = req.read()
#        if not image:
#            return None
        print('here2')
        with open(imagePath, 'wb+') as f:
            f.write(image)
        return imagePath
    
    def get_artist_pic_url(pic_path):
        if len(pic_path) < 5:
            return None
        if pic_path[:2] in ('55', '90',):
            pic_path = '100/' + pic_path[2:]
        url = ''.join(['http://img4.kwcdn.kuwo.cn/', 'star/starheads/', pic_path, ])
        return url
    
    def is_lrc_path_exists(title):
        lrcName = title + '.lrc'
        lrcPath = os.path.join(Configures.lrcsDir, lrcName)
        if os.path.exists(lrcPath):
            return lrcPath
        return None
    
#获取歌词   
    def  get_lrc_path(title, musicId):
        lrcName = title+'.lrc'
        lrcPath = os.path.join(Configures.lrcsDir, lrcName)
#        print(lrcPath)
#        if os.path.exists(lrcPath):
#            return lrcPath
        if musicId:
            lrcContent = SearchOnline.get_lrc_from_musicid(musicId)
        else:
            lrcContent = SearchOnline.get_lrc_from_title(title)
        with open(lrcPath, 'w') as f:
            if not lrcContent:
                f.write('None')
            elif lrcContent == Configures.URLERROR:
                f.write('Configures.URLERROR')
            else:
                f.write(lrcContent)
        return lrcPath
    
    def get_lrc_from_title(title):
        try:
            artist = title.split('._.')[0].strip()
            songName = title.split('._.')[1].strip()
            print('searchOnline_%s'%artist)
            url = ''.join([
                'http://search.kuwo.cn/r.s?ft=music&rn=1', '&newsearch=1&primitive=0&cluster=0&itemset=newkm&rformat=xml&encoding=utf8&artist=', 
                parse_quote(artist), 
                '&all=', 
                parse_quote(songName), 
                '&pn=0'
            ])
            reqContent = url_open(url)
            print(reqContent)
            if reqContent ==  Configures.URLERROR:
                return Configures.URLERROR
            if not reqContent:
                return None
#            try:
#                songsWrap = jsonLoads(reqContent)
#            except ValueError :
#                return None
#            hit = int(songsWrap['HIT'])
#            songs = songsWrap['abslist']
            songs, hit = parse_songs_wrap(reqContent)
        except:
            return None
#        if hit == Configures.URLERROR:
#            return Configures.URLERROR
        if hit == 0 or  not songs:
            return None
        try:
            musicId = songs[0][3]
            if not musicId:
                return None
            lrcContent = SearchOnline.get_lrc_from_musicid(musicId)
#            if not lrcPath1: 
#                return None
#            if lrcPath1 == Configures.URLERROR:
#                return Configures.URLERROR
            return lrcContent
        except:
            return None
        
        
    
    def get_lrc_from_musicid(musicId):
        url = ('http://newlyric.kuwo.cn/newlyric.lrc?' + 
            SearchOnline.encode_lrc_url(musicId))
#        print(url)
        try:
            req = request.urlopen(url)
        except:
            return Configures.URLERROR
        if req.status != 200 or req.reason != 'OK':
            return Configures.URLERROR
        reqContent = req.read()
        if reqContent ==  Configures.URLERROR:
            return Configures.URLERROR
        if not reqContent:
            return None
        try:
            lrcContent = SearchOnline.decode_lrc_content(reqContent)
#            if not lrcContent:
#                return None
            return lrcContent
#            with open(lrcPath, 'w') as f:
#                f.write(lrcContent)
#            return lrcPath
        except:
            return None
    
    def encode_lrc_url(musicId):
        param = ('user=12345,web,web,web&requester=localhost&req=1&rid=MUSIC_' +
              str(musicId))
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
        #key = 'yeelion'
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

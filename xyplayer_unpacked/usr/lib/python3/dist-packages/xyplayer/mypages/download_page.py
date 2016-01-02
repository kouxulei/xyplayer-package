from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from xyplayer import Configures
from xyplayer.mywidgets import LabelButton, DownloadListItem
from xyplayer.mytables import WorksList
from xyplayer.myplaylists import DownloadWorksModel
from xyplayer.mythreads import DownloadThread

class DownloadPage(QWidget):
    work_complete_signal = pyqtSignal()    #下载任务完成时，用于通 知主程序刷新显示“我的下载”歌单
    def __init__(self, parent = None):
        super(DownloadPage, self).__init__(parent)
        self.setup_ui()
        self.initial_params()
        self.initial_timer()
        
    def setup_ui(self):
        self.titleLabel = LabelButton('下载任务(0/0)')
        self.titleLabel.setFixedSize(110, 33)
        self.titleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.netSpeedInfo = QLabel('0.00 KB/s')
        self.netSpeedInfo.setFixedWidth(135)
        self.netSpeedInfo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        firstLayout = QHBoxLayout()
        firstLayout.setContentsMargins(7, 0, 7, 3)
        firstLayout.addWidget(self.titleLabel)
        firstLayout.addStretch()
        firstLayout.addWidget(self.netSpeedInfo)
        
        self.downloadList = WorksList()
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 5, 0, 0)
        mainLayout.addLayout(firstLayout)
        mainLayout.addWidget(self.downloadList)
        
    def create_connections(self):
        pass
    
    def initial_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
    
    def initial_params(self):
        self.deletePermit = False
        self.timeSpan = 600    #更新网速的时间间隔，单位为ms
        self.allDownloadWorks = {}    #线程的索引表，key为线程名，value为线程
        self.runWorksCount = 0    #当前正在进行的任务数
        self.allWorksCount =len(self.allDownloadWorks)    #管理器中的所有任务数
    
    def download_status_changed(self, ident, isPaused):
        """暂停或重启一个任务。"""
        work = self.allDownloadWorks[ident][0]
        if isPaused:
            if work.downloadStatus != Configures.DownloadCompleted:
                work.pause()
        else:
            args = [work.title, work.album, work.songLink, work.musicPath, work.musicId, work.length, work.lock]
            newDownloadWork = DownloadThread(*args)
            newDownloadWork.setName(ident)
            newDownloadWork.setDaemon(True)
            self.allDownloadWorks[ident][0] = newDownloadWork
            newDownloadWork.start()
            if not self.timer.isActive():
                self.timer.start(self.timeSpan)
    
    def add_a_download_work(self, songLink, musicPath, title, album, musicId, size, lock):
        """开始一个下载任务。"""
        if musicPath in self.allDownloadWorks:
            print('下载任务已存在%s'%musicPath)
            return
        downloadWork = DownloadThread(title, album, songLink, musicPath, musicId, size, lock)
        downloadWork.setDaemon(True)
        downloadWork.setName(musicPath)
        downloadListItem = DownloadListItem(musicPath, title, self.timeSpan)
        downloadListItem.downloadStatusChanged.connect(self.download_status_changed)
        downloadListItem.killWork.connect(self.kill_a_download_work)
        self.downloadList.add_item(downloadListItem, 86)
        self.allDownloadWorks[musicPath] = [downloadWork, downloadListItem]
        downloadWork.start()
        if not self.timer.isActive():
            self.timer.start(self.timeSpan)
    
    def update_progress(self):
        """更新各个下载任务的进度信息。"""
        self.completedWorkNames = []
        aliveThreadExists, netSpeed, runWorks = self.get_state_infos_from_every_works()
        if self.runWorksCount != runWorks or self.allWorksCount != len(self.allDownloadWorks):
            self.runWorksCount = runWorks
            self.allWorksCount = len(self.allDownloadWorks)
            self.titleLabel.set_text('下载任务(%s/%s)'%(self.runWorksCount, self.allWorksCount))
        if aliveThreadExists:
            self.netSpeedInfo.setText("%.2f KB/s"%netSpeed)
        else:
            self.timer.stop()
            self.get_state_infos_from_every_works()    #时钟停止后还要再最后 确认更新一次界面的信息
            self.netSpeedInfo.setText("0.00 KB/s")
            self.titleLabel.set_text('下载任务(0/%s)'%len(self.allDownloadWorks))
        if len(self.completedWorkNames):
            self.work_complete_signal.emit()
    
    def remove_work_from_download_list(self, completedWorkNames):
        for i in sorted(range(self.downloadList.rowCount()), reverse=True):
            if self.downloadList.allListItems[i].ident in completedWorkNames:
                self.downloadList.remove_item_at_row(i)
        for name in completedWorkNames:
            del self.allDownloadWorks[name]
        self.update_progress()
    
    def get_state_infos_from_every_works(self):
        """遍历各个任务，计算需要显示的值。"""
        aliveThreadExists = False    #用于标记是否活动的下载线程
        netSpeed = 0
        runWorks = 0
        for name in self.allDownloadWorks:
            listItem = self.allDownloadWorks[name][1]
            work = self.allDownloadWorks[name][0]
            downloadStatus = work.downloadStatus
            if downloadStatus == Configures.Downloading:
                listItem.update_progress(work.currentLength, work.length)
            else:
                if listItem.statusLabel.text() not in ['已暂停', '已取消', '下载出错', '已完成']:
                    if downloadStatus == Configures.DownloadPaused:
                        listItem.set_pause_state(True, '已暂停')
                    elif downloadStatus == Configures.DownloadCancelled:
                        listItem.set_pause_state(True, '已取消')
                    elif downloadStatus == Configures.DownloadError:
                        listItem.set_pause_state(True, '下载出错')
                    elif downloadStatus == Configures.DownloadCompleted:
                        work.join()
                        listItem.download_completed()
                        self.completedWorkNames.append(name)
            if work.is_alive():
                if not aliveThreadExists:
                    aliveThreadExists = True
                netSpeed += listItem.get_net_speed()
                runWorks += 1
        return aliveThreadExists, netSpeed, runWorks
    
    def kill_a_download_work(self, ident):
        """当下载任务项的取消按键被按下时，移除对应的下载任务。"""
        work = self.allDownloadWorks[ident][0]
        work.stop()
        work.join()    #等待线程执行结束
        self.remove_work_from_download_list([ident])        
    
    def reload_works_from_database(self, lock):
        """在程序启动时，读取数据库中的下载任务信息，并启动"""
        print('Reloading: infos of download works ...')
        downloadWorksModel = DownloadWorksModel()
        for row in range(downloadWorksModel.get_length()):
            args = downloadWorksModel.get_work_info_at_row(row)
            args.append(lock)
            self.add_a_download_work(*args)
        downloadWorksModel.clear_log_file()
    
    def record_works_into_database(self):
        """程序结束时，把未完成的任务记录到数据库中"""
        print('Recording: infos of download works ...')
        downloadWorksModel = DownloadWorksModel()
        for name in self.allDownloadWorks:
            work = self.allDownloadWorks[name][0]
            downloadWorksModel.add_record(*self.get_infos_from_a_work(work))
        downloadWorksModel.commit_records()
        
    def get_infos_from_a_work(self, work):
        title = work.title
        downloadedsize = work.currentLength
        size = work.length
        album = work.album
        songLink = work.songLink
        musicPath = work.musicPath
        musicId = work.musicId
        return [songLink, musicPath, title, album , musicId, size, downloadedsize]

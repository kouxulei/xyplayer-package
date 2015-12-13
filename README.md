#xyplayer-package
xyplayer-package放置[xyplayer](https://github.com/Zheng-Yejian/xyplayer)的deb安装包。  

##<h2 name="installation">程序安装</h2>
下载最新的deb包(用*VERSION*表示某个版本号)：xyplayer_*VERSION*_all.deb  
切换到安装包文件所在的目录下，并执行：

```bash
sudo apt-get install gdebi
sudo gdebi xyplayer_VERSION_all.deb
```

##程序升级
0.8.1以上的版本加入了在线升级的功能：  
右下角菜单键 -> 关于 -> 更新 -> 检查更新 -> 在线更新  
  
***注意***：**由于测试失误，导致v0.8.2-1版本自动更新只下载软件包而没法自动调用gdebi工具安装，如果已经安装此版本，建议采用上述“[程序安装](#installation)”中的方法安装下一版本。**

##欢迎交流
+ qq：1532768931
+ 邮箱：<1035766515@qq.com>

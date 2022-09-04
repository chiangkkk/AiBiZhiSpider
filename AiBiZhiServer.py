import random
from multiprocessing import JoinableQueue as Queue
from multiprocessing import Process
import requests
import json
import os
from threading import Lock, Thread


class AiBiZhiServer:
    baseUrl = 'http://service.aibizhi.adesk.com/v1/wallpaper'
    categoryPath = '/category'
    category = '/4e4d610cdf714d2966000000'
    wallpaper = '/wallpaper'
    skip = 20
    saveImgPath = './download'
    nowCateName = ''
    headers = {
        "User-Agent": "(picasso,170,windows)",
        "Host": "service.aibizhi.adesk.com",
        "If-None-Match": 'W/"570e5c8a1a27db78ca7d51fbca4105b3c02a19c4"',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate'
    }
    downLoadImageHeader = {
        "User-Agent": "(picasso,170,windows)",
        "Host": "img.aibizhi.adesk.com",
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate'

    }

    def __init__(self):
        self.categoryList = None
        self.cateInfo = None
        self.totalCount = None
        self.cateName = None
        self.cateId = None
        self.downloadCount = 1
        self.totalDownloadCount = None
        self.countLock = Lock()
        self.downloadImgUrls = Queue()
        self.cateNum = 0
        self.cateNumLock = Lock()

    def run(self, cateNum, totalDownload, threadCount=8):
        """
        :param cateNum 分类参数
        :param totalDownload 总下载数
        :rtype void 无返回
        """
        saveImgPath = os.getenv('saveImgPath')
        print(saveImgPath)
        if saveImgPath is not None:
            self.saveImgPath = saveImgPath
        self.cateInfo = self.categoryList[cateNum]
        self.totalCount = self.cateInfo['count']
        self.cateName = self.cateInfo['name']
        self.cateId = self.cateInfo['id']

        self.totalDownloadCount = totalDownload
        savePath = '{}/{}'.format(self.saveImgPath, self.cateName)
        if os.path.exists(savePath) is False:
            os.makedirs(savePath)
        task = []
        # 2个线程获取imageUrls
        for i in range(5):
            task.append(Process(target=self.pushQueueImageUrl))

        for i in range(threadCount):
            task.append(Process(target=self.customImageUrl))
        for i in task:
            i.daemon = True
            i.run()
            # i.join()

        # self.downloadImgUrls.join()

    def getCategoreyUrl(self):
        return self.baseUrl + self.categoryPath

    def getCategory(self):
        resp = requests.get(self.getCategoreyUrl(), headers=self.headers)
        self.categoryList = json.loads(resp.content)['res']['category']
        return self.categoryList;

    def getBaseUrl(self):
        return self.baseUrl;

    def getDeclareCategoryUrl(self, skip):
        totalCount = self.totalCount  # 总图数
        if skip > totalCount:
            return None
        skipInfo = ''
        if skip > 0:
            skipInfo = '?skip={}'.format(skip)
        cateUrl = self.baseUrl + self.categoryPath + '/' + self.cateId + \
                  self.wallpaper + skipInfo
        return cateUrl

    def getImageUrl(self, cateUrl):
        if cateUrl is None:
            return []
        resp = requests.get(cateUrl, headers=self.headers)
        respJson = json.loads(resp.content)
        imageUrls = respJson['res']['wallpaper']
        print("get ImageUrls {}".format(imageUrls))
        return imageUrls

    def pushQueueImageUrl(self):
        while True:
            with self.cateNumLock:
                cateNum = self.cateNum
                self.cateNum = self.cateNum + 20
            if (cateNum >= self.totalDownloadCount):
                self.downloadImgUrls.put(None)
                break
            cateUrls = self.getDeclareCategoryUrl(cateNum)
            imageUrls = self.getImageUrl(cateUrls)
            if (len(imageUrls) == 0):
                self.downloadImgUrls.put(None)
                break
            for i in imageUrls:
                self.downloadImgUrls.put(i)
        print("push over")

    def downloadImage(self, imageUrl):
        if self.downloadCount > self.totalDownloadCount:
            return;
        # t = threading.current_thread()
        t = os.getpid()
        print("Thread id : {},正在处理{}张,图片地址:{}".format(t, self.downloadCount, imageUrl['img']))
        if os.path.exists(self.saveImgPath + '/{}/{}.jpg'.format(self.cateName, imageUrl['id'])):
            print("第{}张 {}.jpg已存在".format(self.downloadCount, imageUrl['id']))
            with self.countLock:
                self.downloadCount += 1;
            return False
        print("Thread id : {},开始下载{}张图片".format(t, self.downloadCount))
        while True:
            try:
                resp = requests.get(imageUrl['img'], headers=self.downLoadImageHeader)
                if resp.status_code == 200:
                    break
            except Exception as e:
                print("下载发生异常,正在进行重试")
                print(e.with_traceback())
        with open(self.saveImgPath + '/' + self.cateName + "/" + imageUrl['id'] + '.jpg', 'wb') as f:
            f.write(resp.content)
        with self.countLock:
            self.downloadCount += 1;
        return True

    def customImageUrl(self):
        while True:
            url = self.downloadImgUrls.get()
            self.downloadImgUrls.task_done()
            if url is None:
                print("over download ")
                self.downloadImgUrls.put(None)
                break;
            self.downloadImage(url)

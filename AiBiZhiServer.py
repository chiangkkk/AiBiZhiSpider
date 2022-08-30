import random

import requests
import json
import os
import time


class AiBiZhiServer:
    baseUrl = 'http://service.aibizhi.adesk.com/v1/wallpaper'
    categoryPath = '/category'
    category = '/4e4d610cdf714d2966000000'
    wallpaper = '/wallpaper'
    skip = 20
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
        pass

    def run(self, cateNum, totalDownload, userSleep=False):
        """
        :param cateNum 分类参数
        :param totalDownload 总下载数
        :param userSleep 是否下载时睡眠
        :rtype: void 无返回
        """
        self.cateInfo = self.categoryList[cateNum]
        self.totalCount = self.cateInfo['count']
        self.cateName = self.cateInfo['name']
        self.cateId = self.cateInfo['id']
        if os.path.exists('./download/{}'.format(self.cateName)) is False:
            os.mkdir('./download/{}'.format(self.cateName))
        now = 0
        count = 0;
        while now * 20 < totalDownload:
            cateUrl = self.getDeclareCategoryUrl(now * 20)
            imageUrls = self.getImageUrl(cateUrl)
            if len(imageUrls) == 0:
                print("未加载到图片资源,程序结束")
                exit(1)
            needSleep = False
            for imageUrl in imageUrls:
                count += 1
                needSleep = self.downloadImage(imageUrl, count)
            if needSleep and userSleep:
                sleepTime = random.randint(5, 10)
                print("休息{}s".format(sleepTime))
                time.sleep(sleepTime)

            now += 1

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
            print('已近到达下载上线或已超过图库上线')
            exit(0)
        skipInfo = ''
        if skip > 0:
            skipInfo = '?skip={}'.format(skip)
        cateUrl = self.baseUrl + self.categoryPath + '/' + self.cateId + \
                  self.wallpaper + skipInfo
        return cateUrl

    def getImageUrl(self, cateUrl):
        resp = requests.get(cateUrl, headers=self.headers)
        respJson = json.loads(resp.content)
        imageUrls = respJson['res']['wallpaper']
        print("get ImageUrls {}".format(imageUrls))
        return imageUrls

    def downloadImage(self, imageUrl, count):
        print("正在处理{}张,图片地址:{}".format(count, imageUrl['img']))
        if os.path.exists('download/{}/{}.jpg'.format(self.cateName, imageUrl['id'])):
            print("第{}张-{}.jpg已存在".format(count, imageUrl['id']))
            return False
        print("开始下载{}张图片".format(count))
        resp = None
        while True:
            try:
                resp = requests.get(imageUrl['img'], headers=self.downLoadImageHeader)
                if resp.status_code == 200:
                    break
            except Exception as e:
                print(e.with_traceback())
        with open('download/' + self.cateName + "/" + imageUrl['id'] + '.jpg', 'wb') as f:
            f.write(resp.content)
        return True

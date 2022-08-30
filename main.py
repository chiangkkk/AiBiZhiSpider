from AiBiZhiServer import AiBiZhiServer as server


def getUserDigitInptup(inputStr, min, max):
    userInput = -1
    strIsDigit = False
    while (strIsDigit is False) or (min <= userInput <= max is False):
        userInput = input(inputStr)
        strIsDigit = userInput.isdigit()
        if strIsDigit:
            userInput = int(userInput)
    return userInput;


if __name__ == '__main__':
    server = server()
    categoryList = server.getCategory()
    print("现在共用分类{}种，以下为具体分类信息".format(len(categoryList)))
    cateNum = 0
    for category in categoryList:
        print("{}. {} 数量:{}".format(cateNum + 1, category['rname'], category['count']))
        cateNum += 1

    userCate = getUserDigitInptup('请输入需要下载分类的序号:', 1, 18)
    userCate -= 1

    userNum = getUserDigitInptup("请输入你要下载的数量(0-99999)", 0, 99999)
    server.run(userCate, userNum)
    print("程序运行完成")

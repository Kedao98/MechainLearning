from math import log
from collections import Counter
import numpy as np
import operator
import matplotlib.pyplot as plt
import pickle

def createDataSet():
    dataSet = [[0, 0, 0, 0, 'no'],  # 数据集
               [0, 0, 0, 1, 'no'],
               [0, 1, 0, 1, 'yes'],
               [0, 1, 1, 0, 'yes'],
               [0, 0, 0, 0, 'no'],
               [1, 0, 0, 0, 'no'],
               [1, 0, 0, 1, 'no'],
               [1, 1, 1, 1, 'yes'],
               [1, 0, 1, 2, 'yes'],
               [1, 0, 1, 2, 'yes'],
               [2, 0, 1, 2, 'yes'],
               [2, 0, 1, 1, 'yes'],
               [2, 1, 0, 1, 'yes'],
               [2, 1, 0, 2, 'yes'],
               [2, 0, 0, 0, 'no']]
    featureNames = ['age', 'working', 'ownHouse', 'Credition']  # 分类属性
    return dataSet, featureNames

def createPlot(inTree):
    def getNumLeafs(myTree):
        numLeafs = 0  # 初始化叶子
        firstStr = next(iter(
            myTree))  # python3中myTree.keys()返回的是dict_keys,不在是list,所以不能使用myTree.keys()[0]的方法获取结点属性，可以使用list(myTree.keys())[0]
        secondDict = myTree[firstStr]  # 获取下一组字典
        for key in secondDict.keys():
            if type(secondDict[key]).__name__ == 'dict':  # 测试该结点是否为字典，如果不是字典，代表此结点为叶子结点
                numLeafs += getNumLeafs(secondDict[key])
            else:
                numLeafs += 1
        return numLeafs

    def getTreeDepth(myTree):
        maxDepth = 0  # 初始化决策树深度
        firstStr = next(iter(
            myTree))  # python3中myTree.keys()返回的是dict_keys,不在是list,所以不能使用myTree.keys()[0]的方法获取结点属性，可以使用list(myTree.keys())[0]
        secondDict = myTree[firstStr]  # 获取下一个字典
        for key in secondDict.keys():
            if type(secondDict[key]).__name__ == 'dict':  # 测试该结点是否为字典，如果不是字典，代表此结点为叶子结点
                thisDepth = 1 + getTreeDepth(secondDict[key])
            else:
                thisDepth = 1
            if thisDepth > maxDepth: maxDepth = thisDepth  # 更新层数
        return maxDepth

    def plotNode(nodeTxt, centerPt, parentPt, nodeType):
        arrow_args = dict(arrowstyle="<-")  # 定义箭头格式
        createPlot.ax1.annotate(nodeTxt, xy=parentPt, xycoords='axes fraction',  # 绘制结点
                                xytext=centerPt, textcoords='axes fraction',
                                va="center", ha="center", bbox=nodeType, arrowprops=arrow_args)

    def plotMidText(cntrPt, parentPt, txtString):
        xMid = (parentPt[0] - cntrPt[0]) / 2.0 + cntrPt[0]  # 计算标注位置
        yMid = (parentPt[1] - cntrPt[1]) / 2.0 + cntrPt[1]
        createPlot.ax1.text(xMid, yMid, txtString, va="center", ha="center", rotation=30)

    def plotTree(myTree, parentPt, nodeTxt):
        decisionNode = dict(boxstyle="sawtooth", fc="0.8")  # 设置结点格式
        leafNode = dict(boxstyle="round4", fc="0.8")  # 设置叶结点格式
        numLeafs = getNumLeafs(myTree)  # 获取决策树叶结点数目，决定了树的宽度
        depth = getTreeDepth(myTree)  # 获取决策树层数
        firstStr = next(iter(myTree))  # 下个字典
        cntrPt = (plotTree.xOff + (1.0 + float(numLeafs)) / 2.0 / plotTree.totalW, plotTree.yOff)  # 中心位置
        plotMidText(cntrPt, parentPt, nodeTxt)  # 标注有向边属性值
        plotNode(firstStr, cntrPt, parentPt, decisionNode)  # 绘制结点
        secondDict = myTree[firstStr]  # 下一个字典，也就是继续绘制子结点
        plotTree.yOff = plotTree.yOff - 1.0 / plotTree.totalD  # y偏移
        for key in secondDict.keys():
            if type(secondDict[key]).__name__ == 'dict':  # 测试该结点是否为字典，如果不是字典，代表此结点为叶子结点
                plotTree(secondDict[key], cntrPt, str(key))  # 不是叶结点，递归调用继续绘制
            else:  # 如果是叶结点，绘制叶结点，并标注有向边属性值
                plotTree.xOff = plotTree.xOff + 1.0 / plotTree.totalW
                plotNode(secondDict[key], (plotTree.xOff, plotTree.yOff), cntrPt, leafNode)
                plotMidText((plotTree.xOff, plotTree.yOff), cntrPt, str(key))
        plotTree.yOff = plotTree.yOff + 1.0 / plotTree.totalD

    fig = plt.figure(1, facecolor='white')  # 创建fig
    fig.clf()  # 清空fig
    axprops = dict(xticks=[], yticks=[])
    createPlot.ax1 = plt.subplot(111, frameon=False, **axprops)  # 去掉x、y轴
    plotTree.totalW = float(getNumLeafs(inTree))  # 获取决策树叶结点数目
    plotTree.totalD = float(getTreeDepth(inTree))  # 获取决策树层数
    plotTree.xOff = -0.5 / plotTree.totalW;
    plotTree.yOff = 1.0;  # x偏移
    plotTree(inTree, (0.5, 1.0), '')  # 绘制决策树
    plt.show()  # 显示绘制结果

def ID3(dataSet,featureNames,testDataOrder,epslion=0.0):
    def chooseBestFeature(dataSet):
        def calcShannonEntropy(dataSet):
            dataSize = len(dataSet)
            labelCount = dict()
            for data in dataSet:
                if data[-1] not in labelCount.keys():  # label is the last col
                    labelCount[data[-1]] = 0
                labelCount[data[-1]] += 1

            ShannonEntropy = 0.0
            for k in labelCount.keys():
                p = labelCount[k] / dataSize
                ShannonEntropy += -p * log(p, 2)

            return ShannonEntropy

        def calcConditionalEntropy(dataSet, featureIndexs):

            classCount = Counter(np.array(dataSet[:])[:, featureIndexs])
            dataSize = len(dataSet)
            conditionalEntropy = 0.0
            for feature in classCount.keys():
                newDataSet = dataSetSplit(dataSet, targetFeatureIndex=featureIndexs, targetFeatureValue=feature)
                conditionalEntropy += (classCount[feature] / dataSize) * calcShannonEntropy(newDataSet)
            return conditionalEntropy

        InfoGainList = list()
        for i in range(len(dataSet[0]) - 1):
            InfoGain = calcShannonEntropy(dataSet) - calcConditionalEntropy(dataSet, i)
            InfoGainList.append(InfoGain)

        return InfoGainList.index(max(InfoGainList)), max(InfoGainList)

    def dataSetSplit(dataSet, targetFeatureIndex, targetFeatureValue):
        splitedData = list()
        for row in dataSet:
            if row[targetFeatureIndex] == int(targetFeatureValue):
                temp = row[:targetFeatureIndex]
                temp.extend(row[targetFeatureIndex + 1:])
                splitedData.append(temp)
        return splitedData
    #STEP 1
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList):#if all cases have the same label return it
        return classList[0]
    # STEP 2
    if len(dataSet[0]) <= 1 or len(featureNames) < 1: #if the dataset is empty return the label of most repetitions
        classCount = Counter(classList)
        return sorted(classCount.items(),key=operator.itemgetter(1),reverse=True)[0][0]
        #dict.items() return tuples of (key,value)
        #operator.itemgetter(i) a function to get ith element
        #operator.itemgetter(i,j) a function to get tuple of ith and jth elements : (a[i],a[j])
        #reverse = True descend ordered
    # STEP 3
    bestFeatureIndex, InfoGain = chooseBestFeature(dataSet)
    bestFeature = featureNames[bestFeatureIndex]
    testDataOrder.append(bestFeature)
    # STEP 4
    if InfoGain < epslion:
        classCount = Counter(classList)
        return sorted(classCount.items(), key=operator.itemgetter(1), reverse=True)[0][0]
    # STEP 5 & STEP 6
    decisionTree = {bestFeature:{}}
    del(featureNames[bestFeatureIndex])
    featureValues = set([data[bestFeatureIndex] for data in dataSet])

    for value in featureValues:
        subDataSet = dataSetSplit(dataSet,bestFeatureIndex,value)
        decisionTree[bestFeature][value] = ID3(subDataSet,featureNames[:],testDataOrder)

    return decisionTree

def classify(inputTree, featLabels, testVec):
    firstStr = next(iter(inputTree))                                                        #获取决策树结点
    secondDict = inputTree[firstStr]                                                        #下一个字典
    featIndex = featLabels.index(firstStr)
    for key in secondDict.keys():
        if testVec[featIndex] == key:
            if type(secondDict[key]).__name__ == 'dict':
                classLabel = classify(secondDict[key], featLabels, testVec)
            else: classLabel = secondDict[key]
    return classLabel

def storeTree(myTree,dirt):
    with open(dirt,'wb') as fw:
        pickle.dump(myTree,fw)
def loadTree(dirt):
    fr = open(dirt,'rb')
    return pickle.load(fr)


# dataSet,featureNames = createDataSet()
# testDataOrder = list()
# myTree = ID3(dataSet,featureNames,testDataOrder)
# storeTree(myTree,r'classifierStorage.txt')

myTree = loadTree(r'classifierStorage.txt')
print(myTree)

# testData = [0,1]
# res = classify(myTree,testDataOrder,testData)
# print(res)
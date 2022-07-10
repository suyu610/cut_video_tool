import time
from ffmpy3 import FFmpeg
import os
import re

def cutMovie(originMoviePath,outputMoviePath,startTime,endTime):
	ff = FFmpeg(
	    inputs={f'{originMoviePath}': None},
	    outputs={outputMoviePath: f'-c copy -ss {startTime} -to {endTime} -y'}
	    )
	ff.run()
def startProcessVideoByFileNameAndTimeList(filePath,timeList):
	# print(filePath)
	n = filePath.rfind("\\")#找到"\\"出现的位置

	if(n==-1):
		n = filePath.rfind("/")#找到"\\"出现的位置
	fileName = filePath[n+1:] #输出为 class1.py
	
	path = filePath[:n]	
	suffixIndex = fileName.rfind('.')
	suffix = fileName[suffixIndex:]
	fileName = fileName[:suffixIndex]
	length = int(len(timeList)/2)

	for i in range(0,length):
		start = timeList[i*2]
		end = timeList[i*2+1]
		output = path+"/"+fileName+"__"+str(i) + suffix
		print("filePath",filePath)
		print("output",output)
		print("start",start)
		print("end",end)
		cutMovie(filePath,output,start['time'],end['time'])

def apply_ascyn(func, args, callback):
    """ 
    func 函数的是处理的函数
    args 表示的参数
    callback 表示的函数处理完成后的 该执行的动作
    """
    result = func(*args)
    callback(result)


def startProcessVideo(videoDict,outputMoviePath):
	# {'filePath': 'E:/porn/新建文件夹/极品711【1.21~1.23,2.33~3.32】.MP4', 
	# 'fileName': '极品711【1.21~1.23,2.33~3.32】.MP4', 
	# 'partCount': 2, 
	# 'timePartInfoArr': [('1:21', '1:23'), ('2:33', '3:32')]}
	for key in videoDict:
		filePath = videoDict[key]['filePath']
		for index,part in enumerate(videoDict[key]['timePartInfoArr']):
			# cutMovie()
			fileName = videoDict[key]['fileName']
			suffixIndex = fileName.rfind('.')
			suffix = fileName[suffixIndex:]
			p2 = re.compile(r'[【](.*)[】]', re.S)  
			partInfo = re.findall(p2, fileName)
			if(len(partInfo)!=0):
				fileName = fileName.replace("【"+partInfo[0]+"】","").replace(suffix,'')

			output = outputMoviePath+"/"+fileName+"__"+str(index) + suffix
			cutMovie(filePath,output,part[0],part[1])

# 字节bytes转化kb\m\g
def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"
 
    if kb >= 1024:
        M = kb / 1024
        return "%.2fM" % (M)
    else:
        return "%.2fkb" % (kb)
 
# 获取文件大小
def getDocSize(path):
    try:
        size = os.path.getsize(path)
        return formatSize(size)
    except Exception as err:
        print(err)

def parseFileName(filePath,fileName):
	resultDict = {"filePath":filePath,"fileName":fileName,"partCount":0,"timePartInfoArr":[]}
	#贪婪匹配【xxxxx】
	p2 = re.compile(r'[【](.*)[】]', re.S)  
	partInfo = re.findall(p2, fileName)
	if(len(partInfo)!=0):
		partList = partInfo[0].split(",")
		resultDict['partCount'] = len(partList)
		# 用~分割
		for part in partList:
			times = part.split("~")
			resultDict['timePartInfoArr'].append((times[0].replace('.',':'),times[1].replace('.',':')))
	return resultDict
		
def isVideoFile(fileName):
	fileName = fileName.lower()
	validSuffixArr = ["wmv","asf","asx","rm"," rmvb","mpg","mpeg","mpe","3gp","mov","mp4","m4v","avi","dat","mkv","flv","vob"]
	index = fileName.rfind('.')
	suffix = fileName[index + 1:]
	return suffix in validSuffixArr
		 

def main():
	videoDict = {'b30c82a4-0677-426d-9dd3-6b2def4c94f2': {'filePath': 'E:/porn/新建文件夹/极品711【1.21~1.23,2.33~3.32】.MP4', 'fileName': '极品711【1.21~1.23,2.33~3.32】.MP4', 'partCount': 2, 'timePartInfoArr': [('1:21', '1:23'), ('2:33', '3:32')]}}
	startProcessVideo(videoDict,"E:/porn/新建文件夹/")
	# parseFileName("你好呀【1.00~1.21,1.12~1.22】.mp4")

if __name__ == '__main__':
	main()
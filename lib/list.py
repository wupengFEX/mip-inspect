# -*- coding: UTF-8 -*-

import re
import os
import sys, getopt
import ssl
import json
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
import xlwt

global params
params = []
global tasks
tasks = []
global result
global session
global futures
futures = []

result = json.loads('{ \
    "total": 0, \
    "success": 0, \
    "fail": 0 \
}')

def openUrlFile (urls):
	global params
	filePth = './urls.txt'
	if len(urls):
		params = urls.split(',')
	elif os.path.exists(filePth):
		content = open(filePth)
		lines = content.readlines()
		for i, line in enumerate(lines):
			params.append(''.join(line).strip('\n'))

def handleRequest(url, extensions, res):
	extList = [];
	if len(extensions) != 0:
		extList = extensions.split(',')
	pattern = re.compile("<(mip-[^>\s]+)[^>]*>")
	data = res.content.decode()
	exts = pattern.findall(data)
	mapList = {
		'url': url,
		'exts': {}
	}
	if len(extList) == 0:
		for key in exts:
			if mapList['exts'].get(key):
				mapList['exts'][key] += 1
			else:
				mapList['exts'][key] = 1
	else:
		for i, inputkey in enumerate(extList):
			for j, mapkey in enumerate(exts):
				if extList[i] == exts[j]:
					if mapList['exts'].get(inputkey):
						mapList['exts'][inputkey] += 1
					else:
						mapList['exts'][inputkey] = 1

	if len(mapList['exts']) > 0:
		print(mapList)

	# workbook = xlwt.Workbook()
	# sheet = workbook.add_sheet("MIP INSPECT")
	# sheet.write(0, 0, 'foobar')
	# workbook.save("mipInspect.xls")

def handleConfig ():
	ssl._create_default_https_context = ssl._create_unverified_context

def handleSession (extensions):
	global tasks
	global result
	global session
	global futures
	result['total'] = len(params);

	session = FuturesSession(max_workers=10)
	for url in params:
		send(url, extensions)
	for future in futures:
		try:
			future.result(timeout=3)
		except:
			result['fail'] += 1
			print('Url ' + url + ' Handle failed!')

def send (url, extensions):
	global tasks
	global result
	global session
	future = session.get(url, background_callback=lambda sess, resp: callback(sess, resp, url, extensions), timeout=3)
	futures.append(future)

def callback (sess, resp, url, extensions):
	global result
	if (resp.status_code == 200):
		result['success'] += 1
		handleRequest(url, extensions, resp)
	else:
		result['fail'] += 1
		print('Url ' + url + ' Handle failed!')

def getList (urls, extensions):
	handleConfig()
	openUrlFile(urls)
	handleSession(extensions)

def handleOpt ():
	urls = ''
	extensions = ''
	argv = sys.argv[1:]
	try:
		opts, args = getopt.getopt(argv,"hu:e:",["urls=","extensions="])
	except getopt.GetoptError:
		print('python list.py -u <urls> -e <extensions>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('list.py -u <urls> -e <extensions>')
			sys.exit()
		elif opt in ("-u", "--urls"):
			urls = arg
		elif opt in ("-e", "--extensions"):
			extensions = arg
	print('输入的文件为：', urls)
	print('输出的文件为：', extensions)
	getList(urls, extensions)

handleOpt()
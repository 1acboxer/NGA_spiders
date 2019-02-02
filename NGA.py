# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import requests
import time
import random
import re
from multiprocessing.dummy import Pool
import csv
import json
import sys


class Spider(object):
	def __init__(self):
		self.ss = set()
		# self.date = '2000-10-01'

	def get_headers(self):
		user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
		               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
		               'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
		               'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
		               'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
		               'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
		               'Opera/9.52 (Windows NT 5.0; U; en)',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
		               'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
		               'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
		user_agent = random.choice(user_agents)
		headers = {'host': "bbs.nga.cn",
		           'connection': "keep-alive",
		           'cache-control': "no-cache",
		           'upgrade-insecure-requests': "1",
		           'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
		           'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		           'referer': "http://bbs.ngacn.cc/misc/adpage_insert_2.html?http://bbs.ngacn.cc/read.php?tid=13427591&page=2",
		           'accept-encoding': "gzip, deflate",
		           'accept-language': "zh-CN,zh;q=0.9",
		           'cookie': 'UM_distinctid=165d243d684e9-0111554226bb1c-3c604504-13edd4-165d243d68516f; taihe=aebe409faefff51e20f2dde377f1cea6; ngacn0comUserInfo=%25B0%25EB%25CF%25C4%25A8q%25A5%25A1%258EU%259B%25F6%09%25E5%258D%258A%25E5%25A4%258F%25E2%2595%25AD%25E3%2582%25A1%25E5%25B6%25B6%25E6%25B6%25BC%0939%0939%09%0910%090%090%090%090%09; ngaPassportUid=43320220; ngaPassportUrlencodedUname=%25B0%25EB%25CF%25C4%25A8q%25A5%25A1%258EU%259B%25F6; ngaPassportCid=Z8ltrcjgo616kor6sbbpgr0thdnbrsr96ge8kte5; ngacn0comUserInfoCheck=10d5d900ae3f241cd4bc9d2e144794f3; ngacn0comInfoCheckTime=1537976770; taihe_session=6444150154287a3254e70831f46a8868; CNZZDATA30043604=cnzz_eid%3D364786080-1536830942-%26ntime%3D1537976642; CNZZDATA30039253=cnzz_eid%3D943882560-1536826159-%26ntime%3D1537971608; Hm_lvt_5adc78329e14807f050ce131992ae69b=1536830988,1536839697,1537976774; lastvisit=1537976828; lastpath=/read.php?tid=12689996&page=2; bbsmisccookies=%7B%22insad_refreshid%22%3A%7B0%3A%22/153794231025962%22%2C1%3A1538581572%7D%2C%22pv_count_for_insad%22%3A%7B0%3A-46%2C1%3A1537981224%7D%2C%22insad_views%22%3A%7B0%3A1%2C1%3A1537981224%7D%7D; Hm_lpvt_5adc78329e14807f050ce131992ae69b=1537976834'
		           }
		return headers

	def p_time(self, stmp):  # 将时间戳转化为时间
		stmp = float(str(stmp)[:10])
		timeArray = time.localtime(stmp)
		otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
		return otherStyleTime

	def replace(self, x):
		x = re.sub(re.compile('<.*?>', re.S), '', x)
		x = re.sub(re.compile('\n'), ' ', x)
		x = re.sub(re.compile('\r'), ' ', x)
		x = re.sub(re.compile('\r\n'), ' ', x)
		x = re.sub(re.compile('[\r\n]'), ' ', x)
		x = re.sub(re.compile('\s{2,}'), ' ', x)
		return x.strip()

	def GetProxies(self):
		# 代理服务器
		proxyHost = "http-dyn.abuyun.com"
		proxyPort = "9020"
		# 代理隧道验证信息
		proxyUser = "HI18001I69T86X6D"
		proxyPass = "D74721661025B57D"
		proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
			"host": proxyHost,
			"port": proxyPort,
			"user": proxyUser,
			"pass": proxyPass,
		}
		proxies = {
			"http": proxyMeta,
			"https": proxyMeta,
		}
		return proxies
	
	def get_detail_page(self, game_id, game_url, product_number, plat_number, page):  # 获取游戏某一页的所有评论
		url = 'http://bbs.nga.cn/read.php?tid=%s&page=%d' % (game_id, page)
		retry = 5
		while 1:
			try:
				results = []
				text = requests.get(url, headers=self.get_headers(), proxies=self.GetProxies(), timeout=10).content.decode('gbk', 'ignore')
				p0 = re.compile(
					"<a href='nuke\.php\?func=ucp&uid=(\d+?)'.*?title='reply time'>(.*?)</span>.*?<span id='postcontent\d+?' class='postcontent ubbcode'>(.*?)</span>",
					re.S)
				items = re.findall(p0, text)
				last_modify_date = self.p_time(time.time())
				for item in items:
					nick_name = item[0]
					cmt_date = item[1].split()[0]
					# if cmt_date < self.date:
					# 	continue
					cmt_time = item[1] + ':00'
					comments = self.replace(item[2])
					like_cnt = '0'
					cmt_reply_cnt = '0'
					long_comment = '0'
					src_url = game_url
					tmp = [product_number, plat_number, nick_name, cmt_date, cmt_time, comments, like_cnt,
					       cmt_reply_cnt, long_comment, last_modify_date, src_url]
					print '|'.join(tmp)
					ee = [nick_name, cmt_date, cmt_time, comments]
					if '|'.join(ee) in self.ss:
						return None
					else:
						self.ss.add('|'.join(ee))
						results.append([x.encode('gbk', 'ignore') for x in tmp])
				return results
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return None
				else:
					continue
	
	def get_all(self, game_url, product_number, plat_number):  # 获取所有评论
		p0 = re.compile('tid=(\d+)')
		game_id = re.findall(p0, game_url)[0]
		page = 1
		while 1:
			print 'page:',page
			t = self.get_detail_page(game_id, game_url, product_number, plat_number, page)
			if t is None:
				return None
			else:
				with open('data_comments_5.csv', 'a') as f:
					writer = csv.writer(f, lineterminator='\n')
					writer.writerows(t)
				page += 1


if __name__ == "__main__":
	spider = Spider()
	# print '==============='
	s1 = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s1.append([i[2], i[0], 'P23'])
	for j in s1:
		print j[1],j[0]
		if j[1] in ['F0000262']:
			spider.get_all(j[0], j[1], j[2])

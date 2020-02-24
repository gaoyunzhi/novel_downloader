#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import cached_url
import yaml
import datetime

def getContent(url):
	content = cached_url.get(url)
	content = yaml.load(content, Loader=yaml.FullLoader)
	b = BeautifulSoup(content['content'], 'html.parser')
	b.get_text(separator="\n")
	next_url = None
	for x in b.find_all('a'):
		if x['href'] and x['href'].startswith('https://www.evernote.com/l'):
			next_url = x['href']
			break
	return b.get_text(separator="\n"), content['title'], next_url

def getTime():
	now = datetime.datetime.now()
	return '%d/%d %d:%d' % (now.month, now.day, now.hour, now.minute)

def countWord(x):
	return len([c for c in x if c.isalpha()])

def download(url, filename = None):
	global word_count
	content = []
	while url:
		text, title, url = getContent(url + '?json=1')
		if not filename:
			filename = title
		content.append(text)
		with open(filename, 'w') as f:
			f.write('\n\n=======\n\n'.join(content))
	word_count += sum([countWord(x) for x in content])

word_count = 0
download('https://www.evernote.com/l/AO9AYm5PtJtHIZb5W7RvOFPjNGxENZ9uQiI', '面向对象编程')
download('https://www.evernote.com/l/AO9Nsp2x2-5LBJCMbJvjQNK6zjezsttrIPw', '乐山景然ABO')
download('https://www.evernote.com/l/AO8Z7ocFEpJJjatcpUFs4oyx1F7g9knqfPA', '学术生涯篇')
download('https://www.evernote.com/l/AO9X4c31vqVPE5Vs0fHDaQ3INH9qfsne36s', '穿越阵容有点大')
with open('word_count.txt', 'a') as f:
	f.write('%s\t\t%d\n' % (getTime(), word_count))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from opencc import OpenCC
from note import Note, clearText
import random
cc = OpenCC('s2tw')

import time
total_translation_time = 0

times_count = [0] * 8

def mkdirs(*args):
	for arg in args:
		os.system('mkdir %s > /dev/null 2>&1' % arg)

def getRaw(notes):
	return ''.join(['\n\n\n==== %s  ===\n\n\n' % note.title + 
		note.raw_text for note in notes])

def getContent(notes):
	outline_count = sum(['大纲' in note.title for note in notes])
	if outline_count < len(notes) / 2:
		notes = [note for note in notes if '【大纲】' not in note.title]
	text = ''.join(['\n\n\n==== %s  ===\n\n\n' % note.title + 
		note.text for note in notes])
	return clearText(text)



def processNote(url, title, dirname):
	root_note = Note(url, times_count)

	if root_note.isNewFormat():
		# 看看 evernote_urls 能不能 compute on the fly, 需不需要
		# 我担心 translate 是最花时间的
		notes = [ Note(sub_url, times_count) for sub_url in root_note.evernote_urls]
	else:
		sub_url = root_note.next_url
		notes = [root_note]
		while sub_url:
			note = Note(sub_url, times_count)
			notes.append(note)
			sub_url = note.next_url

	mkdirs(dirname, 'txt', 'traditional', 'raw')
	content = getContent(notes)
	with open('%s/%s.md' % (dirname, title), 'w') as f:
		f.write(content)
	with open('txt/%s.txt' % title, 'w') as f:
		f.write(content)
	global total_translation_time
	start = time.time()
	if random.random() < 0.05:
		with open('traditional/%s.md' % cc.convert(title), 'w') as f:
			f.write(cc.convert(content))
	total_translation_time += time.time() - start
	with open('raw/%s.md' % title, 'w') as f:
		f.write(getRaw(notes))
	if dirname in ['critics', 'original']:
		word_count = [note.word_count for note in notes]
		with open('other/word_count_detail.txt', 'a') as f:
			f.write('%s %d %s\n' % (title, sum(word_count), str(word_count)))

def commit():
	command = 'git add . && git commit -m auto_commit && git push -u -f'
	os.system(command)

def getDirName(series):
	series_map = {
		'笔记': 'critics', 
		'旧稿': 'other', 
		'其他': 'other', 
		'大纲': 'other'}
	for key in series_map:
		if key in series:
			return series_map[key]
	return 'original'

def process(root_url):
	start1 = time.time()
	mkdirs('other')
	os.system('rm other/word_count_detail.txt')

	note = Note(root_url, times_count)
	series = None
	for item in note.soup.find_all('div'):
		link = item.find('a')
		if link:
			processNote(link['href'], link.text, getDirName(series))
		else:
			series = item.text.strip() or series

	start = time.time()
	commit()
	print(time.time() - start, 'commit time')
	print('translation_time', total_translation_time)
	print('total_time', time.time() - start1)
	print(times_count)

if __name__ == '__main__':
	process('https://www.evernote.com/l/AO8X_19lBzpIFJ2QRKX0hE_Hzrc-qBlE4Yw')
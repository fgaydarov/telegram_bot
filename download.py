# coding: utf8
"""
File content Functions for working with Pytube module and DB Sqlite3


"""

from pytube import YouTube
import math
import re
import sqlite3


def checkDb(dbname):
	conn = sqlite3.connect(dbname)
	conn.execute('CREATE TABLE IF NOT EXISTS "telegram_files" ("id"	INTEGER NOT NULL,"name"	REAL,"telegram_id"	TEXT,"url"	TEXT,"type"	TEXT,PRIMARY KEY("id" AUTOINCREMENT))')
	conn.close()

def download_video(url,downloadPath):
    VideoList = dict()
    video = YouTube(url)
    video = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    VideoList["video_saved_path"] = video.download(downloadPath)
    VideoList["video_title"] = video.title
    return VideoList


def progressBarForBot(current, total, sProgressbarEmpty, sProgressbarEmptyList):

	procentmy = round (current * 100 / total)
	numberIndex = math.floor (procentmy/10)
	#print(numberIndex, end=' = numberIndex\n')
	if numberIndex>0:
		numberIndex = numberIndex-1
		sProgressbarEmptyList[numberIndex] = "#"
		sProgressbarEmpty = " ".join(sProgressbarEmptyList)
	st = sProgressbarEmpty + " " + f"{current * 100 / total:.1f}%"
	return st


def check_url(url,dbname,type):
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()
	data = cur.execute( "select telegram_id from telegram_files where url=? and type=?",[url,type] )
	for row in data:
		return row[0]

	conn.close()
	return 0

def save_url(url,dbname,type,telegram_id,video_title):
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()
	sql = 'INSERT INTO telegram_files (name, telegram_id, url, type) values(?, ?, ?, ?)'
	data = [video_title, telegram_id, url, type]
	cur.execute(sql, data)
	id = cur.lastrowid
	conn.commit()
	conn.close()
	return id

def getnewheight (width_old, height_old, width_new):
	height_new = 0
	height_new = int( (float(height_old) * float(width_new)) / width_old)
	return height_new
"""
This Python Script contains all logic necessary to start Telegram Bot.
Youtube: is a TelegramBot for downloading Video from YouTube. You can also convert Video to Audio
Copyright (c) 2023-2033 Farid Gaydarov

Author: Farid Gaydarov gaydarov@web.de
		20.03.2023

"""

import config
from pyrogram.handlers import MessageHandler
from pyrogram import Client,  filters
import logging
import download
import os
import validation
import moviepy.editor as mp
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton, ReplyKeyboardRemove)
from pyrogram  import enums
import math
import sqlite3


logging.basicConfig(level=logging.INFO)

bot = Client(
    "ses1",
    api_id = config.apiIdTelegramUser,
    api_hash = config.apiHashTelegramUser,
    workers = 5,
    bot_token=config.tokenBotTelegram
)
"""Pyrogram Client, the main means for interacting with Telegram.
    Please add your Api Id Hash and Token in config.py
"""


download.checkDb(config.dbname)
MainList = dict()
p = os.getcwd()

@bot.on_message(filters.command("start", ["!", "/"]))
def connect(chat, m):
	try:
		userID = m.chat.id
		TestMessage = bot.send_message(userID, "Hello. I will upload a video from YouTube for you. Please enter YouTube Link.")

	except Exception as e:
		print(e)


@bot.on_message()
async  def get(chat, m):

	url=m.text
	userID = m.chat.id
	MainList['chat.id'] = m.chat.id
	MainList['url'] = m.text

	try:
		url = validation.valid_link(url)
		Keyboard_ = await bot.send_message(m.chat.id,
		    "Select Video or Audio",
		    reply_markup=InlineKeyboardMarkup(
		        [
		            [
		                InlineKeyboardButton(
		                    "Video",
		                    callback_data="video"
		                ),
		                InlineKeyboardButton(
		                    "Audio",
		                    callback_data="audio"
		                )
		            ]

		        ]

		    )
		)
		MainList['Keyboard_'] = Keyboard_



	except Exception as e:
		await bot.send_message(m.chat.id, f'Something went wrong! Error `{e}`')

@bot.on_callback_query()
async def answer(bot, callback_query):
    if callback_query.data:
        VideoList = dict()
        await bot.delete_messages(MainList['chat.id'],MainList['Keyboard_'].id)
        sProgressbarEmpty = "[][][][][][][][][][]"
        sProgressbarEmptyList = ["[]","[]","[]","[]","[]","[]","[]","[]","[]","[]"]


    if callback_query.data=="video":
        print ("we save video")
        await bot.delete_messages(MainList['chat.id'],MainList['Keyboard_'].id)
        file_id = download.check_url(MainList['url'],config.dbname,'video')
        if file_id:
           #print ("found file id " + str(file_id) )
           await bot.send_video(MainList['chat.id'], file_id)
        else:
           Message = await bot.send_message(MainList['chat.id'], 'We start Video Downloading...')
           VideoList = download.download_video(MainList['url'],config.downloadPath)
           path, file = os.path.split(VideoList['video_saved_path'])
           filename,extension =  os.path.splitext(file)
           mp_video = mp.VideoFileClip(VideoList['video_saved_path'])
           clip = mp_video.subclip(0, 5)
           dimenssion = clip.size
           clipwidth = dimenssion[0]
           clipheight = dimenssion[1]

           await bot.edit_message_text(MainList['chat.id'],Message.id,'Video was saved! We start transfer to Telegram Server')
           Message2 = await bot.send_message(MainList['chat.id'], sProgressbarEmpty +' 0.1%')

           async def progress(current, total):
                progressBarMy = download.progressBarForBot(current, total, sProgressbarEmpty,sProgressbarEmptyList)
                await bot.edit_message_text(MainList['chat.id'],Message2.id,progressBarMy)
           #aMess = await bot.send_video(MainList['chat.id'], VideoList["video_saved_path"], progress=progress)
           aMess = await bot.send_video(MainList['chat.id'], VideoList["video_saved_path"], caption=VideoList["video_title"], width=clipwidth, height=clipheight,  progress=progress)
           file_id = aMess.video.file_id
           download.save_url(MainList['url'],config.dbname,'video',file_id,VideoList["video_title"])
           mp_video.close()
           if not config.saveYouTubeFilesOnServer: os.remove(VideoList['video_saved_path'])
           await bot.delete_messages(MainList['chat.id'],Message.id)
           await bot.delete_messages(MainList['chat.id'],Message2.id)

    if callback_query.data=="audio":
        print ("we save audio")
        await bot.delete_messages(MainList['chat.id'],MainList['Keyboard_'].id)
        file_id = download.check_url(MainList['url'],config.dbname,'audio')
        if file_id:
           #print ("found file id " + str(file_id) )
           await bot.send_audio(MainList['chat.id'], file_id)
        else:

           Message = await bot.send_message(MainList['chat.id'], 'We start downloading Audio...')
           VideoList = download.download_video(MainList['url'],config.downloadPath)

           path, file = os.path.split(VideoList['video_saved_path'])
           filename,extension =  os.path.splitext(file)
           audio_saved_path = config.downloadPath + '/'+ filename +'.mp3'
           mp_video = mp.VideoFileClip(VideoList['video_saved_path'])
           audio_saved_path = path + '/'+ filename +'.mp3'
           mp_video.audio.write_audiofile(audio_saved_path)

           Message2 = await bot.send_message(MainList['chat.id'], sProgressbarEmpty +' 0.1%')
           async def progress(current, total):
                 progressBarMy = download.progressBarForBot(current, total, sProgressbarEmpty,sProgressbarEmptyList)
                 await bot.edit_message_text(MainList['chat.id'],Message2.id,progressBarMy)
           aMess = await bot.send_audio(MainList['chat.id'], audio_saved_path, caption=VideoList["video_title"], progress=progress)
           file_id = aMess.audio.file_id
           download.save_url(MainList['url'],config.dbname,'audio',file_id,VideoList["video_title"])
           mp_video.close()
           if not config.saveYouTubeFilesOnServer:
               os.remove(VideoList['video_saved_path'])
               os.remove(audio_saved_path)

           await bot.delete_messages(MainList['chat.id'],Message.id)
           await bot.delete_messages(MainList['chat.id'],Message2.id)


bot.run()
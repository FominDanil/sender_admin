import asyncio
import datetime
import os
import subprocess

from pyrogram import Client
import uuid
from celery import Celery
from pyrogram.raw.functions.messages import GetScheduledHistory
from yt_dlp import YoutubeDL
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips


from conf import USER_SESSION_NAME, USER_API_ID, USER_API_HASH, PHONE, REDIS_URI, schedule

celery = Celery('tasks', broker=f'redis://{REDIS_URI}/0')


def get_app() -> Client:
    return Client(USER_SESSION_NAME, api_id=USER_API_ID, api_hash=USER_API_HASH, phone_number=PHONE, workdir=os.getcwd())


def download_video(url):
    
    name = f'{uuid.uuid4().hex}.mp4'
    opts = {'format': 'best[ext=mp4]', 'outtmpl': name, }
    with YoutubeDL(opts) as yt:
        err = yt.download([url])
        if err:
            print(f'some errors: {err}')

    clip = VideoFileClip(name).subclip(4)
    full_video_name = f'{uuid.uuid4().hex}.mp4'
    command = f"ffmpeg -ss 4 -i {name} -c:v copy -c:a copy {full_video_name}"
    subprocess.call(command, shell=True)
    clip_size = clip.size
    video_duration = clip.duration

    part_duration = video_duration / 5

    clips = []
    for i in range(5):
        start = i * part_duration
        end = start + 6
        clip_part = clip.subclip(start, end)
        clips.append(clip_part)
    final_clip = concatenate_videoclips(clips, method="compose")

    combined_name = f'{uuid.uuid4().hex}.mp4'
    final_clip.write_videofile(combined_name)
    final_clip_size = final_clip.size
    os.remove(name)

    id_short_video = [combined_name, final_clip_size[0], final_clip_size[1]]
    id_full_video = [full_video_name, clip_size[0], clip_size[1]]

    return id_short_video, id_full_video


async def main_func(url, chat_id):
    videos = download_video(url)
    app = get_app()
    try:
        await app.start()
        peer = await app.resolve_peer(chat_id[0])
        scheduled_messages_history = await app.invoke(GetScheduledHistory(peer=peer, hash=0))
        scheduled_messages = scheduled_messages_history.messages
        if scheduled_messages:
            old_time = datetime.datetime.fromtimestamp(scheduled_messages[0].date)
        else:
            old_time = None
        if not old_time or old_time < datetime.datetime.now():
            sending_time = 0
            for time in schedule:
                if datetime.datetime.now().time() < time:
                    sending_time = time
                    break
            if sending_time == 0:
                sending_time = schedule[0]
                sending_date = datetime.date.today() + datetime.timedelta(days=1)
            else:
                sending_date = datetime.date.today()

            sending_datetime = datetime.datetime.combine(sending_date, sending_time)

        else:
            old_time_date = old_time.date()
            old_time_time = old_time.time()

            sending_time = 0
            for time in schedule:
                if old_time_time < time:
                    sending_time = time
                    break

            if sending_time == 0:

                sending_time = schedule[0]
                sending_date = old_time_date + datetime.timedelta(days=1)
            else:
                sending_date = old_time_date

            sending_datetime = datetime.datetime.combine(sending_date, sending_time)

        await app.send_video(chat_id[0], videos[0][0], width=videos[0][1], height=videos[0][2], supports_streaming=True, schedule_date=sending_datetime)
        await app.send_video(chat_id[1], videos[1][0], width=videos[1][1], height=videos[1][2], supports_streaming=True)
    finally:
        await app.stop()
        os.remove(videos[0][0])
        os.remove(videos[1][0])


@celery.task
def prepare_video(url, chat_id):
    asyncio.run(main_func(url, chat_id))

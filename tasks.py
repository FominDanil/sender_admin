import asyncio
import datetime
import os
import subprocess
import random

from pyrogram import Client
import uuid
from celery import Celery
from pyrogram.raw.functions.messages import GetScheduledHistory
from yt_dlp import YoutubeDL
from moviepy.video.io.VideoFileClip import VideoFileClip


from conf import USER_SESSION_NAME, USER_API_ID, USER_API_HASH, PHONE, REDIS_URI, schedule

celery = Celery('tasks', broker=f'redis://{REDIS_URI}/0')


def get_app() -> Client:
    return Client(USER_SESSION_NAME, api_id=USER_API_ID, api_hash=USER_API_HASH, phone_number=PHONE, workdir=os.getcwd())


def download_video(url):

    name = f'{uuid.uuid4().hex}.mp4'
    opts = {'format': 'best[ext=mp4]', 'outtmpl': name}
    with YoutubeDL(opts) as yt:
        err = yt.download([url])
        if err:
            print(f'some errors: {err}')

    clip = VideoFileClip(name)
    video_duration = int(clip.duration - 40)
    full_video_name = f'{uuid.uuid4().hex}.mp4'
    command = f"ffmpeg -ss 20 -i {name} -t {video_duration} -c:v copy -c:a copy {full_video_name}"
    subprocess.call(command, shell=True)
    clip_size = clip.size

    thumb = f'{uuid.uuid4().hex}.png'
    command = f'ffmpeg -i {full_video_name} -ss 00:00:1.0 -frames:v 1 {thumb}'
    subprocess.call(command, shell=True)

    if video_duration > 185:
        part_time = int(video_duration / 4)
        part1_name = f'{uuid.uuid4().hex}.mp4'
        part2_name = f'{uuid.uuid4().hex}.mp4'
        part3_name = f'{uuid.uuid4().hex}.mp4'

        short_video_duration = random.randint(90, 180)
        part_duration = int(short_video_duration // 3)
        subprocess.run(f"ffmpeg -ss {part_time} -i {full_video_name} -t {part_duration} -vsync 2 -c:v copy -c:a copy {part1_name}", shell=True, check=True)
        subprocess.run(f"ffmpeg -ss {part_time*2} -i {full_video_name} -t {part_duration} -vsync 2 -c:v copy -c:a copy {part2_name}", shell=True, check=True)
        subprocess.run(f"ffmpeg -ss {part_time*3} -i {full_video_name} -t {part_duration} -vsync 2 -c:v copy -c:a copy {part3_name}", shell=True, check=True)
        short_video_duration = part_duration * 3

        combined_name = f'{uuid.uuid4().hex}.mp4'
        subprocess.run(f'ffmpeg -i {part1_name} -i {part2_name} -i {part3_name} -vsync 2 -filter_complex "concat=n=3:v=1:a=1" {combined_name}', shell=True, check=True)

        os.remove(part1_name)
        os.remove(part2_name)
        os.remove(part3_name)

        id_short_video = [combined_name, clip_size[0], clip_size[1], short_video_duration]
        id_full_video = [full_video_name, clip_size[0], clip_size[1], video_duration]

    else:
        id_short_video = [full_video_name, clip_size[0], clip_size[1], video_duration]
        id_full_video = [full_video_name, clip_size[0], clip_size[1], video_duration]
    os.remove(name)
    return id_short_video, id_full_video, thumb


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

        await app.send_video(chat_id[0], videos[0][0], width=videos[0][1], height=videos[0][2], supports_streaming=True, schedule_date=sending_datetime, duration=videos[0][3], thumb=videos[2])
        await app.send_video(chat_id[1], videos[1][0], width=videos[1][1], height=videos[1][2], supports_streaming=True, duration=videos[1][3], thumb=videos[2])
    finally:
        await app.stop()
        os.remove(videos[0][0])
        os.remove(videos[1][0])
        os.remove(videos[2])


@celery.task
def prepare_video(url, chat_id):
    asyncio.run(main_func(url, chat_id))


# cli.send_video(430625699, a[1][0], width=a[1][1], height=a[1][2], supports_streaming=True)
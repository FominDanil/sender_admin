# Admin sender bot

This project is for downloading videos from various sites and for deferred sending to the channels Telegram, the bot also knows how to change the video based on your request - cut, impose a watermark, remove the sound and more.. The application uses Python, Celery, and Redis. The entire project can be spun up using Docker Compose. 

## Requirements
- Python 3.10
- Docker and Docker Compose
- Telegram account
- Telegram bot api token

## Installation

Firstly, you need to clone this repository:

```bash
git clone https://github.com/FominDanil/sender_admin.git
cd sender_admin
```

## Configuration
### .env
The application uses environment variables for configuration. Rename `.env.example` to `.env` and fill in the necessary details:

```bash
cp .env.example .env
nano .env
```

- BOT_TOKEN: get it from @BotFather
- USER_API_ID, USER_API_HASH: get it from https://my.telegram.org
- USER_SESSION_NAME: name of the session file, you can specify any name
- PHONE: telegram account phone number

>if you want to change the telegram account, replace the PHONE and USER_SESSION_NAME or delete the old file with the name USER_SESSION_NAME.session

### config.py
Next, you need to set up the necessary configurations in the `conf.py` file:

```bash
nano conf.py
```

- schedule: fill the schedule array with datetime.time objects with the schedule time. **Necessarily** in ascending order. By default, the schedule is set for every 3 hours
- channels: fill the channels array with arrays consisting of the id of the public channel, the id of the closed channel, the text that will be on the selection button to send to this channel
- button_text and button_url: the text and link that will be added to each post in the public channel

### Setting up a Session File

In order to use the application in Docker, it is necessary to first create a session file. This can be done by running `register.py` and following the instructions:

```bash
pip install -r requirements.txt
python register.py
```

## Usage

>Be sure to add a telegram account to the administrators of each channel

Once you have the session file and your environment variables set up, you can start the application using Docker Compose:

```bash
docker-compose up -d --build
```

The application will now run in the background, downloading videos from the specified YouTube channels and posting them to the specified Telegram channels according to the schedule defined in the configuration.

## Telegram 
1. Send the bot a link to the video you want to download and distribute to one of your channels for delayed/instant sending

![Imgur](https://imgur.com/B8hAAZy.png)

2. Choose channel

![Imgur](https://imgur.com/JROvqDb.png)

3. Bot sent your video to a specific channel, the screenshot shows the method with delayed sending


![Imgur](https://imgur.com/j9hGUaP.png)weafvdvfasrfvsdrgfvd
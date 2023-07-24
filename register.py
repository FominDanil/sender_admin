from pyrogram import Client

from conf import USER_API_ID, USER_API_HASH, USER_SESSION_NAME, PHONE

app = Client(USER_SESSION_NAME, api_id=USER_API_ID, api_hash=USER_API_HASH, phone_number=PHONE)


async def main():
    await app.start()
    await app.stop()


app.run(main())

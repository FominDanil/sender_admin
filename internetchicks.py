import aiohttp
from bs4 import BeautifulSoup


async def get_link(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

            # Создаем объект BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Находим кнопку с <span>PLAYER 02</span>
            button = soup.find('button', string='PLAYER 02')

            if button:
                # Получаем значение атрибута onClick кнопки
                onclick_value = button.get('onclick')
                return onclick_value.split("'")[1]
            else:
                return None

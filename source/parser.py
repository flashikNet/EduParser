import aiohttp
from bs4 import BeautifulSoup as bs
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Sneaker

BASE_URL = 'https://ufa.streetfoot.ru/catalog/{filter}'
FILTER_FORMAT = '?filtering=1&filter_brands={brand}-brand'


async def get_sneakers(url, brand):
    sneakers = []
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url) as response:
                html = await response.text()
                soup = bs(html, 'lxml')
                products = soup.find_all("li", class_="product")
                for product in products:
                    name = product.find('h3').text
                    price = product.find('span', class_="amount").text
                    sneakers.append({
                        "name": name,
                        "price": price,
                        "brand": brand})
                next_link_tag = soup.find('a', class_="next page-numbers")
                if next_link_tag is None:
                    break
                url = next_link_tag['href']
    return sneakers


async def save_sneakers_to_db(brand: str, db: AsyncSession):
    url = BASE_URL.format(filter=FILTER_FORMAT.format(brand=brand))
    result = await db.execute(select(Sneaker).filter(Sneaker.brand == brand))
    sneakers = result.scalars()

    for sneaker in sneakers:
        await db.delete(sneaker)

    sneakers = await get_sneakers(url, brand)
    for sneaker in sneakers:
        db.add(Sneaker(
            name=sneaker["name"],
            price=sneaker["price"],
            brand=brand))
    await db.commit()

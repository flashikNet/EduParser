from bs4 import BeautifulSoup as bs
import requests

BASE_URL = 'https://ufa.streetfoot.ru/catalog/{filter}'
FILTER_FORMAT = '?filtering=1&filter_brands={brand}-brand'


def get_sneakers(url):
    sneakers = []
    with requests.Session() as session:
        while True:
            page = session.get(url)
            soap = bs(page.text, 'lxml')
            products = soap.find_all("li", class_="product")
            for product in products:
                name = product.find('h3').text
                price = product.find('span', class_="amount").text
                sneakers.append({
                    "name": name,
                    "price": price,
                })
            next_link_tag = soap.find('a', class_="next page-numbers")
            if next_link_tag is None:
                break
            url = next_link_tag['href']
    return sneakers


def main():
    brand = input("Введите бренд (например: crocs):\n").lower()
    if brand:
        filter_string = FILTER_FORMAT.format(brand=brand)
    else:
        print("Будет выведен весь каталог кроссовок. Вы уверены?(y/n)")
        answer = input()
        if answer != 'y':
            main()
            return
        filter_string = ''

    url = BASE_URL.format(filter=filter_string)
    sneakers = get_sneakers(url)

    if sneakers:
        print(f'Найдено {len(sneakers)} кроссовок {brand}:')
        print(*[f'{i}. {s["name"]}: {s["price"]}'
                for i, s in enumerate(sneakers, 1)], sep='\n')
    else:
        print(f'Не найдено кроссовок бренда "{brand}"')


if __name__ == "__main__":
    main()

# Парсер кроссовок по брендам

**Описание:**  
Этот парсер является домашней работой в рамках дисциплины **'Основы Web-API'** и предназначен для сбора данных о кроссовках с сайта **streetfoot.ru**. Приложение запрашивает название бренда у пользователя, а затем собирает информацию о всех моделях выбранного бренда, включая название и цену. Если товары размещены на нескольких страницах, парсер обходит их все и собирает полные данные по каталогу.

## Список доступных брендов:

- `adidas`
- `alexander-mcqueen`
- `asics`
- `balenciaga`
- `balmain`
- `cat-sofa`
- `converse`
- `crocs`
- `dc-shoes`
- `dior`
- `dolce-gabbana`
- `dr-martens`
- `fila`
- `golden-goose`
- `merrell`
- `native`
- `new-balance`
- `nike`
- `premiata`
- `puma`
- `reebok`
- `rick-owens`
- `timberland`
- `under-armour`
- `vans`
- `versace`

## Основные функции:

- **Запрос по бренду:**  
  Приложение запрашивает название бренда. Например, для бренда **Crocs** пользователь вводит `crocs`.
- **Обход страниц:**  
  Парсер автоматически переходит на следующую страницу, если товары не умещаются на одной странице.
- **Вывод результатов:**  
  Выводит общее количество найденных товаров и информацию о каждом: название модели и цену.
- **Режим всего каталога:**  
  Если бренд не указан, парсер предлагает вывести весь каталог кроссовок.

## Пример использования:

```plaintext
Введите бренд (например: crocs):
crocs

Найдено 5 кроссовок crocs:
1. Crocs Classic Clog: 3,499₽
2. Crocs Literide Clog: 4,299₽
...

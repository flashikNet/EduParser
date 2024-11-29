from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from database import AsyncSessionLocal, init_db
from models import Sneaker
from pydantic import BaseModel
from parser import save_sneakers_to_db

app = FastAPI(on_startup=[init_db])


# Зависимость для получения сессии БД
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Pydantic-схема для обновления данных
class SneakerUpdate(BaseModel):
    name: str | None = None
    price: str | None = None
    brand: str | None = None


# Эндпоинт для парсинга и наполнения БД
@app.post("/parse/{brand}")
async def parse_brand(brand: str, db: AsyncSession = Depends(get_db)):
    await save_sneakers_to_db(brand, db)
    return {"message": f"Парсинг завершён для бренда: {brand}"}


# Эндпоинт для получения списка кроссовок из БД
@app.get("/sneakers/{brand}", response_model=List[dict])
async def read_sneakers(brand: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sneaker).filter(Sneaker.brand == brand))
    sneakers = result.scalars().all()

    if not sneakers:
        raise HTTPException(status_code=404, detail="Кроссовки не найдены")

    return [{
        "id": s.id,
        "name": s.name,
        "price": s.price,
        "brand": s.brand
    } for s in sneakers]


# Эндпоинт для редактирования информации о кроссовке
@app.put("/sneakers/{sneaker_id}")
async def update_sneaker(sneaker_id: int,
                         sneaker_data: SneakerUpdate,
                         db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sneaker).filter(Sneaker.id == sneaker_id))
    sneaker = result.scalars().first()

    if not sneaker:
        raise HTTPException(status_code=404, detail="Кроссовок не найден")

    if sneaker_data.name:
        sneaker.name = sneaker_data.name
    if sneaker_data.price:
        sneaker.price = sneaker_data.price
    if sneaker_data.brand:
        sneaker.brand = sneaker_data.brand

    await db.commit()
    return {"message": "Кроссовок успешно обновлён",
            "sneaker": {
                "id": sneaker.id,
                "name": sneaker.name,
                "price": sneaker.price,
                "brand": sneaker.brand
                }
            }

# Эндпоинт для удаления кроссовка из БД


@app.delete("/sneakers/{sneaker_id}")
async def delete_sneaker(sneaker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sneaker).filter(Sneaker.id == sneaker_id))
    sneaker = result.scalars().first()

    if not sneaker:
        raise HTTPException(status_code=404, detail="Кроссовок не найден")

    await db.delete(sneaker)
    await db.commit()

    return {"message": "Кроссовок успешно удалён"}

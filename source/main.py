from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from database import AsyncSessionLocal, init_db
from models import Sneaker
from pydantic import BaseModel
from parser import save_sneakers_to_db
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    ## WebSocket Уведомления
    Этот WebSocket позволяет получать уведомления о действиях с данными.

    ### Пример использования на js:
    ```javascript
    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.onopen = () => {
    console.log("Соединение установлено");
    };

    socket.onmessage = (event) => {
        console.log("Уведомление:", event.data);
    };

    socket.onclose = () => {
        console.log("Соединение закрыто");
    };
    ```
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Ожидаем сообщения от клиента
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Эндпоинт для парсинга и наполнения БД
@app.post("/parse/{brand}")
async def parse_brand(brand: str, db: AsyncSession = Depends(get_db)):
    await save_sneakers_to_db(brand, db)
    await manager.broadcast(f"Бренд {brand} успешно обновлён в базе данных.")
    return {"message": f"Парсинг завершён для бренда: {brand}"}


# Эндпоинт для получения списка кроссовок из БД
@app.get("/sneakers/{brand}", response_model=List[dict])
async def read_sneakers(brand: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sneaker).filter(Sneaker.brand == brand))
    sneakers = result.scalars().all()

    if not sneakers:
        raise HTTPException(status_code=404, detail="Кроссовки не найдены")

    await manager.broadcast(f"Данные для бренда {brand} запрошены.")
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
    await manager.broadcast(f"Кроссовок с ID {sneaker_id} обновлён.")
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
    await manager.broadcast(f"Кроссовок с ID {sneaker_id} удалён.")
    return {"message": "Кроссовок успешно удалён"}

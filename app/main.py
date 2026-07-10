from fastapi import FastAPI, HTTPException
from app.database import SessionLocal, engine
from app.models import Base, Item

# Создаём таблицы (в продакшене через миграции, но для пет-проекта ок)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SRE Pet Project")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items")
def list_items():
    db = SessionLocal()
    try:
        items = db.query(Item).all()
        return [{"id": i.id, "name": i.name, "value": i.value} for i in items]
    finally:
        db.close()

@app.post("/items")
def create_item(name: str, value: int):
    db = SessionLocal()
    try:
        item = Item(name=name, value=value)
        db.add(item)
        db.commit()
        db.refresh(item)
        return {"id": item.id, "name": item.name, "value": item.value}
    finally:
        db.close()
@app.get("/version")
def version():
    return {"version": "0.1.0", "author": "SRE student"}

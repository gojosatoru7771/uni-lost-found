from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from uni_lost_found.config import TITLE, VERSION, DESCRIPTION
from uni_lost_found.schemas import Item, ItemCreate

app = FastAPI(title=TITLE, version=VERSION, description=DESCRIPTION)

db_items: List[Item] = []
item_id_counter = 1
from datetime import datetime

db_items.extend([
    Item(
        id=1, type="found", category="electronics", title="iPhone 13",
        description= "Найдена синяя мобилка айфон в черном чехле",
        location="Библиотека, 2 этаж", time=datetime.now(), is_resolved=False, claims=[]
    ),
    Item(
        id=2, type="found", category="documents", title="Студенческий билет",
        description="Найден студенческий на имя Саматова Аэлита",
        location="Коворкинг 3 корпуса", time=datetime.now(), is_resolved=False, claims=[]
    ),
    Item(
        id=3, type="lost", category="clothing", title="Куртка черная",
        description="Потерял кожаную куртку Zara, внутри были ключи",
        location="Гардероб или столовая", time=datetime.now(), is_resolved=False, claims=[]
    ),
    Item(
        id=4, type="lost", category="other", title="Ключи от дома",
        description="Связка ключей с брелком в виде наручников",
        location="Двор университета", time=datetime.now(), is_resolved=True, claims=[]
    )
])
item_id_counter = 5


def find_matches(new_item: Item) -> List[Item]:
    matches = []
    new_text = (new_item.title + " " + new_item.description).lower()
    new_words = set(new_text.split())

    for item in db_items:
        if item.type != new_item.type and not item.is_resolved:


            category_match = item.category == new_item.category

            existing_text = (item.title + " " + item.description).lower()
            existing_words = set(existing_text.split())
            common_words = new_words.intersection(existing_words)

            if len(common_words) >= 1 or (category_match and len(common_words) > 0):
                matches.append(item)
    return matches



@app.get("/items", response_model=List[Item])
def get_items(
        type: Optional[str] = Query(None, description="Фильтр: lost или found"),
        category: Optional[str] = Query(None, description="Фильтр по категории"),
        search: Optional[str] = Query(None, description="Поисковый запрос по названию/описанию")
):
    filtered_items = db_items

    if type:
        filtered_items = [i for i in filtered_items if i.type == type]
    if category:
        filtered_items = [i for i in filtered_items if i.category == category]
    if search:
        search = search.lower()
        filtered_items = [
            i for i in filtered_items
            if search in i.title.lower() or search in i.description.lower()
        ]

    return filtered_items


@app.post("/items/create")
def create_item(item_data: ItemCreate):
    global item_id_counter

    new_item = Item(
        id=item_id_counter,
        type=item_data.type,
        category=item_data.category,
        title=item_data.title,
        description=item_data.description,
        location=item_data.location,
        time=item_data.time,
        is_resolved=False,
        claims=[]
    )
    item_id_counter += 1

    potential_matches = find_matches(new_item)
    db_items.append(new_item)

    return {
        "status": "Успешно добавлено",
        "your_item": new_item,
        "matches_found": potential_matches
    }


@app.post("/items/{item_id}/claim")
def claim_item(item_id: int, student_name: str, contact: str):
    for item in db_items:
        if item.id == item_id:
            if item.is_resolved:
                raise HTTPException(status_code=400, detail="Эта вещь уже возвращена")

            claim = {"student_name": student_name, "contact": contact}
            item.claims.append(claim)
            return {"message": "Вы успешно заявили права на вещь. Владелец/нашедший свяжется с вами!",
                    "current_claims": item.claims}

    raise HTTPException(status_code=404, detail="Вещь не найдена")



@app.put("/items/{item_id}/resolve")
def resolve_item(item_id: int):
    for item in db_items:
        if item.id == item_id:
            item.is_resolved = True
            return {"message": f"Вещь с ID {item_id} успешно возвращена владельцу!"}
    raise HTTPException(status_code=404, detail="Вещь не найдена")



@app.get("/stats")
def get_service_stats():
    total_items = len(db_items)
    lost_count = len([i for i in db_items if i.type == "lost"])
    found_count = len([i for i in db_items if i.type == "found"])
    resolved_count = len([i for i in db_items if i.is_resolved])

    success_rate = (resolved_count / total_items * 100) if total_items > 0 else 0

    return {
        "total_announcements": total_items,
        "total_lost_items": lost_count,
        "total_found_items": found_count,
        "successfully_returned": resolved_count,
        "success_rate_percentage": f"{round(success_rate, 1)}%"
    }
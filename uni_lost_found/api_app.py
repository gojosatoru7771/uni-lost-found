from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Uni Lost & Found API",
    description="Расширенный REST API для университетского Бюро Находок с полной валидацией данных",
    version="2.0.0"
)


class CategoryBase(BaseModel):
    name: str = Field(..., example="Электроника")

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

class UserBase(BaseModel):
    username: str = Field(..., example="bmstu_student")
    email: str = Field(..., example="student@bmstu.ru")

class UserRegister(UserBase):
    password: str = Field(..., min_length=6, example="secret123")

class UserLogin(BaseModel):
    username: str = Field(..., example="bmstu_student")
    password: str = Field(..., example="secret123")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserProfileResponse(UserBase):
    id: int
    is_active: bool
    registered_at: datetime

class ItemBase(BaseModel):
    title: str = Field(..., example="Пропуск в УЛК")
    description: str = Field(..., example="Найден на 2 этаже возле коворкинга")
    location: str = Field(..., example="УЛК, 2 этаж")
    category_id: int = Field(..., example=1)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, example="claimed")

class ItemResponse(ItemBase):
    id: int
    status: str = Field(..., example="found")
    created_at: datetime
    owner_id: Optional[int] = None

class ReviewCreate(BaseModel):
    item_id: int
    comment: str = Field(..., example="Спасибо большое, забрал на вахте!")
    rating: int = Field(..., ge=1, le=5, example=5)

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    comment: str
    rating: int
    created_at: datetime




@app.post("/api/v1/auth/register", response_model=UserProfileResponse, tags=["Auth"])
def register(user: UserRegister):
    return {"id": 1, "username": user.username, "email": user.email, "is_active": True, "registered_at": datetime.now()}

@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Auth"])
def login(user: UserLogin):
    return {"access_token": "token_secret_123", "token_type": "bearer"}

@app.get("/api/v1/items", response_model=List[ItemResponse], tags=["Items"])
def get_items():
    return [{
        "id": 1, "title": "Пропуск в УЛК", "description": "Найден на 2 этаже",
        "location": "УЛК, 2 этаж", "category_id": 1, "status": "found", "created_at": datetime.now()
    }]

@app.post("/api/v1/items", response_model=ItemResponse, tags=["Items"])
def create_item(item: ItemCreate):
    return {
        "id": 99, "title": item.title, "description": item.description,
        "location": item.location, "category_id": item.category_id, "status": "found", "created_at": datetime.now()
    }

@app.put("/api/v1/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def update_item(item_id: int, item: ItemUpdate):
    return {
        "id": item_id, "title": "Обновленная вещь", "description": "Описание",
        "location": "ГУК", "category_id": 2, "status": "claimed", "created_at": datetime.now()
    }

@app.get("/api/v1/categories", response_model=List[CategoryResponse], tags=["Categories"])
def get_categories():
    return [{"id": 1, "name": "Документы"}, {"id": 2, "name": "Электроника"}]

@app.post("/api/v1/reviews", response_model=ReviewResponse, tags=["Reviews"])
def leave_review(review: ReviewCreate):
    return {"id": 1, "user_id": 10, "item_id": review.item_id, "comment": review.comment, "rating": review.rating, "created_at": datetime.now()}
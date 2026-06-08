import streamlit as st
from datetime import datetime
from PIL import Image
import os


st.set_page_config(page_title="Поиск вещей КГТУ/АУЦА", page_icon="🔍", layout="wide")


UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


if "db_items" not in st.session_state:
    st.session_state.db_items = [
        {
            "id": 1, "type": "Найдено", "category": "Электроника", "title": "iPhone 13",
            "description": "Синий айфон в черном чехле. Нашел на 2 этаже.",
            "location": "Библиотека", "time": "2026-06-09", "image": None
        },
        {
            "id": 2, "type": "Потеряно", "category": "Одежда", "title": "Черная куртка",
            "description": "Кожаная куртка Zara, внутри в кармане были ключи.",
            "location": "Гардероб", "time": "2026-06-09", "image": None
        }
    ]


st.title("🔍 Студенческий сервис «Поиск Вещей КГТУ/АУЦА»")
st.write("Публикуйте потерянные и найденные вещи. Система автоматически ищет совпадения!")

tab1, tab2 = st.tabs(["📋 Все объявления и Поиск", "➕ Добавить вещь"])

with tab1:
    st.header("Поиск по базе вещей")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("Введите ключевое слово для поиска (например: айфон, куртка)", "")
    with col2:
        filter_type = st.selectbox("Тип объявления", ["Все", "Потеряно", "Найдено"])
    with col3:
        filter_cat = st.selectbox("Категория", ["Все", "Электроника", "Документы", "Одежда", "Другое"])

    filtered_items = st.session_state.db_items

    if filter_type != "All" and filter_type != "Все":
        filtered_items = [i for i in filtered_items if i["type"] == filter_type]
    if filter_cat != "All" and filter_cat != "Все":
        filtered_items = [i for i in filtered_items if i["category"] == filter_cat]
    if search_query:
        q = search_query.lower()
        filtered_items = [i for i in filtered_items if q in i["title"].lower() or q in i["description"].lower()]

    if not filtered_items:
        st.warning("Ничего не найдено по вашему запросу.")
    else:
        cols = st.columns(3)
        for idx, item in enumerate(filtered_items):
            with cols[idx % 3]:
                st.subheader(f"{item['title']}")

                if item['type'] == "Потеряно":
                    st.error(f"🔴 {item['type']} | {item['category']}")
                else:
                    st.success(f"🟢 {item['type']} | {item['category']}")

                if item["image"]:
                    st.image(item["image"], use_container_width=True)
                else:
                    st.info("📷 Нет фотографии")

                st.write(f"**Описание:** {item['description']}")
                st.write(f"📍 **Место:** {item['location']}")
                st.caption(f"📅 Дата: {item['time']}")
                st.divider()

with tab2:
    st.header("Заполните данные о вещи")

    with st.form("add_form", clear_on_submit=True):
        item_type = st.radio("Вы потеряли или нашли вещь?", ["Потеряно", "Найдено"])
        category = st.selectbox("Выберите категорию", ["Электроника", "Документы", "Одежда", "Другое"])
        title = st.text_input("Название предмета (например: Ключи с брелком)", placeholder="Кратко")
        description = st.text_area("Подробное описание предмета", placeholder="Цвет, марка, особые приметы...")
        location = st.text_input("Где это произошло?", placeholder="Корпус, аудитория, этаж...")

        uploaded_file = st.file_uploader("Загрузите фото вещи (если есть)", type=["jpg", "jpeg", "png"])

        submit_btn = st.form_submit_button("Опубликовать на сайт", type="primary")

        if submit_btn:
            if not title or not description:
                st.error("Пожалуйста, заполните название и описание!")
            else:
                img_path = None
                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    img_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{uploaded_file.name}")
                    image.save(img_path)

                new_item = {
                    "id": len(st.session_state.db_items) + 1,
                    "type": item_type,
                    "category": category,
                    "title": title,
                    "description": description,
                    "location": location,
                    "time": str(datetime.now().date()),
                    "image": img_path
                }

                new_words = set((title + " " + description).lower().split())
                matches = []
                for item in st.session_state.db_items:
                    if item["type"] != item_type:
                        item_words = set((item["title"] + " " + item["description"]).lower().split())
                        if new_words.intersection(item_words):
                            matches.append(item)

                st.session_state.db_items.append(new_item)
                st.balloons()  # Эффект разлетающихся шариков при успехе!
                st.success("🎉 Объявление успешно добавлено!")

                if matches:
                    st.warning(" Внимание! Система автоматического поиска нашла возможные совпадения:")
                    for m in matches:
                        st.write(
                            f" В базе есть предмет: **{m['title']}** в локации *{m['location']}* (Описание: {m['description']})")
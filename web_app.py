# web_app.py - Помогалка AI v3.0 (Web PRO)
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import os
import json
from datetime import datetime

st.set_page_config(
    page_title="Помогалка AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══ КРАСИВЫЕ СТИЛИ ═══
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
h1 {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3rem !important;
    font-weight: 900 !important;
}
h2, h3 {
    color: #f1f5f9 !important;
}
.stButton > button {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(59, 130, 246, 0.5) !important;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    margin-right: 8px !important;
    color: #94a3b8 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
    color: white !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b) !important;
}
.stSuccess { border-radius: 10px !important; }
.stInfo { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ═══ ФУНКЦИИ ═══
def _get_font(size, bold=False):
    candidates = []
    if bold:
        candidates += ["C:/Windows/Fonts/arialbd.ttf",
                        "C:/Windows/Fonts/segoeuib.ttf"]
    candidates += ["C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/segoeui.ttf"]
    for f in candidates:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except:
                continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and line:
            lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)
    return lines


TEMPLATES = {
    "vibrant": {"name": "🔥 Яркий", "bg": "#fff7ed", "header": "#f97316",
                "header_text": "#ffffff", "price_bg": "#dc2626",
                "price_text": "#ffffff", "title": "#7c2d12",
                "desc": "#44403c", "accent": "#f97316"},
    "minimal": {"name": "⬛ Минимализм", "bg": "#ffffff", "header": "#000000",
                "header_text": "#ffffff", "price_bg": "#000000",
                "price_text": "#ffffff", "title": "#111111",
                "desc": "#555555", "accent": "#000000"},
    "premium": {"name": "👑 Премиум", "bg": "#1a1a1a", "header": "#d4af37",
                "header_text": "#000000", "price_bg": "#d4af37",
                "price_text": "#000000", "title": "#f5f5f5",
                "desc": "#a3a3a3", "accent": "#d4af37"},
    "ocean": {"name": "🌊 Океан", "bg": "#f0f9ff", "header": "#0891b2",
              "header_text": "#ffffff", "price_bg": "#0e7490",
              "price_text": "#ffffff", "title": "#164e63",
              "desc": "#155e75", "accent": "#0891b2"},
    "candy": {"name": "🍬 Конфетка", "bg": "#fdf2f8", "header": "#ec4899",
              "header_text": "#ffffff", "price_bg": "#db2777",
              "price_text": "#ffffff", "title": "#831843",
              "desc": "#9f1239", "accent": "#ec4899"},
}


def create_card(name, price, description, features, image_file=None,
                 template="vibrant"):
    t = TEMPLATES.get(template, TEMPLATES["vibrant"])
    W, H = 1000, 1300
    card = Image.new("RGB", (W, H), t["bg"])
    draw = ImageDraw.Draw(card)
    draw.rectangle([0, 0, W, 130], fill=t["header"])
    draw.text((40, 45), "ХИТ ПРОДАЖ", font=_get_font(52, True),
              fill=t["header_text"])
    y = 170
    if image_file is not None:
        try:
            img = Image.open(image_file).convert("RGB")
            img.thumbnail((880, 500), Image.LANCZOS)
            x = (W - img.width) // 2
            card.paste(img, (x, y))
            y += img.height + 30
        except:
            y += 430
    else:
        y += 430
    draw.text((60, y), name or "Товар", font=_get_font(56, True),
              fill=t["title"])
    y += 90
    draw.rectangle([60, y, 470, y + 100], fill=t["price_bg"])
    draw.text((90, y + 20), f"{price or 999} руб",
              font=_get_font(60, True), fill=t["price_text"])
    y += 140
    draw.text((60, y), "Описание:", font=_get_font(40, True),
              fill=t["accent"])
    y += 55
    for line in _wrap(draw, description or "Отличный товар",
                       _get_font(32), W - 120):
        draw.text((60, y), line, font=_get_font(32), fill=t["desc"])
        y += 45
    y += 20
    if features:
        draw.text((60, y), "Характеристики:", font=_get_font(36, True),
                  fill=t["accent"])
        y += 55
        for feat in features[:8]:
            draw.text((80, y), "- " + feat, font=_get_font(30),
                      fill=t["desc"])
            y += 45
    draw.rectangle([0, H - 80, W, H], fill=t["header"])
    draw.text((40, H - 65), "Закажите сейчас!",
              font=_get_font(36, True), fill=t["header_text"])
    return card


def create_meme(image_file, top_text, bottom_text):
    img = Image.open(image_file).convert("RGB")
    if img.width > 800:
        ratio = 800 / img.width
        img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
    draw = ImageDraw.Draw(img)
    font = _get_font(int(img.width / 15), True)
    for text, y_pos in [(top_text.upper(), 10),
                          (bottom_text.upper(), img.height - 80)]:
        if not text:
            continue
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        x = (img.width - w) // 2
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                draw.text((x + dx, y_pos + dy), text, font=font,
                          fill="black")
        draw.text((x, y_pos), text, font=font, fill="white")
    return img


def enhance_photo(img):
    img = ImageEnhance.Brightness(img).enhance(1.05)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = ImageEnhance.Color(img).enhance(1.3)
    img = ImageEnhance.Sharpness(img).enhance(1.8)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150,
                                              threshold=3))
    return img


def upscale_photo(img, scale=2):
    new_size = (img.width * scale, img.height * scale)
    up = img.resize(new_size, Image.LANCZOS)
    up = up.filter(ImageFilter.UnsharpMask(radius=2, percent=120,
                                            threshold=3))
    return up


# ═══ ИСТОРИЯ ═══
def add_history(action, info):
    try:
        with open("history.json", "r", encoding="utf-8") as f:
            h = json.load(f)
    except:
        h = []
    h.insert(0, {
        "action": action, "info": info,
        "time": datetime.now().strftime("%d.%m.%Y %H:%M")
    })
    h = h[:30]
    try:
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(h, f, ensure_ascii=False, indent=2)
    except:
        pass


def get_history():
    try:
        with open("history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# ═══ САЙДБАР ═══
with st.sidebar:
    st.markdown("# 🤖")
    st.markdown("## Помогалка AI")
    st.caption("v3.0 PRO Edition")
    st.markdown("---")
    st.markdown("### 📋 Возможности")
    st.markdown("""
    - 📦 Карточки (5 шаблонов)
    - 🖼️ Улучшение фото
    - 🔍 Апскейл x2
    - 🎨 Создатель мемов
    - 📝 Генератор текстов
    """)
    st.markdown("---")
    with st.expander("🕒 История"):
        hist = get_history()
        if not hist:
            st.caption("Пока пусто")
        else:
            for h in hist[:8]:
                st.caption(f"**{h['action']}** — {h['time']}")
    st.markdown("---")
    st.caption("Сделано с ❤️")


# ═══ ЗАГОЛОВОК ═══
st.markdown('<h1>🤖 Помогалка AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8; font-size:1.1rem;">'
            'Твой нейросеть-помощник в браузере</p>',
            unsafe_allow_html=True)
st.markdown("---")


# ═══ ВКЛАДКИ ═══
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Карточка", "🖼️ Фото", "🎨 Мем", "📝 Текст", "ℹ️ О программе"
])


# ═══ КАРТОЧКА ═══
with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📝 Данные товара")
        template_names = list(TEMPLATES.keys())
        template = st.selectbox("🎨 Шаблон", template_names,
            format_func=lambda x: TEMPLATES[x]["name"])
        name = st.text_input("Название", "Наушники Sony")
        price = st.text_input("Цена", "4990")
        description = st.text_area("Описание",
            "Премиальные беспроводные наушники с шумоподавлением",
            height=100)
        features_raw = st.text_input("Характеристики (через запятую)",
            "Bluetooth 5.3, Шумоподавление, 30 часов")
        photo = st.file_uploader("📷 Фото (необязательно)",
            type=["jpg", "jpeg", "png", "webp"])
        if photo:
            st.image(photo, caption="Предпросмотр", width=200)
        if st.button("✨ Создать карточку", type="primary",
                      use_container_width=True):
            features = [f.strip() for f in features_raw.split(",")
                        if f.strip()]
            with st.spinner("🎨 Рисую карточку..."):
                card = create_card(name, price, description, features,
                                    photo, template)
                st.session_state["card"] = card
                st.session_state["card_name"] = name
                add_history("Карточка", name)
            st.balloons()
            st.success("✅ Готово!")
    with col2:
        st.subheader("👀 Предпросмотр")
        if "card" in st.session_state:
            st.image(st.session_state["card"], use_container_width=True)
            fmt = st.selectbox("Формат", ["PNG", "JPG", "WEBP"],
                                key="card_fmt")
            buf = io.BytesIO()
            img = st.session_state["card"]
            if fmt == "PNG":
                img.save(buf, format="PNG")
            elif fmt == "JPG":
                img.convert("RGB").save(buf, format="JPEG", quality=95)
            else:
                img.save(buf, format="WEBP", quality=95)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(f"💾 Скачать {fmt}", buf.getvalue(),
                file_name=f"card_{ts}.{fmt.lower()}",
                mime=f"image/{fmt.lower()}", use_container_width=True)
        else:
            st.info("👈 Заполни данные слева")


# ═══ ФОТО ═══
with tab2:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📷 Загрузи фото")
        photo_file = st.file_uploader("Выбери фото",
            type=["jpg", "jpeg", "png", "webp"], key="photo_up")
        action = st.radio("Что сделать?",
            ["✨ Улучшить", "🔍 Апскейл x2", "🎭 Удалить фон"])
        if photo_file and st.button("🚀 Обработать", type="primary",
                                      use_container_width=True):
            img = Image.open(photo_file).convert("RGB")
            with st.spinner("⏳ Обрабатываю..."):
                if action.startswith("✨"):
                    result = enhance_photo(img)
                elif action.startswith("🔍"):
                    result = upscale_photo(img, 2)
                else:
                    try:
                        from rembg import remove
                        result = remove(img)
                    except ImportError:
                        st.error("Установи: pip install rembg")
                        result = img
                st.session_state["processed"] = result
                st.session_state["original"] = img
                add_history("Фото", action)
            st.balloons()
            st.success("✅ Готово!")
    with col2:
        st.subheader("👀 Результат")
        if "processed" in st.session_state:
            t1, t2 = st.tabs(["До", "После"])
            with t1:
                st.image(st.session_state["original"],
                          use_container_width=True)
            with t2:
                st.image(st.session_state["processed"],
                          use_container_width=True)
            buf = io.BytesIO()
            st.session_state["processed"].save(buf, format="PNG")
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button("💾 Скачать PNG", buf.getvalue(),
                file_name=f"result_{ts}.png", mime="image/png",
                use_container_width=True)
        else:
            st.info("👈 Загрузи фото")


# ═══ МЕМ ═══
with tab3:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🎨 Создатель мемов")
        meme_img = st.file_uploader("Картинка для мема",
            type=["jpg", "jpeg", "png"], key="meme_up")
        top_text = st.text_input("Верхний текст", "Когда понял что")
        bottom_text = st.text_input("Нижний текст", "Все работает!")
        if meme_img and st.button("🎨 Создать мем", type="primary",
                                    use_container_width=True):
            with st.spinner("Рисую..."):
                meme = create_meme(meme_img, top_text, bottom_text)
                st.session_state["meme"] = meme
                add_history("Мем", top_text)
            st.balloons()
            st.success("✅ Готово!")
    with col2:
        st.subheader("👀 Мем")
        if "meme" in st.session_state:
            st.image(st.session_state["meme"], use_container_width=True)
            buf = io.BytesIO()
            st.session_state["meme"].save(buf, format="PNG")
            st.download_button("💾 Скачать мем", buf.getvalue(),
                file_name=f"meme_{datetime.now():%Y%m%d_%H%M%S}.png",
                mime="image/png", use_container_width=True)
        else:
            st.info("👈 Загрузи картинку")


# ═══ ТЕКСТ ═══
with tab4:
    st.subheader("📝 Генератор текстов")
    st.caption("Помощник для идей, постов, описаний")

    text_type = st.selectbox("Что создать?",
        ["Пост для соцсетей", "Описание товара", "Поздравление",
         "Идея для бизнеса", "Заголовок"])
    topic = st.text_input("Тема / название", "Открытие кофейни")
    tone = st.select_slider("Тон",
        ["Деловой", "Дружеский", "Юмор", "Официальный"], "Дружеский")

    if st.button("✨ Создать текст", type="primary",
                  use_container_width=True):
        with st.spinner("Пишу..."):
            templates_text = {
                "Пост для соцсетей":
                    f"🔥 {topic}\n\n"
                    f"Представляем вам нечто особенное! "
                    f"Это то, что вы так долго ждали.\n\n"
                    f"✅ Качество на высшем уровне\n"
                    f"✅ Доступные цены\n"
                    f"✅ Быстрая доставка\n\n"
                    f"Заказывайте прямо сейчас! 🚀\n"
                    f"#товары #качество #{topic.replace(' ', '')}",
                "Описание товара":
                    f"✨ {topic} ✨\n\n"
                    f"Это идеальный выбор для тех, кто ценит качество "
                    f"и комфорт.\n\n"
                    f"Преимущества:\n"
                    f"• Высокое качество материалов\n"
                    f"• Долгий срок службы\n"
                    f"• Отличный внешний вид\n"
                    f"• Подходит для любого случая\n\n"
                    f"Закажите сегодня и убедитесь сами!",
                "Поздравление":
                    f"🎉 Дорогой друг!\n\n"
                    f"Поздравляю тебя с этим замечательным событием! "
                    f"Желаю тебе всего самого наилучшего, крепкого "
                    f"здоровья, счастья и успехов во всех начинаниях!\n\n"
                    f"Пусть {topic} принесёт тебе только радость! 🎊",
                "Идея для бизнеса":
                    f"💡 Идея: {topic}\n\n"
                    f"**Суть:** организация сервиса в данной сфере.\n\n"
                    f"**Целевая аудитория:** активные люди 20-45 лет.\n\n"
                    f"**Преимущества:**\n"
                    f"• Высокий спрос\n"
                    f"• Низкий порог входа\n"
                    f"• Возможность масштабирования\n\n"
                    f"**Стартовый капитал:** от 50 000 руб.\n"
                    f"**Окупаемость:** 6-12 месяцев.",
                "Заголовок":
                    f"🔥 {topic.upper()} — то, что вы искали!\n\n"
                    f"Или варианты:\n"
                    f"• {topic}: полный обзор\n"
                    f"• 10 причин выбрать {topic}\n"
                    f"• {topic} — секрет успеха",
            }
            result = templates_text.get(text_type, f"Текст про {topic}")
            st.session_state["text"] = result
            add_history("Текст", text_type)
        st.success("✅ Готово!")

    if "text" in st.session_state:
        st.text_area("Результат", st.session_state["text"], height=300)
        st.download_button("💾 Скачать .txt",
            st.session_state["text"].encode("utf-8"),
            file_name=f"text_{datetime.now():%Y%m%d_%H%M%S}.txt",
            mime="text/plain", use_container_width=True)


# ═══ О ПРОГРАММЕ ═══
with tab5:
    st.markdown("""
    ## 🤖 Помогалка AI v3.0 PRO

    Твой нейросеть-помощник в браузере.

    ### ✨ Возможности
    | Функция | Описание |
    |---------|----------|
    | 📦 Карточка товара | 5 шаблонов, добавление фото |
    | 🖼️ Улучшить фото | Повышение резкости, контраста |
    | 🔍 Апскейл x2 | Увеличение в 2 раза |
    | 🎭 Удаление фона | Убирает фон (нужен rembg) |
    | 🎨 Мемы | Создание мемов с текстом |
    | 📝 Тексты | Посты, описания, идеи |
    | 🕒 История | Последние действия |
    | 🎈 Анимации | Шарики и вспышки |

    ### 🚀 Как пользоваться
    1. Выбери вкладку
    2. Заполни данные
    3. Нажми кнопку
    4. Скачай результат

    ### 🌐 Выложить в интернет
    Через **https://streamlit.io/cloud** — бесплатно.
    """)

st.markdown("---")
st.caption("🤖 Помогалка AI © 2026 | v3.0 PRO | Сделано с ❤️")

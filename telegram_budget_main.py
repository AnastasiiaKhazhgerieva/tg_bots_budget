#!/usr/bin/env python3
import os
import requests
import pandas as pd
import sys
from io import BytesIO

BUDGET_TXT_URL = "http://45.8.250.108/budget_updates.txt"
ROUTINE_XLSX_URL = "http://45.8.250.108/main_routine_tg_msg.xlsx"

DASH_MSG = "<a href='http://45.8.250.108/index.html'>Dashboard</a> обновлен."
SLIDES_MSG = ("Обновлены слайды: для "
              "<a href='http://45.8.250.108/Budget_dashboard_upd.pptx'>дэшборда</a> "
              "и для <a href='http://45.8.250.108/Budget_routine_upd.pptx'>ОПР</a>.")
KATYA_MSG = ("Обновил файл для "
             "<a href='http://45.8.250.108/e_r_rollsums_for_Katya.xlsx'>Кати Петреневой</a>.")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID_MAIN")

def download_text(url: str) -> str:
    """Скачивает текст с сервера с обработкой ошибок"""
    print("📥 Скачиваем текст...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"
    print("✅ Текст скачан")
    return response.text.rstrip("\n")

def download_routine_flags(url: str) -> tuple[bool, bool, bool]:
    """Читает флаги из Excel"""
    print("📥 Скачиваем Excel флаги...")
    response = requests.get(url, timeout=30, verify=False)
    response.raise_for_status()
    
    df = pd.read_excel(BytesIO(response.content))
    row = df.iloc[0]
    
    dash = int(row.get("dash", 0)) == 1
    slides = int(row.get("slides", 0)) == 1
    katya = int(row.get("katya", 0)) == 1
    
    print(f"✅ Флаги: dash={dash}, slides={slides}, katya={katya}")
    return dash, slides, katya

def build_message() -> str:
    """Формирует сообщение"""
    base_msg = download_text(BUDGET_TXT_URL)
    
    dash, slides, katya = download_routine_flags(ROUTINE_XLSX_URL)
    
    extra_parts = []
    if dash:
        extra_parts.append(DASH_MSG)
    if slides:
        extra_parts.append(SLIDES_MSG)
    if katya:
        extra_parts.append(KATYA_MSG)

    if extra_parts:
        return base_msg + "\n\n" + "\n\n".join(extra_parts)
    return base_msg

def send_telegram_message(text: str):
    """Отправляет сообщение в Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID_MAIN")
    
    message = text  # убираем двойное экранирование
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    
    print("📤 Отправляем в Telegram...")
    response = requests.post(url, data=payload, timeout=30)
    response.raise_for_status()
    print("✅ Сообщение отправлено!")
    return response.json()

def main():
    try:
        msg = build_message()
        print(f"📝 Сообщение: {msg[:100]}...")
        send_telegram_message(msg)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

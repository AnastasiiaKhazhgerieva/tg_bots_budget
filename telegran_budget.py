#!/usr/bin/env python3
import pandas as pd
import requests
import sys
import os

EXCEL_URL = "http://45.8.250.108/e_budget.xlsx"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def download_excel():
    """Скачивает Excel с сервера"""
    print("📥 Скачиваем Excel...")
    response = requests.get(EXCEL_URL, timeout=30)
    response.raise_for_status()
    
    with open("e_budget.xlsx", "wb") as f:
        f.write(response.content)
    print("✅ Excel скачан")
    return True

def parse_excel():
    """Парсит данные из Excel"""
    df = pd.read_excel("e_budget.xlsx")
    row = df.iloc[0]  # Единственная строка
    
    date = row['Дата']
    income_plan = row['Доходы план']
    income_fact = row['Доходы факт']
    expense_plan = row['Расходы план']
    expense_fact = row['Расходы факт']
    
    return {
        'date': date,
        'income_plan': income_plan,
        'income_fact': income_fact,
        'expense_plan': expense_plan,
        'expense_fact': expense_fact
    }

def send_telegram(data):
    """Отправляет красивое сообщение в TG"""
    message = f"""💰 <b>Федеральный бюджет</b> (<code>{data['date']}</code>):

📈 <b>Доходы:</b>
План: <code>{data['income_plan']}</code>
Факт: <code>{data['income_fact']}</code>

📉 <b>Расходы:</b>
План: <code>{data['expense_plan']}</code>
Факт: <code>{data['expense_fact']}</code>"""
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    response = requests.post(url, data=payload, timeout=30)
    response.raise_for_status()
    print("✅ Сообщение отправлено в Telegram!")
    return True

def main():
    try:
        download_excel()
        data = parse_excel()
        print(f"📊 Данные: {data}")
        send_telegram(data)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

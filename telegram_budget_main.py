import os
import requests
import pandas as pd

BUDGET_TXT_URL = "http://45.8.250.108/budget_updates.txt"
ROUTINE_XLSX_URL = "https://45.8.250.108/main_routine_tg_msg.xlsx"

DASH_MSG = "<a href='http://45.8.250.108/index.html'>Dashboard</a> обновлен."
SLIDES_MSG = ("Обновлены слайды: для "
              "<a href='http://45.8.250.108/Budget_dashboard_upd.pptx'>дэшборда</a> "
              "и для <a href='http://45.8.250.108/Budget_routine_upd.pptx'>ОПР</a>.")
KATYA_MSG = ("Обновил файл для "
             "<a href='http://45.8.250.108/e_r_rollsums_for_Katya.xlsx'>Кати Петреневой</a>.")


def download_text(url: str) -> str:
    resp = requests.get(url)
    resp.raise_for_status()
    # В файле уже UTF‑8, берём как есть
    resp.encoding = "utf-8"
    return resp.text


def download_routine_flags(url: str):
    resp = requests.get(url, verify=False)  # self‑signed https, если надо
    resp.raise_for_status()

    # читаем excel из памяти
    from io import BytesIO
    df = pd.read_excel(BytesIO(resp.content))

    # ожидаем одну строку и столбцы dash, slides, katya
    row = df.iloc[0]
    dash = str(row.get("dash", "")).strip().upper() == "T"
    slides = str(row.get("slides", "")).strip().upper() == "T"
    katya = str(row.get("katya", "")).strip().upper() == "T"
    return dash, slides, katya


def build_message():
    base_msg = download_text(BUDGET_TXT_URL).rstrip("\n")

    dash, slides, katya = download_routine_flags(ROUTINE_XLSX_URL)

    extra_parts = []
    if dash:
        extra_parts.append(DASH_MSG)
    if slides:
        extra_parts.append(SLIDES_MSG)
    if katya:
        extra_parts.append(KATYA_MSG)

    if extra_parts:
        return base_msg + "\n" + "\n".join(extra_parts)
    else:
        return base_msg


def send_telegram_message(text: str):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID_MAIN")

    if not bot_token or not chat_id:
        raise RuntimeError("Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID_MAIN")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",  # чтобы теги <a> работали
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    return resp.json()


def main():
    msg = build_message()
    send_telegram_message(msg)


if __name__ == "__main__":
    main()

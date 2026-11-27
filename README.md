# NEXUS IT Support System — Web Edition

Веб-версия исходного проекта на Flask, SQLite, HTML и CSS. Сохранены Factory, Strategy, Observer и Singleton.

## Запуск на Windows (VS Code)

1. Откройте папку `NEXUS_Web` в VS Code.
2. В терминале выполните:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\activate
   python -m pip install -r requirements.txt
   python app.py
   ```
3. Откройте в браузере http://127.0.0.1:5000

Если активация окружения запрещена PowerShell, можно запускать команды напрямую:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Демонстрационные аккаунты

- `admin` / `admin123` (Admin)
- `user` / `user123` (User)
- `support` / `support123` (IT Support)

При первом запуске создаётся новый файл `support.db`. Чтобы перенести свои заявки, **при остановленном сервере** скопируйте `support.db` из исходного проекта в папку `NEXUS_Web`, заменив новый файл. Сделайте резервную копию перед заменой.

## Важно

Это локальная учебная версия. Для размещения в интернете нужно настроить постоянный SECRET_KEY, HTTPS, сменить демонстрационные пароли, отключить debug, добавить ограничение попыток входа и использовать production WSGI-сервер. Не публикуйте SQLite-базу с пользовательскими данными.

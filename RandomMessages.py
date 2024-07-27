import tkinter as tk
from tkinter import messagebox
from telethon import TelegramClient
import random, asyncio, json, os, time

DATA_FILE = 'data.json'
SESSION_FILE = 'RandomMessages.session'

client = None
loop = asyncio.get_event_loop()

async def get_username(api_id, api_hash):
    async with TelegramClient('RandomMessages', api_id, api_hash, system_version='4.16.30-vxCUSTOM') as client:
        me = await client.get_me()
        return me.username

async def send_code_async(api_id, api_hash, phone):
    global client
    try:
        client = TelegramClient('RandomMessages', api_id, api_hash, system_version='4.16.30-vxCUSTOM')
        await client.connect()
        await client.send_code_request(phone)
        status_label.config(text="Код отправлен на ваш телефон.", fg='green')
    except ConnectionError:
        status_label.config(text="Невозможно отправлять запросы пока отключено", fg='red')
    except Exception as e:
        status_label.config(text=f"Не удалось войти в систему: {e}", fg='red')

def send_code():
    api_id = api_id_entry.get()
    api_hash = api_hash_entry.get()
    phone = phone_entry.get()

    if not api_id or not api_hash or not phone:
        status_label.config(text="Все поля должны быть заполнены!", fg='red')
        return

    loop.run_until_complete(send_code_async(api_id, api_hash, phone))

async def verify_code_async(phone, code):
    global client
    try:
        await client.sign_in(phone=phone, code=code)
        me = await client.get_me()
        username_label.config(text=me.username)
        status_label.config(text="Успешно вошли в систему!", fg='green')
    except ConnectionError:
        status_label.config(text="Невозможно отправлять запросы пока отключено", fg='red')
    except Exception as e:
        status_label.config(text=f"Не удалось войти в систему: {e}", fg='red')

def verify_code():
    global client
    if not client:
        status_label.config(text="Клиент не инициализирован.", fg='red')
        return

    code = code_entry.get()
    phone = phone_entry.get()
    loop.run_until_complete(verify_code_async(phone, code))

# Функция для отправки сообщения
async def send_message(internal_messages, internal_api_id, internal_api_hash, sendToUsername):
    try:
        async with TelegramClient('RandomMessages', internal_api_id, internal_api_hash, system_version='4.16.30-vxCUSTOM') as internal_client:
            rand_msg = random.choice(internal_messages)
            await internal_client.send_message(sendToUsername, rand_msg)
            status_label.config(text='ОТПРАВЛЕНО: ' + str(rand_msg), fg='green')
            print('ОТПРАВЛЕНО: ' + str(rand_msg))
    except ValueError:
        status_label.config(text="Возникла ошибка при попытке отправить сообщение указанному адресату.", fg='red')
    except Exception as e:
        status_label.config(text=f"Произошла ошибка: {e}", fg='red')

# Функция для запуска отправки сообщения при нажатии кнопки
def start_sending():
    api_id = api_id_entry.get()
    api_hash = api_hash_entry.get()
    recipient = recipient_entry.get()
    messages = messages_entry.get("1.0", tk.END).strip().split('\n')

    if not api_id or not api_hash or not recipient or not messages:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
        return

    try:
        api_id = int(api_id)
        loop.run_until_complete(send_message(messages, api_id, api_hash, recipient))
    except ValueError:
        status_label.config(text="Неправильный формат api_id.", fg='red')
    except Exception as e:
        status_label.config(text=f"Произошла ошибка: {e}", fg='red')

async def send_multiple_messages(internal_messages, internal_api_id, internal_api_hash, sendToUsername, count, interval, allow_repeats):
    try:
        async with TelegramClient('RandomMessages', internal_api_id, internal_api_hash, system_version='4.16.30-vxCUSTOM') as internal_client:
            messages_to_send = internal_messages.copy() if not allow_repeats else internal_messages
            for _ in range(count):
                if not messages_to_send:
                    messages_to_send = internal_messages.copy()
                rand_msg = random.choice(messages_to_send)
                await internal_client.send_message(sendToUsername, rand_msg)
                if not allow_repeats:
                    messages_to_send.remove(rand_msg)
                print('ОТПРАВЛЕНО: ' + str(rand_msg))
                await asyncio.sleep(interval)
            status_label.config(text=f'{count} сообщений отправлено.', fg='green')
    except ValueError:
        status_label.config(text="Возникла ошибка при попытке отправить сообщение указанному адресату.", fg='red')
    except Exception as e:
        status_label.config(text=f"Произошла ошибка: {e}", fg='red')

def start_sending_multiple():
    api_id = api_id_entry.get()
    api_hash = api_hash_entry.get()
    recipient = recipient_entry.get()
    messages = messages_entry.get("1.0", tk.END).strip().split('\n')
    try:
        count = int(count_entry.get())
        interval = float(interval_entry.get())
    except ValueError:
        status_label.config(text="Неправильный формат количества сообщений или интервала.", fg='red')
        return

    if not api_id or not api_hash or not recipient or not messages:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
        return

    try:
        api_id = int(api_id)
        allow_repeats = repeat_mode.get() == 1
        loop.run_until_complete(send_multiple_messages(messages, api_id, api_hash, recipient, count, interval, allow_repeats))
    except ValueError:
        status_label.config(text="Неправильный формат api_id.", fg='red')
    except Exception as e:
        status_label.config(text=f"Произошла ошибка: {e}", fg='red')

# Функция для сохранения данных в файл
def save_data():
    data = {
        "api_id": api_id_entry.get(),
        "api_hash": api_hash_entry.get(),
        "phone": phone_entry.get(),
        "recipient": recipient_entry.get(),
        "messages": messages_entry.get("1.0", tk.END).strip(),
        "code": code_entry.get(),
        "count": count_entry.get(),
        "interval": interval_entry.get(),
        "repeat_mode": repeat_mode.get()
    }
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

# Функция для загрузки данных из файла
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            api_id_entry.insert(0, data.get("api_id", ""))
            api_hash_entry.insert(0, data.get("api_hash", ""))
            phone_entry.insert(0, data.get("phone", ""))
            recipient_entry.insert(0, data.get("recipient", ""))
            messages_entry.insert("1.0", data.get("messages", ""))
            code_entry.insert(0, data.get("code", ""))
            count_entry.insert(0, data.get("count", ""))
            interval_entry.insert(0, data.get("interval", ""))
            repeat_mode.set(data.get("repeat_mode", 1))

# Функция для загрузки имени пользователя
async def load_username():
    api_id = api_id_entry.get()
    api_hash = api_hash_entry.get()
    if api_id and api_hash:
        try:
            username = await get_username(api_id, api_hash)
            username_label.config(text=f"{username}")
        except Exception as e:
            status_label.config(text=f"Не удалось загрузить имя пользователя: {e}", fg='red')

# Функция для удаления файла сессии
def delete_session():
    try:
        os.remove(SESSION_FILE)
        status_label.config(text="Файл сессии удален.", fg='green')
    except FileNotFoundError:
        status_label.config(text="Файл сессии не найден.", fg='red')
    except Exception as e:
        status_label.config(text=f"Ошибка при удалении файла сессии: {e}", fg='red')

# Создаем GUI
root = tk.Tk()
root.title("Telegram Spammer")
root.iconbitmap('icon.ico')

tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5)
username_label = tk.Label(root, text="")
username_label.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="API ID:").grid(row=1, column=0, padx=10, pady=5)
api_id_entry = tk.Entry(root, width=30)
api_id_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="API Hash:").grid(row=2, column=0, padx=10, pady=5)
api_hash_entry = tk.Entry(root, width=30)
api_hash_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Phone Number:").grid(row=3, column=0, padx=10, pady=5)
phone_entry = tk.Entry(root, width=30)
phone_entry.grid(row=3, column=1, padx=10, pady=5)

send_code_button = tk.Button(root, text="Send Code", command=send_code)
send_code_button.grid(row=3, column=2, padx=10, pady=5)

tk.Label(root, text="Telegram Code:").grid(row=4, column=0, padx=10, pady=5)
code_entry = tk.Entry(root, width=30)
code_entry.grid(row=4, column=1, padx=10, pady=5)

verify_code_button = tk.Button(root, text="Verify Code", command=verify_code)
verify_code_button.grid(row=4, column=2, padx=10, pady=5)

tk.Label(root, text="Recipient Username:").grid(row=5, column=0, padx=10, pady=5)
recipient_entry = tk.Entry(root, width=30)
recipient_entry.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="Messages (one per line):").grid(row=6, column=0, padx=10, pady=5)
messages_entry = tk.Text(root, height=10, width=30)
messages_entry.grid(row=6, column=1, padx=10, pady=10)

send_multiple_button = tk.Button(root, text="Send Multiple Messages", command=start_sending_multiple)
send_multiple_button.grid(row=7, column=0, columnspan=1, padx=10, pady=10)

tk.Label(root, text="Number of Messages:").grid(row=7, column=1, padx=10, pady=5, sticky='w')
count_entry = tk.Entry(root, width=10)
count_entry.grid(row=7, column=1, padx=10, pady=5, sticky='e')

repeat_mode = tk.IntVar()
repeat_mode.set(1)  # Default to allow repeats

tk.Label(root, text="Repeat Mode:").grid(row=10, column=0, padx=10, pady=5)
repeat_radio1 = tk.Radiobutton(root, text="Rep", variable=repeat_mode, value=1)
repeat_radio2 = tk.Radiobutton(root, text="No Rep", variable=repeat_mode, value=2)
repeat_radio1.grid(row=11, column=0, padx=10, pady=5, sticky='w')
repeat_radio2.grid(row=11, column=0, padx=10, pady=5, sticky='e')

tk.Label(root, text="Interval (seconds):").grid(row=11, column=1, padx=10, pady=5, sticky='w')
interval_entry = tk.Entry(root, width=10)
interval_entry.grid(row=11, column=1, padx=10, pady=5, sticky='e')

send_button = tk.Button(root, text="Send Message", command=start_sending)
send_button.grid(row=12, column=0, columnspan=1, pady=10)

delete_button = tk.Button(root, text="Delete Session", command=delete_session)
delete_button.grid(row=12, column=1, padx=10, columnspan=1, pady=10)

status_label = tk.Label(root, text="", fg='red')
status_label.grid(row=13, columnspan=2, pady=10)

load_data()

root.protocol("WM_DELETE_WINDOW", lambda: [save_data(), root.destroy()])

root.mainloop()

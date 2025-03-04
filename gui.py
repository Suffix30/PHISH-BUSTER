import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter import Toplevel, Label, Button
import threading
import json
import yaml
from phishbuster import validate_url, send_posts, PROXIES, load_config

threads = []
stop_event = threading.Event()
request_count = 0

def start_flooding(url, threads_count, proxies, rate_limit, payload):
    if not validate_url(url):
        messagebox.showerror("Invalid URL", "㉿ The URL provided is invalid or not reachable ㉿")
        return
    stop_event.clear()
    for _ in range(threads_count):
        thread = threading.Thread(target=send_posts, args=(url, proxies, rate_limit, payload, stop_event), daemon=True)
        threads.append(thread)
        thread.start()

def stop_flooding():
    stop_event.set()
    global threads
    threads = []

def load_config_file():
    config_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("YAML files", "*.yaml")])
    if config_path:
        config = load_config(config_path)
        if config:
            entry_url.delete(0, ctk.END)
            entry_url.insert(0, config.get('url', ''))
            entry_threads.delete(0, ctk.END)
            entry_threads.insert(0, config.get('threads', 25))
            check_proxies.set(config.get('proxies', False))
            entry_rate_limit.delete(0, ctk.END)
            entry_rate_limit.insert(0, config.get('rate_limit', 0))
            PROXIES.extend(config.get('proxies_list', []))
            entry_payload.delete(0, ctk.END)
            entry_payload.insert(0, config.get('payload', ''))

def upload_payload_file():
    payload_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("YAML files", "*.yaml")])
    if payload_path:
        with open(payload_path, 'r') as file:
            if payload_path.endswith('.json'):
                payload_data = json.load(file)
            elif payload_path.endswith('.yaml'):
                payload_data = yaml.safe_load(file)
            entry_payload.delete(0, ctk.END)
            entry_payload.insert(0, json.dumps(payload_data))

def start():
    url = entry_url.get()
    threads_count = entry_threads.get()
    rate_limit = entry_rate_limit.get()
    payload = entry_payload.get()
    if not url:
        messagebox.showerror("Input Error", "㉿ URL is required ㉿")
        return
    if not threads_count.isdigit() or int(threads_count) <= 0:
        messagebox.showerror("Input Error", "㉿ Number of Threads must be a positive integer ㉿")
        return
    if rate_limit and (not is_float(rate_limit) or float(rate_limit) < 0):
        messagebox.showerror("Input Error", "㉿ Rate Limit must be a non-negative float ㉿")
        return
    threads_count = int(threads_count)
    rate_limit = float(rate_limit) if rate_limit else 0
    proxies = check_proxies.get()
    global PROXIES
    PROXIES = [entry.get() for entry in proxy_entries if entry.get()]
    if payload.endswith('.json') or payload.endswith('.yaml'):
        payload = load_config(payload)
    threading.Thread(target=start_flooding, args=(url, threads_count, proxies, rate_limit, payload), daemon=True).start()
    threading.Thread(target=update_status, daemon=True).start()

def show_info(message):
    info_window = Toplevel(app)
    info_window.title("Information")
    Label(info_window, text=message, wraplength=400, font=('Arial', 12)).pack(padx=10, pady=10)
    Button(info_window, text="Close", command=info_window.destroy, font=('Arial', 12)).pack(pady=5)
    info_window.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (info_window.winfo_width() // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (info_window.winfo_height() // 2)
    info_window.geometry(f"+{x}+{y}")
    info_window.transient(app)
    info_window.grab_set()
    info_window.resizable(False, False)
    info_window.attributes('-topmost', True)

def add_proxy_field():
    row = len(proxy_entries)
    entry = ctk.CTkEntry(proxy_frame, width=400, font=('Arial', 14))
    entry.grid(row=row, column=0, pady=5, padx=5)
    delete_btn = ctk.CTkButton(proxy_frame, text="X", width=30, command=lambda: remove_proxy(entry), font=('Arial', 14))
    delete_btn.grid(row=row, column=1, pady=5, padx=5)
    proxy_entries.append(entry)

def remove_proxy(entry):
    entry.grid_forget()
    proxy_entries.remove(entry)

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def update_status():
    global request_count
    while not stop_event.is_set():
        status_label.configure(text=f"Status: Running - Requests sent: {request_count}")
        time.sleep(1)
    status_label.configure(text="Status: Idle")

app = ctk.CTk()
app.title("Phish㉿Buster")
app.geometry("800x600")

proxy_entries = []
check_proxies = ctk.BooleanVar()

def create_label_with_info(parent, text, row, column, info_message):
    label = ctk.CTkLabel(parent, text=text, font=('Arial', 16))
    label.grid(row=row, column=column, pady=10, padx=10, sticky="w")
    info_button = Button(parent, text="?", command=lambda: show_info(info_message), font=('Arial', 12))
    info_button.grid(row=row, column=column + 3, padx=10)
    return label

create_label_with_info(app, "URL", 0, 0, "Enter the URL of the target you want to flood.\nExample: https://example.com/login")
entry_url = ctk.CTkEntry(app, width=500, font=('Arial', 14))
entry_url.grid(row=0, column=1, pady=20, padx=10)

create_label_with_info(app, "Number of Threads", 1, 0, "Enter the number of concurrent threads to use.\nMore threads will send more requests but may also be limited by your system's performance.\nExample: 50")
entry_threads = ctk.CTkEntry(app, width=500, font=('Arial', 14))
entry_threads.grid(row=1, column=1, pady=20, padx=10)

create_label_with_info(app, "Use Proxies", 2, 0, "Check this box if you want to use proxies for requests.\nEnter each proxy below.")
ctk.CTkCheckBox(app, text="", variable=check_proxies).grid(row=2, column=1, pady=10, padx=10, sticky="w")
Button(app, text="+", command=add_proxy_field, font=('Arial', 14)).grid(row=2, column=2, pady=10, padx=10, sticky="w")
proxy_frame = ctk.CTkScrollableFrame(app, width=500, height=100)
proxy_frame.grid(row=3, column=1, pady=10, padx=10, sticky="w", columnspan=2)

create_label_with_info(app, "Rate Limit (seconds)", 4, 0, "Enter the delay in seconds between requests sent by each thread.\nA higher rate limit will slow down the number of requests sent.\nExample: 1")
entry_rate_limit = ctk.CTkEntry(app, width=500, font=('Arial', 14))
entry_rate_limit.grid(row=4, column=1, pady=20, padx=10)

create_label_with_info(app, "Custom Payload", 5, 0, "Enter the custom payload for POST requests.\nYou can also upload a JSON or YAML file with the custom payload.\nExample: {\"username\": \"fakeuser\", \"password\": \"fakepassword123\"}")
entry_payload = ctk.CTkEntry(app, width=500, font=('Arial', 14))
entry_payload.grid(row=5, column=1, pady=20, padx=10)

button_frame = ctk.CTkFrame(app)
button_frame.grid(row=6, column=0, columnspan=3, pady=20)
button_width = 150
button_padding = 10

load_config_button = ctk.CTkButton(button_frame, text="Load Config", command=load_config_file, font=('Arial', 14), width=button_width)
load_config_button.pack(side="left", padx=button_padding)
upload_button = ctk.CTkButton(button_frame, text="Upload Payload File", command=upload_payload_file, font=('Arial', 14), width=button_width)
upload_button.pack(side="left", padx=button_padding)
start_button = ctk.CTkButton(button_frame, text="Start", command=start, font=('Arial', 14), width=button_width)
start_button.pack(side="left", padx=button_padding)
stop_button = ctk.CTkButton(button_frame, text="Stop", command=stop_flooding, font=('Arial', 14), width=button_width)
stop_button.pack(side="left", padx=button_padding)

status_label = ctk.CTkLabel(app, text="Status: Idle", font=('Arial', 14))
status_label.grid(row=7, column=0, columnspan=3, pady=10)

messagebox.showwarning("Disclaimer", "㉿ Use responsibly on authorized systems only ㉿")

app.mainloop()

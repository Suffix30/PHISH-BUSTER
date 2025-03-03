import threading
import requests
import random
import string
import names
from fake_useragent import UserAgent
import logging
import argparse
import json
import time
import yaml

DEFAULT_NUM_THREADS = 25
PROXIES = []
stop_event = threading.Event()
request_count = 0

logging.basicConfig(filename='phishbuster.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def name_gen():
    name_system = random.choice(["FullName", "FullFirstFirstInitial", "FirstInitialFullLast"])
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    if name_system == "FullName":
        return first_name + last_name
    elif name_system == "FullFirstFirstInitial":
        return first_name + last_name[0]
    return first_name[0] + last_name

def generate_random_email():
    name = name_gen()
    NumberOrNo = random.choice(["Number", "No"])
    domain = random.choice(["@gmail.com", "@yahoo.com", "@rambler.ru", "@protonmail.com", "@outlook.com", "@itunes.com"])
    if NumberOrNo == "Number":
        return name + str(random.randint(1, 100)) + domain
    return name + domain

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(characters, k=length))

def load_default_proxies():
    global PROXIES
    if not PROXIES:
        try:
            response = requests.get("https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&timeout=10000&country=all", timeout=5)
            if response.status_code == 200:
                PROXIES.extend([f"http://{line.strip()}" for line in response.text.splitlines() if line.strip()])
                logging.info(f"Loaded {len(PROXIES)} default proxies from ProxyScrape API")
            if not PROXIES:
                try:
                    with open("proxies.txt", "r") as f:
                        PROXIES.extend([line.strip() for line in f if line.strip()])
                    logging.info(f"Loaded {len(PROXIES)} default proxies from proxies.txt")
                except FileNotFoundError:
                    logging.warning("No proxies.txt found, falling back to hardcoded defaults")
                    PROXIES.extend([
                        "http://103.174.238.171:8080",
                        "http://185.199.228.220:7300",
                        "http://162.240.75.37:80"
                    ])
                    logging.info("Using hardcoded default proxies")
        except requests.RequestException as e:
            logging.error(f"Failed to fetch proxies from API: {e}")
            PROXIES.extend(["http://162.240.75.37:80"])

def validate_proxy(proxy):
    try:
        response = requests.get("http://example.com", proxies={'http': proxy, 'https': proxy}, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def send_posts(url, use_proxies=False, rate_limit=0, custom_payload=None):
    global request_count
    while not stop_event.is_set():
        email = generate_random_email()
        password = generate_random_password()
        data = custom_payload if custom_payload else {"email": email, "password": password}
        ua = UserAgent()
        user_agent = ua.random
        headers = {'User-Agent': user_agent}
        try:
            if use_proxies and PROXIES:
                proxy = {'http': random.choice(PROXIES), 'https': random.choice(PROXIES)}
                response = requests.post(url, data=data, headers=headers, proxies=proxy)
                logging.info(f"Email: {email}, Password: {password}, Status Code: {response.status_code}, User-Agent: {user_agent}, Proxy: {proxy}")
            else:
                response = requests.post(url, data=data, headers=headers)
                logging.info(f"Email: {email}, Password: {password}, Status Code: {response.status_code}, User-Agent: {user_agent}")
            request_count += 1
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
        if rate_limit > 0:
            time.sleep(rate_limit)

def validate_url(url):
    try:
        result = requests.get(url)
        return result.status_code == 200
    except requests.RequestException:
        return False

def parse_payload(payload):
    if not payload:
        return None
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON payload: {payload}")
            return None
    return payload

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file) if config_path.endswith('.json') else yaml.safe_load(file)
    required = ['url']
    for field in required:
        if field not in config:
            raise ValueError(f"Config missing required field: {field}")
    return config

def print_stats():
    while not stop_event.is_set():
        print(f"\rRequests sent: {request_count}", end="")
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str)
    parser.add_argument('--threads', type=int, default=DEFAULT_NUM_THREADS)
    parser.add_argument('--proxies', action='store_true')
    parser.add_argument('--proxy-file', type=str)
    parser.add_argument('--rate-limit', type=float, default=0)
    parser.add_argument('--config', type=str)
    parser.add_argument('--payload', type=str)
    args = parser.parse_args()

    if args.config:
        config = load_config(args.config)
        args.threads = config.get('threads', args.threads)
        args.proxies = config.get('proxies', args.proxies)
        args.rate_limit = config.get('rate_limit', args.rate_limit)
        args.url = config.get('url', args.url)
        PROXIES.extend(config.get('proxies_list', []))
        args.payload = config.get('payload', args.payload)

    if args.proxy_file:
        with open(args.proxy_file, 'r') as f:
            PROXIES.extend([line.strip() for line in f if line.strip()])
    elif args.proxies:
        load_default_proxies()

    if PROXIES:
        PROXIES = [p for p in PROXIES if validate_proxy(p)]
        if not PROXIES:
            logging.warning("No working proxies available")
            print("No working proxies found. Proceeding without proxies.")
            args.proxies = False

    if not validate_url(args.url):
        print("Invalid URL or the URL is not reachable.")
        return

    custom_payload = parse_payload(args.payload)
    threads = [threading.Thread(target=send_posts, args=(args.url, args.proxies, args.rate_limit, custom_payload), daemon=True) for _ in range(args.threads)]
    threading.Thread(target=print_stats, daemon=True).start()

    print("WARNING: Use this tool responsibly and only on systems you have permission to test.")
    try:
        for t in threads:
            t.start()
        input("Press Enter to stop...\n")
        stop_event.set()
        for t in threads:
            t.join(timeout=5)
    except KeyboardInterrupt:
        stop_event.set()

if __name__ == "__main__":
    main()

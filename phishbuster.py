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
    else:
        return name + domain

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(characters, k=length))

def send_posts(url, use_proxies=False, rate_limit=0, custom_payload=None):
    while True:
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
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
        
        if rate_limit > 0:
            time.sleep(rate_limit)

def validate_url(url):
    try:
        result = requests.get(url)
        return result.status_code == 200
    except requests.exceptions.RequestException:
        return False

def load_config(config_path):
    with open(config_path, 'r') as file:
        if config_path.endswith('.json'):
            return json.load(file)
        elif config_path.endswith('.yaml'):
            return yaml.safe_load(file)

def main():
    parser = argparse.ArgumentParser(description='PhishBuster - Flood phishing databases with fake data.')
    parser.add_argument('url', type=str, help='The URL of the target you want to flood')
    parser.add_argument('--threads', type=int, default=DEFAULT_NUM_THREADS, help='Number of concurrent threads')
    parser.add_argument('--proxies', action='store_true', help='Use proxies for requests')
    parser.add_argument('--rate-limit', type=float, default=0, help='Rate limit in seconds between requests')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--payload', type=str, help='Custom payload for POST requests')

    args = parser.parse_args()

    if args.config:
        config = load_config(args.config)
        if config:
            args.threads = config.get('threads', args.threads)
            args.proxies = config.get('proxies', args.proxies)
            args.rate_limit = config.get('rate_limit', args.rate_limit)
            args.url = config.get('url', args.url)
            PROXIES.extend(config.get('proxies_list', []))
            args.payload = config.get('payload', args.payload)

    if not validate_url(args.url):
        print("Invalid URL or the URL is not reachable.")
        return

    threads = [threading.Thread(target=send_posts, args=(args.url, args.proxies, args.rate_limit, args.payload), daemon=True) for _ in range(args.threads)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()

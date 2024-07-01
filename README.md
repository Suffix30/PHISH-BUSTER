
# Phish㉿Buster

## Overview
PhishBuster is a tool designed to combat phishing attacks by flooding phisher databases with false information. This script generates random email addresses and passwords and sends them to a specified URL, aiming to disrupt and dilute the accuracy of stolen data.

## Features
- Generate random email addresses and passwords.
- Send POST requests with fake data to specified URLs.
- Use multi-threading to send requests concurrently.
- Randomize User-Agent headers.
- Option to include or exclude numbers in email addresses.
- Support for popular email domains.
- Logging of all requests and responses.
- Input validation for target URLs.
- Rate limiting to control the frequency of requests.
- Error handling and retries for failed requests.
- Configuration via command-line arguments.
- Option to use proxies for requests.
- Load configurations from JSON or YAML files.
- Customizable email and password patterns.
- User-defined payloads for POST requests.
- Professional GUI for easy use, built with customtkinter.

## Installation
1. **Set Up Environment**:
   - Ensure you have Python 3 installed.
   - Create a virtual environment (optional but recommended):
     ```sh
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Install the required packages:
     ```sh
     pip install -r requirements.txt
     ```

## Usage

### Command Line
To run PhishBuster from the command line:
```sh
python3 phishbuster.py <URL> [--threads NUM_THREADS] [--proxies] [--rate-limit SECONDS] [--config CONFIG_FILE] [--payload CUSTOM_PAYLOAD]
```
Example:
```sh
python3 phishbuster.py https://example.com --threads 50 --proxies --rate-limit 1
```

### GUI
To run the PhishBuster GUI:
```sh
python3 gui.py
```

### Configuration File
You can use a JSON or YAML configuration file to set parameters. Example configuration:

```json
{
    "url": "https://example.com",
    "threads": 50,
    "proxies": true,
    "rate_limit": 1,
    "proxies_list": ["http://proxy1.example.com:8080", "http://proxy2.example.com:8080"],
    "payload": {"email": "fake@example.com", "password": "fakepassword123"}
}
```

### Features
- **URL**: The target URL to flood with fake data.
- **Threads**: Number of concurrent threads.
- **Proxies**: Use proxies for requests (Boolean).
- **Rate Limit**: Rate limit in seconds between requests.
- **Config**: Path to a configuration file.
- **Payload**: Custom payload for POST requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details ㉿r don't.

## Disclaimer
**Note:** This script should be used "responsibly" and only on systems you have explicit permission to test against. Misuse of this tool can lead to legal c㉿nsequences.

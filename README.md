# Phish㉿Buster

## Overview
PhishBuster is a tool designed to combat phishing attacks by flooding phisher databases with fake data. It generates random email addresses and passwords, sending them to a target URL to disrupt and dilute stolen data accuracy.

## Features
- Generates random email addresses and passwords with customizable patterns.
- Sends POST requests with fake data to specified URLs.
- Supports multi-threading for concurrent requests with clean shutdown.
- Randomizes User-Agent headers for each request.
- Includes optional numbers in email addresses.
- Supports popular email domains (e.g., Gmail, Yahoo, Protonmail).
- Logs all requests and responses to a file.
- Validates target URLs before starting.
- Offers rate limiting to control request frequency.
- Handles errors gracefully with logging.
- Configurable via command-line arguments or JSON/YAML files.
- Uses proxies with dynamic loading from API, file, or defaults.
- Displays real-time request stats in CLI and GUI.
- Allows custom payloads for POST requests.
- Features a professional GUI built with CustomTkinter.

## Installation
### Set Up Environment
1. Ensure Python 3 is installed.
2. Create a virtual environment (optional but recommended):
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
### Command Line
Run PhishBuster from the command line:

```sh
python3 phishbuster.py <URL> [--threads NUM_THREADS] [--proxies] [--proxy-file FILE] [--rate-limit SECONDS] [--config CONFIG_FILE] [--payload CUSTOM_PAYLOAD]
```

**Example:**
```sh
python3 phishbuster.py https://example.com --threads 50 --proxies --rate-limit 1
```
Press Enter or Ctrl+C to stop.

### GUI
Launch the PhishBuster GUI:

```sh
python3 gui.py
```
Configure options via the interface and click "Start" to begin, "Stop" to halt.

## Configuration File
Use a JSON or YAML file for settings. **Example:**
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
Load it with `--config config.json` (CLI) or the "Load Config" button (GUI).

## Proxy Support
- Specify proxies via `--proxy-file` or a config file.
- If `--proxies` is used without a file, defaults load from ProxyScrape API, `proxies.txt`, or hardcoded fallbacks.
- GUI allows adding/removing proxies dynamically in a scrollable list.

## Options
| Option       | Description |
|-------------|-------------|
| URL         | Target URL to flood. |
| Threads     | Number of concurrent threads (positive integer). |
| Proxies     | Enable proxy use (Boolean). |
| Proxy File  | Path to a file with proxy list. |
| Rate Limit  | Delay between requests in seconds (non-negative float). |
| Config      | Path to a JSON/YAML configuration file. |
| Payload     | Custom POST payload (string or file path). |

## License
Licensed under the MIT License - see the LICENSE file for details, or don’t.

## Disclaimer
**Note:** Use this tool responsibly and only on systems you have explicit permission to test. Misuse may lead to legal consequences.

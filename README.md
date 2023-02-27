<img src="https://github.com/5KRC1/5KRC1/blob/main/images/eAmenu_Linux/eAmenu_Linux-banner.png" alt="Hero Banner"/>

# eAmenu Service | for Linux servers
This is an example of running the eAwaiter package on Linux with crontab.

## Description
To show the use of eAwaiter, I wrote a simple example that is run daily with crontab on Linux.

## Install & Run
To install and run the project follow the following instructions:
### Installation
- Clone the repo,
```bash
git clone https://github.com/5KRC1/eAmenu_Linux && cd eAmenu_Linux
```
- install dependencies
```bash
pip3 install -r requirements.txt
```
- fill in the "config.py"
```python
default = {
    username = "",
    password = "",
    preferred_meal = "",
    default_meal = "",
    favourite_foods = [],
    disliked_foods = []
}
```

### Run once
- run with python
```bash
python3 service.py
```

### Run daily
- make "run_script.sh" executable
```bash
sudo chmod +x run_script.sh
```
- run the script
```bash
./run_script.sh
```

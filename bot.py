import requests
import time
import os
from colorama import Fore, Style, init

init(autoreset=True)

class KiichainBot:
    def __init__(self):
        # Screenshot ထဲက Sitekey အမှန်
        self.site_key = "0x4AAAAAAAADnOjc0PNeA8qVm" 
        self.site_url = "https://explorer.kiichain.io/faucet"
        # Request ပို့ရမည့် endpoint
        self.faucet_url = "https://faucet.kiivalidator.com/api/faucet"
        
        # သင့် Browser ရဲ့ User-Agent အစစ်ကို သုံးပါ
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        
        api_keys = self.load_config("2captcha.txt")
        self.api_key = api_keys[0] if api_keys else None

    def load_config(self, file_name):
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                return [line.strip() for line in f if line.strip()]
        return []

    def solve_captcha(self):
        print(f"{Fore.CYAN}[*] 2Captcha ဖြင့် အဖြေရှာနေပါသည် (စောင့်ပေးပါ)...")
        in_params = {
            'key': self.api_key,
            'method': 'turnstile',
            'sitekey': self.site_key,
            'pageurl': self.site_url,
            'json': 1
        }
        try:
            res = requests.post("http://2captcha.com/in.php", data=in_params).json()
            if res.get('status') != 1: return None
            
            task_id = res['request']
            while True:
                time.sleep(10)
                result = requests.get(f"http://2captcha.com/res.php?key={self.api_key}&action=get&id={task_id}&json=1").json()
                if result.get('status') == 1:
                    print(f"{Fore.GREEN}[+] Captcha Token ရရှိပါပြီ")
                    return result['request']
                if result.get('request') != "CAPCHA_NOT_READY":
                    print(f"{Fore.RED}[-] Error: {result.get('request')}")
                    return None
        except: return None

    def claim(self, address):
        token = self.solve_captcha()
        if not token: return

        # အောင်မြင်ခဲ့တဲ့ Headers များအတိုင်း ပြင်ဆင်ခြင်း
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://explorer.kiichain.io",
            "Referer": "https://explorer.kiichain.io/",
            "User-Agent": self.user_agent
        }
        
        payload = {"address": address, "captcha": token} #

        try:
            # Proxy မသုံးဘဲ တိုက်ရိုက်ပို့ခြင်း
            response = requests.post(self.faucet_url, headers=headers, json=payload, timeout=30)
            print(f"{Fore.MAGENTA}[!] Response: {response.text}") #
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}")

    def start(self):
        # Welcome Logo နေရာ
        print(f"{Fore.GREEN}Starting ADB NODE Bot...")
        accounts = self.load_config("accounts.txt")
        for addr in accounts:
            print(f"\n{Fore.YELLOW}Working on: {addr}")
            self.claim(addr)
            time.sleep(5)

if __name__ == "__main__":
    KiichainBot().start()

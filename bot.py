import requests
import time
import os
from colorama import Fore, Style, init

init(autoreset=True)

class KiichainBot:
    def __init__(self):
        self.site_key = "0x4AAAAAAAADnOjc0PNeA8qVm" #
        self.site_url = "https://explorer.kiichain.io/faucet"
        self.faucet_url = "https://faucet.kiivalidator.com/api/faucet"
        self.captcha_api_key = self.load_config("2captcha.txt")[0] if self.load_config("2captcha.txt") else None

    def welcome(self):
        print(
            f"""
            {Fore.GREEN + Style.BRIGHT}       █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
            {Fore.GREEN + Style.BRIGHT}      ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
            {Fore.GREEN + Style.BRIGHT}      ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
            {Fore.GREEN + Style.BRIGHT}      ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
            {Fore.GREEN + Style.BRIGHT}      ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
            {Fore.GREEN + Style.BRIGHT}      ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
            {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE
            """
        )

    def load_config(self, file_name):
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                return [line.strip() for line in f if line.strip()]
        return []

    def solve_captcha(self, proxy=None):
        if not self.captcha_api_key:
            print(f"{Fore.RED}[!] 2captcha.txt မှာ API Key ထည့်ပေးပါ")
            return None

        print(f"{Fore.CYAN}[*] Captcha ဖြေရှင်းနေပါသည် (2Captcha)...")
        in_params = {
            'key': self.captcha_api_key,
            'method': 'turnstile',
            'sitekey': self.site_key,
            'pageurl': self.site_url,
            'json': 1
        }
        
        try:
            res = requests.post("http://2captcha.com/in.php", data=in_params).json()
            if res.get('status') != 1:
                print(f"{Fore.RED}[-] 2Captcha Error: {res.get('request')}")
                return None
            
            task_id = res.get('request')
            while True:
                time.sleep(5)
                out_params = {'key': self.captcha_api_key, 'action': 'get', 'id': task_id, 'json': 1}
                result = requests.get("http://2captcha.com/res.php", params=out_params).json()
                
                if result.get('status') == 1:
                    print(f"{Fore.GREEN}[+] Captcha အောင်မြင်ပါသည်")
                    return result.get('request')
                elif result.get('request') == "CAPCHA_NOT_READY":
                    continue
                else:
                    return None
        except Exception as e:
            print(f"{Fore.RED}[-] Captcha Error: {str(e)}")
            return None

    def claim(self, address, proxy=None):
        token = self.solve_captcha(proxy)
        if not token: return

        print(f"{Fore.YELLOW}[*] Faucet Claim လုပ်နေသည်: {address[:10]}...")
        
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://explorer.kiichain.io",
            "Referer": "https://explorer.kiichain.io/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        
        payload = {"address": address, "captcha": token}
        proxies = {"http": proxy, "https": proxy} if proxy else None

        try:
            response = requests.post(self.faucet_url, headers=headers, json=payload, proxies=proxies, timeout=30)
            if response.status_code == 200:
                print(f"{Fore.GREEN}[+++] အောင်မြင်ပါသည်: {response.text}")
            else:
                print(f"{Fore.RED}[-] မအောင်မြင်ပါ: {response.text}")
        except Exception as e:
            print(f"{Fore.RED}[-] Request Error: {str(e)}")

    def start(self):
        self.welcome()
        accounts = self.load_config("accounts.txt")
        proxies = self.load_config("proxy.txt")

        if not accounts:
            print(f"{Fore.RED}[!] accounts.txt ထဲမှာ wallet address များ ထည့်ပေးပါ")
            return

        for i, addr in enumerate(accounts):
            proxy = proxies[i % len(proxies)] if proxies else None
            print(f"\n{Fore.WHITE}{'='*50}")
            print(f"{Fore.MAGENTA}Account #{i+1} | Proxy: {proxy if proxy else 'No Proxy'}")
            self.claim(addr, proxy)
            print(f"{Fore.WHITE}{'='*50}")
            time.sleep(2) # အကောင့်တစ်ခုနဲ့တစ်ခုကြား ခေတ္တနားရန်

if __name__ == "__main__":
    bot = KiichainBot()
    bot.start()

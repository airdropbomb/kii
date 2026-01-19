import requests
import time
import os
from colorama import Fore, Style, init

init(autoreset=True)

class KiichainBot:
    def __init__(self):
        # Sitekey အမှန်
        self.site_key = "0x4AAAAAAAADnOjc0PNeA8qVm" 
        self.site_url = "https://explorer.kiichain.io/faucet"
        self.faucet_url = "https://faucet.kiivalidator.com/api/faucet"
        
        # သင့် Browser ရဲ့ User-Agent အစစ်ကို သုံးပေးရပါမယ်
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        
        keys = self.load_config("2captcha.txt")
        self.captcha_api_key = keys[0] if keys else None

    def welcome(self):
        print(f"""
            {Fore.GREEN + Style.BRIGHT}       █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
            {Fore.GREEN + Style.BRIGHT}      ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
            {Fore.GREEN + Style.BRIGHT}      ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
            {Fore.GREEN + Style.BRIGHT}      ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
            {Fore.GREEN + Style.BRIGHT}      ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
            {Fore.GREEN + Style.BRIGHT}      ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
            {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE
        """)

    def load_config(self, file_name):
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                return [line.strip() for line in f if line.strip()]
        return []

    def solve_captcha(self, proxy=None):
        if not self.captcha_api_key:
            print(f"{Fore.RED}[!] Error: 2captcha.txt မတွေ့ပါ")
            return None

        print(f"{Fore.CYAN}[*] Captcha ဖြေရှင်းရန် 2Captcha သို့ ပို့နေသည်...")
        
        in_params = {
            'key': self.captcha_api_key,
            'method': 'turnstile',
            'sitekey': self.site_key,
            'pageurl': self.site_url,
            'userAgent': self.user_agent, # User-Agent ထည့်ပေးခြင်းက အောင်မြင်မှုနှုန်း ပိုများစေပါတယ်
            'json': 1
        }
        
        try:
            res = requests.post("http://2captcha.com/in.php", data=in_params).json()
            if res.get('status') != 1:
                print(f"{Fore.RED}[-!] 2Captcha Error: {res.get('request')}")
                return None
            
            task_id = res.get('request')
            print(f"{Fore.BLUE}[*] Task ID: {task_id} (စောင့်နေသည်...)")
            
            while True:
                time.sleep(10)
                out_params = {'key': self.captcha_api_key, 'action': 'get', 'id': task_id, 'json': 1}
                result = requests.get("http://2captcha.com/res.php", params=out_params).json()
                
                if result.get('status') == 1:
                    print(f"{Fore.GREEN}[+] Captcha အောင်မြင်ပါသည်")
                    return result.get('request')
                elif result.get('request') == "CAPCHA_NOT_READY":
                    print(f"{Fore.WHITE}[.] အဖြေမရသေးပါ၊ ထပ်စောင့်နေသည်...")
                    continue
                else:
                    print(f"{Fore.RED}[-!] Error: {result.get('request')}")
                    return None
        except Exception as e:
            print(f"{Fore.RED}[-!] Connection Error: {str(e)}")
            return None

    def claim(self, address, proxy=None):
        token = self.solve_captcha()
        if not token: return

        print(f"{Fore.YELLOW}[*] Faucet Claim လုပ်နေသည်: {address}")
        
        # Headers အစစ်အမှန်များကို အသုံးပြုခြင်း
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://explorer.kiichain.io",
            "Referer": "https://explorer.kiichain.io/",
            "User-Agent": self.user_agent,
            "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Herond";v="138"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"'
        }
        
        # Payload format
        payload = {"address": address, "captcha": token}
        proxies = {"http": proxy, "https": proxy} if proxy else None

        try:
            response = requests.post(self.faucet_url, headers=headers, json=payload, proxies=proxies, timeout=30)
            print(f"{Fore.MAGENTA}[!] Server Response: {response.text}") #
        except Exception as e:
            print(f"{Fore.RED}[-!] Claim Error: {str(e)}")

    def start(self):
        self.welcome()
        accounts = self.load_config("accounts.txt")
        proxies = self.load_config("proxy.txt")

        if not accounts:
            print(f"{Fore.RED}[!] accounts.txt ဖိုင်ကို စစ်ဆေးပါ")
            return

        for i, addr in enumerate(accounts):
            proxy = proxies[i % len(proxies)] if proxies else None
            print(f"\n{Fore.WHITE}{'='*60}")
            print(f"{Fore.YELLOW}Account #{i+1} | {addr}")
            self.claim(addr, proxy)
            print(f"{Fore.WHITE}{'='*60}")
            time.sleep(5)

if __name__ == "__main__":
    bot = KiichainBot()
    bot.start()

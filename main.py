import asyncio
import json
import os
import random
import re
import sys
import time
from glob import glob
from pathlib import Path
from urllib.parse import unquote

import aiohttp
import requests
from bs4 import BeautifulSoup as bs
from colorama import *
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import RequestWebViewRequest

init(autoreset=True)

merah = Fore.LIGHTRED_EX
hijau = Fore.LIGHTGREEN_EX
kuning = Fore.LIGHTYELLOW_EX
biru = Fore.LIGHTBLUE_EX
hitam = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
putih = Fore.LIGHTWHITE_EX


class GeMod:
    def __init__(self):
        self.xiaomi_page_list = [
            "https://www.gsmarena.com/xiaomi-phones-80.php",
            "https://www.gsmarena.com/xiaomi-phones-f-80-0-p2.php",
            "https://www.gsmarena.com/xiaomi-phones-f-80-0-p3.php",
            "https://www.gsmarena.com/xiaomi-phones-f-80-0-p4.php",
            "https://www.gsmarena.com/xiaomi-phones-f-80-0-p5.php",
            "https://www.gsmarena.com/xiaomi-phones-f-80-0-p6.php",
            "https://www.gsmarena.com/xiaomi-phones-f-80-0-p7.php",
            "https://www.gsmarena.com/xiaomi-phones-f-80-0-p8.php",
        ]
        self.sdk_level_api = {
            "15": "SDK 35",
            "14": "SDK 34",
            "13": "SDK 33",
            "12": "SDK 32",
            "11": "SDK 30",
            "10": "SDK 29",
            "9": "SDK 28",
            "8": "SDK 27",
            "7": "SDK 25",
            "6": "SDK 23",
            "5": "SDK 22",
            "4": "SDK 20",
        }

    def scrape_phone(self, url: str):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        }
        res = requests.get(url, headers=headers)
        parser = bs(res.text, "html.parser")
        device_name = parser.find("h1", attrs={"data-spec": "modelname"}).text
        os = parser.find("td", attrs={"data-spec": "os"})
        # print(os)
        if os is None:
            return False
        try:
            _os = re.search(r"\d+", os.text.split(",")[0]).group()
            os = self.sdk_level_api[_os]
            return device_name, os
        except (AttributeError, KeyError):
            return False

    def generate_model(self):
        while True:
            xiaomi_page = random.choice(self.xiaomi_page_list)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            }
            res = requests.get(xiaomi_page, headers=headers)
            parser = bs(res.text, "html.parser")
            makers = parser.find("div", attrs={"class": "makers"})
            list_device = makers.find_all("li")
            choice_device = random.choice(list_device)
            device_url = "https://gsmarena.com/" + choice_device.find("a").get("href")
            res = self.scrape_phone(device_url)
            if res is False:
                continue
            return res


class Config:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash


async def ensure_even_and_divide(limit_coin):
    # Jika limit_coin tidak genap, kurangi 1
    if limit_coin % 2 != 0:
        limit_coin -= 1

    # Bagi limit_coin dengan 20
    result = limit_coin / 20

    return result


class BayiPetir:
    @staticmethod
    def data_parsing(data):
        res = unquote(data)
        data = {}
        for i in res.split("&"):
            j = unquote(i)
            y, z = j.split("=")
            data[y] = z

        return data

    @staticmethod
    def gen_data_login(data_parser):
        data_user = json.loads(data_parser["user"])
        data = {
            "externalId": int(data_user["id"]),
            "firstName": data_user["first_name"],
            "gameId": 3,
            "initData": {
                "auth_date": data_parser["auth_date"],
                "hash": data_parser["hash"],
                "query_id": data_parser["query_id"],
                "user": data_parser["user"],
            },
            "language": "en",
            "lastName": data_user["last_name"],
            "refId": "",
            "username": data_user["username"],
        }
        return data

    @staticmethod
    async def countdown(t):
        while t:
            menit, detik = divmod(t, 60)
            jam, menit = divmod(menit, 60)
            jam = str(jam).zfill(2)
            menit = str(menit).zfill(2)
            detik = str(detik).zfill(2)
            print(f"Waiting until {jam}:{menit}:{detik} ", flush=True, end="\r")
            t -= 1
            await asyncio.sleep(1)  # Mengganti time.sleep(1) dengan await asyncio.sleep(1)
        print(" " * (len(f"Waiting until {jam}:{menit}:{detik} ") + 2), flush=True, end="\r")

    @staticmethod
    async def http(self, url: str, headers: dict, data=None):
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    if data is None:
                        headers["content-length"] = "0"
                        async with session.get(url, headers=headers) as response:
                            res_text = await response.text()
                            with open(".http_request.log", "a") as log_file:
                                log_file.write("sukses first step" + "\n")
                            return response
                    else:
                        data = json.dumps(data, separators=(",", ":"))
                        headers["content-length"] = str(len(data))
                        async with session.post(url, headers=headers, data=data) as response:
                            res_text = await response.text()

                            with open(".http_request.log", "a") as log_file:
                                log_file.write(res_text + "\n")
                            return response

            except aiohttp.ClientConnectionError as e:
                await app.log(f"{merah}connection error: {e}!")
            except aiohttp.ClientTimeout as e:
                await app.log(f"{merah}connection timeout: {e}!")
            except aiohttp.ClientResponseError as e:
                await app.log(f"{merah}response error: {e}!")
            except Exception as e:
                await app.log(f"{merah}unexpected error: {e}!")
            await asyncio.sleep(1)  # Add a small delay before retrying

    def __init__(self):
        self.sessions = {}
        self.cookie = None
        self.me = None
        self.peer = "FirstGrow_bot"
        self.DEFAULT_APIID = 6
        self.DEFAULT_APIHASH = 'eb06d4abfb49dc3eeb1aeb98ae0f581e'
        self.tap = 1
        self.limit_coin = 1
        self.repeat_tap = 1
        self.start_sending = False
        self.base_url = "tgames-mrfirst.bcsocial.net"
        self.base_headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
            "content-type": "application/json",
            "host": "tgames-mrfirst.bcsocial.net",
            "origin": "https://tgames-mrfirst.bcsocial.net",
            "x-requested-with": "org.telegram.messenger",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://tgames-mrfirst.bcsocial.net/",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en,en-US;q=0.9",
        }
        self.ws_headers = {
            "Host": "tgames-mrfirst.bcsocial.net",
            "Connection": "Upgrade",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
            "Upgrade": "websocket",
            "Origin": "https://tgames-mrfirst.bcsocial.net",
            "Sec-WebSocket-Version": "13",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en,en-US;q=0.9",
            "Cookie": self.cookie,
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits"
        }
        self.ws = None  # Menyimpan referensi ke WebSocket
        self.sending_task = None  # Menyimpan referensi task pengiriman pesan
        self.get_me_task = None  # Menyimpan referensi task get_me

    async def log(self, message):
        year, mon, day, hour, minute, second, _, _, _ = time.localtime()
        mon = str(mon).zfill(2)
        hour = str(hour).zfill(2)
        minute = str(minute).zfill(2)
        second = str(second).zfill(2)
        print(f"{kuning}[{year}-{mon}-{day} {hour}:{minute}:{second}] {putih}[{message}]")

    async def telegram_login(self, phone, config: Config, return_data=False):
        gemod = GeMod()
        session_path = "session"
        if not os.path.exists(session_path):
            os.makedirs(session_path)

        model, system_version = gemod.generate_model()

        # Membuat client Telegram asinkron
        client = TelegramClient(
            f"{session_path}/{phone}",
            api_id=config.api_id,
            api_hash=config.api_hash,
            device_model=model,
            app_version="10.12.0 (4710)",
            system_lang_code="en-US",
            system_version=system_version,
            lang_code="us",
        )

        # Asynchronously connect to Telegram client
        await client.connect()

        # Cek apakah user sudah terotorisasi
        if not await client.is_user_authorized():
            try:
                # Send code request asynchronously
                res = await client.send_code_request(phone)
                code = input("Input login code: ")
                # Sign in asynchronously
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                # Handle 2FA password asynchronously
                password_2fa = input("Input password 2FA: ")
                await client.sign_in(password=password_2fa)

        # Mendapatkan informasi akun setelah login
        me = await client.get_me()
        first_name = me.first_name
        last_name = me.last_name

        # Logging jika tidak meminta data untuk dikembalikan
        if not return_data:
            await app.log(f"{hijau}Login as {putih}{first_name} {last_name}")

        res = None
        if return_data:
            # Request WebView secara asinkron
            _res = await client(
                RequestWebViewRequest(
                    peer=self.peer,
                    bot=self.peer,
                    from_bot_menu=False,
                    url="https://tgames-mrfirst.bcsocial.net",
                    platform="Android",
                )
            )
            # Extract data dari URL
            res = _res.url.split("#tgWebAppData=")[1]

        # Disconnect client setelah selesai
        if client.is_connected():
            await client.disconnect()

        return res if res is not None else None

    async def handle_session(self, session, config):
        while True:
            print("~" * 50)
            file_name = os.path.basename(session)
            file_name_without_ext = os.path.splitext(file_name)[0]
            self.me = file_name_without_ext

            await self.log(f"Handling session: {self.me}")
            phone = Path(session).stem

            data_telegram = await self.telegram_login(phone, config, return_data=True)
            if data_telegram:
                res_parser = self.data_parsing(data_telegram)
                data_login = self.gen_data_login(res_parser)
                res_login = await self.login(data_login)
                res_me = await self.get_me()
                ci_session_cookie = self.get_cookie_value(self.cookie, 'ci_session')
                ws_url = f"wss://tgames-mrfirst.bcsocial.net/ws?sessionId={ci_session_cookie}"

                await self.ws_connection(ws_url)

                # Tutup koneksi WebSocket
                await self.close_ws()
                await app.log(f"{kuning}Tutup WS!")

                # Reset data dan tunggu sebelum memulai ulang
                await asyncio.sleep(2)  # Tunggu sebentar sebelum memulai ulang
                await app.log(f"{hijau}Mulai ulang sistem!")

    async def start_bot(self, config):
        # Proses async untuk menangani bot
        while True:
            sessions = glob("session/*.session")  # Mengambil semua sesi
            if len(sessions) == 0:
                await app.log("0 account detected!")
                await app.log("Add an account first or copy your available session to the session folder")
                sys.exit()

            total_account = len(sessions)
            await app.log(f'Account detected: {total_account}')

            tasks = []
            for session in sessions:
                tasks.append(self.handle_session(session, config))

            # Run all tasks asynchronously
            await asyncio.gather(*tasks)
            break  # Remove the break if you want this to run indefinitely

    async def main_async(self):
        banner = f"""
    {hijau}AUTO TAP-TAP FOR {putih}BEBEKTOD {hijau}/ {putih}FirstDuck_bot
    
    {hijau}By: {putih}t.me/AkasakaID
    {hijau}Github: {putih}@AkasakaID
        """
        while True:
            arg = sys.argv
            if "noclear" not in arg:
                os.system("cls" if os.name == "nt" else "clear")
            print(banner)

            # Menggunakan konteks manajer untuk membaca file
            with open("config.json", "r") as file:
                config = json.load(file)

            cfg = Config(config["api_id"], config["api_hash"])
            if not cfg.api_id:
                cfg.api_id = self.DEFAULT_APIID
            if not cfg.api_hash:
                cfg.api_hash = self.DEFAULT_APIHASH

            print(
                """
    1. Create Session
    2. Start Bot
                """
            )
            choice = input("input number : ")
            if not choice:
                await app.log(f"{merah}you must input number !")
                sys.exit()

            if choice == "1":
                phone = input("input telegram phone number : ")
                await self.telegram_login(phone, cfg)
                input("press enter to continue")
                continue

            if choice == "2":
                # Memulai bot secara asinkron untuk menangani beberapa akun
                await self.start_bot(cfg)
                pass

    async def get_me(self):
        url = "https://tgames-mrfirst.bcsocial.net/panel/users/getUser"
        headers = self.base_headers.copy()
        headers["Cookie"] = self.cookie
        data = json.dumps({})
        headers["Content-Length"] = str(len(data))

        res = await self.http(self, url, headers, data)  # Pastikan menggunakan await

        # Pastikan kamu mendapatkan teks dari respons asinkron
        res_text = await res.text()
        if "please login" in res_text:
            return False

        # Pastikan kamu mendapatkan JSON dari respons asinkron
        res_json = await res.json()
        balance = res_json["data"]["balance"]
        next_claim = res_json["data"]["nextClaimTime"]
        level = res_json["data"]["level"]

        await app.log(
            f"{self.me} | {putih}level : {hijau}{level} {biru}| {putih}balance : {hijau}{balance}"
        )

    def get_cookie_value(self, cookie_string, key):
        # Menggunakan regex untuk mengekstrak nilai cookie berdasarkan key
        match = re.search(rf'{key}=([^;]+)', cookie_string)
        return match.group(1) if match else None

    async def ws_connection(self, ws_url):
        ws_headers = {
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36"
        }

        # Inisialisasi WebSocket
        async def connect_and_listen():
            async with aiohttp.ClientSession(headers=ws_headers) as session:
                async with session.ws_connect(ws_url) as ws:
                    self.ws = ws
                    await self.log("WebSocket connection established")

                    self.get_me_task = asyncio.create_task(self.periodic_get_me())

                    try:
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self.handle_message(ws, msg.data)
                            elif msg.type == aiohttp.WSMsgType.CLOSED:
                                await self.log("WebSocket connection closed")
                                break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                await self.log("WebSocket error occurred")
                                break
                    except Exception as e:
                        await self.log(f"WebSocket error: {e}")
                    finally:
                        await self.log("WebSocket connection ended")

        try:
            # Batasi waktu koneksi WebSocket dengan timeout
            await self.log(f"{merah}WebSocket akan reset setiap 28 menit")
            await asyncio.wait_for(connect_and_listen(), timeout=1600)
        except asyncio.TimeoutError:
            await self.log(f"{merah}Koneksi WebSocket ditutup setelah 28 menit")

    async def handle_message(self, ws, message):
        # Handle incoming WebSocket message

        # Check message and respond accordingly
        if message == "#1":
            await ws.send_str("#2")  # Send #2 as a string

            # Mulai pengiriman pesan setelah mengirim #2
            if self.sending_task is None or self.sending_task.done():
                self.sending_task = asyncio.create_task(self.send_repeated_messages())

    async def send_repeated_messages(self):
        await app.log(
            f"{self.me} | {kuning}Mengirim Tap {self.repeat_tap * 20}"
        )
        start_sending = True
        while start_sending:
            for i in range(20):  # Mengirim 20 kali
                message = {
                    "action": "tap",
                    "data": {
                        "value": self.repeat_tap
                    }
                }
                if self.ws:
                    await self.ws.send_str(json.dumps(message))
                else:
                    await self.log("WebSocket is not connected")
                    await app.log(
                        f"{self.me} | {merah}WebSocket is not connected"
                    )
                    break
                await asyncio.sleep(1)  # Delay 1 detik antara pengiriman pesan

            # Jika pengiriman selesai, hentikan loop
            start_sending = False
            await app.log(
                f"{self.me} | {hijau}Sukses Send tap {self.repeat_tap * 20}"
            )

    async def periodic_get_me(self):
        while True:
            await self.get_me()
            await asyncio.sleep(30)  # Tunggu 30 detik sebelum panggil lagi

    async def close_ws(self):
        if self.ws:
            await self.ws.close()
            await self.log("WebSocket connection closed.")
            self.ws = None  # Reset referensi WebSocket

        if self.get_me_task:
            self.get_me_task.cancel()

    async def bypass_captcha(self, data_captcha):
        captcha = data_captcha.replace("=", "")
        try:
            result = eval(captcha)  # Pastikan data yang diterima aman
        except Exception as e:
            await app.log(
                f"{self.me} | {merah}failed to evaluate captcha expression: {e}"
            )
            return

        url = "https://tgames-duck.bcsocial.net/panel/users/verifyCapcha"
        headers = self.base_headers.copy()
        headers["Cookie"] = self.cookie
        data = json.dumps({"code": result})
        headers["Content-Length"] = str(len(data))

        res = await self.http(url, headers, data)  # Pastikan menggunakan await

        res_text = await res.text()  # Mendapatkan teks dari respons asinkron
        if "ok" in res_text:
            await app.log(
                f"{self.me} | {hijau}success bypass captcha !"
            )

    async def login(self, data):
        first_url = "https://tgames-mrfirst.bcsocial.net/"
        login_url = "https://tgames-mrfirst.bcsocial.net/panel/users/login"

        async with aiohttp.ClientSession() as session:
            # Step 1: GET request to firstUrl to get cookies
            async with session.get(first_url) as get_response:
                cookies = get_response.cookies  # Get cookies from the response

                # Extract __cf_bm cookie
                cf_bm_cookie = cookies.get("__cf_bm")

                # Prepare headers and cookie
                _headers = self.base_headers.copy()
                if cf_bm_cookie:
                    cookie_header = f"__cf_bm={cf_bm_cookie.value}"
                    _headers['Cookie'] = cookie_header

                # Prepare data for the POST request
                data = json.dumps(data, separators=(",", ":"))

                # Step 2: POST request to login
                async with session.post(login_url, headers=_headers, data=data) as post_response:
                    res_text = await post_response.text()

                    if post_response.status == 200:
                        await app.log(
                            f"{self.me} | {hijau}Login successful!"
                        )

                        # Parse the response as JSON
                        res_json = await post_response.json()

                        # Correctly handle the cookies
                        string_cookie = ""
                        for key, cookie in post_response.cookies.items():
                            string_cookie += f"{key}={cookie.value}; "
                        self.cookie = string_cookie.rstrip("; ")  # Remove the last semicolon and space

                        # Extract user data from the JSON response
                        data = res_json.get("data", {})
                        balance = data.get("balance")
                        next_claim = data.get("nextClaimTime")
                        first_name = data.get("firstName")
                        last_name = data.get("lastName")
                        level = data.get("level")
                        self.tap = data.get("earnByTap")
                        self.limit_coin = data.get("limitCoinValue")
                        self.repeat_tap = await ensure_even_and_divide(self.limit_coin)
                        await app.log(
                            f"{self.me} | {putih}level : {hijau}{level} {biru}| {putih}balance : {hijau}{balance}"
                        )
                        await app.log(
                            f"{self.me} | {hijau}Energy {self.limit_coin}"
                        )

                        # Check for captcha
                        if "captcha" in data.keys():
                            captcha_value = data.get("captcha")
                            if captcha_value:
                                await app.log(
                                    f"{self.me} | {kuning}captcha detected!"
                                )
                                await self.bypass_captcha(captcha_value)

                    else:
                        await app.log(
                            f"{self.me} | {merah}Login failed!"
                        )

        # if res.status != 200:
        #     await app.log(f"{kuning}need the latest data to log in,")
        #     await app.log(
        #         f"{kuning}please retrieve the latest data and update the data file"
        #     )
        #     sys.exit()
        #
        # return res
        #


if __name__ == "__main__":
    try:
        app = BayiPetir()
        asyncio.run(app.main_async())
    except KeyboardInterrupt:
        sys.exit()

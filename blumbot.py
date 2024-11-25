import sys, os, subprocess, pyautogui, time, random
from termcolor import colored
from pynput import keyboard
from pynput.mouse import Button, Controller

mouse = Controller()
time.sleep(0.5)

white = '\033[1;97m'
red = '\033[1;91m'
green = '\033[1;92m'
yellow = '\033[1m\033[93m'
blue = '\033[1;94m'
reset = '\033[0m'
whitered = '\033[97m\033[41m'
whitegreen = '\033[97m\033[42m'
redgreen = '\033[1;91m\033[42m'

# ------------------ FUNCTIONS ------------------
def click(x, y):
    mouse.position = (x, y + random.randint(1, 3))
    mouse.press(Button.left)
    mouse.release(Button.left)

def find_and_activate_window(window_name, messages):
    platform = sys.platform
    window_rect = None

    if platform == "win32":
        import pygetwindow as gw
        # Finding windows with a title
        windows = gw.getWindowsWithTitle(window_name)
        if windows:
            telegram_window = windows[0]
            window_rect = (
                telegram_window.left, telegram_window.top, telegram_window.width, telegram_window.height
            )
            try:
                telegram_window.activate()
            except:
                telegram_window.minimize()
                telegram_window.restore()

    elif platform == "darwin":
        # AppleScript for Mac OS window activation
        script = f"""
        tell application "System Events"
            set winList to every window of every process whose name is "{window_name}"
            if (count of winList) > 0 then
                set frontmost of first item of winList to true
                return properties of window 1 of process "{window_name}"
            end if
        end tell
        """
        process = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        output = process.stdout.strip()
        if "window" in output:
            pass

    elif platform.startswith("linux"):
        try:
            # Using wmctrl and xwininfo for get window info in Linux
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if window_name in line:
                    window_id = line.split(None, 1)[0]
                    # Window activation
                    subprocess.run(['wmctrl', '-i', '-a', window_id])

                    # Window size request
                    win_info = subprocess.run(['xwininfo', '-id', window_id], capture_output=True, text=True).stdout
                    for info_line in win_info.splitlines():
                        if "Absolute upper-left X" in info_line:
                            x = int(info_line.split(":")[1].strip())
                        elif "Absolute upper-left Y" in info_line:
                            y = int(info_line.split(":")[1].strip())
                        elif "Width" in info_line:
                            width = int(info_line.split(":")[1].strip())
                        elif "Height" in info_line:
                            height = int(info_line.split(":")[1].strip())
                    window_rect = (x, y, width, height)
                    break
        except FileNotFoundError:
            print(messages["wmctrl_xwininfo_err_msg"])
    
    return window_rect

def take_screenshot(window_rect, messages):
    if window_rect:
        scrn = pyautogui.screenshot(region=window_rect)
        scrn.save("screenshot.png")
    else:
        print(messages["fail_capture_msg"])

    return scrn

# Инициализация переменных
paused = False
def on_press(key):
    global paused
    try:
        if key.char.lower() == 'k':  # Используем char.lower() чтобы обрабатывать и 'k', и 'K'
            paused = not paused
            if paused:
                print(messages["pause_message"])
            else:
                print(messages["continue_message"])
            time.sleep(0.2)  # Исключаем повторное нажатие
    except AttributeError:
        # В случае, если нажатая клавиша не имеет атрибута char, просто пропускаем
        pass

def set_language(language_choice):
   if language_choice == 1:
       return {
           "wmctrl_xwininfo_err_msg": f"{white}wmctrl or xwininfo is not installed. Please install them using your package manager{reset}",
           "fail_capture_msg": f"{white}Failed to capture window region{reset}",
           "close_bot_msg": f"{white}The bot was closed{reset}",
           "pause_message": f"{white}Paused",
           "continue_message": f"{white}Continuing",
           "window_input": f"\n{white} [?] | Enter Window {green}(1 - TelegramDesktop){white}: {reset}",
           "window_not_found": f"{white} [>] | Your Window - {{}} {yellow}not found!{reset}",
           "window_found": f"{green} [>] | Window found - {{}}\n{green} Now bot working... {white}Press {yellow}'K'{white} on the keyboard to pause.{reset}",
           "pause_message": f"{blue} Bot paused...\n{white} Press {yellow}'K'{white} again on the keyboard to continue{reset}",
           "continue_message": f"{blue} Bot continue working...{reset}",
           "adv_msg": f"{blue}Make sure that you using app {{}} (not Telegram Web).\nAnd your Blum bot is opened in {{}}{reset}"
       }
   elif language_choice == 2:
       return {
           "wmctrl_xwininfo_err_msg": f"{white}wmctrl или xwininfo не установлены. Установите их через пакетный менеджер.{reset}",
           "fail_capture_msg": f"{white}Не могу найти окно для захвата{reset}",
           "close_bot_msg": "Бот был закрыт",
           "pause_message": "Пауза",
           "continue_message": "Продолжаю",
           "window_input": f"\n{white} [?] | Введите окно {green}(1 - TelegramDesktop){white}: {reset}",
           "window_not_found": f"{white} [>] | Окно - {{}} {yellow}не найдено!{reset}",
           "window_found": f"{green} [>] | Окно найдено - {{}}\n{green} Бот работает... {white}Нажмите кнопку {yellow}'K'{white} чтобы продолжить{reset}",
           "pause_message": f"{blue} Бот приостановлен...\n{white} Нажмите кнопку {yellow}'K'{white} чтобы продолжить{reset}",
           "continue_message": f"{blue} Бот продолжает работу...{reset}",
           "adv_msg": f"Убедитесь, что вы используете приложение {{}} (не Telegram Web).\nИ что Blum бот открыт в вашем {{}}{reset}"
       }

def coosing_language():
    while True:
        try:
            language_choice = int(input(f"\n  {white}blum.bot@main:~# {reset}"))
            if language_choice in [1, 2, 3]:
                break
            else:
                print(f"{red} Yo bro wrong choose. You can input {yellow}1 {red}or {yellow}2{red}.{reset}")
        except ValueError:
            print(f" {red}What??? your input not valid. Please enter number {yellow}1 {red} or {yellow}2 {red}bro.{reset}")

    return language_choice

def print_welcome():
    print(f"""{green}
      {green}|      |                         {yellow}  |             |   
      {green}__ \\   |  |   |  __ `__ \\        {yellow}  __ \\    _ \\   __| 
      {green}|   |  |  |   |  |   |   | {red}_____|{yellow}  |   |  (   |  |   
      {green}_.__/  _| \\__,_| _|  _|  _|       {yellow} _.__/  \\___/  \\__| {reset}
    """)
    print(f" {whitegreen}Contact on telegram: @rus_99_pk{reset}")
    print(f" {yellow}Donations USDT (TRC20):{white} TLX57npAx31fXsxvpe2ZAMfd71de6EJSbE{reset}")
    print(f" {yellow}Donations USDT (TON):{white} UQBmCrZaRPAW1KQL02B_J3F2JqquahDcA2KOrOWuoCH8mVcY{reset}")
    print()
    print(colored("  ...:::: CHOOSE LANGUAGE ::::...", 'light_cyan'))
    print(colored("  [ ", 'white') + colored("1 ", 'light_green') + colored("] ", 'white') + colored("English", 'light_yellow'))
    print(colored("  [ ", 'white') + colored("2 ", 'light_green') + colored("] ", 'white') + colored("Русский", 'light_yellow'))

# ------------------ MAIN ------------------
print_welcome()
language_choice = coosing_language()
messages = set_language(language_choice)

while True:
    window_name = input(messages["window_input"])

    if window_name == '1':
        window_name = "TelegramDesktop"
        break
    elif window_name == '2':
        window_name = "KotatogramDesktop"
        break
    else:
        continue

if not find_and_activate_window(window_name, messages):
    print(messages["window_not_found"].format(window_name))
    print(messages["adv_msg"].format(window_name, window_name))
else:
    print(messages["window_found"].format(window_name))
    paused = False

    # Running listner
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    # Main application circle
    try:
        while True:
            if paused:
                continue
            window_rect = find_and_activate_window(window_name, messages)
            try:
                scrn = take_screenshot(window_rect, messages)
            except UnboundLocalError:
                print (messages["close_bot_msg"])
                os._exit(0)
            
            width, height = scrn.size
            pixel_found = False

            if pixel_found:
                break

            for x in range(0, width, 20):
                for y in range(0, height, 20):
                    r, g, b = scrn.getpixel((x, y))
                    if (b in range(0, 125)) and (r in range(102, 220)) and (g in range(200, 255)):
                        screen_x = window_rect[0] + x
                        screen_y = window_rect[1] + y
                        click(screen_x + 4, screen_y)
                        time.sleep(0.001)
                        pixel_found = True
                        break
            time.sleep(0.1)
    except KeyboardInterrupt:
        # For correct user break
        pass
    finally:
        listener.stop()
import sys, os, subprocess, pyautogui, time, random
from pynput import keyboard
from pynput.mouse import Button, Controller

mouse = Controller()
paused = False

white = '\033[1;97m'
red = '\033[1;91m'
green = '\033[1;92m'
yellow = '\033[1m\033[93m'
blue = '\033[1;94m'
reset = '\033[0m'
whitered = '\033[97m\033[41m'
whitegreen = '\033[97m\033[42m'
redgreen = '\033[1;91m\033[42m'

def print_welcome():
    print(f"""{green}
      {green}|      |                         {yellow}  |             |   
      {green}__ \\   |  |   |  __ `__ \\        {yellow}  __ \\    _ \\   __| 
      {green}|   |  |  |   |  |   |   | {red}_____|{yellow}  |   |  (   |  |   
      {green}_.__/  _| \\__,_| _|  _|  _|       {yellow} _.__/  \\___/  \\__| {reset}
    """)
    print(f" {whitegreen}Contact on telegram: @rus_99_pk{reset}")
    print(f" {yellow}Donations USDT (TRC20):{white} TLX57npAx31fXsxvpe2ZAMfd71de6EJSbE{reset}")
    print(f" {yellow}Donations USDT (TON):{white} UQBmCrZaRPAW1KQL02B_J3F2JqquahDcA2KOrOWuoCH8mVcY{reset}\n")
    print("Starting...")
    time.sleep(2)

def click(x, y):
    mouse.position = (x, y)
    mouse.press(Button.left)
    mouse.release(Button.left)

def take_screenshot(window_rect):
    if window_rect:
        scrn = pyautogui.screenshot(region=window_rect)
        return scrn
    else:
        print("Failed to capture window region")
        return None

def find_and_activate_window(window_name):
    platform = sys.platform
    window_rect = None

    if platform == "win32":
        import pygetwindow as gw
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

    elif platform.startswith("linux"):
        try:
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if window_name in line:
                    window_id = line.split(None, 1)[0]
                    subprocess.run(['wmctrl', '-i', '-a', window_id])

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
            print("wmctrl or xwininfo is not installed.")

    return window_rect

def is_color_in_range(r, g, b, color_ranges, tolerance):
    return any(
        (r in range(color[0] - tolerance, color[0] + tolerance + 1)) and
        (g in range(color[1] - tolerance, color[1] + tolerance + 1)) and
        (b in range(color[2] - tolerance, color[2] + tolerance + 1))
        for color in color_ranges
    )

def on_press(key):
    global paused
    if key == keyboard.KeyCode(char='k'):  # Use 'k' to pause/resume
        paused = not paused
        state = "paused" if paused else "resumed"
        print(f"Bot {state}")

def main_loop(window_name):
    window_rect = find_and_activate_window(window_name)
    while not window_rect:
        print(f"Window '{window_name}' not found. Retrying in 1 second...")
        time.sleep(1)
        window_rect = find_and_activate_window(window_name)

    print(f"Window '{window_name}' activated. Starting the bot...")
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    target_colors = [(253, 124, 142), (60, 211, 0), (130, 220, 233)]
    avoid_colors = [(208, 208, 208), (139, 130, 130)]
    tolerance = 30
    
    try:
        while True:
            if paused:
                continue  # Skip processing if paused

            scrn = take_screenshot(window_rect)
            if scrn is None:
                break

            width, height = scrn.size
            found_static_color = False

            for x in range(0, width, 5):  # Reduced step size for more detailed checks
                for y in range(0, height, 5):
                    r, g, b = scrn.getpixel((x, y))
                    if is_color_in_range(r, g, b, target_colors, tolerance):
                        if not is_color_in_range(r, g, b, avoid_colors, tolerance):
                            screen_x = window_rect[0] + x
                            screen_y = window_rect[1] + y
                            print(f"Clicking on: {screen_x}, {screen_y}")
                            click(screen_x, screen_y)
                            found_static_color = (r == 253 and g == 124 and b == 142)
                            if found_static_color:
                                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Bot stopped manually.")
    finally:
        listener.stop()
        print("Bot has stopped.")

# Example usage
if __name__ == "__main__":
    print_welcome()
    window_name_choice = "Mini App: Blum"  # Change to your required window name
    main_loop(window_name_choice)
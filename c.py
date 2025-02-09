import pysrt
import time
import os
import re
from datetime import timedelta
from colorama import init, Fore, Style
import wcwidth
import threading
import sys


def remove_ansi_escape(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def clear_screen():
    print("\033[H\033[J", end="")

def move_cursor(x, y):
    print(f"\033[{y};{x}H", end="")


def display_karaoke_subtitles(subtitle_file, stop_event, karaoke_lines_count, max_height, print_lock):
    init(autoreset=True)
    terminal_width = os.get_terminal_size().columns

    try:
        subs = pysrt.open(subtitle_file)
    except (pysrt.exceptions.Error, FileNotFoundError, Exception) as e:
        print(f"Lỗi: {e}")
        return

    def display_buffer(buffer, start_row, max_height, print_lock):
        with print_lock:
            for i, line in enumerate(buffer):
                if start_row + i > max_height:
                    break
                text_without_ansi = remove_ansi_escape(line)
                padding = (terminal_width - wcwidth.wcswidth(text_without_ansi)) // 2
                move_cursor(1, start_row + i)
                print(f"{' ' * padding}{line}{' ' * (terminal_width - padding - wcwidth.wcswidth(text_without_ansi))}", end="")
            print("\033[K", end="")
            if start_row + len(buffer) <= max_height:
                move_cursor(1, start_row + len(buffer))
                print(" " * terminal_width, end="\r")


    def format_completed_line(text):
        return f"{Fore.WHITE}{text}{Style.RESET_ALL}"

    def format_current_line(text, progress):
        highlighted = text[:progress]
        remaining = text[progress:]
        return f"{Fore.GREEN}𝄞 {Style.RESET_ALL}{Fore.CYAN}{highlighted}{Style.RESET_ALL}{remaining}{Fore.RED} ♫{Style.RESET_ALL}"

    def format_next_line(text):
        return f"{Style.DIM}{text}{Style.RESET_ALL}"

    def display_subtitle_karaoke(current_text, duration, completed_lines, next_text=None):
        total_chars = len(current_text)
        if total_chars == 0:
            time.sleep(duration)
            return

        start_time = time.time()

        for i in range(total_chars + 1):
            if stop_event.is_set():
                return None

            current_buffer = []
            for line in completed_lines:
                current_buffer.append(format_completed_line(line))
            current_buffer.append(format_current_line(current_text, i))
            if next_text:
                current_buffer.append(format_next_line(next_text))

            display_buffer(current_buffer, 1, max_height, print_lock)

            elapsed_time = time.time() - start_time
            remaining_time = max(0, duration - elapsed_time)
            if i < total_chars:
                interval = remaining_time / (total_chars - i)
                time.sleep(interval)

        return current_text

    completed_lines = []
    for i, sub in enumerate(subs):
        start_time = timedelta(hours=sub.start.hours, minutes=sub.start.minutes,
                             seconds=sub.start.seconds, milliseconds=sub.start.milliseconds)
        end_time = timedelta(hours=sub.end.hours, minutes=sub.end.minutes,
                           seconds=sub.end.seconds, milliseconds=sub.end.milliseconds)
        duration = (end_time - start_time).total_seconds()

        if i > 0:
            prev_end = timedelta(hours=subs[i-1].end.hours, minutes=subs[i-1].end.minutes,
                               seconds=subs[i-1].end.seconds, milliseconds=subs[i-1].end.milliseconds)
            delay = (start_time - prev_end).total_seconds()
            if delay > 0:
                delay_start = time.time()
                while time.time() - delay_start < delay:
                    if stop_event.is_set():
                        return
                    time.sleep(0.1)

        current_text = sub.text
        next_text = subs[i + 1].text if i + 1 < len(subs) else None
        display_lines = completed_lines[-3:] if i>2 else completed_lines[-i:]


        completed_text = display_subtitle_karaoke(current_text, duration, display_lines, next_text)
        if completed_text is None:
            break
        completed_lines.append(completed_text)
        if len(completed_lines) > karaoke_lines_count:
            completed_lines.pop(0)



def display_progress_bar(song_title, total_duration, stop_event, print_lock, bar_length=40, icons="⏮  ▶  ⏭  🔁", start_at=0):  
    def format_time(seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def progress_bar(current, total, bar_length, song_title, icons):
        terminal_width = os.get_terminal_size().columns
        height = os.get_terminal_size().lines
        progress_y = height - 3

        fraction = current / total
        filled_length = int(round(bar_length * fraction))
        pointer = '●'
        bar = ('\033[95m' + '─' * filled_length + pointer + '\033[0m'
               if filled_length < bar_length else '\033[95m' + '─' * filled_length + '\033[0m')
        remaining = '\033[37m' + '─' * (bar_length - filled_length - (1 if filled_length < bar_length else 0)) + '\033[0m'

        current_time_str = format_time(current)
        total_time_str = format_time(total)

        with print_lock:
            # Title
            title_padding = (terminal_width - len(song_title)) // 2
            move_cursor(1, progress_y - 2)
            print(" " * title_padding + f"\033[95m{song_title}\033[0m" + " " * (terminal_width - title_padding - len(song_title)))

            # Progress Bar
            progress_line = f'{current_time_str} {bar}{remaining} {total_time_str}'
            padding = (terminal_width - len(remove_ansi_escape(progress_line))) // 2
            move_cursor(1, progress_y - 1)
            print(f'{" " * padding}{progress_line}{" " * (terminal_width - padding - len(remove_ansi_escape(progress_line)))}', end="")

            # Icons
            icons_padding = (terminal_width - len(icons)) // 2
            move_cursor(1, progress_y)
            print(" " * icons_padding + icons + " " * (terminal_width - icons_padding - len(icons)), flush=True)

    for i in range(start_at, total_duration + 1):  
        if stop_event.is_set():
            break
        progress_bar(i, total_duration, bar_length, song_title, icons)

        wait_start = time.time()
        while time.time() - wait_start < 1:
          if stop_event.is_set(): return
          time.sleep(0.1)

if __name__ == "__main__":
    stop_event = threading.Event()
    print_lock = threading.Lock()

    terminal_height = os.get_terminal_size().lines
    karaoke_lines = 5
    progress_bar_lines = 3
    karaoke_height = terminal_height - progress_bar_lines - 1

    thread1 = threading.Thread(target=display_karaoke_subtitles, args=("test.srt", stop_event, karaoke_lines, karaoke_height, print_lock))
    thread2 = threading.Thread(target=display_progress_bar, args=("Dù cho tận thế - Erik", 300, stop_event, print_lock, 120, "⏮  ▶  ⏭  🔁", 47))  # start_at=47

    thread1.start()
    thread2.start()

    try:
        while thread1.is_alive() and thread2.is_alive():
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nhehe")
        stop_event.set()

    finally:
        thread1.join()
        thread2.join()
        clear_screen()
        print("Kết thúc")
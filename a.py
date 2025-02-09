import pysrt
import time
import os
import re
from datetime import timedelta
from colorama import init, Fore, Style
import wcwidth

def display_karaoke_subtitles(subtitle_file):
    init(autoreset=True)
    terminal_width = os.get_terminal_size().columns
    
    try:
        subs = pysrt.open(subtitle_file)
    except (pysrt.exceptions.Error, FileNotFoundError, Exception) as e:
        print(f"Lỗi: {e}")
        return

    def remove_ansi_escape(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def display_buffer(buffer):
        print("\033[H\033[J", end="")
        for line in buffer:
            text_without_ansi = remove_ansi_escape(line)
            padding = (terminal_width - wcwidth.wcswidth(text_without_ansi)) // 2
            print(f"{' ' * padding}{line}")

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
            current_buffer = []
            
            # Thêm các dòng đã hoàn thành
            for line in completed_lines:
                current_buffer.append(format_completed_line(line))
            
            # Thêm dòng hiện tại với hiệu ứng karaoke
            current_buffer.append(format_current_line(current_text, i))
            
            # Thêm dòng tiếp theo (nếu có)
            if next_text:
                current_buffer.append(format_next_line(next_text))
            
            display_buffer(current_buffer)
            
            elapsed_time = time.time() - start_time
            remaining_time = max(0, duration - elapsed_time)
            if i < total_chars:
                interval = remaining_time / (total_chars - i)
                time.sleep(interval)
        
        return current_text

    completed_lines = []
    for i, sub in enumerate(subs):
        # Tính thời gian hiển thị
        start_time = timedelta(hours=sub.start.hours, minutes=sub.start.minutes, 
                             seconds=sub.start.seconds, milliseconds=sub.start.milliseconds)
        end_time = timedelta(hours=sub.end.hours, minutes=sub.end.minutes,
                           seconds=sub.end.seconds, milliseconds=sub.end.milliseconds)
        duration = (end_time - start_time).total_seconds()

        # Xử lý delay giữa các dòng
        if i > 0:
            prev_end = timedelta(hours=subs[i-1].end.hours, minutes=subs[i-1].end.minutes,
                               seconds=subs[i-1].end.seconds, milliseconds=subs[i-1].end.milliseconds)
            delay = (start_time - prev_end).total_seconds()
            if delay > 0:
                time.sleep(delay)

        current_text = sub.text
        next_text = subs[i + 1].text if i + 1 < len(subs) else None

        # Logic hiển thị số dòng tăng dần
        if i == 0:
            # Dòng đầu tiên: hiển thị 2 dòng
            display_lines = []
        elif i == 1:
            # Dòng thứ hai: hiển thị 3 dòng
            display_lines = completed_lines[-1:]
        elif i == 2:
            # Dòng thứ ba: hiển thị 4 dòng
            display_lines = completed_lines[-2:]
        else:
            # Từ dòng thứ tư trở đi: hiển thị 5 dòng
            display_lines = completed_lines[-3:]

        # Hiển thị karaoke và cập nhật completed_lines
        completed_text = display_subtitle_karaoke(current_text, duration, display_lines, next_text)
        completed_lines.append(completed_text)

display_karaoke_subtitles('loi.srt')
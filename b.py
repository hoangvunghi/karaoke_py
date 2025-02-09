import time
import os

def display_progress_bar(song_title, total_duration, bar_length=40, icons="⏮  ▶  ⏭  🔁"):
    """
    Hiển thị thanh tiến trình của bài hát với tiêu đề, thời gian và các biểu tượng điều khiển.
    
    :param song_title: Tên bài hát (str)
    :param total_duration: Thời lượng tổng cộng của bài hát (giây) (int)
    :param bar_length: Độ dài của thanh tiến trình (int)
    :param icons: Các biểu tượng điều khiển (str)
    """
    def format_time(seconds):
        """Định dạng thời gian từ giây sang phút:giây."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def progress_bar(current, total, bar_length, song_title="", icons=""):
        """Hiển thị thanh tiến trình."""
        fraction = current / total
        filled_length = int(round(bar_length * fraction))
        pointer = '●'
        bar = ('\033[95m' + '─' * filled_length + pointer + '\033[0m' if filled_length < bar_length else '\033[95m' + '─' * filled_length + '\033[0m')
        remaining = '\033[37m' + '─' * (bar_length - filled_length - (1 if filled_length < bar_length else 0)) + '\033[0m'
        current_time_str = format_time(current)
        total_time_str = format_time(total)
        terminal_width = os.get_terminal_size().columns if os.name != 'nt' else 80

        # Tiêu đề (căn giữa, in 1 lần)
        if current == 0:
            title_padding = (terminal_width - len(song_title)) // 2
            print(" " * title_padding + f"\033[95m{song_title}\033[0m")

        # Thanh tiến trình + thời gian (căn giữa)
        progress_line = f'{current_time_str} {bar}{remaining} {total_time_str}'
        padding = (terminal_width - len(progress_line)) // 2
        print(f'\r{" " * padding}{progress_line}', end='')

    # Chạy thanh tiến trình
    for i in range(total_duration + 1):
        progress_bar(i, total_duration, bar_length, song_title)
        time.sleep(1)
    
    print()  # Xuống dòng sau khi thanh tiến trình hoàn thành

    # In các biểu tượng điều khiển (căn giữa, ở dòng riêng)
    terminal_width = os.get_terminal_size().columns if os.name != 'nt' else 80
    icons_padding = (terminal_width - len(icons)) // 2
    print(" " * icons_padding + icons)

# Gọi hàm với thông tin bài hát
display_progress_bar(
    song_title="Dù Cho Tận Thế - Erik",
    total_duration=233,
    bar_length=40,
    icons="⏮  ▶  ⏭  🔁"
)
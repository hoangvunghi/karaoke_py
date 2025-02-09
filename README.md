# Karaoke Subtitle Display in Terminal

This Python script displays karaoke-style subtitles in the terminal, synchronized with a progress bar.  It's designed to make it easy to follow along with song lyrics, highlighting the currently sung portion of the text.

## Features

*   **Karaoke Highlighting:**  The currently sung word or phrase is highlighted in a different color, providing a visual cue for timing.
*   **Multi-line Display:**  Shows the current line, a few lines of previously sung lyrics, and the next line (if available), giving context.
*   **Progress Bar:** A visual progress bar at the bottom of the terminal shows the song's elapsed time and total duration.
*   **ANSI Escape Codes:** Uses ANSI escape codes for color and cursor positioning, providing a visually appealing display (compatible with most modern terminals).
*   **Threaded Execution:**  The subtitle display and progress bar run in separate threads, ensuring smooth updates and responsiveness.
*   **Error Handling:** Includes basic error handling for subtitle file loading.
*   **Screen Clearing:** Clears the screen before and after displaying the subtitles.
*   **Customizable:**  Allows modification of the number of karaoke lines, progress bar length, control icons, and song/subtitle information via command-line arguments (or by editing the script directly).
* **Character Width Handling:** The `wcwidth` library is used to accurately measure the display width of characters, including wide characters (like those in many Asian languages), ensuring correct alignment and spacing in the terminal.
* **Virtual Environment Support:** Instructions are included for setting up and using a virtual environment.
* **Requirements File:** Dependencies are managed through a `requirements.txt` file.

## Requirements

*   Python 3 (tested with 3.7+)
*   `pysrt`: For parsing SRT subtitle files.
*   `colorama`: For cross-platform colored terminal output.
*   `wcwidth`: For determining character display width.

These dependencies are listed in `requirements.txt` and can be installed using `pip`.

## Setup (with Virtual Environment - Recommended)

It's highly recommended to use a virtual environment to manage dependencies and avoid conflicts with other Python projects.

1.  **Clone the repository (or download the Python script and requirements.txt):**

    ```bash
    git clone https://github.com/hoangvunghi/karaoke_py.git
    cd karaoke_py
    ```

2.  **Create a virtual environment (using `venv`):**

    ```bash
    python3 -m venv venv
    ```

    This creates a directory named `venv` containing the virtual environment.  You can name it something else if you prefer.

3.  **Activate the virtual environment:**

    *   **On Linux/macOS:**

        ```bash
        source venv/bin/activate
        ```

    *   **On Windows (cmd.exe):**

        ```bash
        venv\Scripts\activate
        ```

    After activation, your terminal prompt should change to indicate that the virtual environment is active (e.g., `(venv) $`).

4.  **Install dependencies from `requirements.txt`:**

    ```bash
    pip install -r requirements.txt
    ```

    This command installs the necessary packages (`pysrt`, `colorama`, and `wcwidth`) into your virtual environment.

## Usage

1.  **Make sure your virtual environment is activated (if you used one).**

2.  **Place your SRT subtitle file in the same directory as the script.**  The example script uses `test.srt`.  You can change this in the code.

3.  **Run the script:**

    ```bash
    python c.py
    ```

    *   The script will start displaying the karaoke subtitles and the progress bar.
    *   Press Ctrl+C to interrupt and exit the script.

4.  **Deactivate the virtual environment (when you're finished):**
    ```bash
    deactivate
    ```

## Code Explanation

(The code explanation remains the same as in the previous response.  I've included it here for completeness.)

*   **`remove_ansi_escape(text)`:** Removes ANSI escape codes from a string.  This is used to calculate string lengths correctly for display purposes, ignoring the color codes.

*   **`clear_screen()`:** Clears the terminal screen.

*   **`move_cursor(x, y)`:** Moves the cursor to the specified coordinates (x, y) in the terminal.

*   **`display_karaoke_subtitles(...)`:**  This is the main function for displaying the karaoke subtitles.
    *   It opens and parses the SRT file using `pysrt`.
    *   It uses `colorama` to initialize colored output.
    *   It calculates the center alignment based on the terminal width.
    *   `display_buffer(...)`:  Handles displaying a buffer of lines (completed, current, and next) at a specified row, centered on the screen.
    *   `format_completed_line(...)`, `format_current_line(...)`, `format_next_line(...)`:  These functions format the lines with different colors to indicate their status (completed, current, upcoming).
    *   The main loop iterates through the subtitles, calculating durations and delays.
    *   The inner loop (`display_subtitle_karaoke(...)`) handles the character-by-character highlighting of the current line, creating the karaoke effect.
    *   It uses a `stop_event` (a `threading.Event`) to gracefully exit if Ctrl+C is pressed.
    *   It uses a `print_lock` (a `threading.Lock`) to prevent race conditions when multiple threads are printing to the terminal.

*   **`display_progress_bar(...)`:** This function displays the progress bar.
    *   `format_time(...)`: Formats seconds into a `mm:ss` string.
    *   `progress_bar(...)`:  Draws the progress bar, including the current and total time, a filled bar, and control icons.  It centers the output on the screen.
    *   The loop updates the progress bar every second.

*   **`if __name__ == "__main__":`:** This block executes when the script is run directly.
    *   It creates the `stop_event` and `print_lock`.
    *   It gets the terminal height and calculates sizes for the karaoke and progress bar areas.
    *   It creates and starts the two threads (one for subtitles, one for the progress bar).
    *   It waits for the threads to complete (or for a KeyboardInterrupt).
    *   It cleans up by joining the threads and clearing the screen.

## Customization

*   **Subtitle File:** Change the filename `"test.srt"` in the `display_karaoke_subtitles` function to your subtitle file.
*   **Song Title and Duration:**  Modify the arguments to `display_progress_bar` to match your song's title, total duration (in seconds), control icons, and optional starting time (in seconds).
*   **Karaoke Lines:** Change the `karaoke_lines` variable to adjust the number of displayed karaoke lines.
*   **Progress Bar Length:** Change the `bar_length` parameter in the `display_progress_bar` function call.
*   **Colors:** Modify the `Fore` and `Style` constants from `colorama` to change the colors used for highlighting.

## Improvements and Future Work

*   **Command-Line Arguments:** Add support for command-line arguments to specify the subtitle file, song title, duration, etc., making the script more flexible.  Use `argparse` for this.
*   **Configuration File:**  Allow loading settings from a configuration file (e.g., JSON or YAML).
*   **More Robust Error Handling:** Handle more potential errors, such as invalid SRT file formats or missing files.
*   **Support for Other Subtitle Formats:**  Extend support to other subtitle formats besides SRT (e.g., ASS, VTT).
*   **Pause/Resume/Seek:**  Implement pause, resume, and seek functionality. This could be controlled by key presses and would require more sophisticated synchronization between the threads.
* **Dynamic Resizing:** Handle terminal window resizing. The current code assumes a fixed terminal size; adapting to resizing would require recalculating layout and redrawing.

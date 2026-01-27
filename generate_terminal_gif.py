"""
GitHub Profile Terminal GIF Generator
Based on x0rzavi/github-readme-terminal

Requirements:
    pip install github-readme-terminal python-dotenv pillow

Usage:
    python generate_terminal_gif.py
"""

import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from PIL import Image
import tempfile

# Load .env file BEFORE importing gifos
load_dotenv()

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# Load local TOML config files
with open("gifos_settings.toml", "rb") as f:
    local_settings = tomllib.load(f)

with open("ansi_escape_colors.toml", "rb") as f:
    local_colors = tomllib.load(f)

# Set environment variables from local config before importing gifos
general = local_settings.get("general", {})
files = local_settings.get("files", {})

# General settings - only set string values, gifos doesn't convert types from env vars properly
os.environ["GIFOS_GENERAL_DEBUG"] = str(general.get("debug", False)).lower()
os.environ["GIFOS_GENERAL_CURSOR"] = general.get("cursor", "_")
os.environ["GIFOS_GENERAL_SHOW_CURSOR"] = str(general.get("show_cursor", True)).lower()
os.environ["GIFOS_GENERAL_BLINK_CURSOR"] = str(general.get("blink_cursor", True)).lower()
os.environ["GIFOS_GENERAL_USER_NAME"] = general.get("user_name", "Fynn9563")
os.environ["GIFOS_GENERAL_COLOR_SCHEME"] = general.get("color_scheme", "yoru")

# File settings
os.environ["GIFOS_FILES_FRAME_BASE_NAME"] = files.get("frame_base_name", "frame_")
os.environ["GIFOS_FILES_FRAME_FOLDER_NAME"] = files.get("frame_folder_name", "frames")
os.environ["GIFOS_FILES_OUTPUT_GIF_NAME"] = files.get("output_gif_name", "output")

import gifos
from gifos.utils.load_config import ansi_escape_colors as gifos_colors


def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_bg_color():
    """Get background color from config (local first, then gifos built-in)."""
    scheme = general.get("color_scheme", "yoru")
    # Try local config first, then fall back to gifos built-in colors
    if scheme in local_colors:
        bg_hex = local_colors[scheme].get("default_colors", {}).get("bg", "#0c0e0f")
    else:
        bg_hex = gifos_colors.get(scheme, {}).get("default_colors", {}).get("bg", "#0c0e0f")
    return hex_to_rgb(bg_hex)


def prepare_transparent_image(image_path, bg_color=None):
    """
    Composite a transparent PNG onto the terminal background color.
    This works around gifos not handling alpha channels properly.
    Returns path to the temporary composited image.
    """
    if bg_color is None:
        bg_color = get_bg_color()
    with Image.open(image_path) as img:
        # Ensure image has alpha channel
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Create background with terminal color
        background = Image.new('RGB', img.size, bg_color)

        # Composite the image onto the background using alpha as mask
        background.paste(img, (0, 0), img)

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        background.save(temp_file.name, 'PNG')
        return temp_file.name

# Font files
FONT_FILE_LOGO = "./fonts/vtks-blocketo.regular.ttf"
FONT_FILE_BITMAP = "./fonts/gohufont-uni-14.pil"
FONT_FILE_TRUETYPE = "./fonts/IosevkaTermNerdFont-Bold.ttf"

# Configuration - read from local gifos_settings.toml
USER_NAME = general.get("user_name", "Fynn9563")
DISPLAY_NAME = "fynn"
ROLE = "DevOps & Cloud Engineer"
LOCATION = "Somewhere in the cloud"
TIMEZONE = "Australia/Melbourne"


def main():
    t = gifos.Terminal(750, 500, 15, 15, FONT_FILE_BITMAP, 15)

    # Set custom prompt: fynn@fynn-os ~> (matching the example style)
    t.set_prompt(f"\x1b[92m{DISPLAY_NAME}@fynn-os\x1b[0m \x1b[94m~>\x1b[0m ")

    t.gen_text("", 1, count=20)
    t.toggle_show_cursor(False)
    year_now = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y")
    t.gen_text("FYNN_OS Modular BIOS v4.2.0", 1)
    t.gen_text(f"Copyright (C) {year_now}, \x1b[31mFynn Industries Ltd.\x1b[0m", 2)
    t.gen_text("\x1b[94mGitHub Profile ReadMe Terminal, Rev 9563\x1b[0m", 4)
    t.gen_text("Quantum(tm) GIFCPU - 420Hz", 6)
    t.gen_text(
        "Press \x1b[94mDEL\x1b[0m to enter SETUP, \x1b[94mESC\x1b[0m to cancel Memory Test",
        t.num_rows,
    )
    for i in range(0, 131072, 14336):
        t.delete_row(7)
        if i < 60000:
            t.gen_text(f"Memory Test: {i}", 7, count=2, contin=True)
        else:
            t.gen_text(f"Memory Test: {i}", 7, contin=True)
    t.delete_row(7)
    t.gen_text("Memory Test: 131072K OK", 7, count=10, contin=True)
    t.gen_text("", 11, count=10, contin=True)

    t.clear_frame()
    t.gen_text("Initiating Boot Sequence ", 1, contin=True)
    t.gen_typing_text(".....", 1, contin=True)
    t.gen_text("\x1b[96m", 1, count=0, contin=True)
    t.set_font(FONT_FILE_LOGO, 66)
    os_logo_text = "FYNN OS"
    mid_row = (t.num_rows + 1) // 2
    mid_col = (t.num_cols - len(os_logo_text) + 1) // 2
    effect_lines = gifos.effects.text_scramble_effect_lines(
        os_logo_text, 3, include_special=False
    )
    for i in range(len(effect_lines)):
        t.delete_row(mid_row + 1)
        t.gen_text(effect_lines[i], mid_row + 1, mid_col + 1)

    t.set_font(FONT_FILE_BITMAP, 15)
    t.clear_frame()
    t.clone_frame(5)
    t.toggle_show_cursor(False)
    t.gen_text("\x1b[93mFYNN_OS v4.2.0 (tty1)\x1b[0m", 1, count=5)
    t.gen_text("login: ", 3, count=5)
    t.toggle_show_cursor(True)
    t.gen_typing_text(USER_NAME, 3, contin=True)
    t.gen_text("", 4, count=5)
    t.toggle_show_cursor(False)
    t.gen_text("password: ", 4, count=5)
    t.toggle_show_cursor(True)
    t.gen_typing_text("*********", 4, contin=True)
    t.toggle_show_cursor(False)
    time_now = datetime.now(ZoneInfo(TIMEZONE)).strftime("%a %b %d %I:%M:%S %p %Z %Y")
    t.gen_text(f"Last login: {time_now} on tty1", 6)

    t.gen_prompt(7, count=5)
    prompt_col = t.curr_col
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mclea", 7, contin=True)
    t.delete_row(7, prompt_col)
    t.gen_text("\x1b[92mclear\x1b[0m", 7, count=3, contin=True)

    ignore_repos = []
    git_user_details = gifos.utils.fetch_github_stats(USER_NAME, ignore_repos)
    user_age = gifos.utils.calc_age(10, 11, 1992)  # Birthday: 10/11/1992
    t.clear_frame()
    top_languages = [lang[0] for lang in git_user_details.languages_sorted]
    user_details_lines = f"""
    \x1b[30;101m{DISPLAY_NAME}@GitHub\x1b[0m
    --------------
    \x1b[96mOS:       \x1b[93mArch Linux x86_64\x1b[0m
    \x1b[96mRole:     \x1b[93m{ROLE}\x1b[0m
    \x1b[96mLocation: \x1b[93m{LOCATION}\x1b[0m
    \x1b[96mUptime:   \x1b[93m{user_age.years} years, {user_age.months} months, {user_age.days} days\x1b[0m
    \x1b[96mIDE:      \x1b[93mneovim, VSCode\x1b[0m

    \x1b[30;101mGitHub Stats:\x1b[0m
    --------------
    \x1b[96mUser Rating:  \x1b[93m{git_user_details.user_rank.level}\x1b[0m
    \x1b[96mTotal Stars:  \x1b[93m{git_user_details.total_stargazers}\x1b[0m
    \x1b[96mTotal Commits ({int(year_now) - 1}): \x1b[93m{git_user_details.total_commits_last_year}\x1b[0m
    \x1b[96mTotal PRs:    \x1b[93m{git_user_details.total_pull_requests_made}\x1b[0m
    \x1b[96mMerged PR %:  \x1b[93m{git_user_details.pull_requests_merge_percentage}\x1b[0m
    \x1b[96mContributions:\x1b[93m{git_user_details.total_repo_contributions}\x1b[0m
    \x1b[96mTop Languages:\x1b[0m
    \x1b[93m  {top_languages[0] if len(top_languages) > 0 else ''}\x1b[0m
    \x1b[93m  {top_languages[1] if len(top_languages) > 1 else ''}\x1b[0m
    \x1b[93m  {top_languages[2] if len(top_languages) > 2 else ''}\x1b[0m
    \x1b[93m  {top_languages[3] if len(top_languages) > 3 else ''}\x1b[0m
    \x1b[93m  {top_languages[4] if len(top_languages) > 4 else ''}\x1b[0m
    """
    t.gen_prompt(1)
    prompt_col = t.curr_col
    t.clone_frame(10)
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mfetch.s", 1, contin=True)
    t.delete_row(1, prompt_col)
    t.gen_text("\x1b[92mfetch.sh\x1b[0m", 1, contin=True)
    t.gen_typing_text(f" -u {USER_NAME}", 1, contin=True)

    t.toggle_show_cursor(False)
    # Paste avatar image - pre-composite with background to fix transparency
    bg_color = get_bg_color()
    print(f"Avatar background color: RGB{bg_color}")
    avatar_with_bg = prepare_transparent_image("./icon.png", bg_color)
    t.paste_image(avatar_with_bg, 10, 2, size_multiplier=0.07)
    # Clean up temp file
    os.unlink(avatar_with_bg)
    t.gen_text(user_details_lines, 2, 35, count=5, contin=True)
    t.gen_prompt(t.curr_row)
    t.toggle_show_cursor(True)
    t.gen_typing_text(
        "\x1b[92m# Thanks for stopping by! Have a great day :D",
        t.curr_row,
        contin=True,
    )
    t.gen_text("", t.curr_row, count=120, contin=True)

    # Generate GIF - try ffmpeg first, fall back to Pillow if it fails
    print("Generating GIF...")
    output_file = "output.gif"
    try:
        t.gen_gif()
        # Check if ffmpeg actually created a valid GIF (it may print errors but not raise exception)
        if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
            print("GIF generated with ffmpeg")
        else:
            raise Exception("ffmpeg output missing or too small")
    except Exception as e:
        print(f"ffmpeg failed ({e}), falling back to Pillow...")
        create_gif_from_frames()

    print("\nDone! Generated: output.gif")

    # Update README
    readme_content = """<div align="justify">
<picture>
    <source media="(prefers-color-scheme: dark)" srcset="./output.gif">
    <source media="(prefers-color-scheme: light)" srcset="./output.gif">
    <img alt="fynn-os" src="output.gif">
</picture>
</div>
"""
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("INFO: README.md file generated")


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]


def create_gif_from_frames():
    frames_dir = "frames"
    output_file = "output.gif"
    fps = 15
    frame_duration = int(1000 / fps)

    frame_files = [f for f in os.listdir(frames_dir) if f.endswith('.png')]
    frame_files.sort(key=natural_sort_key)

    if not frame_files:
        print("No frames found!")
        return

    print(f"Found {len(frame_files)} frames, creating GIF at {fps} FPS...")

    frames = []
    for i, filename in enumerate(frame_files):
        filepath = os.path.join(frames_dir, filename)
        img = Image.open(filepath)
        img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
        frames.append(img)
        if (i + 1) % 100 == 0:
            print(f"  Loaded {i + 1}/{len(frame_files)} frames...")

    print("Saving GIF...")
    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=0
    )

    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"  Size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()

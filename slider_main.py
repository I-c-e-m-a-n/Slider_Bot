# Slider modules
import slider_helper as sh
from slider_helper import sendMailSingle


# display windows modules
import tkinter as tk
import customtkinter as ck
from tkinter import *
from PIL import ImageTk, Image

# sounds modules
from gtts import gTTS
from playsound import playsound

# web moduless
import webbrowser as wb
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# threads
import threading
import random as rd

# visual
from slider_visual import SliderVisual

# others
import datetime



print("Slider now active.")

# ---- Loading instance from helper (main controls ticking) ----
loading = sh.Loading()

def schedule_daily_email(gui, news_list, recipient_email):
    """
    Schedule news summaries email for 9:00am local time daily while program is active.
    """
    def task():
        print("Running scheduled news summary send...")
        try:
            sh.send_news_summaries(news_list, recipient_email)
        except Exception as e:
            print("Scheduled email failed:", e)

    def check_time():
        now = datetime.datetime.now()
        # Run at exactly 9:00 AM
        if now.hour == 9 and now.minute == 0 and now.second < 29:
            # Launch in a background thread (non-blocking)
            threading.Thread(target=task, daemon=True).start()
            # Prevent multiple sends in same minute
            gui.root.after(60000, check_time)  # wait 1 min before checking again
        else:
            gui.root.after(1000 * 30, check_time)  # check every 30s

    # Kick off loop
    gui.root.after(1000, check_time)

def main():
    gui = SliderVisual()

    gui.btn_open_mail.configure(
        command=lambda: loading.run_task_with_loading(gui, loading, sh.getMail, gui.open_mail_window)
    )
    gui.btn_open_weather.configure(
        command=lambda: loading.run_task_with_loading(gui, loading, sh.getWeatherCurrent, gui.open_weather_window)
    )

    gui.btn_open_news.configure(
        command=lambda: loading.run_task_with_loading(gui, loading, sh.getNews, gui.open_news_window)
    )

    gui.btn_text_tools.configure(
        command=lambda: loading.run_task_with_loading(gui, loading, sh.summarizeText, gui.open_text_tools_window)
    )

    schedule_daily_email(gui, sh.getNews(), "example@mail.com")

    gui.run()




if __name__ == "__main__":
    main()
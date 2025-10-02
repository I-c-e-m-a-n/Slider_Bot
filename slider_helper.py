### Link for APIs: https://github.com/public-apis/public-apis

### Math
import numpy as np
import pandas as pd
import random as rd
import math as m

### Functionality
import datetime
from datetime import datetime
import time
import copy
import json
import webbrowser
import requests
from PIL import Image
import os
import os.path
import threading
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlparse, parse_qs


### Speech 
# Sound and Speech
from gtts import gTTS
from playsound import playsound


### Language Processing
import nltk
import re
import heapq
from nltk.corpus import stopwords


### GPT
import openai

### Google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import imaplib

### Email
import smtplib
import email
from email import utils
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


############################################################

###CONSTANTS
#Google
GMAIL_USER = 'YOUR EMAIL'
GMAIL_PASS = 'YOUR ACCOUNT PASSWORD'
HELPER_USER = 'ANY ADDITIONAL'

#Stocks https://marketstack.com/dashboard
STOCK_API_KEY = 'YOUR KEY'

#News https://gnews.io/dashboard 
NEWS_API_KEY = "YOUR NEWS KEY"

###HELPERs
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt_tab")
############################################################


class Loading:
    keep_loading = False

    # -------------------------------
    # LOADING FUNCTION
    # -------------------------------
    # uses some apis to collect random texts for loading screens
    def random_loading(self, num):
        while self.keep_loading:
            if not num:
                try:
                    url = "https://api.chucknorris.io/jokes/random"
                    response = requests.get(url)
                    data = response.json()
                    text = data['value']
                    # ret = "Bots know about Chuck Norris too.....\n" + text + "\n"
                    ret = "Chuck Norris: " + text
                except:
                    ret = "You think you would get a loading screen????? lmaoooo" + "\n"
            elif num == 1:
                try:
                    url = "https://corporatebs-generator.sameerkumar.website/"
                    response = requests.get(url)
                    data = response.json()
                    text = data['phrase']
                    # ret = "Random Corporate Bullshit/Buzzwords for your next email :p\n" + text + "\n"
                    ret = "Corporate Buzzwords: " + text
                except:
                    ret = "Entertain yourself broo ....... lmaoooo" + "\n"
            elif num == 2:
                try: 
                    url = "https://techy-api.vercel.app/api/json"
                    response = requests.get(url)
                    data = response.json()
                    text = data['message']
                    # ret = "Wanna sound like a nerd??? Say\n" + "'" + text + "'" + "\n"
                    ret = text
                except:
                    ret = "Yeah I'm bored too, bet I can count to 10 million faster than you tho ....... lmaoooo" + "\n"
            elif num == 3:
                try: 
                    url = "https://api.adviceslip.com/advice"
                    response = requests.get(url)
                    data = response.json()
                    text = data['slip']['advice']
                    # ret = "Heres some Life Advice... From a BOT...\n" + text + "\n"
                    ret = "Life Advice: " + text
                except:
                    ret = "No Fun Fact for you today lmaoooo" + "\n"
            elif num == 4:
                try: 
                    url = "https://api.breakingbadquotes.xyz/v1/quotes"
                    response = requests.get(url)
                    data = response.json()
                    text = data[0]['quote'] + " \n- " + data[0]['author']
                    # ret = "Wanna go cooking??\n" + text + "\n"
                    ret = text + " Breaking Bad"
                except:
                    ret = "What did you expect, a joke? Look in the mirror ....... lmaoooo" + "\n"
            elif num == 5:
                try: 
                    url = "https://api.gameofthronesquotes.xyz/v1/random"
                    response = requests.get(url)
                    data = response.json()
                    text = data['sentence'] + " \n- " + data['character']['name'] + " " + data['character']['house']['name']
                    # ret = "Ice and Fire huh...\n" + text + "\n"
                    ret = text + " Game of Thrones"
                except:
                    ret = "Busy watchin Game of Thrones, wait a min ....... lmaoooo" + "\n"
            else:
                ret = "You look like you're having fun. Thats right, I see you." + "\n"
            # print(ret)
            return ret
    
    def get_random_loading(self, load):
        """
        Ask helper.Loading for one random loading string.
        IMPORTANT: loading_instance.keep_loading must be True to enter the loop in helper.
        """
        try:
            # Ensure helper's while-loop condition is satisfied
            load.keep_loading = True
            msg = load.random_loading(rd.randint(0, 5))
            # Safety fallback if helper returned nothing
            if not msg:
                msg = "Warming up the circuits..."
            return msg
        except Exception as e:
            return f"Loading tip failed: {e}"

    def run_task_with_loading(self, gui, load, task_func, callback):
        """
        1) Creates a loading window in gui
        2) Ticks every 5s -> pulls text from helper.Loading.random_loading()
        3) Runs task_func() in a background thread
        4) On completion -> closes loading window and opens the result window via callback(result)
        """
        loading_win, dynamic_updater, stop_flag = gui.create_loading_window()

        # --- Start ticking immediately (replace "Starting..." right away) ---
        def tick():
            if stop_flag["running"]:
                new_text = load.get_random_loading(load)
                dynamic_updater(new_text)
                gui.root.after(9000, tick)

        tick()

        # --- Background job ---
        def run_job():
            try:
                result = task_func()
            except Exception as e:
                result = [f"Task error: {e}"]
            finally:
                # Stop helper's loop so future calls don't depend on it
                load.keep_loading = False

            def finish():
                stop_flag["running"] = False
                # Close loading window then open the proper result window
                try:
                    loading_win.destroy()
                except Exception:
                    pass
                callback(result)

            gui.root.after(0, finish)

        threading.Thread(target=run_job, daemon=True).start()
    
# -------------------------------
# TIME CONVERSION FUNCTION
# -------------------------------
# converts 24hr time to 12hr time
def to12hr(time_string):
    hour, minute, second = time_string.split(":")
    hour = int(hour)
    if hour == 0:
        return "12:" + minute + " AM"
    elif hour < 12:
        return str(hour) + ":" + minute + " AM"
    elif hour == 12:
        return "12:" + minute + " PM"
    else:
        return str(hour - 12) + ":" + minute + " PM"

# -------------------------------
# TEMP CONVERSION FUNCTION
# -------------------------------
# converts farenheite to celsius
def fahrenheit_to_celsius(temperature):
    celsius = (temperature - 32) * 5 / 9
    return round(celsius, 2)

# -------------------------------
# RANDOM FUNCTION
# -------------------------------
# returns a random integer between the range a and b
def rand(a, b):
    return rd.randint(a, b)


############################################################
    


###MAIN FUNCTIONS

# -------------------------------
# MAIL FUNCTIONS
# -------------------------------
# uses gmail api to send emails
def sendMailSingle(recepient, name, subject, body):
    msg = MIMEMultipart()
    msg['From'] = HELPER_USER
    msg['To'] = recepient
    msg['Subject'] = subject
    mail = ("Hello " + name + ",\n\n" +
            body + 
            "\n\n\n\n\nThis email was sent by Slider Bot.")
    msg.attach(MIMEText(mail, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(HELPER_USER, recepient, msg.as_string())
        print(name,'\'s Email sent successfully!')
    except Exception as e:
        print('Failed to send email. Error:', str(e))
    finally:
        server.quit()
    
    return

# uses gmail api to retrieve personal email mailbox
def getMail():
    """{
  "sender": "john@example.com",
  "name": "John Doe",
  "subject": "Meeting Tomorrow",
  "snippet": "Hi, just reminding you about...",
  "body": "Full message body here...",
  "date": "Tue, 30 Sep 2025 10:00:00 +0000",
  "recipient": "john@example.com"  # for replying
}
"""
    ret = []
    loading = Loading()
    loading.keep_loading = True
    x = threading.Thread(target=Loading.random_loading, args=(loading, 1), daemon=True)
    x.start()

    # Connect to Gmail IMAP server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    print("Getting from mailbox of: " + GMAIL_USER)
    mail.login(GMAIL_USER, GMAIL_PASS)

    mail.select("inbox")

    # Search for unread emails
    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()

    # Get the last 30 unread emails
    last = email_ids[-30:]

    for eid in reversed(last):
        status, msg_data = mail.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                subject = msg["subject"] or "No Subject"
                from_ = msg["from"] or "Unknown Sender"
                date_ = msg["date"] or ""
                to_ = msg["to"] or GMAIL_USER  # fallback recipient

                # Try to extract sender email and name separately
                try:
                    sender_name, sender_email = utils.parseaddr(from_)
                except Exception:
                    sender_name, sender_email = from_, from_

                # Extract message body (text/plain only)
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            try:
                                body = part.get_payload(decode=True).decode(errors="ignore")
                            except Exception:
                                body = ""
                            break
                else:
                    try:
                        body = msg.get_payload(decode=True).decode(errors="ignore")
                    except Exception:
                        body = ""

                # Short snippet preview
                snippet = body.strip().split("\n")[0][:200]

                # Store as dict
                ret.append({
                    "sender": sender_email,
                    "name": sender_name or sender_email,
                    "subject": subject,
                    "snippet": snippet,
                    "body": body,
                    "date": date_,
                    "recipient": sender_email  # reply-to same sender
                })

        # Mark email back as unread
        mail.store(eid, '-FLAGS', '\\Seen')

    mail.close()
    mail.logout()
    loading.keep_loading = False
    return ret

# uses gmail api to send news summaries to desired mailbox
def send_news_summaries(news_list, recipient_email, subject=f"News Summary by Slider Bot at: {str(datetime.now())}"):
    print("sending Email now")
    parts = []
    for a in news_list:
        title = a.get("title", "No Title")
        url = a.get("url", "")
        summary = ""

        try:
            if url:
                article_data = fetchArticle(url)
                if isinstance(article_data, dict):
                    article_text = (
                        article_data.get("content")
                        or article_data.get("body")
                        or article_data.get("text")
                        or ""
                    )
                else:
                    article_text = str(article_data)

                summary = summarizeText(article_text, max_sentences=15)
                summary += f"\n\nWebsite url: {url}\n\n\n\n"
        except Exception as e:
            summary = f"Tokenizer failed: {e}"

        if not summary.strip():
            summary = "No summary available."

        parts.append((title, summary))

    # --- Build HTML only ---
    html_lines = []
    for title, summary in parts:
        html_lines.append(
            f"<div style='margin-bottom:25px;'>"
            f"<b style='font-size:14pt; color:#222;'>{title}</b><br><br>"
            f"<div style='font-size:11pt; white-space:pre-line;'>{summary}</div>"
            f"</div>"
        )

    html_body = "<html><body style='font-family:Arial,sans-serif;'>" + "".join(html_lines) + "</body></html>"

    msg = MIMEMultipart("alternative")
    msg["From"] = HELPER_USER
    msg["To"] = recipient_email
    msg["Subject"] = subject

    # Only attach HTML
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(HELPER_USER, recipient_email, msg.as_string())
        print("News summaries email sent successfully to", recipient_email)
    except Exception as e:
        print("Failed to send email. Error:", str(e))
    finally:
        server.quit()
    
    print("Email sent")


    return "done"


# -------------------------------
# WEATHER FUNCTIONS
# -------------------------------
# uses weather api to return the current weather
def getWeatherCurrent():
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/singapore?unitGroup=us&key=[YOUR KEY HERE]3&contentType=json"
    response = requests.get(url)
    data = response.json()

    alerts = ""
    for item in data["alerts"]:
        alerts += "\n" + str(
            item["event"] + "\n" + item["headline"] + "\n" + item["description"]
        )

    ret = (
        "Alerts: "
        + alerts
        + " \nTime of Measurement: "
        + str(to12hr(data["currentConditions"]["datetime"]))
        + " \nTemperature: "
        + str(fahrenheit_to_celsius(int(data["currentConditions"]["temp"])))
        + "celsius"
        + " \nUV Index: "
        + str(data["currentConditions"]["uvindex"])
        + " \nSunrise Time: "
        + str(to12hr(data["currentConditions"]["sunrise"]))
        + " \nSunset Time: "
        + str(to12hr(data["currentConditions"]["sunset"]))
        + " \nAdditional Information: "
        + str(data["description"])
    )
    return ret

# uses weather api to return weather prediction for the next 10 days
def getWeatherCurrentTen():
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/singapore?unitGroup=us&key=[YOUR KEY HERE]]&contentType=json"
    response = requests.get(url)
    data = response.json()

    ret = []

    for item in data["days"]:
        ret.append(
            (
                "Date: "
                + str(item["datetime"])
                + " \nTemperature: "
                + str(fahrenheit_to_celsius((int(item["temp"]))))
                + " \nUV Index: "
                + str(item["uvindex"])
                + " \nSunrise Time: "
                + str(to12hr(item["sunrise"]))
                + " \nSunset Time: "
                + str(to12hr(item["sunset"]))
                + " \nAdditional Information: "
                + str(item["description"])
            )
        )
    return ret

# -------------------------------
# CALENDER FUNCTION
# -------------------------------
# uses google calender api to retrieve personal calender
def getCalender():
    SERVICE_ACCOUNT_FILE = "Code_Slider/sheets-379102-73e1f035d3f9.json"
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    # Authenticate using service account
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=credentials)

    # Define the time range: now to 30 days from now
    now = datetime.datetime.utcnow().isoformat() + "Z"
    thirty_days = (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat() + "Z"

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            timeMax=thirty_days,
            maxResults=100,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if events:
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
    else:
        print("No events found.")
    
    return

# -------------------------------
# NEWS FUNCTIONS
# -------------------------------
# uses https://gnews.io/dashboard to get news
def getNews():
    BASE_URL = "https://gnews.io/api/v4/top-headlines"
    categories = ["general"]#, "technology", "business", "world"]
    articles = []

    def parse_articles(data):
        for item in data.get("articles", []):
            title = item.get("title", "No Title")
            source = item.get("source", {}).get("name", "Unknown Source")
            desc = item.get("description", "") or ""
            content = item.get("content", "") or ""
            summary = (desc or content)[:250]
            url = item.get("url", "")
            articles.append({
                "title": title,
                "source": source,
                "summary": summary,
                "url": url
            })

    try:
        for country in ['sg']:#, 'us']:
            for category in categories:
                url = f"{BASE_URL}?category={category}&lang=en&country={country}&max=10&apikey={NEWS_API_KEY}"
                response = requests.get(url)
                if response.status_code == 200:
                    parse_articles(response.json())
                else:
                    articles.append({
                        "title": f"Error fetching {category} news",
                        "source": "System",
                        "summary": f"Status code {response.status_code}",
                        "url": ""
                    })
    except Exception as e:
        articles.append({
            "title": "Error fetching news",
            "source": "System",
            "summary": str(e),
            "url": ""
        })

    return articles

# takes url and parses through the web page to get the article text and images
def fetchArticle(url):
    """Fetch and extract readable article text + images"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove junk sections
        for tag in soup(["script", "style", "header", "footer", "nav", "aside", "form"]):
            tag.extract()

        # Collect visible paragraphs
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text().strip()
            if text and len(text.split()) >= 5:  # 🚨 filter junk here
                paragraphs.append(text)

        article_text = "\n\n".join(paragraphs)
        if not article_text:
            article_text = "Could not extract article text."

        # Collect images (still allow some)
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and src.lower().startswith(("http://", "https://")):
                images.append(src)
            elif src:
                images.append(urljoin(url, src))

        return {"text": article_text, "images": images[:5]}
    except Exception as e:
        return {"text": f"Error fetching article: {str(e)}", "images": []}

# -------------------------------
# TOKENIZER FUNCTION
# -------------------------------
def summarizeText(text, max_sentences=10):
    """Extractive summary using word frequencies, filter out short fragments"""
    try:
        sentences = nltk.sent_tokenize(text)
        if len(sentences) <= 2:  # too short to summarize
            return text

        stop_words = set(stopwords.words("english"))
        word_frequencies = {}
        for word in nltk.word_tokenize(text.lower()):
            if word.isalnum() and word not in stop_words:
                word_frequencies[word] = word_frequencies.get(word, 0) + 1

        if not word_frequencies:  # edge case
            return " ".join(sentences[:max_sentences])

        max_freq = max(word_frequencies.values())
        word_frequencies = {k: v / max_freq for k, v in word_frequencies.items()}

        sentence_scores = {}
        for sent in sentences:
            words = nltk.word_tokenize(sent.lower())
            if len(words) < 3:  # relax filter
                continue
            score = sum(word_frequencies.get(w, 0) for w in words)
            if score > 0:
                sentence_scores[sent] = score

        if not sentence_scores:
            return " ".join(sentences[:max_sentences])  # fallback

        # pick top sentences by score
        summary_sentences = heapq.nlargest(min(max_sentences, len(sentence_scores)),
                                           sentence_scores, key=sentence_scores.get)

        return " ".join(summary_sentences)

    except Exception as e:
        return " ".join(nltk.sent_tokenize(text)[:max_sentences])
    
    
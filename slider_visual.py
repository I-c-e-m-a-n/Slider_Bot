# Windows and Visuals
import customtkinter as ck
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Custom Module
import slider_helper as sh
from slider_helper import fetchArticle, summarizeText, sendMailSingle, Loading


# Sound and Speech
from gtts import gTTS
from playsound import playsound


# Extras
import os
import threading
import tempfile
import pygame
import random
import math
import time



class SliderVisual:
    def __init__(self):
        ck.set_appearance_mode("dark")
        ck.set_default_color_theme("blue")

        self.root = ck.CTk()
        self.root.title("Slider Bot")
        self.root.geometry(str(self.root.winfo_screenwidth())+'x'+str(self.root.winfo_screenheight()))

        pygame.mixer.init()
        self.speech_threads = {}   # track threads per window
        self.speech_stop_flags = {}
        self.is_thinking = False


        # -------------------------------
        # BACKGROUND 
        # -------------------------------

        # ===========================
        # Animated Particle Background
        # ===========================
        self.bg_canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight(), highlightthickness=0, bg="#050a14")
        self.bg_canvas.pack(fill="both", expand=True)

        

        self.cx, self.cy = self.root.winfo_screenwidth()/2, self.root.winfo_screenheight()/2  # window center (half of 1000x800)

        self.particles = []
        for _ in range(int(self.cy*0.7)):  # number of dots
            r = random.randint(20, 40)/10
            shade = random.choice(["#00aaff", "#89ddf2", "#033657", "#FCFDFD", "#0307f1"])
            
            base_radius = random.randint(0, self.cx*0.9)#3 * random.uniform(0.5, 1.5)  # orbit distance with ±100% variation
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.01, 0.017) * random.choice([-1,1])
            self.particles.append({
                "r": r, "color": shade,
                "base_radius": base_radius, "angle": angle,
                "speed": speed, "last_attract": 0,
                "draw_x": self.cx, "draw_y": self.cy
            })

        self.cursor = {"x": self.cx, "y": self.cy}
        self.root.bind("<Motion>", self.update_cursor)

        # -------------------------------
        # BUTTONS ON TOP OF BACKGROUND
        # -------------------------------
        self.btn_open_mail = ck.CTkButton(
            self.root,
            text="Open Emails",
            fg_color="#00f2ff",
            hover_color="#0099cc",
            text_color="black",
            corner_radius=15,
            font=("Orbitron", 16, "bold")
        )
        self.btn_open_mail.place(relx=0.5, rely=0.2, anchor="center")

        self.btn_open_weather = ck.CTkButton(
            self.root,
            text="Open Weather",
            fg_color="#00f2ff",
            hover_color="#0099cc",
            text_color="black",
            corner_radius=15,
            font=("Orbitron", 16, "bold")
        )
        self.btn_open_weather.place(relx=0.5, rely=0.35, anchor="center")

        # New button for news
        self.btn_open_news = ck.CTkButton(
            self.root,
            text="Open News",
            fg_color="#00f2ff",
            hover_color="#0099cc",
            text_color="black",
            corner_radius=15,
            font=("Orbitron", 16, "bold")
        )
        self.btn_open_news.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_text_tools = ck.CTkButton(
            self.root,
            text="Text Tools",
            fg_color="#00f2ff",
            hover_color="#0099cc",
            text_color="black",
            corner_radius=15,
            font=("Orbitron", 16, "bold")
            )
        self.btn_text_tools.place(relx=0.5, rely=0.65, anchor="center")

        self.btn_give_history = ck.CTkButton(
            self.root,
            text="Give History",
            fg_color="#00f2ff",
            text_color="black",
            corner_radius=12
        )

        # Start background animation
        self.animate_background()



    # -------------------------------
    # SPEAK FUNCTION
    # -------------------------------
    def speak_text(self, text, window=None, accent="us"):
        """Speak text in background, stop when window closes"""
        if not text.strip():
            return
        stop_flag = {"stop": False}

        tld_map = {
            "us": "com",
            "uk": "co.uk",
            "au": "com.au",
            "ca": "ca",
            "ie": "ie",
            "in": "co.in"
        }

        def run_speech():
            self.is_thinking = True  # start glowing/erratic mode

            # Speed up audio file
            def change_speed(sound, speed=1.25):
                # speed > 1.0 → faster, < 1.0 → slower
                new_frame_rate = int(sound.frame_rate * speed)
                return sound._spawn(sound.raw_data, overrides={"frame_rate": new_frame_rate}).set_frame_rate(sound.frame_rate)
            
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tts = gTTS(text=text, lang="en", tld=tld_map.get(accent, "com"))
                    tts.save(tmp.name)

                    pygame.mixer.music.load(tmp.name)
                    pygame.mixer.music.play()

                    # Poll until playback finishes or stop_flag is set
                    while pygame.mixer.music.get_busy():
                        if stop_flag["stop"]:
                            pygame.mixer.music.stop()
                            break
                        pygame.time.wait(200)

                os.remove(tmp.name)
            except Exception as e:
                messagebox.showerror("Error", f"Text-to-Speech failed:\n{str(e)}")
            finally:
                self.is_thinking = False  # return to calm mode

        # If a window was provided, stop speech when window closes
        if window:
            def on_close():
                stop_flag["stop"] = True
                if window in self.speech_threads:
                    del self.speech_threads[window]
                if window in self.speech_stop_flags:
                    del self.speech_stop_flags[window]
                window.destroy()

            window.protocol("WM_DELETE_WINDOW", on_close)

        t = threading.Thread(target=run_speech, daemon=True)
        t.start()

        if window:
            self.speech_threads[window] = t
            self.speech_stop_flags[window] = stop_flag


    # -------------------------------
    # SCROLL FUNCTION
    # -------------------------------
    def _bind_mousewheel(self, widget, target_canvas):
        def _on_mousewheel(event):
            if event.num == 5 or event.delta < 0:
                target_canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                target_canvas.yview_scroll(-1, "units")

        # Windows / macOS
        widget.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux
        widget.bind_all("<Button-4>", _on_mousewheel)
        widget.bind_all("<Button-5>", _on_mousewheel)


    # -------------------------------
    # CURSOR POSITION FUNCTION
    # -------------------------------
    def update_cursor(self, event):
        self.cursor["x"] = event.x
        self.cursor["y"] = event.y

    
    # -------------------------------
    # PRETTY BACKGROUND FUNCTIONs
    # -------------------------------
    def animate_background(self):
        self.bg_canvas.delete("all")
        now = time.time()

        # Update particle positions
        for p in self.particles:
            # Orbit around center
            p["angle"] += p["speed"]
            base_x = self.cx + math.cos(p["angle"]) * p["base_radius"]
            base_y = self.cy + math.sin(p["angle"]) * p["base_radius"]

            # Cursor attraction
            dx = self.cursor["x"] - base_x
            dy = self.cursor["y"] - base_y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 30:
                p["last_attract"] = now

            if now - p["last_attract"] < 4:
                base_x += dx * 0.9
                base_y += dy * 0.9

            # Thinking animation
            if self.is_thinking:
                p["speed"] += random.uniform(-0.007,0.007)
                if abs(p["speed"]) > 0.025:
                    p["speed"] = random.uniform(0.01, 0.017) * random.choice([-1,1])
                p["base_radius"] -= 3
                if p["base_radius"] < 35:
                    p["base_radius"] = random.uniform(self.cx*0.5,self.cx*1.1)
               
            else:
                p["base_radius"] += 1
                if p["base_radius"] > self.cy*0.9:
                    p["base_radius"] = random.uniform(self.cy*0.45,self.cy*0.6)
                p["speed"] += 0.01 *p['speed']
                if abs(p["speed"]) > 0.012:
                    p["speed"] = random.uniform(0.007, 0.01) * random.choice([-1,1])
                # base_x += dx * 0.07
                # base_y += dy * 0.07
                


            p["draw_x"], p["draw_y"] = base_x, base_y

            # Glow color when thinking
            color = self.glow_color(p["color"], random.randint(0,5)/10) if self.is_thinking else p["color"]

            self.bg_canvas.create_oval(
                p["draw_x"] - p["r"], p["draw_y"] - p["r"],
                p["draw_x"] + p["r"], p["draw_y"] + p["r"],
                fill=color, outline=""
            )

        # Draw particles
        for p in self.particles:
            self.bg_canvas.create_oval(
                p["draw_x"] - p["r"], p["draw_y"] - p["r"],
                p["draw_x"] + p["r"], p["draw_y"] + p["r"],
                fill=p["color"], outline=""
            )

        # Draw connecting lines
        def _blend_color(fg, bg, alpha):
            """Blend fg color into bg with given alpha (0–1)."""
            fg = fg.lstrip("#")
            bg = bg.lstrip("#")
            fr, fg_, fb = int(fg[0:2], 16), int(fg[2:4], 16), int(fg[4:6], 16)
            br, bg_, bb = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
            r = int(fr * alpha + br * (1 - alpha))
            g = int(fg_ * alpha + bg_ * (1 - alpha))
            b = int(fb * alpha + bb * (1 - alpha))
            return f"#{r:02x}{g:02x}{b:02x}"

        # Draw connecting lines with fade
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles[i+1:], i+1):
                dx = p1["draw_x"] - p2["draw_x"]
                dy = p1["draw_y"] - p2["draw_y"]
                dist = math.sqrt(dx * dx + dy * dy)
                if not self.is_thinking and dist < self.cy*0.1 : #- 15 * random.choice([-1,1]):
                    alpha = max(0, 1 - dist / 120)
                    color = _blend_color("#2e67adff", "#050a14", alpha)
                    self.bg_canvas.create_line(
                        p1["draw_x"], p1["draw_y"],
                        p2["draw_x"], p2["draw_y"],
                        fill=color, width=random.choice([0.9,1,1.3]))
                elif dist < self.cy*0.08:
                    alpha = max(0, 1 - dist / 120)
                    color = _blend_color("#1d4153ff", "#003929FF", alpha)
                    self.bg_canvas.create_line(
                        p1["draw_x"], p1["draw_y"],
                        p2["draw_x"], p2["draw_y"],
                        fill=color, width=random.choice([0.9,1,1.3]))
        self.root.after(30, self.animate_background)
   
    def glow_color(self, hex_color, intensity=random.randint(0,5)/10):
        """Blend color toward white based on intensity (0–1)."""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = int(r + (255 - r) * intensity)
        g = int(g + (255 - g) * intensity)
        b = int(b + (255 - b) * intensity)
        return f"#{r:02x}{g:02x}{b:02x}"
    

    # -------------------------------
    # EMAIL POPUP FUNCTION
    # -------------------------------
    def _prompt_email_summaries(self, news_list):
        """Popup to collect recipient email, then ask main to send the summaries."""
        popup = ck.CTkToplevel(self.root)
        popup.title("Send News Summaries")
        popup.geometry("420x160")
        popup.configure(bg="#050a14")

        ck.CTkLabel(
            popup, text="Send to (email address):",
            font=("Arial", 13, "bold"), text_color="#00f2ff"
        ).pack(pady=(12, 6))

        email_var = tk.StringVar()
        entry = ck.CTkEntry(popup, textvariable=email_var, width=360)
        entry.pack(pady=4)
        entry.focus_set()

        info = ck.CTkLabel(
            popup, text="We’ll send all summaries in one email.",
            font=("Arial", 11), text_color="gray"
        )
        info.pack(pady=(2, 10))

        btns = ck.CTkFrame(popup, fg_color="transparent")
        btns.pack(pady=4)

        def on_send():
            recipient = email_var.get().strip()
            if not recipient or "@" not in recipient or "." not in recipient.split("@")[-1]:
                messagebox.showerror("Invalid Email", "Please enter a valid email address.")
                return

            # Delegate to main; it will build the email and send it
            try:
                def task_func():
                    # run in background: just send the email
                    sh.send_news_summaries(news_list, recipient)
                    return "OK"

                def callback(_):
                    try:
                        popup.destroy()
                    except Exception as e:
                        print('Failed to send email. Error:', str(e))
                    messagebox.showinfo("Sent", "News summaries have been emailed.")

                load = Loading()
                load.run_task_with_loading(self, load, task_func, callback)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send summaries:\n{e}")

        ck.CTkButton(btns, text="Send", fg_color="#00f2ff", text_color="black",
                    corner_radius=12, command=on_send).pack(side="left", padx=6)
        ck.CTkButton(btns, text="Cancel", fg_color="#333", text_color="white",
                    corner_radius=12, command=popup.destroy).pack(side="left", padx=6)
    
    
    # -------------------------------
    # LOADING WINDOW
    # -------------------------------
    def create_loading_window(self):
        win = ck.CTkToplevel(self.root)
        win.title("Loading")
        win.geometry("520x240")
        win.configure(bg="#050a14")

        # Enter thinking mode
        self.is_thinking = True

        ck.CTkLabel(
            win,
            text="LOADING...",
            font=("Orbitron", 20, "bold"),
            text_color="#00f2ff"
        ).pack(pady=(16, 8))

        dynamic_label = ck.CTkLabel(
            win,
            text="Starting...",
            font=("Arial", 14),
            wraplength=480,
            justify="left",
            text_color="white"
        )
        dynamic_label.pack(padx=16, pady=(0, 12), fill="x")

        ck.CTkButton(
            win, text="Speak", fg_color="#00f2ff",
            command=lambda: self.speak_text(dynamic_label.cget("text"), window=win, accent='au')
        ).pack(pady=5)

        stop_flag = {"running": True}

        def dynamic_updater(new_text: str):
            try:
                dynamic_label.configure(text=str(new_text))
            except Exception:
                pass

        # When user closes the loading window, stop "thinking"
        def on_close():
            stop_flag["running"] = False
            self.is_thinking = False   #  return to calm mode
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        return win, dynamic_updater, stop_flag


    # -------------------------------
    # EMAIL WINDOW
    # -------------------------------
    def open_mail_window(self, mails):
        self.is_thinking = False
        win = ck.CTkToplevel(self.root)
        win.title("Emails")
        win.geometry("700x560")
        win.configure(bg="#050a14")

        canvas = tk.Canvas(win, bg="#0a0f1c", highlightthickness=0)
        scrollbar = ck.CTkScrollbar(win, orientation="vertical", command=canvas.yview)
        holder = ck.CTkFrame(canvas, fg_color="#0f1626", corner_radius=10)

        holder.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=holder, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Enable scrolling with mouse wheel
        self._bind_mousewheel(win, canvas)

        for mail in mails:
            block = ck.CTkFrame(holder, corner_radius=10, fg_color="#1a2238")
            block.pack(fill="x", pady=8, padx=12)

            sender = mail.get("sender", "Unknown Sender")
            subject = mail.get("subject", "No Subject")
            snippet = mail.get("snippet", "")
            recipient = mail.get("recipient", sender)

            ck.CTkLabel(
                block,
                text=f"From: {sender}",
                font=("Arial", 14, "bold"),
                text_color="#00f2ff"
            ).pack(anchor="w", pady=(8, 2), padx=10)
            ck.CTkLabel(
                block,
                text=snippet,
                font=("Arial", 14),
                wraplength=640,
                justify="left",
                text_color="white"
            ).pack(anchor="w", pady=(0, 10), padx=10)

            button_frame = ck.CTkFrame(block, fg_color="transparent")
            button_frame.pack(anchor="e", padx=10, pady=(0, 10))

            reply_btn = ck.CTkButton(
                button_frame,
                text="Reply",
                fg_color="#00f2ff",
                hover_color="#0099cc",
                text_color="black",
                corner_radius=12,
                command=lambda s=sender, r=recipient, subj=subject, body=mail.get("body", ""), dt=mail.get("date", ""):
                    self.open_reply_window(s, r, subj, body, dt)
            )
            reply_btn.pack(anchor="e", padx=10, pady=(0, 10))

            ck.CTkButton(
                button_frame,
                text="View",
                fg_color="#0099cc",
                text_color="black",
                corner_radius=12,
                command=lambda s=sender, subj=subject, body=mail.get("body", ""), dt=mail.get("date", ""):
                    self.open_view_window(s, subj, body, dt, recipient)
            ).pack(anchor="e", padx=10, pady=(0, 10))


    # -------------------------------
    # VIEW EMAIL WINDOW
    # -------------------------------
    def open_view_window(self, sender, subject, body, date, recipient):
        self.is_thinking = False
        win = ck.CTkToplevel(self.root)
        win.title("View Email")
        win.geometry("650x650")
        win.configure(bg="#050a14")

        ck.CTkLabel(win, text=f"From: {sender}", font=("Arial", 14, "bold"), text_color="#00f2ff").pack(anchor="w", padx=10, pady=(10, 0))
        ck.CTkLabel(win, text=f"Subject: {subject}", font=("Arial", 14, "italic"), text_color="white").pack(anchor="w", padx=10, pady=(0, 5))
        ck.CTkLabel(win, text=f"Date: {date}", font=("Arial", 11), text_color="gray").pack(anchor="w", padx=10, pady=(0, 10))

        text_box = tk.Text(win, wrap="word", bg="#1a1a1a", fg="white", insertbackground="white")
        text_box.insert("1.0", body)
        text_box.config(state="disabled")
        text_box.pack(padx=10, pady=10, fill="both", expand=True)

        win_button_frame = ck.CTkFrame(win, fg_color="transparent")

        # Reply button
        reply_btn = ck.CTkButton(
            win_button_frame,
            text="Reply",
            fg_color="#00f2ff",
            hover_color="#0099cc",
            text_color="black",
            corner_radius=12,
            command=lambda s=sender, r=recipient, subj=subject, b=body, dt=date:
                self.open_reply_window(s, r, subj, b, dt)
        )
        reply_btn.pack(side="left", padx=5, pady=10)

        # Speak button
        speak_btn = ck.CTkButton(
            win_button_frame,
            text="Speak",
            fg_color="#0099cc",
            hover_color="#0077aa",
            text_color="black",
            corner_radius=12,
            command=lambda: self.speak_text(body, window=win)
        )

        speak_btn.pack(side="left", padx=5, pady=10)

        # Pack the frame to the right
        win_button_frame.pack(anchor="e", padx=10, pady=10)


    # -------------------------------
    # REPLY WINDOW
    # -------------------------------
    def open_reply_window(self, sender, recipient, subject, original_body, original_date):
        self.is_thinking = False
        win = ck.CTkToplevel(self.root)
        win.title(f"Reply to {sender}")
        win.geometry("600x450")
        win.configure(bg="#050a14")

        ck.CTkLabel(win, text=f"From: {sender}", font=("Arial", 14, "bold"), text_color="#00f2ff").pack(anchor="w", padx=10, pady=(10, 0))
        ck.CTkLabel(win, text=f"Subject: {subject}", font=("Arial", 14, "italic"), text_color="white").pack(anchor="w", padx=10, pady=(0, 5))
        ck.CTkLabel(win, text=f"Date: {original_date}", font=("Arial", 11), text_color="gray").pack(anchor="w", padx=10, pady=(0, 10))

        reply_box = tk.Text(win, wrap="word", height=10, width=70, bg="#1a1a1a", fg="#00f2ff", insertbackground="white")
        reply_box.pack(padx=10, pady=10, fill="both", expand=True)

        def send_reply():
            body = reply_box.get("1.0", tk.END).strip()
            if not recipient:
                messagebox.showerror("Error", "No recipient found. Cannot send email.")
                win.destroy()
                return
            try:
                full_body = (
                    body
                    + "\n\n-------------------------\n"
                    + f"On {original_date}, {sender} wrote:\n"
                    + original_body
                )
                sh.sendMailSingle(recipient, sender, f"Re: {subject}", full_body)
                messagebox.showinfo("Success", f"Reply sent successfully to {sender}!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send reply:\n{str(e)}")
            win.destroy()

        bottom_frame = ck.CTkFrame(win, fg_color="transparent")
        bottom_frame.pack(pady=10)

        ck.CTkButton(win, text="Send", fg_color="#00f2ff", hover_color="#0099cc", text_color="black", corner_radius=12, command=send_reply).pack(pady=10)
        ck.CTkButton(bottom_frame, text="Speak", fg_color="#0099cc", text_color="black", corner_radius=12, command=lambda: self.speak_text(reply_box.get("1.0", tk.END), window=win)).pack(side="left", padx=5)


    # -------------------------------
    # WEATHER WINDOW
    # -------------------------------
    def open_weather_window(self, weather):
        self.is_thinking = False
        win = ck.CTkToplevel(self.root)
        win.title("Weather")
        win.geometry("520x360")
        win.configure(bg="#050a14")

        ck.CTkLabel(
            win,
            text="Weather Report",
            font=("Orbitron", 16, "bold"),
            text_color="#00f2ff"
        ).pack(pady=12)

        # Collect all weather info into one string
        weather_text = ""
        if isinstance(weather, dict):
            for k, v in weather.items():
                line = f"{k}: {v}"
                ck.CTkLabel(
                    win,
                    text=line,
                    font=("Arial", 14),
                    text_color="white"
                ).pack(anchor="w", padx=16, pady=2)
                weather_text += line + "\n"
        else:
            ck.CTkLabel(
                win,
                text=str(weather),
                font=("Arial", 14),
                wraplength=480,
                justify="left",
                text_color="white"
            ).pack(anchor="w", padx=16, pady=2)
            weather_text = str(weather)

        # Speak button — correct usage
        ck.CTkButton(
            win,
            text="Speak",
            fg_color="#00f2ff",
            command=lambda: self.speak_text(weather_text, window=win)
        ).pack(pady=10)

    
    # -------------------------------
    # NEWS WINDOW
    # -------------------------------
    def open_news_window(self, news_list):
        self.is_thinking = False
        win = ck.CTkToplevel(self.root)
        win.title("News")
        win.geometry("900x1000")
        win.configure(bg="#050a14")

        # State variable for headlines mode
        headlines_only = {"active": False}

        # Toggle button
        def toggle_view():
            headlines_only["active"] = not headlines_only["active"]
            refresh_view()

        toggle_btn = ck.CTkButton(
            win,
            text="Show Headlines Only",
            fg_color="#00f2ff",
            hover_color="#0099cc",
            text_color="black",
            corner_radius=12,
            command=toggle_view
        )
        toggle_btn.pack(pady=5)

        # Email Summaries button
        email_btn = ck.CTkButton(
            win,
            text="Email Summaries",
            fg_color="#00cc44",
            hover_color="#04551F",
            text_color="black",
            corner_radius=12,
            command=lambda: self._prompt_email_summaries(news_list)
        )
        email_btn.pack(pady=5)

        # Scrollable frame
        canvas = tk.Canvas(win, bg="#0a0f1c", highlightthickness=0)
        scrollbar = ck.CTkScrollbar(win, orientation="vertical", command=canvas.yview)
        content_frame = ck.CTkFrame(canvas, fg_color="#0f1626", corner_radius=10)

        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw", width=win.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._bind_mousewheel(win, canvas)

        def refresh_view():
            # Clear old content
            for widget in content_frame.winfo_children():
                widget.destroy()

            if headlines_only["active"]:
                toggle_btn.configure(text="Show Summaries")

                # Speak All Headlines button
                ck.CTkButton(
                    content_frame,
                    text="Speak All Headlines",
                    fg_color="#00f2ff",
                    text_color="black",
                    corner_radius=12,
                    command=lambda: self.speak_text(
                        "\n".join([a.get("title", "No Title") for a in news_list]),
                        window=win
                    )
                ).pack(pady=8)

                for article in news_list:
                    block = ck.CTkFrame(content_frame, corner_radius=10, fg_color="#1a2238")
                    block.pack(fill="x", expand=True, pady=6, padx=12)

                    title = article.get("title", "No Title")
                    url = article.get("url", "")

                    ck.CTkLabel(
                        block, text=title,
                        font=("Arial", 13, "bold"), text_color="#00f2ff",
                        wraplength=640,  # wrap text at near window width
                        justify="left"
                    ).pack(anchor="w", expand=True, padx=10, pady=(6, 2), fill="x")

                    button_frame = ck.CTkFrame(block, fg_color="transparent")
                    button_frame.pack(anchor="e", expand=True, padx=10, pady=(0, 8))

                    ck.CTkButton(
                        button_frame,
                        text="Read",
                        fg_color="#0099cc",
                        text_color="black",
                        corner_radius=12,
                        command=lambda u=url, t=title: self.open_article_window(u, t)
                    ).pack(side="left", padx=5)

                    ck.CTkButton(
                        button_frame,
                        text="Speak",
                        fg_color="#00f2ff",
                        text_color="black",
                        corner_radius=12,
                        command=lambda s=title: self.speak_text(s, window=win)
                    ).pack(side="left", padx=5)

            else:
                toggle_btn.configure(text="Show Headlines Only")
                for article in news_list:
                    block = ck.CTkFrame(content_frame, corner_radius=10, fg_color="#1a2238")
                    block.pack(fill="x", pady=8, padx=12)

                    title = article.get("title", "No Title")
                    source = article.get("source", "Unknown")
                    summary = article.get("summary", "")
                    url = article.get("url", "")

                    ck.CTkLabel(
                        block, text=title,
                        font=("Arial", 14, "bold"), wraplength=800, justify="left", text_color="#00f2ff"
                    ).pack(anchor="w", padx=10, pady=(8, 0))
                    ck.CTkLabel(
                        block, text=f"Source: {source}",
                        font=("Arial", 11), text_color="gray"
                    ).pack(anchor="w", padx=10, pady=(0, 4))
                    ck.CTkLabel(
                        block, text=summary,
                        font=("Arial", 14), wraplength=800, justify="left", text_color="white"
                    ).pack(anchor="w", padx=10, pady=(0, 10))

                    button_frame = ck.CTkFrame(block, fg_color="transparent")
                    button_frame.pack(anchor="e", padx=10, pady=(0, 10))

                    ck.CTkButton(
                        button_frame,
                        text="View",
                        fg_color="#0099cc",
                        text_color="black",
                        corner_radius=12,
                        command=lambda u=url, t=title: self.open_article_window(u, t)
                    ).pack(side="left", padx=5)

                    ck.CTkButton(
                        button_frame,
                        text="Speak",
                        fg_color="#00f2ff",
                        text_color="black",
                        corner_radius=12,
                        command=lambda s=summary: self.speak_text(s, window=win, accent="uk")
                    ).pack(side="left", padx=5)

        # Initial view
        refresh_view()


    # -------------------------------
    # ARTICLE WINDOW
    # -------------------------------
    def open_article_window(self, url, title):
        self.is_thinking = False
        article_data = fetchArticle(url)
        article_text = article_data["text"]
        article_images = article_data["images"]

        # Summarize
        summary_text = summarizeText(article_text, max_sentences=10)

        win = ck.CTkToplevel(self.root)
        win.title(title[:50] + "...")
        win.geometry("800x800")
        win.configure(bg="#050a14")

        # Title
        ck.CTkLabel(
            win, text=title, font=("Arial", 14, "bold"), text_color="#00f2ff"
        ).pack(anchor="w", padx=10, pady=(8, 0))

        # -------------------------------
        # Scrollable container for summary + images
        # -------------------------------
        content_frame = ck.CTkFrame(win, fg_color="#0f1626", corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(content_frame, bg="#0a0f1c", highlightthickness=0)
        scrollbar = ck.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
        holder = ck.CTkFrame(canvas, fg_color="#0f1626")

        holder.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=holder, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Enable scrolling with mouse wheel
        self._bind_mousewheel(win, canvas)

        # -------------------------------
        # Summary text only
        # -------------------------------
        summary_label = ck.CTkLabel(
            holder,
            text=summary_text,
            font=("Arial", 14),
            wraplength=700,
            justify="left",
            text_color="white"
        )
        summary_label.pack(anchor="w", padx=10, pady=10)

        # -------------------------------
        # Images
        # -------------------------------
        self.article_images = getattr(self, "article_images", [])
        for img_url in article_images:
            try:
                import requests
                from PIL import Image, ImageTk
                from io import BytesIO

                img_data = requests.get(img_url, timeout=5).content
                pil_img = Image.open(BytesIO(img_data))
                pil_img.thumbnail((700, 400))
                tk_img = ImageTk.PhotoImage(pil_img)

                img_label = tk.Label(holder, image=tk_img, bg="#0f1626")
                img_label.pack(pady=10)
                self.article_images.append(tk_img)
            except Exception:
                continue

        # -------------------------------
        # Buttons
        # -------------------------------
        button_frame = ck.CTkFrame(win, fg_color="transparent")
        button_frame.pack(anchor="e", padx=10, pady=10)

        ck.CTkButton(
            button_frame,
            text="Speak",
            fg_color="#00f2ff",
            text_color="black",
            corner_radius=12,
            command=lambda: self.speak_text(summary_text, window=win)
        ).pack(side="left", padx=5)

        # ck.CTkButton(
        #     button_frame,
        #     text="Give History",
        #     fg_color="#00f2ff",
        #     text_color="black",
        #     corner_radius=12,
        #     command=lambda s=summary_text, t=title: self.show_article_history(s, t)
        # ).pack(side="left", padx=5)

        ck.CTkButton(
            button_frame,
            text="Open in Browser",
            fg_color="#ff6600",
            text_color="black",
            corner_radius=12,
            command=lambda: os.system(f"open {url}" if os.name == "posix" else f"start {url}")
        ).pack(side="left", padx=5)

        # -------------------------------
        # Email Summary Section
        # -------------------------------
        email_frame = ck.CTkFrame(win, fg_color="transparent")
        email_frame.pack(fill="x", padx=10, pady=(5, 10))

        ck.CTkLabel(email_frame, text="Send summary to:", text_color="white").pack(side="left", padx=5)
        recipient_entry = ck.CTkEntry(email_frame, placeholder_text="recipient@example.com", width=220)
        recipient_entry.pack(side="left", padx=5)

        def send_summary():
            recipient = recipient_entry.get().strip()
            if recipient:
                sendMailSingle(recipient, "Reader", f"Summary: {title}", summary_text)
                messagebox.showinfo("Success", f"Summary emailed to {recipient}")
            else:
                messagebox.showwarning("Missing Email", "Please enter a recipient email address.")

        ck.CTkButton(
            email_frame,
            text="Email Summary",
            fg_color="#00cc44",
            text_color="black",
            corner_radius=12,
            command=send_summary
        ).pack(side="left", padx=5)


    # -------------------------------
    # TEXT WINDOW
    # -------------------------------
    def open_text_tools_window(self, x):
        self.is_thinking = False
        win = ck.CTkToplevel(self.root)
        win.title("Text Tools")
        win.geometry("600x500")
        win.configure(bg="#050a14")

        ck.CTkLabel(
            win, text="Enter your text below:",
            font=("Arial", 14, "bold"), text_color="#00f2ff"
        ).pack(pady=10)

        # Input text box
        input_box = tk.Text(
            win, wrap="word", bg="#1a1a1a",
            fg="white", insertbackground="white", height=15
        )
        input_box.pack(fill="both", expand=True, padx=10, pady=10)

        # Output summary box
        summary_box = tk.Text(
            win, wrap="word", bg="#0f1626",
            fg="white", insertbackground="white", height=7
        )
        summary_box.pack(fill="x", padx=10, pady=(0, 10))
        summary_box.insert("1.0", "Summary will appear here...")
        summary_box.config(state="disabled")

        # Buttons
        button_frame = ck.CTkFrame(win, fg_color="transparent")
        button_frame.pack(pady=10)

        def speak_input():
            text = input_box.get("1.0", "end").strip()
            if text:
                self.speak_text(text, window=win)

        def summarise_input():
            text = input_box.get("1.0", "end").strip()
            if text:
                summary = summarizeText(text, max_sentences=3)
                summary_box.config(state="normal")
                summary_box.delete("1.0", "end")
                summary_box.insert("1.0", summary)
                summary_box.config(state="disabled")

        ck.CTkButton(
            button_frame,
            text="Speak",
            fg_color="#00f2ff",
            text_color="black",
            corner_radius=12,
            command=speak_input
        ).pack(side="left", padx=5)

        ck.CTkButton(
            button_frame,
            text="Summarise",
            fg_color="#00f2ff",
            text_color="black",
            corner_radius=12,
            command=summarise_input
        ).pack(side="left", padx=5)



    def run(self):
        self.root.mainloop()




   # -------------------------------
    # ARTICLE HISTORY WINDOW............. DO NOT USE
    # -------------------------------
    # def show_article_history(self, summary_text, title):
    #     win = ck.CTkToplevel(self.root)
    #     win.title("Article History / Context")
    #     win.geometry("850x600")
    #     win.configure(bg="#050a14")

    #     ck.CTkLabel(
    #         win, text=f"Context for: {title}",
    #         font=("Arial", 14, "bold"),
    #         text_color="#00f2ff"
    #     ).pack(pady=10)

    #     text_box = tk.Text(win, wrap="word", bg="#1a1a1a", fg="white",
    #                     insertbackground="white", font=("Arial", 12))
    #     text_box.pack(fill="both", expand=True, padx=10, pady=10)

    #     try:
    #         history = giveArticleHistory(summary_text)
    #     except Exception as e:
    #         history = f"Error retrieving history: {str(e)}"

    #     # Insert and highlight trigger phrases (marked with ** in giveArticleHistory)
    #     parts = history.split("**")
    #     for i, part in enumerate(parts):
    #         if i % 2 == 1:  # odd indices = trigger
    #             start = text_box.index("end-1c")
    #             text_box.insert("end", part)
    #             end = text_box.index("end-1c")
    #             text_box.tag_add("highlight", start, end)
    #         else:
    #             text_box.insert("end", part)

    #     text_box.tag_config("highlight", foreground="#ffaa00", font=("Arial", 12, "bold"))
    #     text_box.config(state="disabled")

    #     ck.CTkButton(
    #         win,
    #         text="Speak",
    #         fg_color="#00f2ff",
    #         text_color="black",
    #         corner_radius=12,
    #         command=lambda: self.speak_text(history, window=win)
    #     ).pack(side="left", padx=5)

    #     ck.CTkButton(
    #         win, text="Close", fg_color="#00f2ff",
    #         command=win.destroy
    #     ).pack(pady=10)
"""
Marcus V.A — Modern Chat GUI
DedSec V.A  |  gui.py

ChatGPT-style voice chat interface built with tkinter.
Preserves all original logic: subprocess streaming, Groq Whisper STT,
waveform animation, boot sequence, glitch ticker.
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import subprocess
import sys
import os
import time
import random
import math
from datetime import datetime

# ──────────────────────────────────────────────
#  THEME
# ──────────────────────────────────────────────
BG_APP      = "#0F0F0F"   # outer window
BG_SIDEBAR  = "#161616"   # left panel
BG_CHAT     = "#0F0F0F"   # message area
BG_BUBBLE_A = "#1E1E1E"   # Marcus bubble
BG_BUBBLE_U = "#4A3F9F"   # user bubble  (purple)
BG_INPUT    = "#1A1A1A"   # input bar bg
BG_HEADER   = "#111111"   # top bar

ACCENT      = "#7C6FCD"   # purple accent
ACCENT_HI   = "#9D91E8"   # hover accent
GREEN       = "#1D9E75"   # online dot / status
RED         = "#E05C5C"   # mic active
DIM         = "#555555"   # muted text
MID         = "#888888"   # secondary text
LIGHT       = "#E8E8E8"   # primary text
WHITE       = "#FFFFFF"

FONT_UI     = ("Segoe UI",    11)
FONT_MSG    = ("Segoe UI",    12)
FONT_META   = ("Segoe UI",     9)
FONT_TITLE  = ("Segoe UI",    13, "bold")
FONT_SMALL  = ("Segoe UI",     9)
FONT_BTN    = ("Segoe UI",    10)
FONT_MONO   = ("Courier New", 10)

TICKER_MSGS = [
    "ENCRYPTION ACTIVE", "NODE: CHICAGO-03", "PACKET LOSS: 0.00%",
    "UPLINK STABLE", "SIGNAL STRENGTH: MAX", "FIREWALL: ENGAGED",
    "NEURAL LINK: ACTIVE", "GHOST MODE: STANDBY", "DEDSEC NET: SECURE",
    "LATENCY: 2ms", "MEMORY: LOADED", "VOICE ENGINE: READY",
]

BOOT_LINES = [
    ("[ DedSec V.A ]  Initializing secure shell...", "dim"),
    ("[ MARCUS ]  Loading neural core ............. OK", "ok"),
    ("[ MEMORY ]  Reading memory.json ............. OK", "ok"),
    ("[ VOICE  ]  ElevenLabs engine standby ....... OK", "ok"),
    ("[ NET    ]  Establishing encrypted channel .. OK", "ok"),
    ("[ AUTH   ]  Identity verified. Welcome back.", "hi"),
]

GLITCH_CHARS = "!@#$%^&*<>?/|\\█▓▒░"


# ──────────────────────────────────────────────
#  WAVEFORM WIDGET
# ──────────────────────────────────────────────
class WaveformCanvas(tk.Canvas):
    """Animated equalizer bar — pulses when Marcus is speaking/thinking."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._bars    = 32
        self._active  = False
        self._heights = [1.0] * self._bars
        self._targets = [1.0] * self._bars
        self.after(50, self._loop)

    def activate(self):
        self._active = True

    def deactivate(self):
        self._active = False
        self._targets = [1.0] * self._bars

    def _loop(self):
        if self._active:
            cx = self._bars // 2
            for i in range(self._bars):
                dist = abs(i - cx) / cx
                peak = 28 * (1 - dist * 0.55) * random.uniform(0.3, 1.0)
                self._targets[i] = max(1.5, peak)
        for i in range(self._bars):
            self._heights[i] += (self._targets[i] - self._heights[i]) * 0.3
        self._draw()
        self.after(40, self._loop)

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()  or 400
        h = self.winfo_height() or 36
        mid   = h / 2
        gap   = w / self._bars
        bw    = max(1, gap * 0.45)
        for i, bh in enumerate(self._heights):
            x = i * gap + gap / 2
            # colour: bright purple when tall, dim otherwise
            ratio = bh / 28
            if ratio > 0.6:
                col = ACCENT_HI
            elif ratio > 0.25:
                col = ACCENT
            else:
                col = "#2A2440"
            self.create_rectangle(
                x - bw, mid - bh,
                x + bw, mid + bh,
                fill=col, outline=""
            )


# ──────────────────────────────────────────────
#  ROUNDED-RECT HELPER
# ──────────────────────────────────────────────
def rounded_rect(canvas, x1, y1, x2, y2, r=12, **kw):
    canvas.create_arc(x1,     y1,     x1+2*r, y1+2*r, start= 90, extent=90, style="pieslice", **kw)
    canvas.create_arc(x2-2*r, y1,     x2,     y1+2*r, start=  0, extent=90, style="pieslice", **kw)
    canvas.create_arc(x1,     y2-2*r, x1+2*r, y2,     start=180, extent=90, style="pieslice", **kw)
    canvas.create_arc(x2-2*r, y2-2*r, x2,     y2,     start=270, extent=90, style="pieslice", **kw)
    canvas.create_rectangle(x1+r, y1, x2-r, y2, **kw)
    canvas.create_rectangle(x1, y1+r, x2, y2-r, **kw)


# ──────────────────────────────────────────────
#  MAIN GUI
# ──────────────────────────────────────────────
class MarcusGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Marcus — DedSec V.A")
        self.root.configure(bg=BG_APP)
        self.root.geometry("980x720")
        self.root.minsize(700, 500)
        self.root.resizable(True, True)

        # State
        self._streaming   = False
        self._mic_active  = False
        self._cursor_job  = None
        self._cursor_vis  = True
        self.glitch_on    = False
        self._msg_widgets = []   # list of (frame, text_widget) for bubbles
        self._current_bubble = None  # text widget being streamed into

        self._build_layout()
        self.root.after(300, self._boot_sequence)

    # ──────────────────────────────────────────
    #  LAYOUT
    # ──────────────────────────────────────────
    def _build_layout(self):
        # ── Sidebar ───────────────────────────
        self.sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # ── Main panel ────────────────────────
        main = tk.Frame(self.root, bg=BG_APP)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_header(main)
        self._build_chat(main)
        self._build_waveform_bar(main)
        self._build_input_bar(main)

    # ── Sidebar ───────────────────────────────
    def _build_sidebar(self):
        sb = self.sidebar

        # Logo
        logo_frame = tk.Frame(sb, bg=BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, padx=16, pady=(20, 8))

        tk.Label(logo_frame, text="◈", bg=BG_SIDEBAR, fg=ACCENT,
                 font=("Segoe UI", 20)).pack(side=tk.LEFT)
        tk.Label(logo_frame, text="  MARCUS", bg=BG_SIDEBAR, fg=LIGHT,
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

        tk.Label(sb, text="DedSec V.A", bg=BG_SIDEBAR, fg=DIM,
                 font=FONT_SMALL).pack(anchor="w", padx=20)

        self._sidebar_divider(sb)

        # Status card
        status_card = tk.Frame(sb, bg="#1C1C1C", padx=12, pady=10)
        status_card.pack(fill=tk.X, padx=12, pady=4)

        row = tk.Frame(status_card, bg="#1C1C1C")
        row.pack(fill=tk.X)
        self._dot = tk.Label(row, text="●", bg="#1C1C1C", fg="#333", font=("Segoe UI", 8))
        self._dot.pack(side=tk.LEFT)
        self._status_lbl = tk.Label(row, text="  Offline", bg="#1C1C1C",
                                    fg=DIM, font=FONT_SMALL)
        self._status_lbl.pack(side=tk.LEFT)

        self._sidebar_divider(sb)

        # Nav buttons
        nav_items = [
            ("🗨  New chat",      self._clear_chat),
            ("💾  Memory",        lambda: None),
            ("⌨  Shortcuts",     lambda: None),
            ("⚙  Settings",      lambda: None),
        ]
        for label, cmd in nav_items:
            btn = tk.Button(sb, text=label, bg=BG_SIDEBAR, fg=MID,
                            activebackground="#222", activeforeground=LIGHT,
                            bd=0, anchor="w", padx=16, pady=8,
                            font=FONT_BTN, cursor="hand2", command=cmd)
            btn.pack(fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1E1E1E", fg=LIGHT))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_SIDEBAR, fg=MID))

        self._sidebar_divider(sb)

        # Glitch toggle
        self.glitch_btn = tk.Button(
            sb, text="≋  Glitch mode", bg=BG_SIDEBAR, fg=DIM,
            activebackground="#222", activeforeground=ACCENT,
            bd=0, anchor="w", padx=16, pady=8,
            font=FONT_BTN, cursor="hand2", command=self._toggle_glitch
        )
        self.glitch_btn.pack(fill=tk.X)

        # Ticker at bottom
        tk.Frame(sb, bg=BG_SIDEBAR).pack(fill=tk.BOTH, expand=True)
        self.ticker = tk.Label(sb, text="", bg=BG_SIDEBAR, fg="#2A2A2A",
                               font=("Courier New", 7), wraplength=200, justify="left")
        self.ticker.pack(anchor="w", padx=12, pady=(0, 12))
        self._animate_ticker()

    def _sidebar_divider(self, parent):
        tk.Frame(parent, bg="#222222", height=1).pack(fill=tk.X, padx=12, pady=8)

    # ── Header ────────────────────────────────
    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=BG_HEADER, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=BG_HEADER)
        left.pack(side=tk.LEFT, padx=16, fill=tk.Y)

        # Avatar circle (canvas)
        av = tk.Canvas(left, width=32, height=32, bg=BG_HEADER,
                       highlightthickness=0)
        av.pack(side=tk.LEFT, pady=10)
        av.create_oval(0, 0, 32, 32, fill=ACCENT, outline="")
        av.create_text(16, 16, text="M", fill=WHITE,
                       font=("Segoe UI", 12, "bold"))

        info = tk.Frame(left, bg=BG_HEADER)
        info.pack(side=tk.LEFT, padx=(10, 0), fill=tk.Y)
        tk.Label(info, text="Marcus", bg=BG_HEADER, fg=LIGHT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 0))

        dot_row = tk.Frame(info, bg=BG_HEADER)
        dot_row.pack(anchor="w")
        self._hdr_dot = tk.Label(dot_row, text="●", bg=BG_HEADER,
                                 fg="#333", font=("Segoe UI", 7))
        self._hdr_dot.pack(side=tk.LEFT)
        self._hdr_status = tk.Label(dot_row, text=" Offline", bg=BG_HEADER,
                                    fg=DIM, font=FONT_SMALL)
        self._hdr_status.pack(side=tk.LEFT)

        # Right buttons
        right = tk.Frame(hdr, bg=BG_HEADER)
        right.pack(side=tk.RIGHT, padx=12, fill=tk.Y)

        for text, cmd in [("⊘ Clear", self._clear_chat), ("✕ Quit", self.root.quit)]:
            b = tk.Button(right, text=text, bg=BG_HEADER, fg=DIM,
                          activebackground="#1A1A1A", activeforeground=LIGHT,
                          bd=0, padx=10, pady=6,
                          font=FONT_SMALL, cursor="hand2", command=cmd)
            b.pack(side=tk.LEFT, pady=12)
            b.bind("<Enter>", lambda e, btn=b: btn.config(fg=LIGHT))
            b.bind("<Leave>", lambda e, btn=b: btn.config(fg=DIM))

    # ── Chat area ─────────────────────────────
    def _build_chat(self, parent):
        # Outer frame with scrollbar
        outer = tk.Frame(parent, bg=BG_CHAT)
        outer.pack(fill=tk.BOTH, expand=True)

        vsb = tk.Scrollbar(outer, orient="vertical", bg=BG_CHAT,
                           troughcolor=BG_CHAT, bd=0, width=6,
                           highlightthickness=0)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_canvas = tk.Canvas(outer, bg=BG_CHAT, highlightthickness=0,
                                     yscrollcommand=vsb.set)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=self.chat_canvas.yview)

        self.chat_frame = tk.Frame(self.chat_canvas, bg=BG_CHAT)
        self._chat_window = self.chat_canvas.create_window(
            (0, 0), window=self.chat_frame, anchor="nw"
        )

        self.chat_frame.bind("<Configure>", self._on_chat_configure)
        self.chat_canvas.bind("<Configure>", self._on_canvas_configure)
        self.chat_canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_chat_configure(self, e):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.chat_canvas.itemconfig(self._chat_window, width=e.width)

    def _on_mousewheel(self, e):
        self.chat_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    # ── Waveform bar ──────────────────────────
    def _build_waveform_bar(self, parent):
        bar = tk.Frame(parent, bg=BG_APP, height=42)
        bar.pack(fill=tk.X, padx=16, pady=(4, 0))
        bar.pack_propagate(False)

        self.waveform = WaveformCanvas(bar, bg=BG_APP, highlightthickness=0)
        self.waveform.pack(fill=tk.BOTH, expand=True)

    # ── Input bar ─────────────────────────────
    def _build_input_bar(self, parent):
        outer = tk.Frame(parent, bg=BG_APP, pady=10)
        outer.pack(fill=tk.X, padx=16)

        container = tk.Frame(outer, bg=BG_INPUT, pady=0)
        container.pack(fill=tk.X)

        # border trick
        border = tk.Frame(outer, bg=ACCENT, height=1)
        border.pack(fill=tk.X)

        inner = tk.Frame(container, bg=BG_INPUT)
        inner.pack(fill=tk.X, padx=4, pady=6)

        self.entry = tk.Entry(
            inner, bg=BG_INPUT, fg=LIGHT,
            insertbackground=ACCENT,
            font=("Segoe UI", 12),
            bd=0, relief=tk.FLAT,
            highlightthickness=0,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(8, 4))
        self.entry.bind("<Return>", self._send)

        self.mic_btn = tk.Button(
            inner, text="🎙", bg=BG_INPUT, fg=DIM,
            activebackground=BG_INPUT, activeforeground=RED,
            bd=0, font=("Segoe UI Emoji", 14),
            cursor="hand2", command=self._toggle_mic
        )
        self.mic_btn.pack(side=tk.LEFT, padx=4)

        self.send_btn = tk.Button(
            inner, text="➤", bg=ACCENT, fg=WHITE,
            activebackground=ACCENT_HI, activeforeground=WHITE,
            bd=0, font=("Segoe UI", 12),
            cursor="hand2", padx=10, pady=3,
            command=self._send
        )
        self.send_btn.pack(side=tk.LEFT, padx=(0, 6))

        hint = tk.Frame(outer, bg=BG_APP)
        hint.pack(fill=tk.X, pady=(4, 0))
        tk.Label(hint, text="Marcus can make mistakes. Verify important info.",
                 bg=BG_APP, fg="#333", font=("Segoe UI", 8)).pack()

        self.entry.focus_set()

    # ──────────────────────────────────────────
    #  BUBBLE FACTORY
    # ──────────────────────────────────────────
    def _add_bubble(self, text: str, role: str) -> tk.Text:
        """Add a chat bubble. role = 'marcus' | 'user'. Returns the text widget."""
        is_user  = role == "user"
        bg_bbl   = BG_BUBBLE_U if is_user else BG_BUBBLE_A
        fg_txt   = WHITE       if is_user else LIGHT
        anchor   = "e"         if is_user else "w"
        padx_out = (80, 16)    if is_user else (16, 80)

        row = tk.Frame(self.chat_frame, bg=BG_CHAT)
        row.pack(fill=tk.X, padx=16, pady=(8, 0), anchor=anchor)

        if not is_user:
            # Avatar dot
            av = tk.Canvas(row, width=28, height=28, bg=BG_CHAT,
                           highlightthickness=0)
            av.pack(side=tk.LEFT, anchor="n", pady=2, padx=(0, 8))
            av.create_oval(0, 0, 28, 28, fill=ACCENT, outline="")
            av.create_text(14, 14, text="M", fill=WHITE,
                           font=("Segoe UI", 9, "bold"))

        bubble = tk.Frame(row, bg=bg_bbl, padx=14, pady=10)
        bubble.pack(side=tk.RIGHT if is_user else tk.LEFT, padx=padx_out)

        # Text widget (auto-height)
        txt = tk.Text(
            bubble, bg=bg_bbl, fg=fg_txt,
            font=FONT_MSG,
            bd=0, relief=tk.FLAT,
            wrap=tk.WORD,
            highlightthickness=0,
            state=tk.NORMAL,
            cursor="arrow",
            spacing1=2, spacing3=2,
        )
        txt.insert("1.0", text)
        txt.config(state=tk.DISABLED)
        txt.pack()
        self._resize_bubble_text(txt)

        # Timestamp
        ts = tk.Label(row, text=datetime.now().strftime("%H:%M"),
                      bg=BG_CHAT, fg=DIM, font=FONT_META)
        ts.pack(side=tk.RIGHT if is_user else tk.LEFT, anchor="s", padx=4, pady=(0, 2))

        self._scroll_bottom()
        return txt

    def _resize_bubble_text(self, txt: tk.Text):
        """Shrink text widget to fit its content (no extra blank lines)."""
        txt.config(state=tk.NORMAL)
        content = txt.get("1.0", tk.END).rstrip("\n")
        lines   = content.split("\n")
        # Count visual word-wrapped lines
        wrap_px  = 520  # rough max bubble width
        char_px  = 8    # approx char width at 12pt
        cols     = max(1, wrap_px // char_px)
        vis_rows = sum(max(1, math.ceil(len(ln) / cols)) for ln in lines)
        txt.config(width=min(cols, max(len(ln) for ln in lines) + 2) if lines else 40,
                   height=vis_rows)
        txt.config(state=tk.DISABLED)

    def _scroll_bottom(self):
        self.chat_frame.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    # ──────────────────────────────────────────
    #  BOOT SEQUENCE
    # ──────────────────────────────────────────
    def _boot_sequence(self):
        def run():
            # System boot bubble
            self.root.after(0, lambda: self._start_stream_bubble())
            for text, kind in BOOT_LINES:
                time.sleep(0.18)
                self.root.after(0, lambda t=text, k=kind: self._stream_chunk(t + "\n", k))
            time.sleep(0.2)
            self.root.after(0, self._end_stream_bubble)
            self.root.after(0, self._set_online)
            # Greeting
            time.sleep(0.4)
            greeting = "Hey! I'm Marcus, your AI voice assistant.\nType below or tap 🎙 to talk. How can I help?"
            self.root.after(0, lambda: self._add_bubble(greeting, "marcus"))
        threading.Thread(target=run, daemon=True).start()

    # ──────────────────────────────────────────
    #  STREAMING BUBBLE
    # ──────────────────────────────────────────
    def _start_stream_bubble(self):
        """Open a new Marcus bubble for streaming content into."""
        self._current_bubble = self._add_bubble("", "marcus")
        self._streaming = True
        self.waveform.activate()

    def _stream_chunk(self, chunk: str, tag: str = ""):
        """Append text to the currently open streaming bubble."""
        if self._current_bubble is None:
            return
        txt = self._current_bubble
        txt.config(state=tk.NORMAL)
        if tag == "ok":
            txt.tag_config("ok", foreground="#1D9E75")
            txt.insert(tk.END, chunk, "ok")
        elif tag == "hi":
            txt.tag_config("hi", foreground=ACCENT_HI)
            txt.insert(tk.END, chunk, "hi")
        elif tag == "dim":
            txt.tag_config("dim", foreground=DIM)
            txt.insert(tk.END, chunk, "dim")
        else:
            txt.insert(tk.END, chunk)
        txt.config(state=tk.DISABLED)
        self._resize_bubble_text(txt)
        self._scroll_bottom()

    def _end_stream_bubble(self):
        self._current_bubble = None
        self._streaming = False
        self.waveform.deactivate()
        self.send_btn.config(bg=ACCENT, fg=WHITE)

    # ──────────────────────────────────────────
    #  SEND / STREAM
    # ──────────────────────────────────────────
    def _send(self, event=None):
        if self._streaming:
            return
        cmd = self.entry.get().strip()
        if not cmd:
            return
        self.entry.delete(0, tk.END)
        self._add_bubble(cmd, "user")
        threading.Thread(target=self._stream_marcus, args=(cmd,), daemon=True).start()

    def _stream_marcus(self, cmd: str):
        self._streaming = True
        self.root.after(0, lambda: self.send_btn.config(bg="#2A2A2A", fg=DIM))
        self.root.after(0, self._start_stream_bubble)

        got_any = False
        try:
            env = os.environ.copy()
            env["MARCUS_GUI"] = "1"

            proc = subprocess.Popen(
                [sys.executable, "main.py", "--cmd", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=env,
            )

            while True:
                ch = proc.stdout.read(1)
                if not ch:
                    break
                got_any = True
                self.root.after(0, self._stream_chunk, ch)

            proc.wait(timeout=5)

            if not got_any:
                err = proc.stderr.read().strip()
                self.root.after(0, self._stream_chunk, err or "[No response]")

        except subprocess.TimeoutExpired:
            proc.kill()
            self.root.after(0, self._stream_chunk, "[TIMEOUT] Marcus took too long.")
        except Exception as e:
            self.root.after(0, self._stream_chunk, f"[ERROR] {e}")
        finally:
            self.root.after(0, self._end_stream_bubble)

    # ──────────────────────────────────────────
    #  MIC
    # ──────────────────────────────────────────
    def _toggle_mic(self):
        if self._mic_active:
            self._stop_mic()
        else:
            self._start_mic()

    def _start_mic(self):
        self._mic_active = True
        self.mic_btn.config(fg=RED)
        self._add_bubble("🎙 Listening…", "user")
        threading.Thread(target=self._mic_listen, daemon=True).start()

    def _stop_mic(self):
        self._mic_active = False
        self.mic_btn.config(fg=DIM)

    def _mic_listen(self):
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            r.energy_threshold = 400
            r.dynamic_energy_threshold = False
            with sr.Microphone(device_index=2) as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=6, phrase_time_limit=15)

            # Groq Whisper first
            try:
                import io, wave
                from groq import Groq
                from dotenv import load_dotenv
                load_dotenv()
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                buf = io.BytesIO()
                with wave.open(buf, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(audio.sample_width)
                    wf.setframerate(audio.sample_rate)
                    wf.writeframes(audio.get_raw_data())
                buf.seek(0)
                buf.name = "audio.wav"
                result = client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=buf, language="en", response_format="text"
                )
                text = result.strip() if isinstance(result, str) else result.text.strip()
            except Exception:
                text = r.recognize_google(audio)

            if text:
                self.root.after(0, self.entry.delete, 0, tk.END)
                self.root.after(0, self.entry.insert, 0, text)
                self.root.after(0, self._send)
            else:
                self.root.after(0, lambda: self._add_bubble("Didn't catch that. Try again.", "marcus"))

        except Exception as e:
            self.root.after(0, lambda: self._add_bubble(f"Mic error: {e}", "marcus"))
        finally:
            self._mic_active = False
            self.root.after(0, self.mic_btn.config, {"fg": DIM})

    # ──────────────────────────────────────────
    #  STATUS / ONLINE
    # ──────────────────────────────────────────
    def _set_online(self):
        self._dot.config(fg=GREEN)
        self._status_lbl.config(fg=GREEN, text="  Online")
        self._hdr_dot.config(fg=GREEN)
        self._hdr_status.config(fg=GREEN, text=" Online")

    # ──────────────────────────────────────────
    #  CLEAR CHAT
    # ──────────────────────────────────────────
    def _clear_chat(self):
        for w in self.chat_frame.winfo_children():
            w.destroy()

    # ──────────────────────────────────────────
    #  GLITCH
    # ──────────────────────────────────────────
    def _toggle_glitch(self):
        self.glitch_on = not self.glitch_on
        self.glitch_btn.config(fg=ACCENT if self.glitch_on else DIM)
        if self.glitch_on:
            self._do_glitch()

    def _do_glitch(self):
        if not self.glitch_on:
            return
        g = "".join(random.choices(GLITCH_CHARS, k=random.randint(4, 14)))
        self._add_bubble(g, "marcus")
        self.root.after(random.randint(60, 200), self._do_glitch)

    # ──────────────────────────────────────────
    #  TICKER
    # ──────────────────────────────────────────
    def _animate_ticker(self):
        self.ticker.config(text=f"// {random.choice(TICKER_MSGS)} //")
        self.root.after(3500, self._animate_ticker)


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.withdraw()
    app = MarcusGUI(root)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
import os
import subprocess
import threading
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font as tkfont


class MP3ToVideoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 → MP4 (Blank/Colored Video + Audio + Text)")
        self.root.geometry("760x820")
        self.root.resizable(False, False)

        self.audio_files = []
        self.output_dir = tk.StringVar()
        self.status = tk.StringVar(value="Ready.")
        self.progress = tk.DoubleVar(value=0)
        self.use_batch = tk.BooleanVar(value=False)
        self.keep_mp3_audio = tk.BooleanVar(value=False)   # True = -c:a copy (fastest)

        # Background
        self.bg_color = "#000000"          # default black
        self.bg_color_display = tk.StringVar(value="#000000 (black)")

        # Text overlay
        self.enable_text = tk.BooleanVar(value=False)
        self.text_content = tk.StringVar(value="")
        self.font_family = tk.StringVar(value="Arial")
        self.font_size = tk.IntVar(value=72)
        self.font_color = "#FFFFFF"
        self.font_color_display = tk.StringVar(value="#FFFFFF (white)")
        self.text_position = tk.StringVar(value="center")  # center/top/bottom

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        # Mode
        mode_frame = ttk.LabelFrame(self.root, text="Mode")
        mode_frame.pack(fill="x", **pad)
        ttk.Radiobutton(mode_frame, text="Single MP3",
                        variable=self.use_batch, value=False,
                        command=self._refresh_mode).pack(side="left", padx=10, pady=6)
        ttk.Radiobutton(mode_frame, text="Batch folder (all MP3s)",
                        variable=self.use_batch, value=True,
                        command=self._refresh_mode).pack(side="left", padx=10, pady=6)

        # Audio
        audio_frame = ttk.LabelFrame(self.root, text="Audio")
        audio_frame.pack(fill="x", **pad)
        self.audio_label = ttk.Label(audio_frame, text="No file selected", foreground="gray")
        self.audio_label.pack(side="left", padx=10, pady=8, fill="x", expand=True)
        self.audio_btn = ttk.Button(audio_frame, text="Select MP3…", command=self.select_audio)
        self.audio_btn.pack(side="right", padx=10, pady=8)

        # Output
        out_frame = ttk.LabelFrame(self.root, text="Output folder")
        out_frame.pack(fill="x", **pad)
        self.out_label = ttk.Label(out_frame, text="Not set", foreground="gray")
        self.out_label.pack(side="left", padx=10, pady=8, fill="x", expand=True)
        ttk.Button(out_frame, text="Choose…", command=self.select_output)\
            .pack(side="right", padx=10, pady=8)

        # ---------- Options (AUDIO) ----------
        opt_frame = ttk.LabelFrame(self.root, text="Options")
        opt_frame.pack(fill="x", **pad)
        ttk.Checkbutton(
            opt_frame,
            text="Copy MP3 audio as-is (fastest, no re-encode)",
            variable=self.keep_mp3_audio
        ).pack(anchor="w", padx=10, pady=6)
        ttk.Label(
            opt_frame,
            text="Unchecked = re-encode audio to AAC 192k (recommended for YouTube)",
            foreground="gray"
        ).pack(anchor="w", padx=30, pady=(0, 6))

        # Background color
        bg_frame = ttk.LabelFrame(self.root, text="Video background")
        bg_frame.pack(fill="x", **pad)
        ttk.Label(bg_frame, text="Color:").pack(side="left", padx=10, pady=8)
        self.bg_swatch = tk.Label(bg_frame, text="   ", bg=self.bg_color,
                                  relief="solid", borderwidth=1, width=4)
        self.bg_swatch.pack(side="left", padx=6, pady=8)
        ttk.Label(bg_frame, textvariable=self.bg_color_display).pack(side="left", padx=6)
        ttk.Button(bg_frame, text="Choose color…",
                   command=self.choose_bg_color).pack(side="right", padx=10, pady=8)

        # Text overlay
        text_frame = ttk.LabelFrame(self.root, text="Static text overlay (Nepali / English)")
        text_frame.pack(fill="x", **pad)

        ttk.Checkbutton(text_frame, text="Enable text overlay",
                        variable=self.enable_text).grid(row=0, column=0, columnspan=4,
                                                        sticky="w", padx=10, pady=6)

        ttk.Label(text_frame, text="Text:").grid(row=1, column=0, sticky="w", padx=10, pady=4)
        self.text_entry = ttk.Entry(text_frame, textvariable=self.text_content, width=52)
        self.text_entry.grid(row=1, column=1, columnspan=3, sticky="we", padx=6, pady=4)

        ttk.Label(text_frame, text="Font:").grid(row=2, column=0, sticky="w", padx=10, pady=4)
        self.font_combo = ttk.Combobox(text_frame, textvariable=self.font_family,
                                       values=self._available_fonts(), width=24, state="readonly")
        self.font_combo.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(text_frame, text="Size:").grid(row=2, column=2, sticky="e", padx=6, pady=4)
        ttk.Spinbox(text_frame, from_=8, to=300, textvariable=self.font_size,
                    width=6).grid(row=2, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(text_frame, text="Color:").grid(row=3, column=0, sticky="w", padx=10, pady=4)
        self.font_swatch = tk.Label(text_frame, text="   ", bg=self.font_color,
                                    relief="solid", borderwidth=1, width=4)
        self.font_swatch.grid(row=3, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(text_frame, textvariable=self.font_color_display)\
            .grid(row=3, column=2, sticky="w", padx=6, pady=4)
        ttk.Button(text_frame, text="Choose color…",
                   command=self.choose_font_color).grid(row=3, column=3, sticky="w",
                                                        padx=6, pady=4)

        ttk.Label(text_frame, text="Position:").grid(row=4, column=0, sticky="w", padx=10, pady=4)
        pos_frame = ttk.Frame(text_frame)
        pos_frame.grid(row=4, column=1, columnspan=3, sticky="w", padx=6, pady=4)
        for pos in ("top", "center", "bottom"):
            ttk.Radiobutton(pos_frame, text=pos.capitalize(),
                            variable=self.text_position,
                            value=pos).pack(side="left", padx=6)

        text_frame.columnconfigure(1, weight=1)

        # Progress
        prog_frame = ttk.Frame(self.root)
        prog_frame.pack(fill="x", **pad)
        ttk.Progressbar(prog_frame, variable=self.progress, maximum=100)\
            .pack(fill="x", padx=10, pady=4)

        # Start button
        ttk.Button(self.root, text="▶ Start Conversion", command=self.start_conversion)\
            .pack(pady=8, ipadx=20, ipady=4)

        # Status
        ttk.Label(self.root, textvariable=self.status, foreground="blue")\
            .pack(pady=4)

    def _available_fonts(self):
        fonts = sorted(set(tkfont.families(self.root)))
        preferred = ["Noto Sans Devanagari", "Mangal", "Kalimati",
                     "Arial Unicode MS", "Nirmala UI", "Arial", "DejaVu Sans"]
        ordered = [f for f in preferred if f in fonts]
        ordered += [f for f in fonts if f not in ordered]
        return ordered

    def choose_bg_color(self):
        color = colorchooser.askcolor(color=self.bg_color, title="Choose background color")
        if color and color[1]:
            self.bg_color = color[1]
            self.bg_swatch.config(bg=self.bg_color)
            self.bg_color_display.set(f"{self.bg_color}")

    def choose_font_color(self):
        color = colorchooser.askcolor(color=self.font_color, title="Choose text color")
        if color and color[1]:
            self.font_color = color[1]
            self.font_swatch.config(bg=self.font_color)
            self.font_color_display.set(f"{self.font_color}")

    def _refresh_mode(self):
        self.audio_files = []
        if self.use_batch.get():
            self.audio_btn.config(text="Select folder…")
            self.audio_label.config(text="No folder selected", foreground="gray")
        else:
            self.audio_btn.config(text="Select MP3…")
            self.audio_label.config(text="No file selected", foreground="gray")

    def select_audio(self):
        if self.use_batch.get():
            folder = filedialog.askdirectory(title="Select folder with MP3s")
            if folder:
                self.audio_files = [
                    os.path.join(folder, f)
                    for f in sorted(os.listdir(folder))
                    if f.lower().endswith(".mp3")
                ]
                self.audio_label.config(
                    text=f"{len(self.audio_files)} MP3 file(s) found in {folder}",
                    foreground="black",
                )
        else:
            path = filedialog.askopenfilename(
                title="Select MP3",
                filetypes=[("MP3 files", "*.mp3")]
            )
            if path:
                self.audio_files = [path]
                self.audio_label.config(text=os.path.basename(path), foreground="black")

    def select_output(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_dir.set(folder)
            self.out_label.config(text=folder, foreground="black")

    # ---------- Helpers ----------
    def _hex_to_ffmpeg_color(self, hex_color):
        """Convert #RRGGBB to 0xRRGGBB (ffmpeg color format)."""
        return "0x" + hex_color.lstrip("#").upper()

    def _escape_drawtext(self, text):
        """Escape text for ffmpeg drawtext filter."""
        text = text.replace("\\", "\\\\")
        text = text.replace(":", "\\:")
        text = text.replace("'", "\\'")
        text = text.replace("%", "\\%")
        text = text.replace(",", "\\,")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        return text

    def _fontfile_or_family(self):
        """Return a drawtext font option. Prefer fontfile if we can resolve it."""
        try:
            if os.name == "nt":
                win_fonts = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
                name = self.font_family.get()
                candidates = {
                    "Arial": ["arial.ttf", "ARIAL.TTF"],
                    "Arial Unicode MS": ["arialuni.ttf", "ARIALUNI.TTF"],
                    "Nirmala UI": ["Nirmala.ttf", "NirmalaB.ttf"],
                    "Mangal": ["mangal.ttf", "MANGAL.TTF"],
                    "Kalimati": ["kalimati.ttf"],
                    "Noto Sans Devanagari": ["NotoSansDevanagari-Regular.ttf"],
                }
                for fname in candidates.get(name, []) + [name + ".ttf", name.replace(" ", "") + ".ttf"]:
                    p = os.path.join(win_fonts, fname)
                    if os.path.exists(p):
                        return f"fontfile='{p.replace(chr(92), '/').replace(':', chr(92)+':')}'"
        except Exception:
            pass
        return f"font='{self.font_family.get()}'"

    # ---------- Core ----------
    def start_conversion(self):
        if not self.audio_files:
            messagebox.showerror("Error", "Please select an MP3 file or folder.")
            return
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return
        if self.enable_text.get() and not self.text_content.get().strip():
            messagebox.showerror("Error", "Text overlay is enabled but text is empty.")
            return

        self.progress.set(0)
        threading.Thread(target=self._run_conversion, daemon=True).start()

    def _run_conversion(self):
        try:
            total = len(self.audio_files)
            out_dir = self.output_dir.get()

            self.status.set("Creating base video track…")
            self.root.update_idletasks()

            sig = f"{self.bg_color.lstrip('#')}"
            if self.enable_text.get() and self.text_content.get().strip():
                sig += "_txt"
            blank_path = os.path.join(out_dir, f"_base_1080p_{sig}.mp4")

            if not os.path.exists(blank_path):
                self._make_blank_video(blank_path, duration=4 * 3600)

            for i, audio_path in enumerate(self.audio_files, start=1):
                base = os.path.splitext(os.path.basename(audio_path))[0]
                out_path = os.path.join(out_dir, f"{base}.mp4")

                self.status.set(f"[{i}/{total}] Muxing: {base}")
                self.root.update_idletasks()

                self._mux(blank_path, audio_path, out_path)

                self.progress.set((i / total) * 100)
                self.root.update_idletasks()

            self.status.set(f"✅ Done! {total} video(s) saved.")
            messagebox.showinfo("Success", f"Converted {total} file(s) successfully.")

        except Exception as e:
            self.status.set("❌ Error")
            messagebox.showerror(
                "Conversion error",
                f"{e}\n\n{traceback.format_exc(limit=2)}"
            )

    def _make_blank_video(self, out_path, duration=14400):
        """Create a 1080p solid-color video file, optionally with static text."""
        bg = self._hex_to_ffmpeg_color(self.bg_color)

        vf_parts = []
        if self.enable_text.get() and self.text_content.get().strip():
            text = self._escape_drawtext(self.text_content.get().strip())
            font_opt = self._fontfile_or_family()
            color = self._hex_to_ffmpeg_color(self.font_color)

            pos = self.text_position.get()
            if pos == "top":
                x, y = "(w-text_w)/2", "h*0.08"
            elif pos == "bottom":
                x, y = "(w-text_w)/2", "h-text_h-h*0.08"
            else:
                x, y = "(w-text_w)/2", "(h-text_h)/2"

            drawtext = (
                f"drawtext=text='{text}':{font_opt}:"
                f"fontsize={self.font_size.get()}:fontcolor={color}:"
                f"x={x}:y={y}:"
                f"shadowcolor=black@0.6:shadowx=3:shadowy=3"
            )
            vf_parts.append(drawtext)

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={bg}:s=1920x1080:d={duration}:r=1",
        ]
        if vf_parts:
            cmd += ["-vf", ",".join(vf_parts)]
        cmd += [
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            out_path,
        ]
        self._run_ffmpeg(cmd)

    def _mux(self, blank_path, audio_path, out_path):
        """Combine video track + audio into MP4 (video copied, not re-encoded)."""
        # ---- Audio handling: the fast-mode toggle controls this ----
        if self.keep_mp3_audio.get():
            # FASTEST: stream copy, no re-encode. Output audio stays MP3.
            audio_codec = ["-c:a", "copy"]
        else:
            # Re-encode to AAC (safer for YouTube / broad compatibility).
            audio_codec = ["-c:a", "aac", "-b:a", "192k"]

        cmd = [
            "ffmpeg", "-y",
            "-i", blank_path,
            "-i", audio_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            *audio_codec,
            "-shortest",
            "-movflags", "+faststart",
            out_path,
        ]
        self._run_ffmpeg(cmd)

    def _run_ffmpeg(self, cmd):
        """Run ffmpeg silently, raising on failure."""
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if result.returncode != 0:
            err = result.stderr.decode(errors="replace")
            raise RuntimeError(f"FFmpeg failed:\n{err[-1500:]}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MP3ToVideoGUI(root)
    root.mainloop()
    # ---------- Created By https://github.com/BibekRai-np ----------
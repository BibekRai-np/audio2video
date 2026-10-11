import os
import subprocess
import threading
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class MP3ToVideoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 → MP4 (Fast Mode: Blank Video + Audio)")
        self.root.geometry("720x520")
        self.root.resizable(False, False)

        self.audio_files = []
        self.output_dir = tk.StringVar()
        self.status = tk.StringVar(value="Ready.")
        self.progress = tk.DoubleVar(value=0)
        self.use_batch = tk.BooleanVar(value=False)
        self.keep_mp3_audio = tk.BooleanVar(value=False)   # True = -c:a copy

        self._build_ui()

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

        # Options
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

        # Progress
        prog_frame = ttk.Frame(self.root)
        prog_frame.pack(fill="x", **pad)
        ttk.Progressbar(prog_frame, variable=self.progress, maximum=100)\
            .pack(fill="x", padx=10, pady=4)

        # Start button
        ttk.Button(self.root, text="▶ Start Conversion", command=self.start_conversion)\
            .pack(pady=10, ipadx=20, ipady=4)

        # Status
        ttk.Label(self.root, textvariable=self.status, foreground="blue")\
            .pack(pady=4)

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

    # ---------- Core ----------
    def start_conversion(self):
        if not self.audio_files:
            messagebox.showerror("Error", "Please select an MP3 file or folder.")
            return
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return

        self.progress.set(0)
        threading.Thread(target=self._run_conversion, daemon=True).start()

    def _run_conversion(self):
        try:
            total = len(self.audio_files)
            blank_path = os.path.join(self.output_dir.get(), "_blank_1080p.mp4")

            # Build blank video once (2 hours = 7200s, we make 4 hours to be safe)
            self.status.set("Creating blank 1080p video track…")
            self.root.update_idletasks()
            if not os.path.exists(blank_path):
                self._make_blank_video(blank_path, duration=4 * 3600)

            for i, audio_path in enumerate(self.audio_files, start=1):
                base = os.path.splitext(os.path.basename(audio_path))[0]
                out_path = os.path.join(self.output_dir.get(), f"{base}.mp4")

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
        """Create a single 1080p with a Teal background."""
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x0F766E:s=1920x1080:d={duration}:r=1",   # Your Teal 
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            out_path,
        ]
        self._run_ffmpeg(cmd)

    def _mux(self, blank_path, audio_path, out_path):
        """Combine blank video + audio into MP4 (video is copied, not re-encoded)."""
        if self.keep_mp3_audio.get():
            audio_codec = ["-c:a", "copy"]
        else:
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
# 🎵→🎬 audio2video

**Convert MP3 files into YouTube-ready MP4 videos with custom backgrounds and static text overlays (Nepali & English) — fast, GUI-based, and powered by FFmpeg.**

---

## ✨ Features

- 🎵 **Single MP3 or Batch folder** conversion
- 🎨 **Customizable background color** (default: black)
- 📝 **Static text overlay** for the entire video duration
  - Full **Nepali (Devanagari)** and **English** support
  - Adjustable font family, size, color, and position (top / center / bottom)
  - Soft shadow for readability on any background
- ⚡ **Fast Mode** — copy MP3 audio as-is (no re-encode) for near-instant conversions
- 🎧 **High-quality AAC 192k** re-encode option (recommended for YouTube)
- 🖼️ Fixed **1080p (1920×1080)** output
- 📦 **Smart caching** — the base video is generated once and reused across files with the same settings
- 🚀 **`+faststart`** flag for web-optimized MP4s
- 🖱️ **Zero config** — pick a file, pick a color, click Start

---

## 🖼️ Preview

```
┌─────────────────────────────────────────┐
│  Mode:   ● Single MP3   ○ Batch folder  │
│  Audio:  [ Select MP3… ]                │
│  Output: [ Choose… ]                    │
│  Options:                               │
│    ☐ Copy MP3 audio as-is (fastest)     │
│  Background: [ ■ ] Choose color…        │
│  Text overlay:                          │
│    ☑ Enable   Text: [ नमस्ते ]           │
│    Font: [Nirmala UI ▾]  Size: [72]     │
│    Color: [ ■ ] Position: ○top ●center  │
│                                         │
│  ▶ Start Conversion                     │
│  [████████████░░░░░░░░]  62%            │
└─────────────────────────────────────────┘
```

---

## 🖥️ Requirements

### System

| Component | Version / Notes |
|-----------|-----------------|
| **OS** | Windows 10/11 (primary), Linux & macOS supported |
| **Python** | 3.8 or newer |
| **FFmpeg** | Must be installed and on your system `PATH` |
| **Disk space** | ~200 MB free for the cached base video |

### Python Dependencies

This project uses **only the Python Standard Library** — no `pip install` required.

Modules used:
- `os`, `subprocess`, `threading`, `traceback`
- `tkinter` (+ `ttk`, `filedialog`, `messagebox`, `colorchooser`, `font`)

> ⚠️ **Tkinter** ships with Python on Windows and macOS, but may need a separate install on Linux.

**Verify Tkinter:**
```bash
python -c "import tkinter; print(tkinter.TkVersion)"
```

**Install Tkinter if missing:**

| OS | Command |
|----|---------|
| Ubuntu / Debian | `sudo apt install python3-tk` |
| Fedora / RHEL | `sudo dnf install python3-tkinter` |
| Arch Linux | `sudo pacman -S tk` |
| macOS (Homebrew) | `brew install python-tk` |
| Windows | Re-run Python installer → check **"tcl/tk and IDLE"** |

---

## 🔧 Installation

### 1. Install Python 3.8+

Download from [python.org](https://www.python.org/downloads/).

> **Windows users:** during install, check:
> - ✅ Add Python to PATH
> - ✅ tcl/tk and IDLE

### 2. Install FFmpeg

#### Windows
1. Download from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) (`ffmpeg-release-essentials.zip`)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System **PATH**
4. Verify in a new terminal:
   ```cmd
   ffmpeg -version
   ```

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu / Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Clone the Repo

```bash
git clone https://github.com/YOUR_USERNAME/audio2video.git
cd audio2video
```

### 4. (Optional) Install Nepali-Friendly Fonts

For correct Devanagari conjunct rendering (क्ष, त्र, ज्ञ, etc.):

| Font | Windows | Linux | macOS |
|------|---------|-------|-------|
| **Nirmala UI** | ✅ Pre-installed | — | — |
| **Mangal** | ✅ Pre-installed | `sudo apt install fonts-lohit-deva` | — |
| **Noto Sans Devanagari** | [Download](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari) | `sudo apt install fonts-noto-devanagari` | `brew install --cask font-noto-sans-devanagari` |
| **Kalimati** | — | `sudo apt install ttf-devanagari-fonts` | — |

---

## ▶️ Usage

Run the app:

```bash
python audio2video.py
```

### Step-by-step

1. **Mode** — pick **Single MP3** or **Batch folder**
2. **Audio** — select your `.mp3` file or a folder of MP3s
3. **Output folder** — where to save the MP4s
4. **Options** — choose audio handling:
   - ✅ Copy MP3 audio as-is → **fastest** (no re-encode)
   - ⬜ Unchecked → re-encode to **AAC 192k** (best for YouTube)
5. **Video background** — pick any color (default: black)
6. **Static text overlay** *(optional)*:
   - Enable the checkbox
   - Type text (Nepali or English)
   - Choose font, size, color, position
7. Click **▶ Start Conversion**

The progress bar fills as files are processed. A success dialog appears when done.

---

## 📂 Output

- All MP4s are saved to the chosen output folder
- A base file like `_base_1080p_000000.mp4` is created once and **reused** for all files with the same background/text settings
- Safe to delete at any time — it will regenerate on the next run

### File size reference (per 1 hour of audio)

| Setting | Approx. size |
|---------|--------------|
| Copy audio + blank video | ~30–60 MB |
| AAC 192k + blank video | ~90–100 MB |

Since the video is a static frame, size is dominated by the audio track.

---

## 🧠 How It Works

1. **Base video generation** — FFmpeg creates a 4-hour 1080p solid-color video, optionally with a `drawtext` filter for the static text. Encoded once with:
   ```
   libx264 -preset ultrafast -tune stillimage
   ```
2. **Muxing** — for each MP3:
   - Video is stream-copied (`-c:v copy`) — no re-encoding
   - Audio is either copied (`-c:a copy`) or re-encoded to AAC
   - Output is trimmed to the shorter stream (`-shortest`)
   - `+faststart` moves the moov atom to the front for instant web playback

This makes typical conversions **nearly instant**.

---

## 🛠️ Customization

Want different defaults? Edit the script:

| Setting | Location | Default |
|---------|----------|---------|
| Resolution | `_make_blank_video()` → `s=1920x1080` | 1080p |
| Base duration | `_make_blank_video(..., duration=4*3600)` | 4 hours |
| AAC bitrate | `_mux()` → `"192k"` | 192 kbps |
| Frame rate | `_make_blank_video()` → `r=1` | 1 fps |
| Default text size | `self.font_size = tk.IntVar(value=72)` | 72 |
| Shadow | `_make_blank_video()` → `shadowx=3:shadowy=3` | 3 px |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ffmpeg is not recognized` | FFmpeg isn't on PATH. Re-check install step 2, open a new terminal |
| `No module named 'tkinter'` | Install the Tk package for your OS (table above) |
| Nepali text shows as boxes | Font doesn't support Devanagari. Try **Nirmala UI** or **Mangal** (Windows), or install **Noto Sans Devanagari** |
| "Text overlay is enabled but text is empty" | Add text or disable the checkbox |
| First conversion is slow | The base video is generated once. Later files reuse the cache |
| Audio gets cut off | Base video is 4 hours long. Increase `duration` in `_make_blank_video()` for longer inputs |
| `FFmpeg failed:` error box | Check the message — common causes: corrupted MP3, unsupported codec, or a full/read-only output folder |

---

## 🗺️ Roadmap

- [ ] Multi-line text with auto-wrap
- [ ] Image / logo watermark overlay
- [ ] Custom resolution (720p / 1440p / 4K)
- [ ] Subtitles from SRT files
- [ ] Command-line interface (CLI) mode
- [ ] Drag-and-drop support
- [ ] Preset save / load

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-idea`
3. Commit your changes: `git commit -m "Add amazing idea"`
4. Push: `git push origin feature/amazing-idea`
5. Open a Pull Request

Please keep the code style consistent and test on at least one OS before submitting.

---

## 📜 License

Released under the **MIT License** — free for personal and commercial use.
See [LICENSE](LICENSE) for details.

> FFmpeg is a separate project governed by its own license — see [ffmpeg.org/legal.html](https://ffmpeg.org/legal.html).

---

## 🙏 Credits

- **FFmpeg** — the engine behind all conversions
- **Tkinter** — Python's built-in GUI toolkit
- **Noto / Nirmala / Mangal / Kalimati** — Nepali (Devanagari) rendering support
- Inspired by every podcaster who just wanted a quick MP4 🎙️

---

## ⭐ Show Your Support

If **audio2video** saved you time, give it a ⭐ on GitHub — it helps others discover the project!

---

## 📌 Quick Start (TL;DR)

```bash
# 1. Install FFmpeg
#    Windows: add C:\ffmpeg\bin to PATH
#    macOS:   brew install ffmpeg
#    Linux:   sudo apt install ffmpeg

# 2. Ensure Tkinter is available
python -c "import tkinter; print('OK')"

# 3. Run
python audio2video.py
```

**Turn sound into screen — in one click.** 🎬🎧

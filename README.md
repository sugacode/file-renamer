# ✦ File Renamer

A lightweight, browser-based file renaming tool built with pure Python — no third-party libraries required.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![License](https://img.shields.io/badge/license-MIT-purple)

---

## Features

- **4 rename modes** — Date/Time, Sequential, Custom Pattern, and Manual Rename
- **Live preview** — see new filenames before committing any changes
- **Batch rename** — process an entire folder at once
- **Browser UI** — runs locally, opens automatically in your default browser
- **Zero installation** — uses only Python's built-in standard library (`http.server`, `json`, `pathlib`, `datetime`)

---

## Requirements

- Python 3.8 or newer
- Any modern web browser (Chrome, Firefox, Safari, Edge)

---

## Getting Started

```bash
python3 file_renamer.py
```

The app starts a local server and opens **http://localhost:7474** in your browser automatically.

To stop the server, press `Ctrl+C` in the terminal.

---

## Usage

### Step 1 — Select Files

1. Enter the **full folder path** where your files are located (e.g. `/Users/you/Downloads/photos`)
2. Click the drop zone or drag & drop files to select which ones to rename

### Step 2 — Choose a Format

Pick one of four rename modes:

| Mode | Description | Example |
|---|---|---|
| 📅 **Date / Time** | Prepend or append today's date/time | `2026-05-11_report.pdf` |
| 🔢 **Sequential** | Number files in order | `001_photo.jpg`, `002_photo.jpg` |
| ✏️ **Custom Pattern** | Build a name using placeholders | `{date}_{UPPER}_{num}.jpg` |
| 🖊️ **Manual Rename** | Type a unique name for each file individually | anything you want |

### Step 3 — Preview & Rename

- The preview table updates live as you adjust options
- Click **▶ Rename Files** — a confirmation dialog appears before anything changes

---

## Rename Modes

### 📅 Date / Time

Adds the current date (or time) to each filename.

| Option | Description | Example |
|---|---|---|
| Date Format | Python `strftime` format string | `%Y-%m-%d` → `2026-05-11` |
| Separator | Character between date and name | `_`, `-`, `.` |
| Position | Add before or after the original name | Prefix / Suffix |

Common date format codes:

```
%Y  — 4-digit year        (2026)
%m  — 2-digit month       (05)
%d  — 2-digit day         (11)
%b  — abbreviated month   (May)
%H  — hour (24h)          (14)
%M  — minutes             (30)
```

### 🔢 Sequential Number

Numbers each file in order.

| Option | Description | Default |
|---|---|---|
| Start Number | First number in the sequence | `1` |
| Pad Width | Zero-pad width | `3` (→ `001`) |
| Separator | Character between number and name | `_` |
| Position | Number goes before or after the name | Prefix |

### ✏️ Custom Pattern

Build any filename using placeholders. Click a placeholder tag in the UI to insert it.

| Placeholder | Replaced with |
|---|---|
| `{name}` | Original filename (without extension) |
| `{date}` | Today's date (`YYYY-MM-DD`) |
| `{time}` | Current time (`HH-MM-SS`) |
| `{num}` | Sequence number (zero-padded) |
| `{UPPER}` | Original name in UPPERCASE |
| `{lower}` | Original name in lowercase |

**Example pattern:** `{date}_{UPPER}_{num}` on `report.pdf` → `2026-05-11_REPORT_001.pdf`

### 🖊️ Manual Rename

An editable table appears in the preview panel — type a brand-new name for each file.

- The file **extension is preserved automatically**
- Leave a field **blank** to skip renaming that file
- Press **Tab** or **Enter** to jump to the next row
- **↺ Reset All** — reverts all fields to original names
- **⚡ Fill from pattern** — auto-fills all rows using a pattern, then tweak individually

---

## Project Structure

```
file_renamer.py   # Single-file app — server + HTML UI bundled together
README.md         # This file
```

---

## How It Works

The script starts a minimal HTTP server on `localhost:7474`. The entire UI is an HTML page served from within the Python file itself. The browser communicates with the server via two JSON endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Serves the HTML UI |
| `/preview` | POST | Returns a preview of renamed filenames (no files touched) |
| `/rename` | POST | Performs the actual renaming on disk |

---

## Notes & Tips

- **The folder path you enter must exist on disk** — the app won't create folders for you
- File extensions are always preserved unless you explicitly include a different one in Manual mode
- The preview is generated fresh each time; click **🔍 Refresh Preview** to force an update
- Renaming is **permanent** — there is no undo, so always check the preview first

---

## License

MIT — free to use, modify, and distribute.

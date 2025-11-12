# NexusAutoDL
NexusAutoDL automates the “Download” / “Download with Vortex” flow on [Nexus Mods](https://www.nexusmods.com/).  
It watches one or more monitors, detects the various download buttons (legacy and “New” layouts), and clicks through the dialogs so you can walk away while a Vortex or browser download queue drains.

> ⚠️ **Terms of Service** – Automating Nexus Mods is against their TOS. Use this project at your own risk.

## Highlights
- **Multi-monitor aware** screen capture that can constrain to the primary display with `--force-primary`.
- **Vortex integration**: the scanner can position Vortex and a browser window, keep them visible, and handle the “Staging” / “Understood” pop‑ups in legacy mode.
- **Smart detector**: SIFT templates for classic and “New” download buttons, plus optional debug frames that show each match.
- **Simulation mode** for headless validation and CI, and a `validate.py` script to verify that assets and imports are wired up correctly.

## Requirements
- Python **3.9 or newer**.
- Windows for real automation (requires `pywin32` for window management).  
  macOS/Linux can still run in `--simulate` mode for development.
- Screen configured so that Vortex/browser windows are visible (or pin them with `--window-title` / `--browser`).

Install the Python dependencies with:

```bash
pip install -r requirements.txt
```

## Quick Start
```bash
git clone https://github.com/jaylann/NexusAutoDL
cd NexusAutoDL

# Optional but recommended
python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt

# Dry run (no clicking) with synthetic data
python main.py --simulate --verbose

# Real run: Vortex + Chrome on the primary monitor
python main.py --vortex --browser chrome --window-title "Nexus Mods"
```

When running against the live UI, keep Vortex and your browser visible.  
On multi-monitor setups you can either let NexusAutoDL watch the entire virtual desktop or limit it to the primary monitor with `--force-primary`.

## Command Line Options
| Option | Description |
| --- | --- |
| `--browser {chrome,firefox}` | Tell NexusAutoDL which browser window to launch/move (must be paired with `--vortex` unless you also pass `--simulate`). |
| `--vortex` | Enables the Vortex-aware workflow (window positioning + popup handling + dialog clicks). |
| `--legacy` | Use the legacy button templates and handle the “Staging” / “Understood” dialogs. Leave this off to target the new green download buttons only. |
| `--debug-frame-dir PATH` | Save every detection frame (with bounding boxes + metadata overlay) to help diagnose false positives. |
| `--verbose` | Print detailed logs from detectors, window manager, and scanner state machine. |
| `--force-primary` | Capture only the primary monitor even if others are connected. |
| `--window-title TEXT` | Move any window whose title contains `TEXT` into view before scanning starts. |
| `--min-matches INT` / `--ratio FLOAT` | Fine tune the SIFT descriptor thresholds (defaults: 8 matches, ratio 0.75). |
| `--click-delay FLOAT` | Delay between scan iterations (seconds). |
| `--simulate` | Skip real screen capture and clicking. Useful for dev + CI. |

Run `python main.py --help` for the full list.

## Debugging & Validation
- `python validate.py` – ensures the models import, templates exist, and required assets are present.
- `--debug-frame-dir ./frames` – look at the PNG output to see *exactly* what the detector is clicking. Handy for multi-monitor setups.
- `--simulate` + `--verbose` – combine these flags to follow the state machine without touching your desktop.

## Tips
- Keep Vortex and your browser window un-minimized and visible. The detector looks for the buttons inside the captured region.
- Use the new buttons by default. Drop down to `--legacy` only if you are on an older Nexus layout or the new templates fail to match.
- If you get repeated false positives, inspect the debug frames and tighten `--min-matches` or lower the Lowe ratio (`--ratio`).

## Demo
https://user-images.githubusercontent.com/61842101/202874471-d5700912-16fd-4b7e-ab3f-0b97d05f6d9e.mp4

## Credit
Inspired by [nexus-autodl](https://github.com/parsiad/nexus-autodl).  
Thanks to the broader modding community for templates, testing, and ideas.

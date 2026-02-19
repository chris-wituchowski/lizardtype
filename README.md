# 🦎 LizardType — Typing Trainer

A fun typing game for kids who love reptiles and sea creatures!

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-green)

## Features

- **Two Modes** — Choose between 🦎 Reptiles or 🐠 Sea Creatures
- **Easy Mode** — Type the common name (e.g. "Green Iguana" or "Clownfish")
- **Hard Mode** — Type the scientific name (e.g. "Iguana iguana" or "Amphiprion ocellaris")
- 🖼️ Real animal photos from Wikimedia Commons (all freely licensed)
- 🎨 Theme-specific visuals — jungle leaves for reptiles, rising bubbles for ocean
- 🔤 Underline-style typing prompt that fills in as you type
- 💡 Hint button reveals one letter at a time
- 🎉 Confetti celebration on correct answers
- 📊 Score tracking with streak counter
- 🦎 90+ reptiles including geckos, turtles, snakes, and crocodiles
- 🐠 80+ sea creatures including sharks, whales, octopuses, and jellyfish
- 👶 All images are child-appropriate (no feeding/predation scenes)

## Requirements

- Internet connection (for first-time image downloads; images are cached locally)

## Download & Play

The easiest way to get LizardType is to download a pre-built executable — **no Python installation required**.

1. Go to the [**Latest Release**](https://github.com/chris-wituchowski/lizardtype/releases/latest)
2. Download the file for your platform:
   - **Windows** → `LizardType-Windows.exe`
   - **Linux** → `LizardType-Linux`
3. Run the executable and start typing!

> **Linux users:** You may need to make the file executable first: `chmod +x LizardType-Linux`

---

## Running from Source (Developer Setup)

If you prefer to run from source or want to contribute:

**Requirements:** Python 3.10 or higher

```bash
# Clone the repository
git clone <your-repo-url>
cd LizardType

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running from Source

```bash
python run.py
```

Or directly:

```bash
python src/game.py
```

### Building an Executable

To build a standalone executable locally:

```bash
python build.py
```

The output will be in the `dist/` folder.

## How to Play

1. Choose **Reptiles** 🦎 or **Sea Creatures** 🐠 from the main menu
2. Select **Easy Mode** or **Hard Mode**
3. An animal photo appears — type the name in the underline prompt
4. Click **Hint** (or keep clicking) to reveal letters one at a time
5. Press **Enter** or click **Submit** to check your answer
6. Click **Skip** if you're stuck
7. Try to get the highest score and longest streak!

### Scoring
- **10 points** for a correct answer with no hints
- **−2 points per hint** used (minimum 1 point per correct answer)
- Streaks are tracked — see how many you can get in a row!

## Controls

| Key / Button | Action |
|---|---|
| Type letters | Fill in the animal name |
| Backspace | Delete last character |
| Enter | Submit answer |
| Escape | Return to menu |
| Hint button | Reveal next letter |
| Skip button | Skip to next animal |

## Image Credits

All images are sourced from **Wikimedia Commons** under free licenses
(CC-BY, CC-BY-SA, or Public Domain). Individual credits are shown beneath each
image during gameplay. This application is for personal/educational use only.

## Project Structure

```
LizardType/
├── run.py                  # Launcher script
├── requirements.txt        # Python dependencies
├── README.md
├── src/
│   ├── game.py             # Main game (Pygame)
│   ├── reptile_data.py     # Reptile database (names, facts, image filenames)
│   ├── sea_creature_data.py # Sea creature database (names, facts, image filenames)
│   └── image_manager.py    # Image downloader & cache manager
└── image_cache/            # Auto-created; cached downloaded images
```

## License

This project is for personal and educational use. All reptile photographs are
used under their respective Wikimedia Commons licenses.

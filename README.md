# 🦎 LizardType — Reptile Typing Trainer

A fun typing game for kids who love reptiles!

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-green)

## Features

- **Easy Mode** — Type the common name of the reptile (e.g. "Green Iguana")
- **Hard Mode** — Type the scientific name (e.g. "Iguana iguana")
- 🖼️ Real reptile photos from Wikimedia Commons (all freely licensed)
- 🔤 Underline-style typing prompt that fills in as you type
- 💡 Hint button reveals one letter at a time
- 🎉 Confetti celebration on correct answers
- 📊 Score tracking with streak counter
- 🦎 15 different reptiles including geckos, turtles, snakes, and crocodiles
- 👶 All images are child-appropriate (no feeding/predation scenes)

## Requirements

- Python 3.10 or higher
- Internet connection (for first-time image downloads; images are cached locally)

## Installation

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

## Running the Game

```bash
python run.py
```

Or directly:

```bash
python src/game.py
```

## How to Play

1. Choose **Easy Mode** or **Hard Mode** from the main menu
2. A reptile photo appears — type the name in the underline prompt
3. Click **Hint** (or keep clicking) to reveal letters one at a time
4. Press **Enter** or click **Submit** to check your answer
5. Click **Skip** if you're stuck
6. Try to get the highest score and longest streak!

### Scoring
- **10 points** for a correct answer with no hints
- **−2 points per hint** used (minimum 1 point per correct answer)
- Streaks are tracked — see how many you can get in a row!

## Controls

| Key / Button | Action |
|---|---|
| Type letters | Fill in the reptile name |
| Backspace | Delete last character |
| Enter | Submit answer |
| Escape | Return to menu |
| Hint button | Reveal next letter |
| Skip button | Skip to next reptile |

## Image Credits

All reptile images are sourced from **Wikimedia Commons** under free licenses
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
│   ├── reptile_data.py     # Reptile database (names, facts, image URLs)
│   └── image_manager.py    # Image downloader & cache manager
└── image_cache/            # Auto-created; cached downloaded images
```

## License

This project is for personal and educational use. All reptile photographs are
used under their respective Wikimedia Commons licenses.

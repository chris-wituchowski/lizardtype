"""
Image manager: downloads reptile images from Wikimedia Commons and caches them locally.
All images are freely licensed (CC-BY / CC-BY-SA / Public Domain) from Wikimedia Commons.

Uses the Wikimedia Commons API (action=query) to resolve image URLs, which is the
recommended approach and avoids thumbnail-URL rate limiting (HTTP 429).
"""

import os
import io
import re
import hashlib
import time
import pygame
import requests
from PIL import Image as PILImage


CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "image_cache")

# Wikimedia requires a descriptive User-Agent for API access.
# See https://meta.wikimedia.org/wiki/User-Agent_policy
#
# We use two sessions:
#   _API_SESSION  – for the Wikimedia Commons API (action=query).
#   _DL_SESSION   – for downloading the actual image files from upload.wikimedia.org.
#                   This server rejects generic bot UAs (HTTP 403), so we use a
#                   descriptive desktop-browser-style string per Wikimedia policy.

_API_SESSION = requests.Session()
_API_SESSION.headers.update({
    "User-Agent": (
        "LizardType/1.0 "
        "(Personal educational reptile typing game; "
        "https://github.com/example/LizardType; "
        "lizardtype@example.com)"
    ),
})

_DL_SESSION = requests.Session()
_DL_SESSION.headers.update({
    "User-Agent": (
        "LizardType/1.0 "
        "(Personal educational reptile typing game) "
        "AppleWebKit/537.36 (KHTML, like Gecko)"
    ),
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
})

# Minimum delay between network requests (seconds) to be polite to Wikimedia.
_MIN_REQUEST_DELAY = 0.5
_last_request_time = 0.0


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _polite_delay():
    """Sleep if needed so we don't hammer the server."""
    global _last_request_time
    now = time.monotonic()
    elapsed = now - _last_request_time
    if elapsed < _MIN_REQUEST_DELAY:
        time.sleep(_MIN_REQUEST_DELAY - elapsed)
    _last_request_time = time.monotonic()


def _safe_filename(name: str) -> str:
    """Turn a commons filename into a safe local cache name."""
    h = hashlib.md5(name.encode()).hexdigest()
    return f"{h}.png"


def _resolve_url_via_api(commons_filename: str, width: int = 640) -> str | None:
    """
    Use the Wikimedia Commons API to get a thumbnail URL for a given filename.
    The commons_filename should be just the file part, e.g. "Iguana_iguana_Portoviejo_02.jpg".
    """
    # Strip any "File:" prefix the caller might have included
    commons_filename = re.sub(r"^(?:File|Image):", "", commons_filename, flags=re.IGNORECASE)

    api_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": f"File:{commons_filename}",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": str(width),
        "format": "json",
    }

    _polite_delay()
    try:
        resp = _API_SESSION.get(api_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            ii = page.get("imageinfo", [{}])[0]
            # thumburl is the width-limited version; url is the original
            return ii.get("thumburl") or ii.get("url")
    except Exception as e:
        print(f"  API lookup failed for {commons_filename}: {e}")

    return None


def download_image(commons_filename: str) -> str | None:
    """
    Download an image from Wikimedia Commons and cache it locally.

    `commons_filename` is the Wikimedia Commons file name, e.g.
        "Iguana_iguana_Portoviejo_02.jpg"

    Returns the local file path, or None on failure.
    """
    _ensure_cache_dir()
    local_name = _safe_filename(commons_filename)
    filepath = os.path.join(CACHE_DIR, local_name)

    # Already cached?
    if os.path.exists(filepath):
        return filepath

    # Resolve the real download URL via the API
    url = _resolve_url_via_api(commons_filename)
    if url is None:
        print(f"  Could not resolve URL for: {commons_filename}")
        return None

    # Download the actual image bytes (with retry on 429/403)
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        _polite_delay()
        try:
            resp = _DL_SESSION.get(url, timeout=20)
            if resp.status_code == 429:
                wait = float(resp.headers.get("Retry-After", 2 * attempt))
                print(f"  Rate-limited (429). Waiting {wait}s (attempt {attempt}/{max_retries})...")
                time.sleep(wait)
                continue
            resp.raise_for_status()

            # Convert to PNG via Pillow for consistency
            img = PILImage.open(io.BytesIO(resp.content))
            img = img.convert("RGBA")
            img.save(filepath, "PNG")
            print(f"  Cached: {commons_filename}")
            return filepath
        except Exception as e:
            print(f"  Download attempt {attempt} failed for {commons_filename}: {e}")
            if attempt < max_retries:
                time.sleep(1.5 * attempt)

    return None


def load_pygame_image(commons_filename: str, target_size: tuple[int, int] = (400, 300)) -> pygame.Surface | None:
    """Download (if needed) and load an image as a pygame Surface, scaled to target_size."""
    filepath = download_image(commons_filename)
    if filepath is None:
        return None

    try:
        image = pygame.image.load(filepath).convert_alpha()
        # Scale while maintaining aspect ratio
        img_w, img_h = image.get_size()
        target_w, target_h = target_size
        scale = min(target_w / img_w, target_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        image = pygame.transform.smoothscale(image, (new_w, new_h))
        return image
    except Exception as e:
        print(f"Warning: Could not load image {filepath}: {e}")
        return None


def create_placeholder_surface(text: str, size: tuple[int, int] = (400, 300)) -> pygame.Surface:
    """Create a placeholder surface with text when an image can't be loaded."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((60, 100, 60, 255))

    font = pygame.font.SysFont("Arial", 20)
    lines = [
        "Image not available",
        f"Reptile: {text}",
        "(Check your internet connection)",
    ]
    y = size[1] // 2 - len(lines) * 15
    for line in lines:
        try:
            rendered = font.render(line, True, (255, 255, 255))
        except Exception:
            rendered = font.render(line.encode("ascii", "replace").decode(), True, (255, 255, 255))
        rect = rendered.get_rect(center=(size[0] // 2, y))
        surface.blit(rendered, rect)
        y += 30

    return surface

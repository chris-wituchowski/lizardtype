"""
LizardType — A Reptile Typing Trainer Game
============================================
A fun typing game for kids who love reptiles!

Easy mode:  Type the common name of the reptile shown.
Hard mode:  Type the scientific name of the reptile shown.

Features:
  - Beautiful reptile photos from Wikimedia Commons (all freely licensed)
  - Underline-style typing prompt that fills in as you type
  - Hint button reveals one letter at a time
  - Fun facts shown after each correct answer
  - Score tracking and streak counter
  - Animated confetti celebration on correct answers
  - Child-appropriate images only

Cross-platform: Windows & Linux compatible.
"""

import os
import sys
import random
import math
import threading
import unicodedata
import pygame

# ---------------------------------------------------------------------------
# Ensure src/ is on the path so sibling modules can be imported when running
# this file directly (e.g.  python src/game.py  from the repo root).
# ---------------------------------------------------------------------------
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from reptile_data import REPTILES
from image_manager import load_pygame_image, create_placeholder_surface

# ── Colour palette ─────────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
BG_GREEN    = (34, 85, 34)
DARK_GREEN  = (20, 60, 20)
LEAF_GREEN  = (60, 140, 60)
LIGHT_GREEN = (144, 200, 80)
GOLD        = (255, 210, 60)
ORANGE      = (240, 150, 30)
RED         = (220, 60, 60)
SOFT_WHITE  = (245, 245, 235)
HINT_BLUE   = (80, 160, 240)
SUBMIT_GREEN = (50, 180, 80)
GRAY        = (160, 160, 160)
SHADOW      = (0, 0, 0, 80)
TRANSPARENT_BG = (0, 0, 0, 140)

# ── Layout constants ───────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 900, 700
IMAGE_SIZE = (420, 320)
FPS = 60

# ── Game states ────────────────────────────────────────────────────────────
STATE_MENU      = "menu"
STATE_PLAYING   = "playing"
STATE_CORRECT   = "correct"
STATE_WRONG     = "wrong"
STATE_GAME_OVER = "game_over"


# ═══════════════════════════════════════════════════════════════════════════
#  Confetti particle for celebration
# ═══════════════════════════════════════════════════════════════════════════
class ConfettiParticle:
    COLOURS = [GOLD, ORANGE, LIGHT_GREEN, HINT_BLUE, RED, (200, 80, 220), WHITE]

    def __init__(self):
        self.x = random.randint(0, SCREEN_W)
        self.y = random.randint(-SCREEN_H, 0)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(1.5, 4.5)
        self.size = random.randint(4, 9)
        self.colour = random.choice(self.COLOURS)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-5, 5)
        self.life = random.randint(80, 180)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.angle += self.spin
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        alpha = max(0, min(255, self.life * 3))
        s.fill((*self.colour[:3], alpha))
        rotated = pygame.transform.rotate(s, self.angle)
        surface.blit(rotated, (int(self.x), int(self.y)))


# ═══════════════════════════════════════════════════════════════════════════
#  Floating leaf background particle
# ═══════════════════════════════════════════════════════════════════════════
class LeafParticle:
    def __init__(self):
        self.reset()
        self.y = random.uniform(0, SCREEN_H)

    def reset(self):
        self.x = random.uniform(-20, SCREEN_W + 20)
        self.y = random.uniform(-40, -10)
        self.vy = random.uniform(0.3, 1.0)
        self.vx = random.uniform(-0.3, 0.3)
        self.size = random.randint(5, 12)
        self.colour = random.choice([LEAF_GREEN, LIGHT_GREEN, (80, 160, 50)])
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-2, 2)
        self.sway_offset = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.01, 0.03)
        self.tick = 0

    def update(self):
        self.tick += 1
        self.y += self.vy
        self.x += self.vx + math.sin(self.tick * self.sway_speed + self.sway_offset) * 0.4
        self.angle += self.spin
        if self.y > SCREEN_H + 20:
            self.reset()

    def draw(self, surface):
        s = pygame.Surface((self.size, self.size * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*self.colour, 120), (0, 0, self.size, self.size * 2))
        rotated = pygame.transform.rotate(s, self.angle)
        surface.blit(rotated, (int(self.x), int(self.y)))


# ═══════════════════════════════════════════════════════════════════════════
#  Button helper
# ═══════════════════════════════════════════════════════════════════════════
class Button:
    def __init__(self, rect, text, colour, text_colour=WHITE, font_size=22, border_radius=12):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.colour = colour
        self.text_colour = text_colour
        self.font_size = font_size
        self.border_radius = border_radius
        self.hovered = False

    def draw(self, surface, font=None):
        col = tuple(min(c + 30, 255) for c in self.colour[:3]) if self.hovered else self.colour
        # shadow
        shadow_rect = self.rect.move(3, 3)
        pygame.draw.rect(surface, (0, 0, 0, 60), shadow_rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, col, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=self.border_radius)

        if font is None:
            font = pygame.font.SysFont("Arial", self.font_size, bold=True)
        txt = font.render(self.text, True, self.text_colour)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
#  Main Game class
# ═══════════════════════════════════════════════════════════════════════════
class LizardTypeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("LizardType — Reptile Typing Trainer!")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title   = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 26)
        self.font_body    = pygame.font.SysFont("Arial", 22)
        self.font_typing  = pygame.font.SysFont("Courier New", 32, bold=True)
        self.font_under   = pygame.font.SysFont("Courier New", 32)
        self.font_small   = pygame.font.SysFont("Arial", 18)
        self.font_big     = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_btn     = pygame.font.SysFont("Arial", 22, bold=True)

        # Background leaves
        self.leaves = [LeafParticle() for _ in range(30)]

        # Game state
        self.state = STATE_MENU
        self.difficulty = "easy"      # "easy" or "hard"
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.round_num = 0
        self.total_rounds = 15
        self.typed_text = ""
        self.hint_count = 0
        self.hints_used_total = 0
        self.hint_active = False       # True while the hint button is held down
        self.hint_used_this_round = False
        self.confetti: list[ConfettiParticle] = []
        self.message = ""
        self.message_timer = 0
        self.message_color = GOLD
        self.current_reptile = None
        self.current_image: pygame.Surface | None = None
        self.target_name = ""
        self.show_fun_fact = False
        self.image_loading = False

        # Shuffled reptile order
        self.reptile_order: list[int] = []

        # Menu buttons
        btn_w, btn_h = 220, 55
        cx = SCREEN_W // 2
        self.btn_easy = Button(
            (cx - btn_w - 15, 400, btn_w, btn_h), "Easy Mode", LEAF_GREEN
        )
        self.btn_hard = Button(
            (cx + 15, 400, btn_w, btn_h), "Hard Mode", ORANGE
        )

        # In-game buttons
        self.btn_hint = Button((0, 0, 120, 44), "Peek", HINT_BLUE)
        self.btn_submit = Button((0, 0, 120, 44), "Submit", SUBMIT_GREEN)
        self.btn_skip = Button((0, 0, 120, 44), "Skip", GRAY)

        # Post-round / game-over buttons
        self.btn_next = Button((0, 0, 160, 50), "Next Reptile", LEAF_GREEN, font_size=24)
        self.btn_menu = Button((0, 0, 160, 50), "Main Menu", ORANGE, font_size=24)
        self.btn_play_again = Button((0, 0, 200, 55), "Play Again!", LEAF_GREEN, font_size=26)
        self.btn_menu2 = Button((0, 0, 200, 55), "Main Menu", ORANGE, font_size=26)

    # ── helpers ────────────────────────────────────────────────────────────
    @staticmethod
    def _ascii_name(name: str) -> str:
        """Normalize accented characters to plain ASCII (e.g. á → a)."""
        nfkd = unicodedata.normalize("NFKD", name)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def _target(self, reptile: dict) -> str:
        if self.difficulty == "hard":
            return self._ascii_name(reptile["scientific_name"])
        return self._ascii_name(reptile["common_name"])

    def _start_game(self, difficulty: str):
        self.difficulty = difficulty
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.round_num = 0
        self.hints_used_total = 0
        self.reptile_order = list(range(len(REPTILES)))
        random.shuffle(self.reptile_order)
        self._next_round()

    def _next_round(self):
        if self.round_num >= self.total_rounds:
            self.state = STATE_GAME_OVER
            return
        idx = self.reptile_order[self.round_num % len(self.reptile_order)]
        self.current_reptile = REPTILES[idx]
        self.target_name = self._target(self.current_reptile)
        self.typed_text = ""
        self.hint_count = 0
        self.hint_active = False
        self.hint_used_this_round = False
        self.show_fun_fact = False
        self.message = ""
        self.message_timer = 0
        self.confetti.clear()
        self.state = STATE_PLAYING

        # Load image in background thread to avoid freezing
        self.current_image = None
        self.image_loading = True
        reptile = self.current_reptile

        def _load():
            img = load_pygame_image(reptile["image_file"], IMAGE_SIZE)
            if img is None:
                img = create_placeholder_surface(reptile["common_name"], IMAGE_SIZE)
            self.current_image = img
            self.image_loading = False

        threading.Thread(target=_load, daemon=True).start()

    def _give_hint(self):
        """Activate the hint peek — the answer is shown while the button is held."""
        self.hint_active = True
        if not self.hint_used_this_round:
            self.hint_used_this_round = True
            self.hint_count += 1
            self.hints_used_total += 1

    # Characters that are auto-filled and the player doesn't need to type
    _SKIP_CHARS = {" ", "-"}

    def _submit(self):
        # Normalize: compare ignoring spaces, dashes, and case
        skip = self._SKIP_CHARS
        typed_normalized = "".join(c for c in self.typed_text if c not in skip).lower()
        target_normalized = "".join(c for c in self.target_name if c not in skip).lower()
        if typed_normalized == target_normalized:
            # Correct!
            pts = max(1, 10 - self.hint_count * 2)
            self.score += pts
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            self.state = STATE_CORRECT
            self.show_fun_fact = True
            self.confetti = [ConfettiParticle() for _ in range(80)]
        elif self.difficulty == "easy":
            # Easy mode: let the player try again instead of ending the round
            self.typed_text = ""
            self.message = "Not quite — try again!"
            self.message_color = RED
            self.message_timer = 90  # ~1.5 seconds at 60 FPS
        else:
            self.streak = 0
            self.state = STATE_WRONG
            self.show_fun_fact = True

    def _advance_after_result(self):
        self.round_num += 1
        self._next_round()

    # ── drawing helpers ────────────────────────────────────────────────────
    def _draw_bg(self):
        self.screen.fill(BG_GREEN)
        for leaf in self.leaves:
            leaf.update()
            leaf.draw(self.screen)

    def _draw_top_bar(self):
        bar = pygame.Surface((SCREEN_W, 50), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 100))
        self.screen.blit(bar, (0, 0))

        diff_label = "Easy" if self.difficulty == "easy" else "Hard"
        left = self.font_small.render(
            f"  Mode: {diff_label}   |   Round {self.round_num + 1}/{self.total_rounds}", True, SOFT_WHITE
        )
        self.screen.blit(left, (10, 14))

        right = self.font_small.render(
            f"Score: {self.score}   Streak: {self.streak}   Best: {self.best_streak}  ", True, GOLD
        )
        self.screen.blit(right, (SCREEN_W - right.get_width() - 10, 14))

    def _draw_image_frame(self, y_offset=65):
        """Draw the reptile image centered with a rounded frame."""
        frame_w, frame_h = IMAGE_SIZE[0] + 20, IMAGE_SIZE[1] + 20
        frame_x = (SCREEN_W - frame_w) // 2
        frame_y = y_offset

        # Frame shadow
        pygame.draw.rect(self.screen, (0, 0, 0, 50),
                         (frame_x + 4, frame_y + 4, frame_w, frame_h), border_radius=16)
        # Frame
        pygame.draw.rect(self.screen, DARK_GREEN,
                         (frame_x, frame_y, frame_w, frame_h), border_radius=16)
        pygame.draw.rect(self.screen, LEAF_GREEN,
                         (frame_x, frame_y, frame_w, frame_h), width=3, border_radius=16)

        if self.image_loading:
            txt = self.font_body.render("Loading image...", True, SOFT_WHITE)
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_W // 2, frame_y + frame_h // 2)))
        elif self.current_image is not None:
            img_rect = self.current_image.get_rect(
                center=(frame_x + frame_w // 2, frame_y + frame_h // 2)
            )
            self.screen.blit(self.current_image, img_rect)

        # Credit — small overlay inside the bottom-right of the frame
        if self.current_reptile:
            credit_text = self.current_reptile.get("image_credit", "")
            credit = self.font_small.render(credit_text, True, (200, 220, 200))
            # Semi-transparent background behind the credit text
            cw, ch = credit.get_size()
            credit_bg = pygame.Surface((cw + 8, ch + 4), pygame.SRCALPHA)
            credit_bg.fill((0, 0, 0, 140))
            credit_bg_x = frame_x + frame_w - cw - 14
            credit_bg_y = frame_y + frame_h - ch - 10
            self.screen.blit(credit_bg, (credit_bg_x, credit_bg_y))
            self.screen.blit(credit, (credit_bg_x + 4, credit_bg_y + 2))

        return frame_y + frame_h + 8

    def _draw_typing_area(self, y):
        """Draw the underline prompt and typed letters."""
        target = self.target_name
        typed = self.typed_text

        # Prompt label — rendered above the typing box with clear spacing
        mode_label = "Type the common name:" if self.difficulty == "easy" else "Type the scientific name:"
        lbl = self.font_small.render(mode_label, True, LIGHT_GREEN)
        self.screen.blit(lbl, lbl.get_rect(midbottom=(SCREEN_W // 2, y - 6)))

        # Semi-transparent backdrop
        area_w = min(SCREEN_W - 60, len(target) * 28 + 40)
        area_h = 70
        area_x = (SCREEN_W - area_w) // 2
        area_y = y

        bg = pygame.Surface((area_w, area_h), pygame.SRCALPHA)
        bg.fill(TRANSPARENT_BG)
        pygame.draw.rect(bg, LEAF_GREEN, (0, 0, area_w, area_h), width=2, border_radius=10)
        self.screen.blit(bg, (area_x, area_y))

        # Character cells
        char_w = 24
        total_w = len(target) * char_w
        start_x = (SCREEN_W - total_w) // 2
        cy = area_y + area_h // 2 - 4

        for i, ch in enumerate(target):
            x = start_x + i * char_w
            if ch in self._SKIP_CHARS:
                # Draw the separator character (space/dash) as a fixed label
                if ch == "-":
                    dash = self.font_typing.render("-", True, GRAY)
                    self.screen.blit(dash, dash.get_rect(midbottom=(x + char_w // 2, cy + 14)))
                continue

            if i < len(typed):
                # Show typed character
                if typed[i].lower() == ch.lower():
                    colour = LIGHT_GREEN
                else:
                    colour = RED
                letter = self.font_typing.render(typed[i], True, colour)
                self.screen.blit(letter, letter.get_rect(midbottom=(x + char_w // 2, cy + 14)))
            else:
                # Draw underline placeholder
                pygame.draw.line(
                    self.screen, SOFT_WHITE,
                    (x + 2, cy + 16), (x + char_w - 4, cy + 16), 2
                )

        # Blinking cursor
        cursor_idx = len(typed)
        if cursor_idx < len(target) and pygame.time.get_ticks() % 1000 < 500:
            cx_pos = start_x + cursor_idx * char_w + char_w // 2
            pygame.draw.line(self.screen, WHITE, (cx_pos, cy - 10), (cx_pos, cy + 16), 2)

        return area_y + area_h + 10

    def _draw_buttons_playing(self, y):
        """Position and draw the hint / submit / skip buttons."""
        gap = 20
        total_w = 120 * 3 + gap * 2
        sx = (SCREEN_W - total_w) // 2

        self.btn_hint.rect.topleft   = (sx, y)
        self.btn_submit.rect.topleft = (sx + 120 + gap, y)
        self.btn_skip.rect.topleft   = (sx + 240 + gap * 2, y)

        self.btn_hint.draw(self.screen, self.font_btn)
        self.btn_submit.draw(self.screen, self.font_btn)
        self.btn_skip.draw(self.screen, self.font_btn)

        # Hint usage indicator
        if self.hint_count > 0:
            ht = self.font_small.render(f"Peeked: {self.hint_count}x  (-2 pts each)", True, HINT_BLUE)
            self.screen.blit(ht, ht.get_rect(midtop=(self.btn_hint.rect.centerx, y + 50)))

    def _draw_result_screen(self):
        """Overlay shown after a correct or wrong answer."""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        cy = SCREEN_H // 2 - 100

        if self.state == STATE_CORRECT:
            title = self.font_big.render("Correct!", True, GOLD)
        else:
            title = self.font_big.render("Not quite!", True, RED)
        self.screen.blit(title, title.get_rect(center=(SCREEN_W // 2, cy)))
        cy += 50

        # Show the answer
        answer_label = "Answer: " + self.target_name
        ans = self.font_subtitle.render(answer_label, True, SOFT_WHITE)
        self.screen.blit(ans, ans.get_rect(center=(SCREEN_W // 2, cy)))
        cy += 40

        if self.state == STATE_WRONG:
            you_typed = self.font_body.render(f'You typed: "{self.typed_text}"', True, (200, 180, 180))
            self.screen.blit(you_typed, you_typed.get_rect(center=(SCREEN_W // 2, cy)))
            cy += 35

        # Fun fact
        if self.show_fun_fact and self.current_reptile:
            fact = self.current_reptile["fun_fact"]
            ft = self.font_body.render(fact, True, LIGHT_GREEN)
            # Wrap if too wide
            if ft.get_width() > SCREEN_W - 80:
                words = fact.split()
                lines = []
                line = ""
                for w in words:
                    test = line + " " + w if line else w
                    if self.font_body.size(test)[0] < SCREEN_W - 80:
                        line = test
                    else:
                        lines.append(line)
                        line = w
                if line:
                    lines.append(line)
                for ln in lines:
                    ft = self.font_body.render(ln, True, LIGHT_GREEN)
                    self.screen.blit(ft, ft.get_rect(center=(SCREEN_W // 2, cy)))
                    cy += 28
            else:
                self.screen.blit(ft, ft.get_rect(center=(SCREEN_W // 2, cy)))
                cy += 35

        # Buttons
        btn_y = cy + 20
        self.btn_next.rect.center = (SCREEN_W // 2 - 100, btn_y)
        self.btn_menu.rect.center = (SCREEN_W // 2 + 100, btn_y)
        self.btn_next.draw(self.screen, self.font_btn)
        self.btn_menu.draw(self.screen, self.font_btn)

        # Confetti
        for p in self.confetti:
            p.update()
            p.draw(self.screen)
        self.confetti = [p for p in self.confetti if p.life > 0]

    def _draw_game_over(self):
        self._draw_bg()
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        cy = 160
        t = self.font_title.render("Game Over!", True, GOLD)
        self.screen.blit(t, t.get_rect(center=(SCREEN_W // 2, cy)))
        cy += 70

        lines = [
            f"Final Score:  {self.score}",
            f"Best Streak:  {self.best_streak}",
            f"Hints Used:   {self.hints_used_total}",
            f"Difficulty:   {'Easy' if self.difficulty == 'easy' else 'Hard'}",
        ]
        for ln in lines:
            r = self.font_subtitle.render(ln, True, SOFT_WHITE)
            self.screen.blit(r, r.get_rect(center=(SCREEN_W // 2, cy)))
            cy += 40

        btn_y = cy + 40
        self.btn_play_again.rect.center = (SCREEN_W // 2 - 130, btn_y)
        self.btn_menu2.rect.center = (SCREEN_W // 2 + 130, btn_y)
        self.btn_play_again.draw(self.screen, self.font_btn)
        self.btn_menu2.draw(self.screen, self.font_btn)

        # Confetti continues
        for p in self.confetti:
            p.update()
            p.draw(self.screen)
        self.confetti = [p for p in self.confetti if p.life > 0]

    def _draw_menu(self):
        self._draw_bg()

        cy = 140
        # Title with shadow
        shadow = self.font_title.render("LizardType", True, (0, 0, 0))
        self.screen.blit(shadow, shadow.get_rect(center=(SCREEN_W // 2 + 3, cy + 3)))
        title = self.font_title.render("LizardType", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(SCREEN_W // 2, cy)))
        cy += 55

        tagline = self.font_subtitle.render("Reptile Typing Trainer!", True, LIGHT_GREEN)
        self.screen.blit(tagline, tagline.get_rect(center=(SCREEN_W // 2, cy)))
        cy += 60

        # Decorative lizard ASCII — use monospace font so characters align
        lizard_lines = [
            r"      _  _          ",
            r"     / \/ \    ~~>  ",
            r"    ( o  o )  /     ",
            r"     \ == /--'      ",
            r".----'    `---.     ",
            r"|    RAWR!     |    ",
            r"'-.          .-'    ",
            r"   `--------`       ",
        ]
        mono_font = pygame.font.SysFont("Courier New", 18)
        # Measure the widest line to centre the whole block
        max_w = max(mono_font.size(ln)[0] for ln in lizard_lines)
        block_x = (SCREEN_W - max_w) // 2
        for ln in lizard_lines:
            art = mono_font.render(ln, True, LEAF_GREEN)
            self.screen.blit(art, (block_x, cy))
            cy += 22

        cy += 20
        # Descriptions
        easy_desc = self.font_small.render("Easy: Type the common name", True, SOFT_WHITE)
        hard_desc = self.font_small.render("Hard: Type the scientific name", True, SOFT_WHITE)
        self.screen.blit(easy_desc, easy_desc.get_rect(center=(SCREEN_W // 2 - 120, cy)))
        self.screen.blit(hard_desc, hard_desc.get_rect(center=(SCREEN_W // 2 + 120, cy)))

        self.btn_easy.rect.centery = cy + 50
        self.btn_hard.rect.centery = cy + 50
        self.btn_easy.rect.centerx = SCREEN_W // 2 - 120
        self.btn_hard.rect.centerx = SCREEN_W // 2 + 120
        self.btn_easy.draw(self.screen, self.font_btn)
        self.btn_hard.draw(self.screen, self.font_btn)

        footer = self.font_small.render("Images: Wikimedia Commons (CC-BY/CC-BY-SA/Public Domain)", True, (120, 140, 120))
        self.screen.blit(footer, footer.get_rect(midbottom=(SCREEN_W // 2, SCREEN_H - 15)))

    def _draw_playing(self):
        self._draw_bg()
        self._draw_top_bar()
        y = self._draw_image_frame(y_offset=62)
        y = self._draw_typing_area(y + 30)
        self._draw_buttons_playing(y + 4)

        # ── Hint peek overlay: fixed at bottom of screen, below everything ──
        if self.hint_active:
            hint_text = self.target_name
            hint_rendered = self.font_typing.render(hint_text, True, GOLD)
            hw, hh = hint_rendered.get_size()
            pill_w, pill_h = hw + 24, hh + 16
            pill_x = (SCREEN_W - pill_w) // 2
            pill_y = SCREEN_H - pill_h - 20
            pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            pill_surf.fill((0, 0, 0, 200))
            pygame.draw.rect(pill_surf, GOLD, (0, 0, pill_w, pill_h), width=2, border_radius=8)
            self.screen.blit(pill_surf, (pill_x, pill_y))
            self.screen.blit(hint_rendered, hint_rendered.get_rect(center=(SCREEN_W // 2, pill_y + pill_h // 2)))

        # Flash message
        if self.message and self.message_timer > 0:
            self.message_timer -= 1
            msg = self.font_body.render(self.message, True, self.message_color)
            self.screen.blit(msg, msg.get_rect(center=(SCREEN_W // 2, SCREEN_H - 40)))

    # ── event handling ─────────────────────────────────────────────────────
    def _handle_menu_events(self, event):
        if self.btn_easy.handle_event(event):
            self._start_game("easy")
        if self.btn_hard.handle_event(event):
            self._start_game("hard")

    def _handle_playing_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._submit()
            elif event.key == pygame.K_BACKSPACE:
                # When deleting, skip back over auto-inserted separators
                while self.typed_text and self.typed_text[-1] in self._SKIP_CHARS:
                    self.typed_text = self.typed_text[:-1]
                self.typed_text = self.typed_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU
            else:
                ch = event.unicode
                if ch and ch in self._SKIP_CHARS:
                    # Ignore manually typed spaces/dashes — they are auto-filled
                    pass
                elif ch and len(self.typed_text) < len(self.target_name):
                    # Auto-insert separators: if the current position(s) in the
                    # target are spaces or dashes, insert them automatically so
                    # the player only has to type letters.
                    while (len(self.typed_text) < len(self.target_name)
                           and self.target_name[len(self.typed_text)] in self._SKIP_CHARS):
                        self.typed_text += self.target_name[len(self.typed_text)]
                    # Re-check length after possible separator insertion
                    if len(self.typed_text) < len(self.target_name):
                        self.typed_text += ch

        if self.btn_hint.handle_event(event):
            self._give_hint()
        # Release hint peek when mouse button is released anywhere
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.hint_active = False
        if self.btn_submit.handle_event(event):
            self._submit()
        if self.btn_skip.handle_event(event):
            self.streak = 0
            self.state = STATE_WRONG
            self.show_fun_fact = True

    def _handle_result_events(self, event):
        if self.btn_next.handle_event(event):
            self._advance_after_result()
        if self.btn_menu.handle_event(event):
            self.state = STATE_MENU
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._advance_after_result()

    def _handle_gameover_events(self, event):
        if self.btn_play_again.handle_event(event):
            self._start_game(self.difficulty)
        if self.btn_menu2.handle_event(event):
            self.state = STATE_MENU
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._start_game(self.difficulty)

    # ── main loop ──────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if self.state == STATE_MENU:
                    self._handle_menu_events(event)
                elif self.state == STATE_PLAYING:
                    self._handle_playing_events(event)
                elif self.state in (STATE_CORRECT, STATE_WRONG):
                    self._handle_result_events(event)
                elif self.state == STATE_GAME_OVER:
                    self._handle_gameover_events(event)

            # Draw
            if self.state == STATE_MENU:
                self._draw_menu()
            elif self.state == STATE_PLAYING:
                self._draw_playing()
            elif self.state in (STATE_CORRECT, STATE_WRONG):
                self._draw_playing()  # draw game underneath
                self._draw_result_screen()
            elif self.state == STATE_GAME_OVER:
                self._draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ═══════════════════════════════════════════════════════════════════════════
def main():
    game = LizardTypeGame()
    game.run()


if __name__ == "__main__":
    main()

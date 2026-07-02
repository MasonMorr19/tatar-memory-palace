"""Tatar Nested Hearth -- a Pygame study app for the ASU Tatar course.

Two modes, switch with TAB:
  PALACE    walk the memory-palace stations (read live from the shared
            tatar_db.json spine at the repo root), hear each vocab word and
            the listen/speak model line for that room.
  VERB LAB  walk the 71-verb mnemonic-peg deck, hear the bare verb, and
            cycle through all 7 tenses/moods to hear the conjugated form.

Controls:
  LEFT/RIGHT   previous / next station or verb
  UP/DOWN      Palace: cycle which line is focused (locus, listen, speak, vocab...)
               Verb Lab: cycle tense/mood
  SPACE/ENTER  speak the focused line (cached after first play, so re-hearing
               anything is instant even offline)
  N            Verb Lab: toggle negative
  TAB          switch Palace <-> Verb Lab
  ESC / Q      quit
"""
import sys
import threading
import pygame

from core.data_loader import DataStore
from core.audio_engine import AudioEngine
from core.grammar_rules import conjugate, TENSE_NAMES, PERSONS

WIDTH, HEIGHT = 980, 640
BG = (244, 236, 216)       # parchment, matches the web app's palette
INK = (43, 34, 24)
MAROON = (124, 34, 48)
GOLD = (176, 136, 63)
GREEN = (60, 90, 77)
LINE = (216, 201, 163)
CARD = (255, 253, 246)

TENSE_ORDER = ["pres", "dpast", "ipast", "catfut", "auxfut", "cond", "imp"]


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tatar Nested Hearth")
        self.clock = pygame.time.Clock()

        self.db = DataStore()
        self.audio = AudioEngine()

        self.font_big = pygame.font.SysFont("segoeui", 40, bold=True)
        self.font_med = pygame.font.SysFont("segoeui", 22)
        self.font_small = pygame.font.SysFont("segoeui", 16)
        self.font_mono = pygame.font.SysFont("consolas", 16)

        self.mode = "palace"  # or "verb"
        self.station_idx = 0
        self.line_idx = 0  # which line within a station is focused
        self.verb_idx = 0
        self.tense_idx = 0
        self.negative = False

        self.status = ""
        self.running = True

    # ---------- data helpers ----------

    def current_station(self):
        return self.db.stations[self.station_idx]

    def current_verb(self):
        return self.db.verbs[self.verb_idx]

    def station_lines(self, station):
        """Returns a list of (label, tatar_text, english_text) for everything
        speakable in this station: locus name, listen line, speak line, vocab."""
        lines = [("Locus", station["locus"], station["locus_en"])]
        if station.get("listen"):
            lines.append(("Listen", station["listen"]["tt"], station["listen"]["en"]))
        if station.get("speak"):
            lines.append(("Speak", station["speak"]["tt"], station["speak"]["en"]))
        for surface in station.get("vocab", []):
            gloss = self.db.resolve_gloss(surface)
            lines.append(("Vocab", surface, gloss))
        for expr_tt in station.get("expressions", []):
            e = next((e for e in self.db.expressions if e["tt"] == expr_tt), None)
            if e:
                lines.append(("Expr", e["tt"], e["en"]))
        return lines

    # ---------- audio ----------

    def speak_async(self, text):
        if not text:
            return
        self.status = f"Speaking: {text}"
        threading.Thread(target=self._speak_thread, args=(text,), daemon=True).start()

    def _speak_thread(self, text):
        self.audio.speak(text, blocking=True)
        self.status = ""

    # ---------- input ----------

    def handle_key(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_q):
            self.running = False
        elif key == pygame.K_TAB:
            self.mode = "verb" if self.mode == "palace" else "palace"
        elif key == pygame.K_LEFT:
            self.prev_item()
        elif key == pygame.K_RIGHT:
            self.next_item()
        elif key == pygame.K_UP:
            self.cycle_focus(-1)
        elif key == pygame.K_DOWN:
            self.cycle_focus(1)
        elif key in (pygame.K_SPACE, pygame.K_RETURN):
            self.speak_focused()
        elif key == pygame.K_n and self.mode == "verb":
            self.negative = not self.negative

    def prev_item(self):
        if self.mode == "palace":
            self.station_idx = (self.station_idx - 1) % len(self.db.stations)
            self.line_idx = 0
        else:
            self.verb_idx = (self.verb_idx - 1) % len(self.db.verbs)

    def next_item(self):
        if self.mode == "palace":
            self.station_idx = (self.station_idx + 1) % len(self.db.stations)
            self.line_idx = 0
        else:
            self.verb_idx = (self.verb_idx + 1) % len(self.db.verbs)

    def cycle_focus(self, delta):
        if self.mode == "palace":
            lines = self.station_lines(self.current_station())
            self.line_idx = (self.line_idx + delta) % len(lines)
        else:
            self.tense_idx = (self.tense_idx + delta) % len(TENSE_ORDER)

    def speak_focused(self):
        if self.mode == "palace":
            lines = self.station_lines(self.current_station())
            _, tt, _ = lines[self.line_idx]
            self.speak_async(tt)
        else:
            verb = self.current_verb()
            tense = TENSE_ORDER[self.tense_idx]
            if tense == "imp":
                form, _ = conjugate(verb, "imp", 1, self.negative)
            else:
                form, _ = conjugate(verb, tense, 0, self.negative)
            self.speak_async(form)

    # ---------- rendering ----------

    def draw_text(self, font, text, color, x, y, max_width=None):
        surf = font.render(text, True, color)
        if max_width and surf.get_width() > max_width:
            # crude truncation with ellipsis
            while surf.get_width() > max_width and len(text) > 1:
                text = text[:-1]
                surf = font.render(text + "...", True, color)
        self.screen.blit(surf, (x, y))
        return surf.get_height()

    def draw(self):
        self.screen.fill(BG)
        if self.mode == "palace":
            self.draw_palace()
        else:
            self.draw_verb()
        self.draw_footer()
        pygame.display.flip()

    def draw_palace(self):
        station = self.current_station()
        self.draw_text(self.font_small, f"PALACE  ·  Station {self.station_idx + 1}/{len(self.db.stations)}  ·  {station['zone']}", GOLD, 30, 20)
        self.draw_text(self.font_big, station["locus"], MAROON, 30, 50)
        self.draw_text(self.font_med, station["locus_en"], GREEN, 30, 100)

        lines = self.station_lines(station)
        y = 150
        for i, (label, tt, en) in enumerate(lines):
            focused = i == self.line_idx
            card_rect = pygame.Rect(30, y, WIDTH - 60, 44)
            pygame.draw.rect(self.screen, MAROON if focused else CARD, card_rect, border_radius=8)
            if not focused:
                pygame.draw.rect(self.screen, LINE, card_rect, width=1, border_radius=8)
            text_color = (253, 246, 230) if focused else INK
            label_color = (240, 217, 168) if focused else GOLD
            self.draw_text(self.font_small, label, label_color, card_rect.x + 12, card_rect.y + 4)
            self.draw_text(self.font_med, f"{tt}   —  {en}", text_color, card_rect.x + 12, card_rect.y + 20, max_width=card_rect.width - 24)
            y += 50
            if y > HEIGHT - 90:
                remaining = len(lines) - i - 1
                if remaining > 0:
                    self.draw_text(self.font_small, f"...and {remaining} more (scroll not yet built, use UP/DOWN)", (120, 110, 90), 30, y)
                break

    def draw_verb(self):
        verb = self.current_verb()
        self.draw_text(self.font_small, f"VERB LAB  ·  Verb {self.verb_idx + 1}/{len(self.db.verbs)}", GOLD, 30, 20)
        stem = verb.get("disp") or verb["stem"]
        self.draw_text(self.font_big, stem, MAROON, 30, 50)
        self.draw_text(self.font_med, verb["en"], GREEN, 30, 100)
        self.draw_text(self.font_small, f"peg: {verb['kw']}", INK, 30, 135)
        self.draw_text(self.font_small, verb["sc"], (90, 80, 65), 30, 158, max_width=WIDTH - 60)

        tense = TENSE_ORDER[self.tense_idx]
        neg_label = " (negative)" if self.negative else ""
        card_rect = pygame.Rect(30, 210, WIDTH - 60, 130)
        pygame.draw.rect(self.screen, INK, card_rect, border_radius=12)
        self.draw_text(self.font_small, f"{TENSE_NAMES[tense]}{neg_label}  ·  Мин / I", (207, 155, 143), card_rect.x + 20, card_rect.y + 14)

        if tense == "imp":
            form, _ = conjugate(verb, "imp", 1, self.negative)
        else:
            form, _ = conjugate(verb, tense, 0, self.negative)
        self.draw_text(self.font_big, form, (251, 249, 243), card_rect.x + 20, card_rect.y + 44)

        y = 360
        self.draw_text(self.font_small, "All persons:", GOLD, 30, y)
        y += 26
        for p, (pron, pron_en) in enumerate(PERSONS):
            if tense == "imp" and p not in (1, 4):
                continue
            f, _ = conjugate(verb, tense, p, self.negative)
            self.draw_text(self.font_mono, f"{pron:6s} {f}", INK, 40, y)
            y += 22

        self.draw_text(self.font_small, "UP/DOWN cycles tense · N toggles negative", (120, 110, 90), 30, HEIGHT - 120)

    def draw_footer(self):
        pygame.draw.line(self.screen, LINE, (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 1)
        hint = "← → navigate   ↑ ↓ cycle   SPACE speak   TAB switch mode   ESC quit"
        self.draw_text(self.font_small, hint, (120, 110, 90), 30, HEIGHT - 46)
        if self.status:
            self.draw_text(self.font_small, self.status, GREEN, 30, HEIGHT - 24)

    # ---------- loop ----------

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
            self.draw()
            self.clock.tick(30)
        pygame.quit()


if __name__ == "__main__":
    App().run()

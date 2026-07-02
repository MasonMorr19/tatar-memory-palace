import os
import asyncio
import hashlib
import pygame
import edge_tts

# Tatar has no native TTS voice on any free engine (verified: gTTS's supported
# language list and Edge's neural voice catalog both lack "tt" and "ba"). We
# approximate with a neighboring Cyrillic voice instead -- the same strategy
# the web app's browser speechSynthesis fallback already uses, but with much
# higher audio quality since these are real neural voices, not gTTS/robotic
# browser TTS. Kazakh (kk-KZ), not Russian, is the right stand-in: Kazakh
# Cyrillic already contains Ә, Ң, Ө, Ү and Һ natively, so its text normalizer
# reads them correctly. Russian's alphabet has none of those letters, so
# ru-RU voices were mangling every word that used them (only Җ has no Kazakh
# equivalent -- Kazakh uses plain Ж there). Swap VOICE below if Tatar ever
# gets its own voice.
VOICE = "kk-KZ-AigulNeural"


class AudioEngine:
    def __init__(self, cache_dir="assets/audio_cache", voice=VOICE):
        self.cache_dir = cache_dir
        self.voice = voice
        os.makedirs(self.cache_dir, exist_ok=True)
        pygame.mixer.init()

    def _get_file_path(self, text):
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{self.voice}_{text_hash}.mp3")

    def is_cached(self, text):
        return os.path.exists(self._get_file_path(text))

    def ensure_cached(self, text):
        """Generates and caches the audio for `text` if not already present.
        Returns the file path. Safe to call repeatedly -- no-op on cache hit."""
        file_path = self._get_file_path(text)
        if os.path.exists(file_path):
            return file_path
        try:
            asyncio.run(self._synthesize(text, file_path))
        except Exception as e:
            print(f"[AudioEngine] TTS generation failed for '{text}': {e}")
            return None
        return file_path

    async def _synthesize(self, text, file_path):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(file_path)

    def speak(self, text, blocking=False):
        """Speaks `text`. Caches on first use so repeats are instant and offline.
        Non-blocking by default so the Pygame UI stays responsive; pass
        blocking=True (e.g. for a CLI script) to wait until playback finishes."""
        file_path = self.ensure_cached(text)
        if not file_path:
            return
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            if blocking:
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"[AudioEngine] Playback failed: {e}")

    def is_speaking(self):
        return pygame.mixer.music.get_busy()

    def pregenerate(self, texts):
        """Warms the cache for a batch of phrases (e.g. a whole station) so
        playback during study has zero latency. Skips anything already cached."""
        missing = [t for t in texts if t and not self.is_cached(t)]
        if not missing:
            return
        asyncio.run(self._pregenerate_async(missing))

    async def _pregenerate_async(self, texts):
        for t in texts:
            path = self._get_file_path(t)
            try:
                await self._synthesize(t, path)
            except Exception as e:
                print(f"[AudioEngine] Pregenerate failed for '{t}': {e}")


# Example usage:
# audio = AudioEngine()
# audio.speak("Мин татарча сөйләшәчәкмен.", blocking=True)

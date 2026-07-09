#!/usr/bin/env python
"""
Background music player for drone swarm performances.
Wraps pygame.mixer — pip install pygame if needed.
"""
from __future__ import division, absolute_import, print_function
import time
import threading


class MusicPlayer:
    """Simple background music player with start/stop/pause/fade support."""

    def __init__(self):
        self._loaded = False
        self._playing = False
        self._file = None
        self._init_mixer()

    def _init_mixer(self):
        try:
            import pygame.mixer
            pygame.mixer.init()
        except Exception as e:
            print(f"[Music] pygame 未安装或音频设备不可用: {e}")
            print("[Music] pip install pygame 后重试")

    def load(self, filepath):
        """Load a music file (mp3, wav, ogg)."""
        try:
            import pygame.mixer
            pygame.mixer.music.load(filepath)
            self._file = filepath
            self._loaded = True
            print(f"[Music] 已加载: {filepath}")
        except Exception as e:
            print(f"[Music] 加载失败: {e}")

    def play(self, loops=0, start=0.0, fade_ms=0):
        """
        Start playback.
        loops: -1=无限循环, 0=播放一次, N=额外循环N次
        start: 从第几秒开始
        fade_ms: 淡入毫秒数
        """
        if not self._loaded:
            print("[Music] 请先 load() 加载音乐文件")
            return
        try:
            import pygame.mixer
            if fade_ms > 0:
                pygame.mixer.music.play(loops, start, fade_ms)
            else:
                pygame.mixer.music.play(loops, start)
            self._playing = True
            print(f"[Music] 开始播放 (loops={loops})")
        except Exception as e:
            print(f"[Music] 播放失败: {e}")

    def pause(self):
        """暂停"""
        try:
            import pygame.mixer
            pygame.mixer.music.pause()
            self._playing = False
            print("[Music] 暂停")
        except Exception as e:
            print(f"[Music] 暂停失败: {e}")

    def unpause(self):
        """继续"""
        try:
            import pygame.mixer
            pygame.mixer.music.unpause()
            self._playing = True
            print("[Music] 继续")
        except Exception as e:
            print(f"[Music] 继续失败: {e}")

    def stop(self, fade_ms=0):
        """停止。fade_ms: 淡出毫秒数"""
        try:
            import pygame.mixer
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
            self._playing = False
            print("[Music] 停止")
        except Exception as e:
            print(f"[Music] 停止失败: {e}")

    def set_volume(self, vol):
        """设置音量 0.0 ~ 1.0"""
        try:
            import pygame.mixer
            pygame.mixer.music.set_volume(max(0.0, min(1.0, vol)))
        except Exception:
            pass

    @property
    def is_playing(self):
        try:
            import pygame.mixer
            return pygame.mixer.music.get_busy()
        except Exception:
            return False

    def wait(self):
        """阻塞等待直到音乐播放完毕"""
        while self.is_playing:
            time.sleep(0.1)


# ============================================
# 全局单例
# ============================================
_player = None


def _get_player():
    global _player
    if _player is None:
        _player = MusicPlayer()
    return _player


def load_music(filepath):
    """加载音乐文件"""
    _get_player().load(filepath)


def play_music(loops=0, start=0.0, fade_ms=0):
    """
    开始播放背景音乐

    Parameters:
        loops: -1=无限循环, 0=播放一次
        start: 从第几秒开始播放
        fade_ms: 淡入毫秒数
    """
    _get_player().play(loops, start, fade_ms)


def stop_music(fade_ms=0):
    """停止音乐。fade_ms: 淡出毫秒数"""
    _get_player().stop(fade_ms)


def pause_music():
    """暂停音乐"""
    _get_player().pause()


def unpause_music():
    """继续播放"""
    _get_player().unpause()


def set_music_volume(vol):
    """设置音量 0.0 ~ 1.0"""
    _get_player().set_volume(vol)


def is_music_playing():
    """检查是否正在播放"""
    return _get_player().is_playing


def wait_music():
    """阻塞等待直到音乐播放完毕"""
    _get_player().wait()

#!/usr/bin/env python
"""
PositionViewer — OpenCV-based real-time position monitor (pyfii style)
=======================================================================
Three orthographic views + status panel, matching pyfii's GUI layout.
Drone drawn as 4-motor cross with center LED indicator.

Usage::

    from fwfii import connect, PositionViewer, set_beat_output

    d, h, f1 = connect(71101)
    set_beat_output("off")

    viewer = PositionViewer(programmable=40, trail_length=60)
    viewer.start()
    # … fly …
    viewer.stop()
"""

from __future__ import division, absolute_import, print_function

import cmath
import threading
import time
import traceback
from collections import deque

import numpy as np
import cv2


# ── carpet definitions ─────────────────────────────

CARPET_TYPES = {
    40:  dict(actual=80,   margin=20),
    80:  dict(actual=120,  margin=20),
    360: dict(actual=400,  margin=20),
    560: dict(actual=600,  margin=20),
}

# ── drone color palette (BGR) ──────────────────────

DRONE_COLORS = [
    (0, 0, 255),     # red
    (0, 255, 0),     # green
    (255, 0, 0),     # blue
    (0, 200, 255),   # orange
    (255, 0, 255),   # purple
    (255, 255, 0),   # teal
    (255, 0, 128),   # pink
    (255, 128, 0),   # sky
]


class PositionViewer:
    """Real-time 2D/3-view position monitor (pyfii-style OpenCV GUI).

    Layout (scaled from pyfii's 1200x600):
      +--------------+----------+----------+
      |              |  Front   |  Right   |
      |   Top-Down   |  (X-Z)   |  (Y-Z)   |
      |   (X-Y)      |          |          |
      |              +----------+----------+
      |              |     Status Bar      |
      +--------------+---------------------+
    """

    def __init__(self, programmable=560, margin=None,
                 title="FWFII Position Viewer",
                 scale=1.0, update_interval_ms=80,
                 trail_length=60):
        """
        Parameters
        ----------
        programmable : int
            Carpet programmable size: 40, 80, 360, 560.
        margin : int or None
            Border margin in cm. Auto-derived if None.
        title : str
            Window title.
        scale : float
            Display scale factor (1.0 = ~1200x600 base).
        update_interval_ms : int
            Refresh interval in milliseconds.
        trail_length : int
            Number of history points in the position trail.
        """
        if programmable not in CARPET_TYPES:
            raise ValueError(
                f"Unknown carpet size {programmable!r}. "
                f"Supported: {sorted(CARPET_TYPES.keys())}"
            )

        info = CARPET_TYPES[programmable]
        self._programmable = programmable
        self._actual = info["actual"]
        self._margin = margin if margin is not None else info["margin"]

        self._xmin = -self._margin
        self._xmax = self._programmable + self._margin
        self._ymin = -self._margin
        self._ymax = self._programmable + self._margin
        self._zmin = -10
        self._zmax = max(self._programmable, 300)

        self._title = title
        self._scale = scale
        self._interval = update_interval_ms / 1000.0
        self._trail_len = trail_length
        self._running = False
        self._thread = None

        # Per-drone state
        self._trails = {}       # uavid -> deque of (x, y, z)
        self._led_state = {}    # uavid -> (r, g, b) LED color
        self._color_cache = {}
        self._color_idx = 0

        # Canvas dimensions (pyfii layout: 1200x600 base)
        self._W = int(1200 * scale)
        self._H = int(600 * scale)
        self._V_SIZE = int(600 * scale)
        self._V_SIDE_H = int(270 * scale)
        self._V_STATUS_TOP = int(540 * scale)

        # Drone body size (like pyfii F600)
        self._DRONE_R = 6.3   # half-diagonal (cm), scaled from pyfii's 12.6/2
        self._DRONE_R_PX = 5  # motor circle radius in px

    # ── public API ──────────────────────────────────

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[PositionViewer] started "
              f"(programmable={self._programmable}cm, "
              f"range=[{self._xmin}, {self._xmax}], "
              f"trail={self._trail_len})")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        try:
            cv2.destroyWindow(self._title)
        except Exception:
            cv2.destroyAllWindows()
        print("[PositionViewer] stopped")

    @property
    def is_running(self):
        return self._running

    def set_led(self, uavid, color_bgr):
        """Set the LED color for a drone's center dot (BGR tuple or hex int)."""
        if isinstance(color_bgr, int):
            color_bgr = (color_bgr & 0xFF, (color_bgr >> 8) & 0xFF,
                         (color_bgr >> 16) & 0xFF)
        self._led_state[uavid] = color_bgr

    # ── internal ────────────────────────────────────

    def _run(self):
        bg = self._build_background()
        while self._running:
            try:
                frame = bg.copy()
                self._draw_drones(frame)
                cv2.imshow(self._title, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    self._running = False
                    break
                if cv2.getWindowProperty(self._title, cv2.WND_PROP_VISIBLE) < 1:
                    self._running = False
                    break
            except Exception:
                traceback.print_exc()
            time.sleep(self._interval)
        try:
            cv2.destroyWindow(self._title)
        except Exception:
            pass

    def _build_background(self):
        W, H, VS = self._W, self._H, self._V_SIZE
        img = np.zeros((H, W, 3), dtype=np.uint8)

        # Top-down (XY) area
        cv2.rectangle(img, (0, 0), (VS, VS), (255, 255, 255), -1)

        grid_step = 10 if self._actual <= 120 else 50
        for v in range(self._xmin, self._xmax + 1, grid_step):
            px = self._xy_to_px(v, 0)[0]
            cv2.line(img, (px, 0), (px, VS), (220, 220, 220), 1)
        for v in range(self._ymin, self._ymax + 1, grid_step):
            py = self._xy_to_px(0, v)[1]
            cv2.line(img, (0, py), (VS, py), (220, 220, 220), 1)

        p0 = self._xy_to_px(0, 0)
        p1 = self._xy_to_px(self._programmable, self._programmable)
        cv2.rectangle(img, p0, p1, (128, 128, 128), 1, cv2.LINE_AA)

        b0 = self._xy_to_px(self._xmin, self._ymin)
        b1 = self._xy_to_px(self._xmax, self._ymax)
        cv2.rectangle(img, b0, b1, (0, 0, 0), 2)

        ox, oy = self._xy_to_px(0, 0)
        cv2.line(img, (ox - 8, oy), (ox + 8, oy), (100, 100, 100), 1)
        cv2.line(img, (ox, oy - 8), (ox, oy + 8), (100, 100, 100), 1)

        # Right panels
        cv2.rectangle(img, (VS, 0), (W, self._V_SIDE_H), (40, 40, 40), -1)
        cv2.rectangle(img, (VS, self._V_SIDE_H), (W, self._V_STATUS_TOP),
                      (40, 40, 40), -1)
        cv2.rectangle(img, (VS, self._V_STATUS_TOP), (W, H), (30, 30, 30), -1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, "FRONT (X-Z)", (VS + 10, 20), font,
                    0.45 * self._scale, (200, 200, 200), 1)
        cv2.putText(img, "RIGHT (Y-Z)", (VS + 10, self._V_SIDE_H + 20),
                    font, 0.45 * self._scale, (200, 200, 200), 1)

        for v in range(self._xmin, self._xmax + 1, grid_step):
            px = self._xz_to_px(v, 0)[0]
            if VS <= px < W:
                cv2.line(img, (px, 0), (px, self._V_SIDE_H), (60, 60, 60), 1)
        for v in range(self._ymin, self._ymax + 1, grid_step):
            px = self._yz_to_px(v, 0)[0]
            if VS <= px < W:
                cv2.line(img, (px, self._V_SIDE_H),
                         (px, self._V_STATUS_TOP), (60, 60, 60), 1)

        for z in range(0, self._zmax + 1, 50):
            _, py_f = self._xz_to_px(0, z)
            _, py_r = self._yz_to_px(0, z)
            cv2.line(img, (VS, py_f), (W, py_f), (60, 60, 60), 1)
            cv2.line(img, (VS, py_r), (W, py_r), (60, 60, 60), 1)

        return img

    # ── coordinate transforms ─────────────────────

    def _xy_to_px(self, x, y):
        margin_px = 15
        usable = self._V_SIZE - 2 * margin_px
        px = int(margin_px + (x - self._xmin) / (self._xmax - self._xmin) * usable)
        py = int(margin_px + (self._ymax - y) / (self._ymax - self._ymin) * usable)
        return (px, py)

    def _xz_to_px(self, x, z):
        margin_px = 10
        usable_w = self._W - self._V_SIZE - 2 * margin_px
        usable_h = self._V_SIDE_H - 2 * margin_px
        px = int(self._V_SIZE + margin_px +
                 (x - self._xmin) / (self._xmax - self._xmin) * usable_w)
        py = int(margin_px + (self._zmax - z) / (self._zmax - self._zmin) * usable_h)
        return (px, py)

    def _yz_to_px(self, y, z):
        margin_px = 10
        usable_w = self._W - self._V_SIZE - 2 * margin_px
        usable_h = self._V_STATUS_TOP - self._V_SIDE_H - 2 * margin_px
        px = int(self._V_SIZE + margin_px +
                 (y - self._ymin) / (self._ymax - self._ymin) * usable_w)
        py = int(self._V_SIDE_H + margin_px +
                 (self._zmax - z) / (self._zmax - self._zmin) * usable_h)
        return (px, py)

    # ── drawing ─────────────────────────────────────

    def _get_color(self, uavid):
        if uavid not in self._color_cache:
            self._color_cache[uavid] = DRONE_COLORS[
                self._color_idx % len(DRONE_COLORS)]
            self._color_idx += 1
        return self._color_cache[uavid]

    def _draw_drone_4motor(self, img, x_px, y_px, yaw_rad, color, led_bgr=None):
        """pyfii-style F600 4-motor drone (top-down view).

        Four circles at motor positions, cross lines, center LED dot.
        """
        r = self._DRONE_R_PX
        d = self._DRONE_R  # half-diagonal in display units (unscaled)

        # Motor positions (4 corners, rotated by yaw)
        angles = [np.pi / 4, 3 * np.pi / 4, -3 * np.pi / 4, -np.pi / 4]
        motor_pts = []
        for a in angles:
            mx = int(x_px - d * np.cos(a + yaw_rad))
            my = int(y_px + d * np.sin(a + yaw_rad))
            motor_pts.append((mx, my))
            cv2.circle(img, (mx, my), r, color, 1)

        # Cross lines between opposite motors
        cv2.line(img, motor_pts[0], motor_pts[2], color, 1)
        cv2.line(img, motor_pts[1], motor_pts[3], color, 1)

        # Center LED
        led = led_bgr if led_bgr else color
        cv2.circle(img, (int(x_px), int(y_px)), r - 2, led, -1)

    def _draw_drone_simple(self, img, x_px, y_px, color):
        """Simple circle marker for side views."""
        cv2.circle(img, (x_px, y_px), 4, color, -1)
        cv2.circle(img, (x_px, y_px), 4, (0, 0, 0), 1)

    def _draw_drones(self, img):
        from fwfii.fc.heartbeat import HeartBeat

        with HeartBeat._lock:
            flights = dict(HeartBeat.flights)

        font = cv2.FONT_HERSHEY_SIMPLEX
        status_lines = []

        for uavid, flight in flights.items():
            x, y, z, yaw_cdeg = flight.display_position
            yaw_rad = yaw_cdeg / 100.0 * np.pi / 180.0
            bat_pct = flight.voltage if flight.voltage else 0
            color = self._get_color(uavid)
            led = self._led_state.get(uavid)

            # Trail
            if uavid not in self._trails:
                self._trails[uavid] = deque(maxlen=self._trail_len)
            trail = self._trails[uavid]
            trail.append((x, y, z))
            if len(trail) > 1:
                pts_xy = [self._xy_to_px(t[0], t[1]) for t in trail]
                pts_xz = [self._xz_to_px(t[0], t[2]) for t in trail]
                pts_yz = [self._yz_to_px(t[1], t[2]) for t in trail]
                for i in range(1, len(pts_xy)):
                    alpha = 0.15 + 0.55 * i / len(pts_xy)
                    c = tuple(int(v * alpha) for v in color)
                    cv2.line(img, pts_xy[i - 1], pts_xy[i], c, 1)
                    cv2.line(img, pts_xz[i - 1], pts_xz[i], c, 1)
                    cv2.line(img, pts_yz[i - 1], pts_yz[i], c, 1)

            # Top-down: 4-motor drone
            px, py = self._xy_to_px(x, y)
            self._draw_drone_4motor(img, px, py, yaw_rad, color, led_bgr=led)
            cv2.putText(img, str(uavid), (px + 10, py + 4), font,
                        0.35 * self._scale, color, 1)

            # Side views: simple dots
            fx, fy = self._xz_to_px(x, z)
            self._draw_drone_simple(img, fx, fy, color)
            rx, ry = self._yz_to_px(y, z)
            self._draw_drone_simple(img, rx, ry, color)

            # Status line
            status_lines.append(
                f"#{uavid} Bat:{bat_pct}% {flight.flightmode} {flight.fcstatus} "
                f"({x:.0f},{y:.0f},{z:.0f} yaw:{yaw_cdeg/100:.0f})"
            )

        # Status bar
        cv2.rectangle(img, (self._V_SIZE, self._V_STATUS_TOP),
                      (self._W, self._H), (30, 30, 30), -1)
        y_off = self._V_STATUS_TOP + 15
        for line in status_lines:
            cv2.putText(img, line, (self._V_SIZE + 10, y_off), font,
                        0.35 * self._scale, (220, 220, 220), 1)
            y_off += int(18 * self._scale)
            if y_off > self._H - 5:
                break

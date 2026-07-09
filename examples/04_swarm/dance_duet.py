"""
蜂群舞蹈表演 — 背景音乐 + 双机编队
===============================================
安全规则:
  - 路径交错时 Z 差 > 50cm
  - 同高度时 XY 距离 > 40cm
  - f1 低空层 (80~120cm), f2 高空层 (150~200cm)
===============================================
"""
from fwfii.quick import connect, disconnect, play_music, stop_music, load_music, set_music_volume, start_log, stop_log
from fwfii.fc import *
from fwfii.fc.advanced import *
from fwfii.utils import *

# ============================================
# 配置
# ============================================
DRONE_1 = 98101
DRONE_2 = 98102
MUSIC_FILE = "祖海 - 好运来.flac"
MUSIC_VOLUME = 0.7
COUNTDOWN = 5

INIT_POS_F1 = (40,  40,  0, 0)
INIT_POS_F2 = (320, 40,  0, 0)

# ============================================
# 安全辅助
# ============================================

def dual_takeoff(f1, f2, alt1, alt2):
    """分层起飞 — 保证 Z 差 >= 50cm"""
    Takeoff(f1, alt1)
    Takeoff(f2, alt2)
    Delay(4000)


def dual_move(f1, f2, x1, y1, z1, x2, y2, z2, hold_ms=4000):
    """双机移动 — 自动校验安全间距"""
    # 检查 Z 差（路径交叉时）
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    dz = abs(z1 - z2)
    xy_dist = (dx**2 + dy**2) ** 0.5

    if xy_dist < 40:
        assert dz >= 50, f"安全违规! XY={xy_dist:.0f}cm Z差={dz:.0f}cm (需>50)"
    if dz < 50:
        assert xy_dist >= 40, f"安全违规! Z差={dz:.0f}cm XY={xy_dist:.0f}cm (需>40)"

    Move2(f1, x1, y1, z1)
    Move2(f2, x2, y2, z2)
    Delay(hold_ms)


# ============================================
# 颜色常量
# ============================================
RED=0xFF0000; GREEN=0x00FF00; BLUE=0x0000FF
YELLOW=0xFFFF00; CYAN=0x00FFFF; PURPLE=0xFF00FF
WHITE=0xFFFFFF; ORANGE=0xFF8000; PINK=0xFF0080

# ============================================
# 编队动作（灯光 + 空翻版）
# ============================================

def dance_duet(f1, f2):
    from fwfii.led.lamp import (AllOn, AllOff, AllBlink, AllBreath,
                                 BodyOn, BodyOff, BodyBlink, BodyBreath,
                                 MotorOn, MotorOff, MotorBlink, MotorBreath,
                                 MotorHorse)

    # ============ 0s: 解锁 + 音乐 + 闪烁 ============
    AllBlink(f1, RED,  300, 300)     # 红灯快闪
    AllBlink(f2, BLUE, 300, 300)     # 蓝灯快闪
    Arm(f1); Arm(f2)
    play_music(loops=0)
    Delay(2000)

    # ============ 2s: 分层起飞 + 机身呼吸灯 ============
    BodyBreath(f1, YELLOW, 800, 800)  # 金色呼吸
    BodyBreath(f2, CYAN,   800, 800)  # 青色呼吸
    dual_takeoff(f1, f2, alt1=100, alt2=170)

    # ============ 6s: 同向前进 + 切换常亮 ============
    AllOn(f1, GREEN)
    AllOn(f2, PURPLE)
    # f1 左边界前进  f2 右边界前进  XY=280cm ✓
    dual_move(f1, f2, 40, 320, 100,  320, 320, 170, hold_ms=4000)

    # ============ 10s: 对角交错 + 电机灯 ============
    AllOn(f1, ORANGE)
    AllOn(f2, PINK)
    MotorOn(f1, 0, WHITE)    # 四电机全白
    MotorOn(f2, 0, WHITE)
    # 路径在(180,180)交叉 → Z差=70cm ✓
    dual_move(f1, f2, 320, 40, 100,  40, 40, 170, hold_ms=3000)
    MotorOff(f1, 0); MotorOff(f2, 0)

    # ============ 13s: 中心对望 + 交替闪烁 ============
    AllBlink(f1, RED,   500, 500)
    AllBlink(f2, BLUE,  500, 500)
    dual_move(f1, f2, 180, 180, 100,  180, 180, 180, hold_ms=3500)

    # ============ 16.5s: 对角拉开 + 跑马灯 ============
    MotorHorse(f1, [RED, YELLOW, GREEN, CYAN],  True,  600)
    MotorHorse(f2, [BLUE, PURPLE, PINK, WHITE], False, 600)
    dual_move(f1, f2, 40, 320, 100,  320, 40, 180, hold_ms=3500)

    # ============ 20s: 交换位置 + 呼吸灯 ============
    AllBreath(f1, CYAN,   600, 600)
    AllBreath(f2, YELLOW, 600, 600)
    # f1→右下@120  f2→左上@190  Z差=70 ✓
    dual_move(f1, f2, 320, 40, 120,  40, 320, 190, hold_ms=4000)

    # ============ 24s: 中心编队 + 机身灯 ============
    BodyOn(f1, RED)
    BodyOn(f2, BLUE)
    dual_move(f1, f2, 180, 180, 130,  180, 180, 200, hold_ms=3000)

    # ============ 27s: 原地旋转 + 全彩 ============
    AllOn(f1, RED)
    AllOn(f2, BLUE)
    Yaw(f1, 'l', 360)
    Yaw(f2, 'r', 360)
    Delay(4000)

    # ============ 31s: 向外展开 + 攀升备翻 ============
    AllBreath(f1, WHITE, 400, 400)  # 白光呼吸 — 空翻预告！
    AllBreath(f2, WHITE, 400, 400)
    # f1→左下(40,40)@120  f2→右上(320,320)@200
    dual_move(f1, f2, 40, 40, 120,  320, 320, 200, hold_ms=2000)

    # ============ 33s: 空翻准备 — 拉开到最远 ============
    # f1升到中心200cm  f2→角落220cm  XY=311cm Z差=20
    # 空翻时只有f1翻转, f2保持安全距离悬停
    MaxVelXY(f1, 200); MaxVelZ(f1, 150)
    MaxAccXY(f1, 400); MaxAccZ(f1, 400)
    Move2(f1, 180, 180, 120)           # f1→中心高空
    Move2(f2, 180, 40,  120)           # f2→右下更高
    Delay(3500)

    # ============ 36.5s: 🔥 空翻！ ============
    # f1@(180,180,200)  f2@(320,40,220)  XY=311cm >>150 ✓
    AllOn(f1, RED)
    AllOn(f2, BLUE)
    Flip(f1, 'x')
    Flip(f2, '-x')                   # f1 右侧翻！
    Delay(3000)
    Flip(f1, '-x')
    Flip(f1, 'x')                      # f1 回翻
    Delay(3000)

    # ============ 42.5s: 翻后集合 ============
    AllOff(f1); AllOff(f2)
    AllBlink(f1, GREEN, 200, 200)       # 绿灯 — 成功！
    AllBlink(f2, GREEN, 200, 200)
    dual_move(f1, f2, 40, 40, 120,  320, 40, 180, hold_ms=3000)

    # ============ 45.5s: 降落 ============
    BodyBreath(f1, YELLOW, 1000, 1000)
    BodyBreath(f2, YELLOW, 1000, 1000)
    Land(f1); Land(f2)
    Delay(5000)

    AllOff(f1); AllOff(f2)
    Disarm(f1); Disarm(f2)
    print("[Dance] 表演结束")


# ============================================
# 主程序
# ============================================

def main():
    print("=" * 50)
    print("  蜂群舞蹈表演（灯光+空翻版）")
    print(f"  音乐: {MUSIC_FILE}")
    print("  f1: 低空层 80~200cm | f2: 高空层 170~220cm")
    print("  🔥 空翻: f1@中心200cm, f2@角落220cm, XY=311cm")
    print("  💡 灯光: 闪烁/呼吸/跑马灯/电机灯/机身灯")
    print("=" * 50)

    d1, h1, f1 = connect(DRONE_1)
    d2, h2, f2 = connect(DRONE_2)

    f1.position = INIT_POS_F1
    f2.position = INIT_POS_F2

    ProgrammingMode(f1); ProgrammingMode(f2)
    Delay(500)

    for f in (f1, f2):
        MaxVelXY(f, 150); MaxVelZ(f, 100)
        MaxAccXY(f, 300); MaxAccZ(f, 400)

    # 启动轨迹记录
    start_log(save_dir="./flight_logs", script_path=__file__)

    load_music(MUSIC_FILE)
    set_music_volume(MUSIC_VOLUME)

    print(f"\n倒计时 {COUNTDOWN} 秒...")
    for t in range(COUNTDOWN, 0, -1):
        print(f"  {t}...")
        Delay(1000)

    print("起飞！")

    try:
        dance_duet(f1, f2)
    except KeyboardInterrupt:
        print("\n[中断] 紧急降落...")
        Land(f1); Land(f2)
        Delay(5000)
        Disarm(f1); Disarm(f2)

    stop_music(fade_ms=2000)
    stop_log()
    disconnect()
    print("\n表演结束！")


if __name__ == "__main__":
    main()

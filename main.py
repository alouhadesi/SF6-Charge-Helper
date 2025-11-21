import pygame
import sys
import ctypes
import math
import array
import warnings
from collections import deque

warnings.filterwarnings("ignore")

# --- 1. 虚拟键码 ---
# --- 1. 虚拟键码 (扩充版 - 修复自定义按键无效的问题) ---
VK_CODE = {
    'backspace': 0x08, 'tab': 0x09, 'clear': 0x0C, 'enter': 0x0D, 'return': 0x0D,
    'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12, 'pause': 0x13, 'caps lock': 0x14,
    'escape': 0x1B, 'esc': 0x1B, 'space': 0x20, 'page up': 0x21, 'page down': 0x22,
    'end': 0x23, 'home': 0x24, 'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
    'select': 0x29, 'print': 0x2A, 'execute': 0x2B, 'print screen': 0x2C, 'insert': 0x2D,
    'delete': 0x2E, 'help': 0x2F,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46, 'g': 0x47,
    'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E,
    'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54, 'u': 0x55,
    'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
    'numpad0': 0x60, 'numpad1': 0x61, 'numpad2': 0x62, 'numpad3': 0x63,
    'numpad4': 0x64, 'numpad5': 0x65, 'numpad6': 0x66, 'numpad7': 0x67,
    'numpad8': 0x68, 'numpad9': 0x69, 'multiply': 0x6A, 'add': 0x6B,
    'separator': 0x6C, 'subtract': 0x6D, 'decimal': 0x6E, 'divide': 0x6F,
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74,
    'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79,
    'f11': 0x7A, 'f12': 0x7B,
    'num lock': 0x90, 'scroll lock': 0x91,
    'left shift': 0xA0, 'right shift': 0xA1,
    'left ctrl': 0xA2, 'right ctrl': 0xA3,
    'left alt': 0xA4, 'right alt': 0xA5,
    ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD, '.': 0xBE, '/': 0xBF,
    '`': 0xC0, '[': 0xDB, '\\': 0xDC, ']': 0xDD, "'": 0xDE
}


def is_key_down_vk(vk_code):
    if vk_code is None: return False
    return (ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000) != 0


# --- 2. 默认键位配置 ---
KEY_CONFIG = {
    "BACK": ['a', 'left'],
    "FWD": ['d', 'right'],
    "DOWN": ['s', 'down'],
    "UP": ['w', 'up'],
    "P": ['u', 'i', 'o'],
    "K": ['j', 'k', 'l']
}

# --- 3. 招式数据库 ---
BACK_FWD_MOVES = [
    {"name": "古烈-音速手刀", "charge": 45, "btn": "P"},
    {"name": "春丽-气功拳", "charge": 50, "btn": "P"},
    {"name": "本田-超级头锤", "charge": 40, "btn": "P"},
    {"name": "布兰卡-回旋撞", "charge": 40, "btn": "P"},
    {"name": "DJ-破空飞刃", "charge": 45, "btn": "P"},
    {"name": "维加-电钻", "charge": 45, "btn": "P"},
]

DOWN_UP_MOVES = [
    {"name": "古烈-空翻脚刀", "charge": 45, "btn": "K"},
    {"name": "春丽-回旋鹤脚蹴", "charge": 30, "btn": "K"},
    {"name": "本田-百贯落", "charge": 40, "btn": "K"},
    {"name": "布兰卡-上冲回旋", "charge": 40, "btn": "K"},
    {"name": "DJ-屈体极点", "charge": 40, "btn": "K"},
    {"name": "维加-脚踏", "charge": 40, "btn": "K"},
]

CHAR_PROFILES = [
    {"name": "通用标准",    "t_46": 40, "t_28": 40},
    {"name": "古烈 (Guile)", "t_46": 45, "t_28": 45},
    {"name": "春丽 (Chun-Li)", "t_46": 50, "t_28": 30},
    {"name": "布兰卡 (Blanka)", "t_46": 40, "t_28": 40},
    {"name": "本田 (Honda)",  "t_46": 40, "t_28": 40},
    {"name": "DJ (DeeJay)",   "t_46": 45, "t_28": 40},
    {"name": "维加 (Bison)",  "t_46": 45, "t_28": 40},
    {"name": "极速测试",      "t_46": 30, "t_28": 30},
]

# --- 4. 核心参数 ---
FPS = 60
CHARGE_INTENT_THRESHOLD = 20
ERROR_DURATION = 60

# --- 5. UI 参数 (基准值) ---
REF_WIDTH = 800
REF_HEIGHT = 400
SCROLL_SPEED = 7
JUDGE_LINE_X = 300

# 颜色库
COLOR_BG = (20, 20, 20)
COLOR_JUDGE_LINE = (255, 255, 255)
COLOR_TGT_CORE = (255, 255, 255)
COLOR_TGT_BUFFER = (30, 144, 255)
COLOR_TGT_CHARGE = (218, 165, 32)
COLOR_TGT_PRE = (60, 50, 20)
COLOR_TGT_GAP = (0, 255, 255)

COLOR_P = (255, 60, 60)  # 红
COLOR_K = (255, 160, 20)  # 橙
COLOR_FWD = (50, 205, 50)  # 绿
COLOR_UP = (0, 200, 200)  # 青
COLOR_BACK = (255, 255, 0)  # 黄
COLOR_DOWN = (0, 100, 255)  # 蓝

COLOR_USER_OK = (50, 205, 50)
COLOR_USER_FAIL = (220, 20, 60)
COLOR_OD = (255, 215, 0)
COLOR_WARN_TEXT = (255, 80, 80)
COLOR_TAB_ACTIVE = (80, 80, 80)
COLOR_TAB_INACTIVE = (40, 40, 40)
COLOR_BTN_IDLE = (60, 60, 60)
COLOR_BTN_HOVER = (100, 100, 100)
COLOR_BTN_WAIT = (20, 100, 200)
COLOR_ICON_BORDER = (255, 255, 255)
COLOR_ICON_SYMBOL = (20, 20, 20)


# --- 6. 音效引擎 ---
# --- 6. 音效引擎 (优化版: 使用柔和的正弦波) ---
class SoundEngine:
    def __init__(self):
        try:
            # 初始化混音器
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
            self.enabled = True

            # OK音效: 高频正弦波 (880Hz), 短促, 清脆
            self.snd_ok = self._generate_sine(880, 0.1, 0.2)

            # 错误音效: 低频正弦波 (150Hz), 稍长, 类似 "波~" 的声音，不刺耳
            self.snd_err = self._generate_sine(150, 0.25, 0.3)

        except Exception as e:
            print(f"Audio Init Failed: {e}")
            self.enabled = False

    def _generate_sine(self, freq, duration, volume):
        """生成柔和的正弦波"""
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * n_samples)
        amplitude = int(32767 * volume)

        for i in range(n_samples):
            # 计算正弦波: sin(2 * pi * freq * time)
            t = float(i) / sample_rate
            val = math.sin(2 * math.pi * freq * t)

            # 添加淡入淡出 (Fade In/Out) 以避免爆音
            fade = 1.0
            fade_len = 500  # 约10ms

            # 开头淡入
            if i < fade_len:
                fade = i / fade_len
            # 结尾淡出
            elif i > n_samples - fade_len:
                fade = (n_samples - i) / fade_len

            buf[i] = int(val * amplitude * fade)

        return pygame.mixer.Sound(buffer=buf)

    def play_ok(self):
        if self.enabled: self.snd_ok.play()

    def play_err(self):
        if self.enabled: self.snd_err.play()


# --- 7. 绘图引擎 ---
def draw_arrow_shape(surface, color, x, y, size, direction):
    cx, cy = x + size // 2, y + size // 2
    head_len, head_w = size // 1.8, size // 1.8
    shaft_len, shaft_w = size // 2.2, size // 5
    base_points = [
        (head_len, 0), (0, -head_w), (0, -shaft_w),
        (-shaft_len, -shaft_w), (-shaft_len, shaft_w),
        (0, shaft_w), (0, head_w)
    ]
    angle = 0
    if direction == "UP":
        angle = -90
    elif direction == "DOWN":
        angle = 90
    elif direction == "LEFT":
        angle = 180
    elif direction == "RIGHT":
        angle = 0

    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    final_points = []
    for px, py in base_points:
        rot_x = px * cos_a - py * sin_a
        rot_y = px * sin_a + py * cos_a
        final_points.append((cx + rot_x, cy + rot_y))
    pygame.draw.polygon(surface, color, final_points)
    pygame.draw.polygon(surface, COLOR_ICON_BORDER, final_points, 2)


def draw_text_icon(surface, bg_color, x, y, size, text, shape="CIRCLE", font=None):
    cx, cy = x + size // 2, y + size // 2
    radius = size // 2
    if shape == "CIRCLE":
        pygame.draw.circle(surface, bg_color, (cx, cy), radius)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), radius, 2)
    elif shape == "RHOMBUS":
        pts = [(cx, cy - radius), (cx + radius, cy), (cx, cy + radius), (cx - radius, cy)]
        pygame.draw.polygon(surface, bg_color, pts)
        pygame.draw.polygon(surface, (255, 255, 255), pts, 2)
    if font:
        txt_surf = font.render(text, True, COLOR_ICON_SYMBOL)
        txt_rect = txt_surf.get_rect(center=(cx, cy))
        surface.blit(txt_surf, txt_rect)


def draw_trail_line(surface, color, x, y, w, h):
    line_h = max(4, int(h * 0.15))
    line_y = y + (h - line_h) // 2
    pygame.draw.rect(surface, color, (x, line_y, w + 1, line_h))


def draw_transparent_rect(surf, color, rect, alpha):
    s = pygame.Surface((rect[2], rect[3]))
    s.set_alpha(alpha)
    s.fill(color)
    surf.blit(s, (rect[0], rect[1]))


def create_dynamic_chart(mode_type, move_data, retention):
    end = 160
    act = end + 5
    charge_frames = move_data["charge"]
    btn = move_data["btn"]

    chart = []
    if mode_type == "BACK_FWD":
        chart.append(
            {"track": "CHARGE", "type": "CHARGE", "start": end - charge_frames, "dur": charge_frames, "pre_buffer": 80,
             "text": "按住后"})
        chart.append({"track": "RELEASE", "type": "TAP", "start": act, "dur": 2, "buffer": 6, "text": "前"})
    else:
        chart.append(
            {"track": "CHARGE", "type": "CHARGE", "start": end - charge_frames, "dur": charge_frames, "pre_buffer": 80,
             "text": "按住下"})
        chart.append({"track": "RELEASE", "type": "TAP", "start": act, "dur": 2, "buffer": 6, "text": "上"})

    chart.append({"track": "ATK", "type": "TAP", "start": act, "dur": 2, "buffer": 6, "text": btn})

    loop_start = end + 200
    if mode_type == "BACK_FWD":
        chart.append({"track": "CHARGE", "type": "CHARGE", "start": loop_start, "dur": charge_frames, "pre_buffer": 80,
                      "text": "按住后"})
    else:
        chart.append({"track": "CHARGE", "type": "CHARGE", "start": loop_start, "dur": charge_frames, "pre_buffer": 80,
                      "text": "按住下"})

    chart.append(
        {"track": "RELEASE", "type": "TAP", "start": loop_start + charge_frames + 5, "dur": 2, "buffer": 6, "text": ""})
    chart.append(
        {"track": "ATK", "type": "TAP", "start": loop_start + charge_frames + 5, "dur": 2, "buffer": 6, "text": ""})
    return chart


MODES = {
    0: {"name": "自由练习", "type": "FREE"},
    1: {"name": "横向招式", "type": "BACK_FWD"},
    2: {"name": "纵向招式", "type": "DOWN_UP"},
    3: {"name": "说明/帧数", "type": "INFO"},     # ★ 改名：原本是 MOVELIST
    4: {"name": "按键设置", "type": "SETTINGS"}
}


# --- Input System (支持手柄与全键位版) ---
# --- Input System (带手柄支持 & 宽容缓冲版) ---
class InputSystem:
    def __init__(self):
        # 蓄力计数
        self.charge_cnt_back = 0
        self.charge_cnt_fwd = 0
        self.charge_cnt_down = 0

        # 残留计数
        self.retention_cnt_back = 0
        self.retention_cnt_fwd = 0
        self.retention_cnt_down = 0

        # ★★★ 新增：指令宽容缓冲计时器 ★★★
        self.tolerance_fwd = 0  # 记录"前"松开后的一小段时间
        self.tolerance_up = 0  # 记录"上"松开后的一小段时间

        self.socd_timer = 0
        self.prev_keys = {}
        self.prev_key_states = {}

        self.req_back = 40
        self.req_down = 40
        self.current_retention_limit = 10

    def check_keyboard(self, action_name):
        keys = KEY_CONFIG.get(action_name, [])
        for k_str in keys:
            vk = VK_CODE.get(k_str.lower())
            if is_key_down_vk(vk): return True
        return False

    def check_gamepad(self, action_name):
        if pygame.joystick.get_count() == 0: return False
        joy = pygame.joystick.Joystick(0)
        DEADZONE = 0.5
        hat_x, hat_y = joy.get_hat(0) if joy.get_numhats() > 0 else (0, 0)
        axis_x = joy.get_axis(0) if joy.get_numaxes() > 0 else 0
        axis_y = joy.get_axis(1) if joy.get_numaxes() > 1 else 0

        if action_name == "BACK":
            if hat_x == -1 or axis_x < -DEADZONE: return True
        elif action_name == "FWD":
            if hat_x == 1 or axis_x > DEADZONE: return True
        elif action_name == "DOWN":
            if hat_y == -1 or axis_y > DEADZONE: return True
        elif action_name == "UP":
            if hat_y == 1 or axis_y < -DEADZONE: return True
        elif action_name == "P":
            for b in [2, 3, 4, 6]:
                if b < joy.get_numbuttons() and joy.get_button(b): return True
        elif action_name == "K":
            for b in [0, 1, 5, 7]:
                if b < joy.get_numbuttons() and joy.get_button(b): return True
        return False

    def update(self, is_2p_side=False):
        # 1. 读取物理输入
        raw_left = self.check_keyboard("BACK") or self.check_gamepad("BACK")
        raw_right = self.check_keyboard("FWD") or self.check_gamepad("FWD")
        raw_down = self.check_keyboard("DOWN") or self.check_gamepad("DOWN")
        raw_up = self.check_keyboard("UP") or self.check_gamepad("UP")
        raw_p = self.check_keyboard("P") or self.check_gamepad("P")
        raw_k = self.check_keyboard("K") or self.check_gamepad("K")

        # 2. SOCD
        socd_h, socd_v = False, False
        if raw_left and raw_right:
            clean_left, clean_right = False, False
            socd_h = True
        else:
            clean_left, clean_right = raw_left, raw_right

        if raw_down and raw_up:
            clean_down, clean_up = False, True
            socd_v = True
        else:
            clean_down, clean_up = raw_down, raw_up

        if socd_h or socd_v:
            self.socd_timer += 1
        else:
            self.socd_timer = 0

        # 3. 蓄力计算
        if clean_left:
            self.charge_cnt_back = min(self.charge_cnt_back + 1, 60)
            self.retention_cnt_back = self.current_retention_limit
        else:
            if self.retention_cnt_back > 0:
                self.retention_cnt_back -= 1
            else:
                self.charge_cnt_back = 0

        if clean_right:
            self.charge_cnt_fwd = min(self.charge_cnt_fwd + 1, 60)
            self.retention_cnt_fwd = self.current_retention_limit
        else:
            if self.retention_cnt_fwd > 0:
                self.retention_cnt_fwd -= 1
            else:
                self.charge_cnt_fwd = 0

        if clean_down:
            self.charge_cnt_down = min(self.charge_cnt_down + 1, 60)
            self.retention_cnt_down = self.current_retention_limit
        else:
            if self.retention_cnt_down > 0:
                self.retention_cnt_down -= 1
            else:
                self.charge_cnt_down = 0

        # 4. Edge Detection
        jp_right = clean_right and not self.prev_keys.get("FWD", False)
        jp_up = clean_up and not self.prev_keys.get("UP", False)
        jp_left = clean_left and not self.prev_keys.get("BACK", False)
        jp_down = clean_down and not self.prev_keys.get("DOWN", False)
        jp_p = raw_p and not self.prev_keys.get("P", False)
        jp_k = raw_k and not self.prev_keys.get("K", False)

        self.prev_keys["FWD"] = clean_right
        self.prev_keys["UP"] = clean_up
        self.prev_keys["BACK"] = clean_left
        self.prev_keys["DOWN"] = clean_down
        self.prev_keys["P"] = raw_p
        self.prev_keys["K"] = raw_k

        def get_idxs(name):
            return [i for i, k in enumerate(KEY_CONFIG[name]) if is_key_down_vk(VK_CODE.get(k.lower()))]

        p_idxs = get_idxs("P")
        k_idxs = get_idxs("K")
        if raw_p and not p_idxs: p_idxs = [-1]
        if raw_k and not k_idxs: k_idxs = [-1]

        # 1P/2P 映射
        if is_2p_side:
            logic_back_clean = clean_right
            logic_fwd_clean = clean_left
            logic_jp_back = jp_right
            logic_jp_fwd = jp_left
            logic_raw_back = raw_right
            logic_raw_fwd = raw_left
            logic_charge_val = self.charge_cnt_fwd
            logic_is_charged = self.charge_cnt_fwd >= self.req_back
            logic_ghost = (not clean_right and self.retention_cnt_fwd > 0)
        else:
            logic_back_clean = clean_left
            logic_fwd_clean = clean_right
            logic_jp_back = jp_left
            logic_jp_fwd = jp_right
            logic_raw_back = raw_left
            logic_raw_fwd = raw_right
            logic_charge_val = self.charge_cnt_back
            logic_is_charged = self.charge_cnt_back >= self.req_back
            logic_ghost = (not clean_left and self.retention_cnt_back > 0)

        # ★★★ 宽容度缓冲逻辑 (Input Buffer) ★★★
        # 只要物理按了前(RAW)，就将缓冲池填满 (比如 5帧)
        # 这样即使松手了，接下来的 5帧内 LENIENT_FWD 依然为 True

        if logic_raw_fwd:
            self.tolerance_fwd = 6  # 6帧宽容 (约0.1秒)
        elif self.tolerance_fwd > 0:
            self.tolerance_fwd -= 1

        if raw_up:  # 纵向不分左右，直接用 raw_up
            self.tolerance_up = 6
        elif self.tolerance_up > 0:
            self.tolerance_up -= 1

        # 自由模式专用的左右缓冲
        if raw_right:
            self.tolerance_right = 6
        else:
            self.tolerance_right = getattr(self, 'tolerance_right', 0) - 1

        if raw_left:
            self.tolerance_left = 6
        else:
            self.tolerance_left = getattr(self, 'tolerance_left', 0) - 1

        return {
            "BACK": logic_back_clean, "FWD": logic_fwd_clean,
            "JP_BACK": logic_jp_back, "JP_FWD": logic_jp_fwd,
            "CHARGE_VAL_BACK": logic_charge_val,
            "IS_CHARGED_BACK": logic_is_charged,
            "GHOST_BACK": logic_ghost,

            "RAW_BACK": logic_raw_back,
            "RAW_FWD": logic_raw_fwd,

            # ★★★ 返回宽容判定值 ★★★
            "LENIENT_FWD": self.tolerance_fwd > 0,
            "LENIENT_UP": self.tolerance_up > 0,
            "LENIENT_LEFT": getattr(self, 'tolerance_left', 0) > 0,
            "LENIENT_RIGHT": getattr(self, 'tolerance_right', 0) > 0,

            "ABS_LEFT": clean_left, "ABS_RIGHT": clean_right,
            "RAW_LEFT": raw_left, "RAW_RIGHT": raw_right,
            "JP_LEFT": jp_left, "JP_RIGHT": jp_right,
            "CHARGE_VAL_LEFT": self.charge_cnt_back,
            "CHARGE_VAL_RIGHT": self.charge_cnt_fwd,
            "IS_CHARGED_LEFT": self.charge_cnt_back >= self.req_back,
            "IS_CHARGED_RIGHT": self.charge_cnt_fwd >= self.req_back,
            "GHOST_LEFT": (not clean_left and self.retention_cnt_back > 0),
            "GHOST_RIGHT": (not clean_right and self.retention_cnt_fwd > 0),

            "DOWN": clean_down, "UP": clean_up,
            "JP_DOWN": jp_down, "JP_UP": jp_up,
            "CHARGE_VAL_DOWN": self.charge_cnt_down,
            "IS_CHARGED_DOWN": self.charge_cnt_down >= self.req_down,
            "GHOST_DOWN": (not clean_down and self.retention_cnt_down > 0),
            "RAW_UP": raw_up,

            "P": raw_p, "K": raw_k,
            "JP_P": jp_p, "JP_K": jp_k,
            "P_IDXS": p_idxs, "K_IDXS": k_idxs,
            "JP_P_IDXS": [], "JP_K_IDXS": [],
            "SOCD_H": socd_h, "SOCD_V": socd_v, "SOCD_FRAMES": self.socd_timer
        }


class ErrorManager:
    def __init__(self):
        self.errors = []

    def add(self, msg):
        for e in self.errors:
            if e['msg'] == msg:
                e['timer'] = ERROR_DURATION
                return
        self.errors.append({'msg': msg, 'timer': ERROR_DURATION})

    def update(self):
        for e in self.errors: e['timer'] -= 1
        self.errors = [e for e in self.errors if e['timer'] > 0]

    def draw(self, screen, font, w, h):
        start_y = h - 100
        for i, e in enumerate(self.errors):
            alpha = 255
            if e['timer'] < 20: alpha = int(255 * (e['timer'] / 20))
            txt_surf = font.render(e['msg'], True, COLOR_WARN_TEXT)
            txt_surf.set_alpha(alpha)
            text_rect = txt_surf.get_rect(center=(w // 2, start_y - i * 30))
            bg_rect = text_rect.inflate(20, 10)
            bg_surf = pygame.Surface((bg_rect.w, bg_rect.h))
            bg_surf.fill((0, 0, 0))
            bg_surf.set_alpha(max(0, alpha - 50))
            screen.blit(bg_surf, bg_rect)
            screen.blit(txt_surf, text_rect)


def main():
    pygame.init()
    # ★★★ 新增：初始化手柄模块 ★★★
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joy in joysticks:
        joy.init()
    # ★★★★★★★★★★★★★★★★★★★★

    screen = pygame.display.set_mode((REF_WIDTH, REF_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("SF6 Charge Helper (Final Centered)")
    try:
        icon_surface = pygame.image.load('logo.ico')
        pygame.display.set_icon(icon_surface)
    except:
        pass

    clock = pygame.time.Clock()
    sound_engine = SoundEngine()
    error_mgr = ErrorManager()

    input_sys = InputSystem()
    user_history = deque(maxlen=400)
    frame_count = 0

    current_mode_idx = 0
    current_move_indices = {1: 0, 2: 0}
    char_profile_idx = 0
    is_2p_side = False
    was_charged_back = False
    was_charged_down = False
    binding_action = None

    TAB_COUNT = 5
    last_size = (0, 0)

    font = None
    font_bold = None
    font_alert = None
    font_icon = None

    def update_fonts(h_scale):
        base_size = 12
        try:
            f = pygame.font.SysFont("Microsoft YaHei", int(base_size * h_scale))
            fb = pygame.font.SysFont("Microsoft YaHei", int(14 * h_scale), bold=True)
            fa = pygame.font.SysFont("Microsoft YaHei", int(20 * h_scale), bold=True)
            fi = pygame.font.SysFont("Arial", int(10 * h_scale), bold=True)
        except:
            f = pygame.font.SysFont("SimHei", int(base_size * h_scale))
            fb = pygame.font.SysFont("SimHei", int(14 * h_scale), bold=True)
            fa = pygame.font.SysFont("SimHei", int(20 * h_scale), bold=True)
            fi = f
        return f, fb, fa, fi

    running = True
    while running:
        # 每一帧开始先重置 active_move_data
        active_move_data = None

        # --- 1. 动态尺寸与布局 (Layout Calculation) ---
        WIN_W, WIN_H = screen.get_size()
        if (WIN_W, WIN_H) != last_size:
            h_ratio = WIN_H / REF_HEIGHT
            h_ratio = max(0.8, h_ratio)
            font, font_bold, font_alert, font_icon = update_fonts(h_ratio)
            last_size = (WIN_W, WIN_H)

        tab_width = WIN_W // TAB_COUNT
        top_ui_h = int(80 * (WIN_H / REF_HEIGHT))
        bottom_ui_h = int(40 * (WIN_H / REF_HEIGHT))
        avail_h = WIN_H - top_ui_h - bottom_ui_h

        track_gap = avail_h // 4
        TRACK_H = int(track_gap * 0.75)
        ICON_SIZE = int(TRACK_H * 0.85)

        start_track_y = top_ui_h + 10
        TRACK_Y = {
            "ATK_P": start_track_y,
            "ATK_K": start_track_y + track_gap,
            "RELEASE": start_track_y + track_gap * 2,
            "CHARGE": start_track_y + track_gap * 3
        }

        TAB_H = int(top_ui_h * 0.5)
        SELECTOR_Y = int(top_ui_h * 0.6)

        # --- 2. 事件处理 (Event Handling) ---
        events = pygame.event.get()
        clicked = False
        mx, my = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN: clicked = True
            # 按键绑定逻辑
            if binding_action is not None and event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:
                    key_name = pygame.key.name(event.key)
                    if key_name.lower() in VK_CODE:
                        current_keys = KEY_CONFIG[binding_action[0]]
                        slot_idx = binding_action[1]
                        while len(current_keys) <= slot_idx: current_keys.append("None")
                        current_keys[slot_idx] = key_name
                binding_action = None

        # Tab 切换逻辑
        if clicked and my < TAB_H and binding_action is None:
            idx = mx // tab_width
            if idx in MODES:
                current_mode_idx = idx
                frame_count = 0
                user_history.clear()
                input_sys.charge_cnt_back = 0
                input_sys.charge_cnt_fwd = 0
                input_sys.charge_cnt_down = 0
                error_mgr.errors.clear()

        curr_mode_data = MODES[current_mode_idx]
        mode_type = curr_mode_data["type"]

        # --- 3. 逻辑与数据准备 (Logic & Data Prep) ---

        # A. 招式练习模式 (Mode 1 & 2)
        if mode_type in ["BACK_FWD", "DOWN_UP"]:
            move_list = BACK_FWD_MOVES if mode_type == "BACK_FWD" else DOWN_UP_MOVES
            curr_idx = current_move_indices[current_mode_idx]

            center_x = WIN_W // 2
            btn_h = int(30 * (WIN_H / REF_HEIGHT))
            btn_prev_rect = pygame.Rect(center_x - 150, SELECTOR_Y, 40, btn_h)
            btn_next_rect = pygame.Rect(center_x + 110, SELECTOR_Y, 40, btn_h)

            # 招式切换点击
            if clicked and btn_prev_rect.collidepoint(mx, my):
                current_move_indices[current_mode_idx] = (curr_idx - 1) % len(move_list)
                frame_count = 0
            elif clicked and btn_next_rect.collidepoint(mx, my):
                current_move_indices[current_mode_idx] = (curr_idx + 1) % len(move_list)
                frame_count = 0

            # 1P/2P 切换点击 (仅 Mode 1)
            if mode_type == "BACK_FWD":
                btn_side_w, btn_side_h = 70, 24
                btn_side_rect = pygame.Rect(WIN_W - btn_side_w - 20, TAB_H + 8, btn_side_w, btn_side_h)
                if clicked and btn_side_rect.collidepoint(mx, my):
                    is_2p_side = not is_2p_side

            active_move_data = move_list[current_move_indices[current_mode_idx]]
            charge_val = active_move_data["charge"]
            input_sys.req_back = charge_val
            input_sys.req_down = charge_val
            input_sys.current_retention_limit = 10 if mode_type == "BACK_FWD" else 12

        # B. 自由模式 (Mode 0)
        elif mode_type == "FREE":
            center_x = WIN_W // 2
            btn_h = int(30 * (WIN_H / REF_HEIGHT))
            btn_prev_rect = pygame.Rect(center_x - 180, SELECTOR_Y, 40, btn_h)
            btn_next_rect = pygame.Rect(center_x + 180, SELECTOR_Y, 40, btn_h)

            if clicked and btn_prev_rect.collidepoint(mx, my):
                char_profile_idx = (char_profile_idx - 1) % len(CHAR_PROFILES)
            elif clicked and btn_next_rect.collidepoint(mx, my):
                char_profile_idx = (char_profile_idx + 1) % len(CHAR_PROFILES)

            profile = CHAR_PROFILES[char_profile_idx]
            input_sys.req_back = profile["t_46"]
            input_sys.req_down = profile["t_28"]
            input_sys.current_retention_limit = 10

        else:
            # 说明页/设置页保底
            input_sys.req_back = 40
            input_sys.req_down = 40
            input_sys.current_retention_limit = 10

        # --- 4. 输入读取 (Input Processing) - 必须对所有模式生效 ---

        # 1P/2P 逻辑开关只传给练习模式，自由模式传 False (手动处理)
        pass_2p_flag = is_2p_side if mode_type in ["BACK_FWD", "DOWN_UP"] else False

        curr_input = input_sys.update(is_2p_side=pass_2p_flag)
        user_history.append((frame_count, curr_input))

        # 播放音效
        if (curr_input["IS_CHARGED_LEFT"] or curr_input["IS_CHARGED_RIGHT"]) and not was_charged_back:
            sound_engine.play_ok()
        if curr_input["IS_CHARGED_DOWN"] and not was_charged_down:
            sound_engine.play_ok()
        was_charged_back = (curr_input["IS_CHARGED_LEFT"] or curr_input["IS_CHARGED_RIGHT"])
        was_charged_down = curr_input["IS_CHARGED_DOWN"]

        # --- 5. 判定逻辑 (Judge Logic) - 修复版 ---
        has_new_error = False

        # SOCD 冲突报警 (优先级最高)
        if curr_input["SOCD_H"]:
            if current_mode_idx in [0, 1] and curr_input["SOCD_FRAMES"] > 4:
                error_mgr.add("冲突警告! (后+前 按死)")
                has_new_error = True
        if curr_input["SOCD_V"]:
            if current_mode_idx in [0, 2] and curr_input["SOCD_FRAMES"] > 4:
                error_mgr.add("冲突警告! (下+上 按死)")
                has_new_error = True

        req_frames = input_sys.req_back
        req_down_frames = input_sys.req_down

        # === 自由模式判定 (FREE) ===
        if mode_type == "FREE":
            # 1. 蓄力不足检测 (Charge Insufficient)
            # -------------------------------------------------
            # 场景 A: 左蓄右出 (1P)
            # 检测条件: 按下了右键(JP_RIGHT)
            if curr_input["JP_RIGHT"]:
                val = curr_input['CHARGE_VAL_LEFT']
                # 如果左边没蓄满
                if not curr_input["IS_CHARGED_LEFT"]:
                    # 即使有轻微 SOCD (换手不干净)，只要时间短(<5帧)也报蓄力不足
                    if not curr_input["SOCD_H"] or curr_input["SOCD_FRAMES"] < 5:
                        if val > CHARGE_INTENT_THRESHOLD:  # 只有当蓄力超过一定程度(意图)才报，防止走路时乱报
                            error_mgr.add(f"左(后)蓄力不足! ({val}/{req_frames})")
                            has_new_error = True

            # 场景 B: 右蓄左出 (2P)
            if curr_input["JP_LEFT"]:
                val = curr_input['CHARGE_VAL_RIGHT']
                if not curr_input["IS_CHARGED_RIGHT"]:
                    if not curr_input["SOCD_H"] or curr_input["SOCD_FRAMES"] < 5:
                        if val > CHARGE_INTENT_THRESHOLD:
                            error_mgr.add(f"右(前)蓄力不足! ({val}/{req_frames})")
                            has_new_error = True

            # 2. 抢招检测 (Premature Attack - 互斥优化)
            # -------------------------------------------------
            if curr_input["JP_P"]:
                # 状态检查
                has_charge_left = curr_input["IS_CHARGED_LEFT"] or curr_input["GHOST_LEFT"]
                has_charge_right = curr_input["IS_CHARGED_RIGHT"] or curr_input["GHOST_RIGHT"]

                input_right_ok = curr_input["LENIENT_RIGHT"]  # 宽容缓冲
                input_left_ok = curr_input["LENIENT_LEFT"]

                # 成功判定
                success_1p = has_charge_left and input_right_ok
                success_2p = has_charge_right and input_left_ok

                # 只有两边都失败时，才报错
                if not success_1p and not success_2p:
                    if has_charge_left and not input_right_ok:
                        error_mgr.add("1P抢招! (右未按)")
                        has_new_error = True
                    elif has_charge_right and not input_left_ok:
                        error_mgr.add("2P抢招! (左未按)")
                        has_new_error = True

            # 3. 纵向检测 (Down/Up)
            # -------------------------------------------------
            if curr_input["JP_UP"]:
                val = curr_input['CHARGE_VAL_DOWN']
                if not curr_input["IS_CHARGED_DOWN"]:
                    if not curr_input["SOCD_V"] or curr_input["SOCD_FRAMES"] < 5:
                        if val > CHARGE_INTENT_THRESHOLD:
                            error_mgr.add(f"下蓄力不足! ({val}/{req_down_frames})")
                            has_new_error = True

            if curr_input["JP_K"]:
                pot_down = curr_input["IS_CHARGED_DOWN"] or curr_input["GHOST_DOWN"]
                if pot_down and not curr_input["LENIENT_UP"]:
                    error_mgr.add("抢招! (上未按)")
                    has_new_error = True


        # === 练习模式判定 (Mode 1 & 2) ===
        elif mode_type in ["BACK_FWD", "DOWN_UP"]:
            check_back = (mode_type == "BACK_FWD")
            check_down = (mode_type == "DOWN_UP")

            if check_back:
                # 蓄力不足
                if curr_input["JP_FWD"]:
                    val = curr_input['CHARGE_VAL_BACK']
                    if not curr_input["IS_CHARGED_BACK"]:
                        # 放宽 SOCD 限制
                        if not curr_input["SOCD_H"] or curr_input["SOCD_FRAMES"] < 5:
                            if val > CHARGE_INTENT_THRESHOLD:
                                error_mgr.add(f"后蓄力不足! ({val}/{req_frames})")
                                has_new_error = True

                # 抢招
                active_move = active_move_data if active_move_data else {}
                if active_move.get("btn") == "P":
                    if curr_input["JP_P"]:
                        pot = curr_input["IS_CHARGED_BACK"] or curr_input["GHOST_BACK"]
                        if pot and not curr_input["LENIENT_FWD"]:
                            error_mgr.add("抢招! (前未按)")
                            has_new_error = True

            if check_down:
                # 蓄力不足
                if curr_input["JP_UP"]:
                    val = curr_input['CHARGE_VAL_DOWN']
                    if not curr_input["IS_CHARGED_DOWN"]:
                        if not curr_input["SOCD_V"] or curr_input["SOCD_FRAMES"] < 5:
                            if val > CHARGE_INTENT_THRESHOLD:
                                error_mgr.add(f"下蓄力不足! ({val}/{req_down_frames})")
                                has_new_error = True

                # 抢招
                if active_move_data and active_move_data.get("btn") == "K":
                    if curr_input["JP_K"]:
                        pot = curr_input["IS_CHARGED_DOWN"] or curr_input["GHOST_DOWN"]
                        if pot and not curr_input["LENIENT_UP"]:
                            error_mgr.add("抢招! (上未按)")
                            has_new_error = True

        if has_new_error: sound_engine.play_err()
        error_mgr.update()

        # --- 6. 绘图阶段 (Drawing Phase) ---

        # === A. 说明与帧数参考界面 (INFO - Tab 3) ===
        if mode_type == "INFO":
            screen.fill(COLOR_BG)
            # 画顶部 Tab
            for i in range(TAB_COUNT):
                rect = (i * tab_width, 0, tab_width, TAB_H)
                col = COLOR_TAB_ACTIVE if i == current_mode_idx else COLOR_TAB_INACTIVE
                pygame.draw.rect(screen, col, rect)
                pygame.draw.rect(screen, (20, 20, 20), rect, 2)
                label = font_bold.render(MODES[i]["name"], True, (255, 255, 255))
                screen.blit(label, label.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)))
            pygame.draw.line(screen, COLOR_JUDGE_LINE, (0, TAB_H), (WIN_W, TAB_H), 2)

            # 动态缩放计算
            scale = WIN_H / REF_HEIGHT
            margin_top = int(40 * scale)
            margin_left = int(WIN_W * 0.05)
            line_gap = int(35 * scale)
            box_size = int(20 * scale)
            text_offset = int(10 * scale)

            # 左侧：图例说明
            start_y = TAB_H + margin_top
            screen.blit(font_alert.render("图例说明 (Legend)", True, (255, 255, 255)), (margin_left, start_y))
            start_y += int(45 * scale)

            legend_items = [
                (COLOR_TGT_CHARGE, "金色: 必须按住 (Charge)"),
                (COLOR_TGT_GAP, "青色: 蓄力残留 (Ghost)"),
                (COLOR_TGT_BUFFER, "蓝色: 提前缓冲 (Buffer)"),
                (COLOR_TGT_CORE, "白线: 出招时机 (Just Frame)"),
                (COLOR_USER_FAIL, "红块: 输入冲突 (SOCD)"),
                (COLOR_USER_OK, "绿色: 蓄力完成 (Ready)")
            ]

            for col, desc in legend_items:
                pygame.draw.rect(screen, col, (margin_left, start_y, int(30 * scale), box_size))
                pygame.draw.rect(screen, (200, 200, 200), (margin_left, start_y, int(30 * scale), box_size), 1)
                txt_surf = font.render(desc, True, (200, 200, 200))
                txt_y = start_y + (box_size - txt_surf.get_height()) // 2
                screen.blit(txt_surf, (margin_left + int(30 * scale) + text_offset, txt_y))
                start_y += line_gap

            # 右侧：角色帧数表
            table_x = int(WIN_W * 0.50)
            table_y = TAB_H + margin_top
            row_h = int(30 * scale)
            col_w_name = int(WIN_W * 0.20)
            col_w_val = int(WIN_W * 0.12)

            screen.blit(font_alert.render("角色蓄力帧数表", True, (255, 255, 255)), (table_x, table_y))
            table_y += int(45 * scale)

            headers = ["角色", "横向 [4]6", "纵向 [2]8"]
            total_w = col_w_name + col_w_val * 2
            pygame.draw.rect(screen, (50, 50, 50), (table_x, table_y, total_w, row_h))
            pad = int(5 * scale)
            screen.blit(font_bold.render(headers[0], True, (255, 255, 255)), (table_x + pad, table_y + pad))
            screen.blit(font_bold.render(headers[1], True, COLOR_BACK), (table_x + col_w_name + pad, table_y + pad))
            screen.blit(font_bold.render(headers[2], True, COLOR_DOWN),
                        (table_x + col_w_name + col_w_val + pad, table_y + pad))
            table_y += row_h

            for idx, profile in enumerate(CHAR_PROFILES):
                bg_col = (30, 30, 30) if idx % 2 == 0 else (40, 40, 40)
                pygame.draw.rect(screen, bg_col, (table_x, table_y, total_w, row_h))
                name_short = profile['name'].split(' ')[0]
                screen.blit(font.render(name_short, True, (200, 200, 200)), (table_x + pad, table_y + pad))
                screen.blit(font.render(f"{profile['t_46']} F", True, (255, 255, 200)),
                            (table_x + col_w_name + pad, table_y + pad))
                screen.blit(font.render(f"{profile['t_28']} F", True, (200, 255, 255)),
                            (table_x + col_w_name + col_w_val + pad, table_y + pad))
                table_y += row_h

            pygame.display.flip()
            clock.tick(30)
            continue

        # === B. 按键设置界面 (SETTINGS - Tab 4) ===
        if mode_type == "SETTINGS":
            screen.fill(COLOR_BG)
            for i in range(TAB_COUNT):
                rect = (i * tab_width, 0, tab_width, TAB_H)
                col = COLOR_TAB_ACTIVE if i == current_mode_idx else COLOR_TAB_INACTIVE
                pygame.draw.rect(screen, col, rect)
                pygame.draw.rect(screen, (20, 20, 20), rect, 2)
                label = font_bold.render(MODES[i]["name"], True, (255, 255, 255))
                screen.blit(label, label.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)))
            pygame.draw.line(screen, COLOR_JUDGE_LINE, (0, TAB_H), (WIN_W, TAB_H), 2)

            actions = [
                ("后 (Back)", "BACK", 2), ("前 (Fwd)", "FWD", 2),
                ("下 (Down)", "DOWN", 2), ("上 (Up)", "UP", 2),
                ("拳 (Punch)", "P", 3), ("脚 (Kick)", "K", 3)
            ]

            line_gap = int(45 * (WIN_H / REF_HEIGHT))
            start_y = int(TAB_H * 2)
            col1_x = 50
            col2_x = 200
            slot_w = 100
            slot_h = int(35 * (WIN_H / REF_HEIGHT))
            gap = 10

            screen.blit(font.render("点击槽位修改按键 (支持多键位绑定)", True, (200, 200, 200)), (50, start_y - 30))

            for i, (label_text, act_key, num_slots) in enumerate(actions):
                row_y = start_y + i * line_gap
                lbl = font_bold.render(label_text, True, (255, 255, 255))
                screen.blit(lbl, (col1_x, row_y + (slot_h // 2 - 8)))

                current_keys = KEY_CONFIG[act_key]
                for slot_idx in range(num_slots):
                    btn_rect = pygame.Rect(col2_x + slot_idx * (slot_w + gap), row_y, slot_w, slot_h)
                    is_hover = btn_rect.collidepoint(mx, my)

                    if binding_action == (act_key, slot_idx):
                        bg_c = COLOR_BTN_WAIT
                        txt_str = "..."
                    else:
                        bg_c = COLOR_BTN_HOVER if is_hover else COLOR_BTN_IDLE
                        if slot_idx < len(current_keys):
                            txt_str = current_keys[slot_idx]
                        else:
                            txt_str = "--"

                    pygame.draw.rect(screen, bg_c, btn_rect)
                    pygame.draw.rect(screen, (150, 150, 150), btn_rect, 1)
                    t_surf = font.render(str(txt_str), True, (255, 255, 255))
                    screen.blit(t_surf, t_surf.get_rect(center=btn_rect.center))

                    if clicked and is_hover and binding_action is None: binding_action = (act_key, slot_idx)

            pygame.display.flip()
            clock.tick(30)
            continue

        # === C. 主界面绘图 (Mode 0, 1, 2) ===
        screen.fill(COLOR_BG)

        # 画顶部 Tab
        for i in range(TAB_COUNT):
            rect = (i * tab_width, 0, tab_width, TAB_H)
            col = COLOR_TAB_ACTIVE if i == current_mode_idx else COLOR_TAB_INACTIVE
            pygame.draw.rect(screen, col, rect)
            pygame.draw.rect(screen, (20, 20, 20), rect, 2)
            label = font_bold.render(MODES[i]["name"], True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)))
        pygame.draw.line(screen, COLOR_JUDGE_LINE, (0, TAB_H), (WIN_W, TAB_H), 2)

        # 画顶部深灰色背景条 (UI Background)
        bar_h = int(40 * (WIN_H / REF_HEIGHT))
        pygame.draw.rect(screen, (30, 30, 30), (0, TAB_H, WIN_W, bar_h))

        # 1. 练习模式 UI (Mode 1 & 2)
        if active_move_data:
            # 画 1P/2P 按钮 (只在 Mode 1)
            if mode_type == "BACK_FWD":
                btn_side_w, btn_side_h = 70, 24
                btn_side_rect = pygame.Rect(WIN_W - btn_side_w - 20, TAB_H + 8, btn_side_w, btn_side_h)
                col_side = (200, 100, 50) if is_2p_side else (50, 150, 200)
                txt_side = "2P (Left)" if is_2p_side else "1P (Right)"
                pygame.draw.rect(screen, col_side, btn_side_rect)
                pygame.draw.rect(screen, (255, 255, 255), btn_side_rect, 1)
                txt_surf = font_icon.render(txt_side, True, (255, 255, 255))
                screen.blit(txt_surf, txt_surf.get_rect(center=btn_side_rect.center))

            # 画招式切换 (< >)
            center_x = WIN_W // 2
            btn_h = int(30 * (WIN_H / REF_HEIGHT))
            btn_prev_rect = pygame.Rect(center_x - 150, SELECTOR_Y, 40, btn_h)
            btn_next_rect = pygame.Rect(center_x + 110, SELECTOR_Y, 40, btn_h)
            pygame.draw.rect(screen, (60, 60, 60), btn_prev_rect)
            pygame.draw.rect(screen, (60, 60, 60), btn_next_rect)
            screen.blit(font_bold.render("<", True, (255, 255, 255)), btn_prev_rect.move(13, 5))
            screen.blit(font_bold.render(">", True, (255, 255, 255)), btn_next_rect.move(13, 5))

            info = f"{active_move_data['name']}  [ 蓄力: {active_move_data['charge']}F ]"
            txt_surf = font_bold.render(info, True, (255, 215, 0))
            screen.blit(txt_surf, txt_surf.get_rect(center=(center_x, SELECTOR_Y + (btn_h // 2))))

        # 2. 自由模式 UI (Mode 0)
        elif mode_type == "FREE":
            center_x = WIN_W // 2
            btn_h = int(30 * (WIN_H / REF_HEIGHT))
            btn_prev_rect = pygame.Rect(center_x - 180, SELECTOR_Y, 40, btn_h)
            btn_next_rect = pygame.Rect(center_x + 180, SELECTOR_Y, 40, btn_h)
            pygame.draw.rect(screen, (60, 60, 60), btn_prev_rect)
            pygame.draw.rect(screen, (60, 60, 60), btn_next_rect)
            screen.blit(font_bold.render("<", True, (255, 255, 255)), btn_prev_rect.move(13, 5))
            screen.blit(font_bold.render(">", True, (255, 255, 255)), btn_next_rect.move(13, 5))

            profile = CHAR_PROFILES[char_profile_idx]
            info = f"当前: {profile['name']}   [ 横: {profile['t_46']}F | 纵: {profile['t_28']}F ]"
            txt_surf = font_bold.render(info, True, (0, 255, 255))
            screen.blit(txt_surf, txt_surf.get_rect(center=(center_x, SELECTOR_Y + (btn_h // 2))))

        # 画轨道标签
        labels = [
            ("拳 (P)", TRACK_Y["ATK_P"]),
            ("脚 (K)", TRACK_Y["ATK_K"]),
            ("前 / 上", TRACK_Y["RELEASE"]),
            ("后 / 下", TRACK_Y["CHARGE"])
        ]
        for txt, y in labels:
            pygame.draw.rect(screen, (30, 30, 30), (0, y, WIN_W, TRACK_H))
            screen.blit(font.render(txt, True, (150, 150, 150)), (10, y + int(TRACK_H / 3)))

        # 画目标谱面 (Target Chart) - 仅在练习模式
        if active_move_data:
            retention = 10 if mode_type == "BACK_FWD" else 12
            chart = create_dynamic_chart(mode_type, active_move_data, retention)
            for note in chart:
                t_type = note["track"]
                if t_type == "CHARGE":
                    y = TRACK_Y["CHARGE"]
                elif t_type == "RELEASE":
                    y = TRACK_Y["RELEASE"]
                elif t_type == "ATK":
                    btn_type = active_move_data["btn"]
                    y = TRACK_Y["ATK_P"] if btn_type == "P" else TRACK_Y["ATK_K"]
                start_x = (note["start"] - frame_count) * SCROLL_SPEED + JUDGE_LINE_X
                while start_x + 200 < -400: start_x += 550 * SCROLL_SPEED
                if -400 < start_x < WIN_W:
                    if note["type"] == "CHARGE":
                        pre = note.get("pre_buffer", 0)
                        if pre > 0:
                            pre_w = pre * SCROLL_SPEED
                            draw_transparent_rect(screen, COLOR_TGT_PRE, (start_x - pre_w, y, pre_w, TRACK_H), 80)
                            pygame.draw.line(screen, (100, 100, 50), (start_x - pre_w, y),
                                             (start_x - pre_w, y + TRACK_H), 1)
                        w = note["dur"] * SCROLL_SPEED
                        draw_transparent_rect(screen, COLOR_TGT_CHARGE, (start_x, y, w, TRACK_H), 180)
                        gap_w = retention * SCROLL_SPEED
                        draw_transparent_rect(screen, COLOR_TGT_GAP, (start_x + w, y, gap_w, TRACK_H), 150)
                        pygame.draw.rect(screen, COLOR_TGT_GAP, (start_x + w, y, gap_w, TRACK_H), 1)
                    elif note["type"] == "TAP":
                        buf_w = (note["buffer"] * 2) * SCROLL_SPEED
                        draw_transparent_rect(screen, COLOR_TGT_BUFFER,
                                              (start_x - note["buffer"] * SCROLL_SPEED, y, buf_w, TRACK_H), 50)
                        pygame.draw.rect(screen, COLOR_TGT_CORE, (start_x, y, 3, TRACK_H))
                    if "text" in note: screen.blit(font.render(note["text"], True, (200, 200, 200)), (start_x, y + 5))

        # 画判定线
        pygame.draw.line(screen, COLOR_JUDGE_LINE, (JUDGE_LINE_X, TAB_H), (JUDGE_LINE_X, WIN_H), 2)

        # === 7. 历史记录绘图 (Timeline) - 核心部分 ===
        for rec_frame, data in user_history:
            x = (rec_frame - frame_count) * SCROLL_SPEED + JUDGE_LINE_X
            if -30 < x < WIN_W:
                if data["SOCD_H"] or data["SOCD_V"]:
                    y_list = [TRACK_Y["CHARGE"] + 15, TRACK_Y["RELEASE"] + 15]
                    for y in y_list: pygame.draw.rect(screen, COLOR_USER_FAIL, (x, y, SCROLL_SPEED, 20))
                else:
                    # 箭头方向逻辑
                    if is_2p_side:  # 2P: 物理6(右)是后, 物理4(左)是前
                        arrow_back_dir = "RIGHT"
                        arrow_fwd_dir = "LEFT"
                    else:  # 1P: 物理4(左)是后, 物理6(右)是前
                        arrow_back_dir = "LEFT"
                        arrow_fwd_dir = "RIGHT"

                    # 自由模式下，显示物理方向更直观
                    if mode_type == "FREE":
                        arrow_back_dir = "LEFT"
                        arrow_fwd_dir = "RIGHT"

                    # 后轨道
                    back_col = COLOR_USER_OK if data["IS_CHARGED_BACK"] else COLOR_BACK
                    if mode_type == "FREE":  # 自由模式特殊处理：左蓄力满变绿
                        back_col = COLOR_USER_OK if data["IS_CHARGED_LEFT"] else COLOR_BACK

                    if data["JP_BACK"]:
                        draw_arrow_shape(screen, back_col, int(x), TRACK_Y["CHARGE"], ICON_SIZE, arrow_back_dir)
                    elif data["BACK"]:
                        draw_trail_line(screen, back_col, int(x), TRACK_Y["CHARGE"], SCROLL_SPEED, TRACK_H)
                    # 残留
                    has_ghost_back = data["GHOST_BACK"] and data["IS_CHARGED_BACK"]
                    if mode_type == "FREE": has_ghost_back = data["GHOST_LEFT"] and data["IS_CHARGED_LEFT"]
                    if has_ghost_back: draw_trail_line(screen, COLOR_TGT_GAP, int(x), TRACK_Y["CHARGE"], SCROLL_SPEED,
                                                       TRACK_H)

                    # 下轨道
                    down_col = COLOR_USER_OK if data["IS_CHARGED_DOWN"] else COLOR_DOWN
                    y_offset = TRACK_Y["CHARGE"] + TRACK_H // 3
                    if data["JP_DOWN"]:
                        draw_arrow_shape(screen, down_col, int(x), y_offset, ICON_SIZE, "DOWN")
                    elif data["DOWN"]:
                        draw_trail_line(screen, down_col, int(x), y_offset, SCROLL_SPEED, TRACK_H)
                    elif data["GHOST_DOWN"] and data["IS_CHARGED_DOWN"]:
                        draw_trail_line(screen, COLOR_TGT_GAP, int(x), y_offset, SCROLL_SPEED, TRACK_H)

                    # 前轨道
                    fwd_col = COLOR_FWD
                    if mode_type == "FREE":  # 自由模式：右蓄力满变绿
                        fwd_col = COLOR_USER_OK if data["IS_CHARGED_RIGHT"] else COLOR_FWD

                    if data["JP_FWD"]:
                        draw_arrow_shape(screen, fwd_col, int(x), TRACK_Y["RELEASE"], ICON_SIZE, arrow_fwd_dir)
                    elif data["FWD"]:
                        draw_trail_line(screen, fwd_col, int(x), TRACK_Y["RELEASE"], SCROLL_SPEED, TRACK_H)
                    # 自由模式下，前轨道(物理右)也有残留
                    if mode_type == "FREE" and data["GHOST_RIGHT"] and data["IS_CHARGED_RIGHT"]:
                        draw_trail_line(screen, COLOR_TGT_GAP, int(x), TRACK_Y["RELEASE"], SCROLL_SPEED, TRACK_H)

                    # 上轨道
                    y_offset = TRACK_Y["RELEASE"] + TRACK_H // 3
                    if data["JP_UP"]:
                        draw_arrow_shape(screen, COLOR_UP, int(x), y_offset, ICON_SIZE, "UP")
                    elif data["UP"]:
                        draw_trail_line(screen, COLOR_UP, int(x), y_offset, SCROLL_SPEED, TRACK_H)

                # P/K 绘制 (简略版，保持原样)
                active_p = data["P_IDXS"]
                center_p = TRACK_Y["ATK_P"]
                for i, key_idx in enumerate(active_p):
                    col = COLOR_OD if len(active_p) > 1 else COLOR_P
                    if key_idx in data["JP_P_IDXS"] or data["JP_P"]:
                        draw_text_icon(screen, col, int(x), center_p, ICON_SIZE, "P", "CIRCLE", font_icon)
                    else:
                        draw_trail_line(screen, col, int(x), center_p, SCROLL_SPEED, TRACK_H)

                active_k = data["K_IDXS"]
                center_k = TRACK_Y["ATK_K"]
                for i, key_idx in enumerate(active_k):
                    col = COLOR_OD if len(active_k) > 1 else COLOR_K
                    if key_idx in data["JP_K_IDXS"] or data["JP_K"]:
                        draw_text_icon(screen, col, int(x), center_k, ICON_SIZE, "K", "RHOMBUS", font_icon)
                    else:
                        draw_trail_line(screen, col, int(x), center_k, SCROLL_SPEED, TRACK_H)

        # === 8. 仪表盘 (Meters) ===
        meter_x, meter_y = JUDGE_LINE_X - 50, WIN_H - int(40 * (WIN_H / REF_HEIGHT))

        # 定义 draw_meter (内部函数)
        def draw_meter(offset_x, label, val, req, ghost):
            ratio = val / req
            if val >= req:
                col = COLOR_TGT_GAP if ghost else COLOR_USER_OK
                t = "OK(保留)" if ghost else "完成"
            else:
                col = COLOR_TGT_CHARGE
                t = f"{val}"
            pygame.draw.rect(screen, (50, 50, 50), (offset_x, meter_y, 80, 10))
            pygame.draw.rect(screen, col, (offset_x, meter_y, 80 * min(ratio, 1.0), 10))
            screen.blit(font.render(f"{label}:{t}", True, col), (offset_x, meter_y - 16))

        if mode_type == "BACK_FWD":
            draw_meter(meter_x, "后", curr_input["CHARGE_VAL_BACK"], input_sys.req_back, curr_input["GHOST_BACK"])
        elif mode_type == "DOWN_UP":
            draw_meter(meter_x, "下", curr_input["CHARGE_VAL_DOWN"], input_sys.req_down, curr_input["GHOST_DOWN"])
        elif mode_type == "FREE":
            draw_meter(meter_x - 90, "左(4)", curr_input["CHARGE_VAL_LEFT"], input_sys.req_back,
                       curr_input["GHOST_LEFT"])
            draw_meter(meter_x, "下(2)", curr_input["CHARGE_VAL_DOWN"], input_sys.req_down, curr_input["GHOST_DOWN"])
            draw_meter(meter_x + 90, "右(6)", curr_input["CHARGE_VAL_RIGHT"], input_sys.req_back,
                       curr_input["GHOST_RIGHT"])

        error_mgr.draw(screen, font_alert, WIN_W, WIN_H)

        frame_count += 1
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
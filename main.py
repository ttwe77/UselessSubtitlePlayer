import os
import sys
import time
import random
import threading
import queue
import tkinter as tk
import ctypes
import pygame
import pysrt
import configparser

# -------------------------- 配置文件处理 --------------------------
def load_config():
    """加载配置文件，若不存在则生成默认配置"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    
    # 定义默认配置
    default_config = {
        "Audio": {
            "flac_path": "",          # 手动指定FLAC路径（空则自动查找）
            "loop_play": "True",      # 是否无限循环播放
            "volume": "1.0",          # 音量（0.0-1.0）
            "audio_init_delay": "0.5" # 音频初始化等待时间（秒）
        },
        "Subtitle": {
            "srt_path": "",           # 手动指定SRT路径（空则自动查找）
            "encoding": "utf-8",      # 字幕文件编码
            "check_interval": "0.05", # 字幕时间检查间隔（秒）
            "post_loop_delay": "1.0", # 字幕轮播后等待时间（秒）
            "audio_pos_check_interval": "0.1" # 音频未启动时的检查间隔（秒）
        },
        "Window": {
            "font_name": "Microsoft YaHei UI", # 弹窗字体
            "font_size": "10",                 # 字体大小
            "padx": "30",                      # 文本内边距X
            "pady": "20",                      # 文本内边距Y
            "btn_pady": "0,15",                # 按钮内边距Y（上下）
            "wraplength": "450",               # 文本换行长度
            "topmost": "True",                 # 弹窗是否置顶
            "btn_width": "10",                 # 按钮宽度
            "btn_text": "确定"                 # 按钮文本
        },
        "System": {
            "dpi_awareness": "True",           # 是否启用DPI感知
            "queue_check_interval": "100"      # 队列检查间隔（毫秒）
        },
        "Paths": {
            "work_dir": ""                     # 工作目录（空则为脚本所在目录）
        }
    }

    # 若配置文件不存在，生成默认配置
    if not os.path.exists(config_path):
        config.read_dict(default_config)
        with open(config_path, "w", encoding="utf-8") as f:
            config.write(f)
        print(f"已生成默认配置文件：{config_path}")
    else:
        config.read(config_path, encoding="utf-8")
        # 补充缺失的配置项
        for section, options in default_config.items():
            if section not in config:
                config[section] = options
            else:
                for opt, val in options.items():
                    if opt not in config[section]:
                        config[section][opt] = val
        # 保存补充后的配置
        with open(config_path, "w", encoding="utf-8") as f:
            config.write(f)

    return config, config_path

def get_config_value(config, section, option, val_type=str):
    """安全获取配置值，自动类型转换"""
    try:
        if val_type == bool:
            return config.getboolean(section, option)
        elif val_type == int:
            return config.getint(section, option)
        elif val_type == float:
            return config.getfloat(section, option)
        elif val_type == tuple:
            # 处理逗号分隔的元组（如btn_pady）
            return tuple(map(int, config.get(section, option).split(",")))
        else:
            return config.get(section, option).strip()
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        # 类型转换失败时返回默认值
        default_vals = {
            "Audio": {"loop_play": True, "volume": 1.0, "audio_init_delay": 0.5},
            "Subtitle": {"check_interval": 0.05, "post_loop_delay": 1.0, "audio_pos_check_interval": 0.1},
            "Window": {"font_size": 10, "padx": 30, "pady": 20, "btn_pady": (0,15), "wraplength": 450, "topmost": True, "btn_width": 10, "btn_text": "确定"},
            "System": {"dpi_awareness": True, "queue_check_interval": 100},
        }
        return default_vals.get(section, {}).get(option, "")

# -------------------------- 原有功能函数改造 --------------------------
def find_files(config):
    """自动查找或从配置读取 .flac 和 .srt 文件"""
    work_dir = get_config_value(config, "Paths", "work_dir")
    if not work_dir:
        work_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 优先读取配置中的路径
    flac_path = get_config_value(config, "Audio", "flac_path")
    srt_path = get_config_value(config, "Subtitle", "srt_path")

    # 配置未指定则自动查找
    if not flac_path:
        flac_files = [f for f in os.listdir(work_dir) if f.lower().endswith('.flac')]
        if not flac_files:
            raise FileNotFoundError("在工作目录下未找到 .flac 音频文件（可在config.ini手动指定路径）")
        flac_path = os.path.join(work_dir, flac_files[0])
    else:
        if not os.path.exists(flac_path):
            raise FileNotFoundError(f"配置中指定的FLAC文件不存在：{flac_path}")

    if not srt_path:
        srt_files = [f for f in os.listdir(work_dir) if f.lower().endswith('.srt')]
        if not srt_files:
            raise FileNotFoundError("在工作目录下未找到 .srt 字幕文件（可在config.ini手动指定路径）")
        srt_path = os.path.join(work_dir, srt_files[0])
    else:
        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"配置中指定的SRT文件不存在：{srt_path}")

    return flac_path, srt_path

def set_dpi_awareness(config):
    """根据配置让程序感知 Windows DPI 缩放"""
    if not get_config_value(config, "System", "dpi_awareness", bool):
        return
    try:
        # Windows 10 1607+
        ctypes.windll.shcore.SetProcessDpiAwarenessContext(ctypes.c_int(-2))
    except:
        try:
            # Windows 8.1+
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            # Windows Vista+
            ctypes.windll.user32.SetProcessDPIAware()

def get_screen_workarea():
    """获取主屏幕工作区坐标（排除任务栏）"""
    SPI_GETWORKAREA = 48
    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                    ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
    
    rect = RECT()
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect.left, rect.top, rect.right, rect.bottom

def create_subtitle_popup(text, screen_left, screen_top, screen_right, screen_bottom, root, config):
    """根据配置创建字幕弹窗"""
    popup = tk.Toplevel(root)
    popup.title("字幕")
    popup.resizable(False, False)
    
    # 弹窗置顶配置
    if get_config_value(config, "Window", "topmost", bool):
        popup.wm_attributes("-topmost", 1)
    
    # 读取窗口样式配置
    font_name = get_config_value(config, "Window", "font_name")
    font_size = get_config_value(config, "Window", "font_size", int)
    padx = get_config_value(config, "Window", "padx", int)
    pady = get_config_value(config, "Window", "pady", int)
    wraplength = get_config_value(config, "Window", "wraplength", int)
    btn_text = get_config_value(config, "Window", "btn_text")
    btn_width = get_config_value(config, "Window", "btn_width", int)
    btn_pady = get_config_value(config, "Window", "btn_pady", tuple)
    
    # UI 布局
    label = tk.Label(
        popup, 
        text=text, 
        padx=padx, 
        pady=pady, 
        wraplength=wraplength, 
        font=(font_name, font_size)
    )
    label.pack()
    
    btn = tk.Button(
        popup, 
        text=btn_text, 
        command=popup.destroy, 
        width=btn_width
    )
    btn.pack(pady=btn_pady)
    
    # 计算窗口大小以确保不超出屏幕
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    
    # 计算随机坐标
    max_x = screen_right - width
    max_y = screen_bottom - height
    x = random.randint(screen_left, max_x) if max_x > screen_left else screen_left
    y = random.randint(screen_top, max_y) if max_y > screen_top else screen_top
    
    popup.geometry(f"+{x}+{y}")

def play_audio(flac_path, config):
    """线程：根据配置播放 FLAC 音频"""
    pygame.mixer.init()
    pygame.mixer.music.load(flac_path)
    # 设置音量
    volume = get_config_value(config, "Audio", "volume", float)
    pygame.mixer.music.set_volume(volume)
    # 设置循环播放
    loop = -1 if get_config_value(config, "Audio", "loop_play", bool) else 0
    pygame.mixer.music.play(loop)

def process_subtitles(srt_path, screen_rect, subtitle_queue, config):
    """线程：根据配置处理字幕时间轴"""
    screen_left, screen_top, screen_right, screen_bottom = screen_rect
    encoding = get_config_value(config, "Subtitle", "encoding")
    check_interval = get_config_value(config, "Subtitle", "check_interval", float)
    post_loop_delay = get_config_value(config, "Subtitle", "post_loop_delay", float)
    audio_pos_check_interval = get_config_value(config, "Subtitle", "audio_pos_check_interval", float)
    
    subs = pysrt.open(srt_path, encoding=encoding)
    last_sub_index = len(subs) - 1  # 获取最后一个字幕的索引
    
    while True:
        # 等待音频开始
        while pygame.mixer.music.get_pos() == -1:
            time.sleep(audio_pos_check_interval)
            
        for idx, sub in enumerate(subs):
            start_ms = sub.start.ordinal
            
            # 等待直到字幕时间点
            while True:
                current_pos = pygame.mixer.music.get_pos()
                if current_pos == -1: break # 音频重置
                
                if current_pos >= start_ms:
                    # 将数据发送给主线程
                    subtitle_queue.put((sub.text, screen_left, screen_top, screen_right, screen_bottom))
                    
                    # 如果到达最后一个字幕，显示完成后退出整个函数
                    if idx == last_sub_index:
                        return  # 完全退出函数
                    break
                
                time.sleep(check_interval)
            
            if pygame.mixer.music.get_pos() == -1: 
                break
        
        time.sleep(post_loop_delay)

def main():
    # 加载配置
    config, config_path = load_config()
    
    try:
        flac_path, srt_path = find_files(config)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        input("按回车键退出...")
        return

    set_dpi_awareness(config)
    screen_rect = get_screen_workarea()
    
    # 线程通信队列
    q = queue.Queue()

    # 启动后台线程
    audio_thread = threading.Thread(target=play_audio, args=(flac_path, config), daemon=True)
    audio_thread.start()
    
    # 音频初始化等待（从配置读取）
    audio_init_delay = get_config_value(config, "Audio", "audio_init_delay", float)
    time.sleep(audio_init_delay)
    
    subtitle_thread = threading.Thread(target=process_subtitles, args=(srt_path, screen_rect, q, config), daemon=True)
    subtitle_thread.start()

    # 初始化 Tkinter 主线程
    root = tk.Tk()
    root.withdraw() # 隐藏主窗口

    # 定时检查队列（从配置读取间隔）
    queue_check_interval = get_config_value(config, "System", "queue_check_interval", int)
    def check_queue():
        try:
            while True: # 处理队列中所有积累的消息
                data = q.get_nowait()
                create_subtitle_popup(*data, root, config)
        except queue.Empty:
            pass
        root.after(queue_check_interval, check_queue)

    check_queue()
    root.mainloop()

if __name__ == "__main__":
    main()
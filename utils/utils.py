import ctypes
import sys
import time
import cv2 as cv
import numpy as np
import pyautogui
import pythoncom
import win32api
import win32com.client
import win32con
import win32gui
import win32print
from PIL import ImageGrab
from utils.log import log
from utils import ocr

My_TS = ocr.My_TS()


def click_target(target_path, threshold, flag=True, mode="False", roi=(0, 0, 1920, 1080)):
    target = cv.imread(target_path)
    if mode == "gray":
        pass
        target = cv.cvtColor(target, cv.COLOR_BGR2GRAY)
    while True:
        result = scan_screenshot(target, mode, roi)
        if result["max_val"] > threshold:
            # print(result["max_val"])
            points = calculated(result, target.shape, mode)
            # print(points)
            # move_and_click(points[0], points[1])
            # get_point(*points)
            # exit()
            # log.info("target shape: %s" % target.shape)
            # self.click(points)
            return True, points
        if flag == False:
            return False, [None, None]


# 由click_target调用，返回图片匹配结果
def scan_screenshot(prepared, mode="RBG", roi=(0, 0, 1920, 1080)):
    temp = pyautogui.screenshot(region=roi)
    screenshot = np.array(temp)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
    if mode == "gray":
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
    result = cv.matchTemplate(screenshot, prepared, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    return {
        "screenshot": screenshot,
        "min_val": min_val,
        "max_val": max_val,
        "min_loc": min_loc,
        "max_loc": max_loc,
    }


# 获取游戏窗口句柄
def find_window(title):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd:
        return hwnd
    else:
        return None


# 获取当前活动窗口句柄
def get_active_window():
    return win32gui.GetForegroundWindow()


# 获取屏幕截图并指定坐标位置
def get_pixel_color(x, y):
    screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
    pixel_color = screenshot.getpixel((0, 0))
    return pixel_color


def calculated(result, shape, mode):
    mat_top, mat_left = result["max_loc"]
    if mode == "gray":
        prepared_height, prepared_width = shape
    else:
        prepared_height, prepared_width, prepared_channels = shape
    x = int((mat_top + mat_top + prepared_width) / 2)
    y = int((mat_left + mat_left + prepared_height) / 2)
    return x, y


# 将游戏窗口设为前台
def set_foreground():
    game_title = "崩坏：星穹铁道"  # 替换为你的游戏窗口标题
    game_handle = win32gui.FindWindow(None, game_title)  # 查找游戏窗口句柄
    try:
        win32gui.ShowWindow(game_handle, win32con.SW_RESTORE)  # 恢复窗口到正常显示状态
        win32gui.SetForegroundWindow(game_handle)  # 将窗口切换到前台
    except:
        log.info("游戏窗口未找到,请打开游戏")
        pass


def move_and_click(x, y):
    pyautogui.moveTo(x, y)
    time.sleep(0.1)  # 等待鼠标移动
    pyautogui.click(button='left')


def c_center(x, y, p0):  # 两个目标点坐标，和初始坐标
    center_x = x + p0[0]
    center_y = y + p0[1]
    print(center_x, center_y)
    # 执行点击操作
    move_and_click(center_x, center_y)
    return True


def click_center(p1, p2, p0):  # 两个目标点坐标，和初始坐标
    center_x = int((p1[0] + p2[0]) / 2) + p0[0]
    center_y = int((p1[1] + p2[1]) / 2) + p0[1]
    print(center_x, center_y)
    # 执行点击操作
    move_and_click(center_x, center_y)
    return True


def text_ocr(text, p0=None, _stop=False, _time=2):
    if p0 is None:
        p0 = [0, 0]
    while not _stop:
        screenshot = ImageGrab.grab()
        screenshot = np.array(screenshot)
        pt = My_TS.find_text(img=screenshot, text=[text])
        if pt is not None:
            p_again = click_center(pt[0], pt[2], p0)
            break
        time.sleep(_time)


# 从全屏截屏中裁剪得到游戏窗口截屏
class UniverseUtils:
    def __init__(self):
        set_foreground()
        self.my_nd = win32gui.GetForegroundWindow()
        self.check_bonus = 1
        self._stop = 0
        self.stop_move = 0
        self.opt = 0
        self.fail_count = 0
        self.ts = ocr.My_TS()
        self.debug, self.find = 0, 1
        self.bx, self.by = 1920, 1080
        log.warning("等待游戏窗口")
        self.tss = 'ey.jpg'
        self.ts = ocr.My_TS()

        while True:
            try:
                hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
                Text = win32gui.GetWindowText(hwnd)
                self.x0, self.y0, self.x1, self.y1 = win32gui.GetClientRect(hwnd)
                self.xx = self.x1 - self.x0
                self.yy = self.y1 - self.y0
                self.x0, self.y0, self.x1, self.y1 = win32gui.GetWindowRect(hwnd)
                self.full = self.x0 == 0 and self.y0 == 0
                self.x0 = max(0, self.x1 - self.xx) + 9 * self.full
                self.y0 = max(0, self.y1 - self.yy) + 9 * self.full
                if (self.xx == 1920 or self.yy == 1080) and self.xx >= 1920 and self.yy >= 1080:
                    self.x0 += (self.xx - 1920) // 2
                    self.y0 += (self.yy - 1080) // 2
                    self.x1 -= (self.xx - 1920) // 2
                    self.y1 -= (self.yy - 1080) // 2
                    self.xx, self.yy = 1920, 1080
                self.scx = self.xx / self.bx
                self.scy = self.yy / self.by
                dc = win32gui.GetWindowDC(hwnd)
                dpi_x = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSX)
                dpi_y = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSY)
                win32gui.ReleaseDC(hwnd, dc)
                scale_x = dpi_x / 96
                scale_y = dpi_y / 96
                self.scale = ctypes.windll.user32.GetDpiForWindow(hwnd) / 96.0
                # log.info("DPI: " + str(self.scale) + " A:" + str(int(self.multi * 100) / 100))
                # 计算出真实分辨率
                self.real_width = int(self.xx * scale_x)
                # x01y01:窗口左上右下坐标
                # xx yy:窗口大小
                # scx scy:当前窗口和基准窗口（1920*1080）缩放大小比例
                if Text == "崩坏：星穹铁道":
                    time.sleep(1)
                    if self.xx != 1920 or self.yy != 1080:
                        log.error("分辨率错误")
                    break
                else:
                    time.sleep(0.3)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                time.sleep(0.3)

    def get_screen(self):
        i = 0
        while True:
            try:
                screen_raw = pyautogui.screenshot(region=[self.x0, self.y0, self.xx, self.yy])
                screen_raw = np.array(screen_raw)
            except:
                log.info("截图失败!")
                time.sleep(0.1)
                continue
            if screen_raw.shape[0] > 3:
                break
            else:
                i = min(i + 1, 20)
                log.info("截图失败")
                time.sleep(0.2 * i)
        self.screen = cv.cvtColor(screen_raw, cv.COLOR_BGR2RGB)
        # cv.imwrite("imgs/screen.jpg", self.screen)
        return self.screen

    def click_text(self, text):
        img = self.get_screen()
        pt = self.ts.find_text(img, text)
        if pt is not None:
            self.click((1 - (pt[0][0] + pt[1][0]) / 2 / self.xx, 1 - (pt[0][1] + pt[2][1]) / 2 / self.yy))

    # 点击一个点
    def click(self, points):
        x, y = points
        # 如果是浮点数表示，则计算实际坐标
        if type(x) != type(0):
            x, y = self.x1 - int(x * self.xx), self.y1 - int(y * self.yy)
        # 全屏模式会有一个偏移
        if self.full:
            x += 9
            y += 9
        if self._stop == 0:
            win32api.SetCursorPos((x, y))
            pyautogui.click()
        time.sleep(0.3)

    # 点击与模板匹配的点，flag=True表示必须匹配，不匹配就会一直寻找直到出现匹配
    def click_target(self, target_path, threshold, flag=True):
        target = cv.imread(target_path)
        while True:
            result = self.scan_screenshot(target)
            if result["max_val"] > threshold:
                print(result["max_val"])
                points = self.calculated(result, target.shape)
                self.get_point(*points)
                exit()
                # log.info("target shape: %s" % target.shape)
                # self.click(points)
                return
            if flag == False:
                return

    # 由click_target调用，返回图片匹配结果
    def scan_screenshot(self, prepared):
        temp = pyautogui.screenshot()
        screenshot = np.array(temp)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        result = cv.matchTemplate(screenshot, prepared, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        return {
            "screenshot": screenshot,
            "min_val": min_val,
            "max_val": max_val,
            "min_loc": min_loc,
            "max_loc": max_loc,
        }

    # 计算匹配中心点坐标
    def calculated(self, result, shape):
        mat_top, mat_left = result["max_loc"]
        prepared_height, prepared_width, prepared_channels = shape
        x = int((mat_top + mat_top + prepared_width) / 2)
        y = int((mat_left + mat_left + prepared_height) / 2)
        return x, y

    def get_point(self, x, y):
        # 得到一个点的浮点表示
        x = self.x1 - x
        y = self.y1 - y
        print("获取到点：{:.4f},{:.4f}".format(x / self.xx, y / self.yy))

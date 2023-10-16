import atexit
import time
import cv2 as cv
import numpy as np
import pyautogui
import pyuac
import win32gui
from PIL import ImageGrab
from ppocronnx.predict_system import TextSystem
from main import click_target


class My_TS:
    def __init__(self, lang='ch'):
        self.lang = lang
        self.ts = TextSystem(use_angle_cls=False)
        self.ts.text_recognizer.postprocess_op.character.append(' ')
        self.text = ''

    def sim(self, text, img=None):
        # 比对两个文本是否相似，如果提供了img参数，它会将图片转换为文本并与传入的text比对。比对结果通过字符匹配的方式进行。
        if img is not None:
            self.input(img)
        if len(self.text) < len(text):
            return False
        text += '  '
        f = [[0, 0] for _ in range(len(self.text) + 1)]
        f[0][1] = 1
        for i in range(len(self.text)):
            try:
                if self.text[i] == text[f[i][0]]:
                    f[i + 1][0] = f[i][0] + 1
                if self.text[i] == text[f[i][1]]:
                    f[i + 1][1] = f[i][1] + 1
            except:
                print(text, self.text)
                # log.info('error_sim|' + text + '|' + self.text + '|')
            f[i + 1][0] = max(f[i][0], f[i + 1][0])
            f[i + 1][1] = max(f[i][1], f[i + 1][1], f[i][0] + 1)
        return f[-1][1] >= len(text) - 2

    def input(self, img):
        # 将给定的图像 img 进行OCR识别，然后将识别出的文本转换为小写字母，保存在self.text中
        try:
            self.text = self.ts.ocr_single_line(img)[0].lower()
        except:
            self.text = ''

    def sim_list(self, text_list, img=None):
        # 图像中找到了与text_list中的任何文本匹配的文本，则返回第一个匹配的文本。
        if img is not None:
            self.input(img)
        for t in text_list:
            if self.sim(t):
                return t
        return None

    def split_and_find(self, key_list, img, mode=None):
        white = [255, 255, 255]
        yellow = [126, 162, 180]
        binary_image = np.zeros_like(img[:, :, 0])
        enhance_image = np.zeros_like(img)
        if mode == 'strange':
            binary_image[np.sum((img - yellow) ** 2, axis=-1) <= 512] = 255
            enhance_image[np.sum((img - yellow) ** 2, axis=-1) <= 3200] = [255, 255, 255]
        else:
            binary_image[np.sum((img - white) ** 2, axis=-1) <= 1600] = 255
            enhance_image[np.sum((img - white) ** 2, axis=-1) <= 3200] = [255, 255, 255]
        if mode == 'bless':
            kerneld = np.zeros((7, 3), np.uint8) + 1
            kernele = np.zeros((1, 39), np.uint8) + 1
            kernele2 = np.zeros((7, 1), np.uint8) + 1
            binary_image = cv.dilate(binary_image, kerneld, iterations=2)
            binary_image = cv.erode(binary_image, kernele, iterations=5)
            binary_image = cv.erode(binary_image, kernele2, iterations=2)
            enhance_image = img
        else:
            kernel = np.zeros((5, 9), np.uint8) + 1
            for i in range(2):
                binary_image = cv.dilate(binary_image, kernel, iterations=3)
                binary_image = cv.erode(binary_image, kernel, iterations=2)
        contours, _ = cv.findContours(binary_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        prior = len(key_list)
        rcx, rcy, find = -1, -1, 0
        res = ''
        text_res = ''
        ff = 0
        for c, contour in enumerate(contours):
            x, y, w, h = cv.boundingRect(contour)
            if h == binary_image.shape[0] or w < 55:
                continue
            roi = enhance_image[y:y + h, x:x + w]
            cx = x + w // 2
            cy = y + h // 2
            self.input(roi)
            res += '|' + self.text
            if self.sim('回归不等式') and len(contours) > 1:
                ff = 1
                continue
            # cv.imwrite('tmp'+str(c)+'.jpg',roi)
            for i, text in enumerate(key_list):
                if (self.sim(text) and prior > i) or rcx == -1:
                    rcx, rcy, find = cx, cy, 1 + (self.sim(text) and prior > i)
                    text_res = text
                    if find == 2:
                        prior = i
        if ff and find == 1:
            find = 3
        # print('识别结果：', res + '|', ' 识别到：', text_res)
        return (rcx - img.shape[1] // 2, rcy - img.shape[0] // 2), find

    def find_text(self, img, text):
        for res in self.ts.detect_and_ocr(img):
            self.text = res.ocr_text
            print(res)
            for txt in text:
                if self.sim(txt):
                    print("识别到", txt)
                    return res.box


def click_center(p1, p2, p0):  # 两个目标点坐标，和初始坐标
    center_x = int((p1[0] + p2[0]) / 2) + p0[0]
    center_y = int((p1[1] + p2[1]) / 2) + p0[1]
    print(center_x, center_y)
    # 执行点击操作
    move_and_click(center_x, center_y)
    return True


def move_and_click(x, y):
    pyautogui.moveTo(x, y)
    time.sleep(0.05)  # 等待鼠标移动
    pyautogui.click(button='left')


def get_roi(p0, p1):
    x, y, width, height = p0[0], p0[1], p1[0] - p0[0], p1[1] - p0[1]
    return x, y, width, height


def enum_windows_callback(hwnd, hwnds):
    class_name = win32gui.GetClassName(hwnd)
    name = win32gui.GetWindowText(hwnd)
    try:
        if (
                class_name == "ConsoleWindowClass"
                and win32gui.IsWindowVisible(hwnd)
                and "gui" in name[-7:]
        ):
            hwnds.append(hwnd)
    except:
        pass
    return True


def list_handles():
    hwnds = []
    win32gui.EnumWindows(enum_windows_callback, hwnds)
    hwnds.append(0)
    return hwnds


mynd = list_handles()[0]


def cleanup():
    try:
        win32gui.ShowWindow(mynd, 1)
    except:
        pass


def on_key_press(event):
    global stop_flag
    if event.name == '`':  # 按下 "`" 键
        stop_flag = True


# def again():
#     # 创建 My_TS 实例
#     my_ts = My_TS()
#     # 截取屏幕区域（这里假设您知道对象在屏幕的位置，您可以根据需要进行调整） 1195 927 1319 971
#     p0 = [640, 233]
#     p1 = [1320, 1005]
#     p2 = [667, 414]
#     p3 = [1652, 765]
#     # x, y, width, height = get_roi(p0, p1)
#     # x, y, width, height = 1195, 927, 125, 45
#     # x1, y1, x2, y2 = p2[0], p2[1], p3[0] - p2[0], p3[1] - p2[1]
#     # screenshot_s = pyautogui.screenshot(region=(x, y, width, height))
#     # 使用 My_TS 进行文字识别
#     try_again = None
#     for i in range(999):
#         screenshot_s = ImageGrab.grab(bbox=(640, 233, 1320, 1005))
#         # screenshot_s.save("../screenshot.png")
#         screenshot_s = np.array(screenshot_s)
#         print(i)
#         # my_ts.sim("再来", screenshot_s)
#         try_again = my_ts.find_text(screenshot_s, ["再来"])  # 用目标文本替换"目标文本" 1250,950
#         # exit_ = my_ts.find_text(screenshot_s, ["退出关卡"])  # 用目标文本替换"目标文本" 700,950
#         if try_again is not None:
#             break
#         time.sleep(1)
#     # 如果找到了目标文本
#     points = try_again
#     print("点击再试一次", points)
#     # 计算对象的中心点坐标
#     # click_center(points[0], points[2], p0)
#     move_and_click(1250, 950)
#     time.sleep(0.5)
#     screenshot2 = ImageGrab.grab(bbox=(667, 414, 1652, 765))
#     # screenshot2.save("../screenshot2.png")
#     screenshot2 = np.array(screenshot2)
#     cancel = my_ts.find_text(screenshot2, ["取消"])  # 体力不足
#     if cancel is not None:
#         print("点击退出")
#         move_and_click(700, 950)
#         move_and_click(700, 950)
#         t, p = click_target("../img/talk.png", 0.9)
#         if t:
#             print("任务完成")
#
#     else:
#         again()


if __name__ == '__main__':
    atexit.register(cleanup)
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
        # 不稳定已弃用
    # again()

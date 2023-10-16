import threading
import pyautogui
import pyuac
import win32gui
import keyboard
import time
import sys
from utils.utils import set_foreground, get_pixel_color, move_and_click, find_window, click_target, get_active_window, \
    c_center


class FindBaoxiangThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(FindBaoxiangThread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        self.__data = []  # 示例实例变量

    def run(self):
        while self.__running.is_set():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到self.__flag为True后返回
            try:
                # 在这里实现查找宝箱的逻辑
                # 使用 click_target 函数查找并点击宝箱图片
                find, p = click_target("./img/baoxiang.png", 0.9, True)
                if find:
                    print("开宝箱")
                    keyboard.press_and_release('f')
                find_n, p1 = click_target("./img/naqu.png", 0.9, True)
                if find_n:
                    print("拿取")
                    keyboard.press_and_release("f")
                find_t, p_t = click_target("./img/tioaguo.png", 0.9, True)
                if find_t:
                    print("跳过")
                    move_and_click(p_t[0], p_t[1])
            except Exception as e:
                # 添加异常处理
                print("FindBaoxiangThread Exception occurred: ", e)
                self.__running.clear()

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False
        print("窗口检测停止.")


# 底部框 0.2s
class BottomDialogueThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(BottomDialogueThread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        self.__data = []  # 示例实例变量
        self.target_x = 960  # 底部对话框的目标坐标
        self.target_y = 1010

    def run(self):
        while self.__running.is_set():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到self.__flag为True后返回
            try:
                hide, p = click_target("img/hide.png", 0.9, flag=False)
                if hide:
                    keyboard.press_and_release('space')
                # 检测底部对话框颜色
                color = get_pixel_color(self.target_x, self.target_y)
                if color == (222, 206, 157):
                    print("发现底部对话框")
                    move_and_click(1322, 805)
                time.sleep(0.1)  # 适当的休眠时间，避免过于频繁检测
            except Exception as e:
                # 添加异常处理
                print("BottomDialogueThread Exception occurred: ", e)
                self.__running.clear()

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False
        print("窗口检测停止.")


class dialogue(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(dialogue, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        self.__data = []  # 示例实例变量

    def run(self):
        while self.__running.is_set():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到self.__flag为True后返回
            # try:
            # 修改线程的执行逻辑
            pause = False
            while True:
                t1 = time.time()
                # 获取指定坐标位置的颜色信息
                # 根据优先级依次点击目标,优先度 task>xuanze>end>talk
                # 现在采用多处排队减少资源消耗 （可以使用多线程，每一处判断都用线程处减少时间）
                history, p = click_target("img/history.png", 0.8, flag=False, mode="gray", roi=(25, 38, 45, 40))
                if history:
                    p0 = (1294, 227)
                    # 任务 已测
                    find, p = click_target('img/task.png', 0.8, flag=False, mode="gray", roi=(1294, 227, 70, 570))

                    # 箭头对话框
                    d, p1 = click_target('img/xuanze.png', 0.8, flag=False, mode="gray", roi=(1294, 227, 70, 570))
                    dialogue_x, dialogue_y = p1

                    # # 退出框
                    end, p2 = click_target('img/end.png', 0.8, flag=False, mode="gray", roi=(1294, 227, 70, 570))
                    end_x, end_y = p2

                    # # 谈话框
                    t, p3 = click_target('img/talk.png', 0.8, flag=False, mode="gray", roi=(1294, 227, 70, 570))
                    talk_x, talk_y = p3

                    if find and p is not None:
                        print("发现任务框")
                        if p is not None:
                            x, y = p
                            c_center(x, y, p0)

                    elif d and p1 is not None:
                        print("发现箭头对话框")
                        # 模拟点击对话框1，可以根据实际情况模拟按键或鼠标点击
                        x, y = dialogue_x, dialogue_y
                        c_center(x, y, p0)

                    elif end and p2 is not None:
                        print("发现结束框")
                        # 模拟点击结束框
                        x, y = end_x, end_y
                        c_center(x, y, p0)

                    elif t and p3 is not None:
                        print("发现谈话框")
                        # 模拟点击谈话框1
                        x, y = talk_x, talk_y
                        c_center(x, y, p0)
                    else:
                        continue

                    # 监听按键事件，如果按下了"]"键，退出循环
                    if keyboard.is_pressed(']') and not pause:
                        pause = True
                        self.__flag.clear()  # 设置为False, 让线程阻塞

                    elif keyboard.is_pressed(']') and pause:
                        pause = False
                        self.__flag.set()  # 设置为True, 让线程停止阻塞

                    time.sleep(0.05)  # 可以调整获取颜色信息的频率
                    t2 = time.time()
                    print(t2 - t1)

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞
        print("窗口检测暂停.")

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞
        print("窗口检测恢复.")

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False
        print("窗口检测停止.")


# 初始化全局变量
_stop = False


def on_key_press(event):
    global _stop
    if event.name == '`':  # 按下 "`" 键
        _stop = not _stop


def auto_dialogue():
    if not pyuac.isUserAdmin():
        sys.exit()
    # 你的游戏窗口标题
    set_foreground()
    game_title = "崩坏：星穹铁道"
    game_handle = find_window(game_title)  # 331754
    is_in = "waiting"
    if not game_handle:
        print(f"Game window with title: {game_title} not found.")
        sys.exit()
    else:
        dialogueThread = dialogue()  # 预加载
        dialogueThread.start()
        bottom_dialogue_thread = BottomDialogueThread()
        bottom_dialogue_thread.start()
        find_baoxiang_thread = FindBaoxiangThread()
        find_baoxiang_thread.start()
        # 启动键盘监听线程
        keyboard.on_press(on_key_press)
        while True:
            # 获取当前活动窗口句柄
            current_handle = get_active_window()
            Text = win32gui.GetWindowText(current_handle)

            # 判断当前活动窗口是否为目标窗口
            if Text == "崩坏：星穹铁道" and not _stop:
                if not pyautogui.FAILSAFE:
                    # 恢复功能
                    pyautogui.FAILSAFE = True
                    dialogueThread.resume()
                    bottom_dialogue_thread.resume()
                    find_baoxiang_thread.resume()
                if is_in != "target":
                    print("当前位于目标窗口")
                    is_in = "target"
            else:
                # 如果不是目标窗口，停用pyautogui功能，以及停用线程
                if is_in != "waiting":
                    dialogueThread.pause()
                    bottom_dialogue_thread.pause()
                    find_baoxiang_thread.pause()
                    pyautogui.FAILSAFE = False
                    print("等待目标窗口")
                    is_in = "waiting"
                time.sleep(0.5)


if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        pass
    if not pyuac.isUserAdmin():
        exit()
    auto_dialogue()

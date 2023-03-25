import random
import time
import os
import json
import pyautogui as pyautogui
import serial
from . import BezierTrajectory


class DataComm:
    """
    属性：
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
    """

    def __init__(self, screen_width=3840, screen_height=2160):
        self.hex_dict = {"ST": b'\x02',
                         "NU": b"\x00",
                         "LE": b"\x01",
                         "RI": b"\x02",
                         "CE": b"\x04"
                         }
        self.number_list = 0
        self.le = 0
        self.deviation = 0
        self.bias = 0
        self.type = 0
        self.X_MAX = screen_width
        self.Y_MAX = screen_height

    """
    发送数据到串口，将鼠标光标移动到屏幕上的绝对位置。
    
    参数：
        x (int)：鼠标光标的x坐标。
        y (int)：鼠标光标的y坐标。
        ctrl (str)：按下的控制键（可选）。
        port (serial)：要写入数据的串口（可选）。
    
    返回：
        如果成功发送数据，则返回True，否则返回False。
    """

    def send_data_absolute(self, x: int, y: int, ctrl: str = '', port: serial = serial) -> bool:
        # 将字符转写为数据包
        HEAD = b'\x57\xAB'  # 帧头
        ADDR = b'\x00'  # 地址
        CMD = b'\x04'  # 命令
        LEN = b'\x07'  # 数据长度
        DATA = bytearray(b'\x02')  # 数据

        # 鼠标按键
        if ctrl == '':
            DATA.append(0)
        elif isinstance(ctrl, int):
            DATA.append(ctrl)
        else:
            DATA += self.hex_dict[ctrl]

        # 坐标
        X_Cur = (4096 * x) // self.X_MAX
        Y_Cur = (4096 * y) // self.Y_MAX
        DATA += X_Cur.to_bytes(2, byteorder='little')
        DATA += Y_Cur.to_bytes(2, byteorder='little')

        if len(DATA) < 7:
            DATA += b'\x00' * (7 - len(DATA))
        else:
            DATA = DATA[:7]

        # 分离HEAD中的值，并计算和
        HEAD_hex_list = list(HEAD)
        HEAD_add_hex_list = sum(HEAD_hex_list)

        # 分离DATA中的值，并计算和
        DATA_hex_list = list(DATA)
        DATA_add_hex_list = sum(DATA_hex_list)

        try:
            SUM = sum([HEAD_add_hex_list, int.from_bytes(ADDR, byteorder='big'),
                       int.from_bytes(CMD, byteorder='big'), int.from_bytes(LEN, byteorder='big'),
                       DATA_add_hex_list]) % 256  # 校验和
        except OverflowError:
            print("int too big to convert")
            return False
        packet = HEAD + ADDR + CMD + LEN + DATA + bytes([SUM])  # 数据包
        port.ser.write(packet)  # 将命令代码写入串口
        return True  # 如果成功，则返回True，否则引发异常

    """
    发送相对于鼠标的数据。
    
    参数：
        x (int)：鼠标的x坐标。
        y (int)：鼠标的y坐标。
        ctrl (str)：按下的控制键。
        port (Serial)：鼠标的串口。
    
    返回：
        bool：如果成功发送数据，则返回True，否则返回False。
    """

    def send_data_relatively(self, x: int, y: int, ctrl: str = '', port: serial = serial) -> bool:
        # 将字符转写为数据包
        HEAD = b'\x57\xAB'  # 帧头
        ADDR = b'\x00'  # 地址
        CMD = b'\x05'  # 命令
        LEN = b'\x05'  # 数据长度
        DATA = bytearray(b'\x01')  # 数据

        # 鼠标按键
        if ctrl == '':
            DATA.append(0)
        elif isinstance(ctrl, int):
            DATA.append(ctrl)
        else:
            DATA += self.hex_dict[ctrl]

        # x坐标
        if x == 0:
            DATA.append(0)
        elif x < 0:
            DATA += (0 - abs(x)).to_bytes(1, byteorder='big', signed=True)
        else:
            DATA += x.to_bytes(1, byteorder='big', signed=True)

        # y坐标，这里为了符合坐标系直觉，将<0改为向下，>0改为向上
        y = - y
        if y == 0:
            DATA.append(0)
        elif y < 0:
            DATA += (0 - abs(y)).to_bytes(1, byteorder='big', signed=True)
        else:
            DATA += y.to_bytes(1, byteorder='big', signed=True)

        DATA += b'\x00' * (5 - len(DATA)) if len(DATA) < 5 else DATA[:5]

        # 分离HEAD中的值，并计算和
        HEAD_hex_list = list(HEAD)
        HEAD_add_hex_list = sum(HEAD_hex_list)

        # 分离DATA中的值，并计算和
        DATA_hex_list = list(DATA)
        DATA_add_hex_list = sum(DATA_hex_list)

        try:
            SUM = sum([HEAD_add_hex_list, int.from_bytes(ADDR, byteorder='big'),
                       int.from_bytes(CMD, byteorder='big'), int.from_bytes(LEN, byteorder='big'),
                       DATA_add_hex_list]) % 256  # 校验和
        except OverflowError:
            print("int too big to convert")
            return False
        packet = HEAD + ADDR + CMD + LEN + DATA + bytes([SUM])  # 数据包
        port.ser.write(packet)  # 将命令代码写入串口
        return True  # 如果成功，则返回True，否则引发异常
    
    """ 
    功能：move_to_basic
    
    描述：此函数调用轨迹生成函数生成的逐差数组，将数组中的数据发送到串口以控制鼠标移动。
    
    参数：
    - self：对象实例
    - x：目标的x坐标。
    - y：目标的y坐标。
    - ctrl：鼠标移动的控制字符（默认为空字符串）。
    - port：串口（默认为serial）。
    
    返回：
    - None
    """  
    
    def move_to_basic(self, x: int, y: int, ctrl: str = '', port: serial = serial) -> None:
        coordinate = [x, y]
        number_list = int((((x ** 2) + (y ** 2)) ** 0.5))
        le = random.randint(4, 10)
        deviation = random.randint(0, int(min(abs(x) % 499, abs(y) % 499) / 5))
        bias = random.uniform(0, 0.8)
        type_ = 3
        bezierTrajectory = BezierTrajectory.BezierTrajectory()
        bezier_array = bezierTrajectory.get_track([0, 0], coordinate, number_list, le, deviation, bias, type_)

        # test
        # print("====================参数信息=============================================")
        # print("x=%d y=%d number_list=%d le=%d deviation=%d bias=%f type=%d" % (
        #     x, y, number_list, le, deviation, bias, type_))

        # 将bezier_array数组转为整数
        for i in range(len(bezier_array)):
            bezier_array[i][0] = int(bezier_array[i][0])
            bezier_array[i][1] = int(bezier_array[i][1])

        # 定义prefix_bezier_array数组，存放差值
        prefix_bezier_array = [[0, 0]]
        for i in range(len(bezier_array) - 1):
            prefix_bezier_array.append(
                [bezier_array[i + 1][0] - bezier_array[i][0], bezier_array[i + 1][1] - bezier_array[i][1]])

        # 过滤prefix_bezier_array数组中的部分[0,0]元素
        # new_bezier_array = []
        # count = 0
        # for i in range(len(prefix_bezier_array)):
        #     if prefix_bezier_array[i] == [0, 0]:
        #         count += 1
        #         if count < 2:
        #             new_bezier_array.append(prefix_bezier_array[i])
        #     else:
        #         count = 0
        #         new_bezier_array.append(prefix_bezier_array[i])
        # prefix_bezier_array = new_bezier_array

        # 定义prefix_bezier_array数组，存放差值
        for i in range(len(prefix_bezier_array)):
            self.send_data_relatively(int(prefix_bezier_array[i][0]), int(prefix_bezier_array[i][1]), ctrl, port)
            time.sleep(0.0016)

    """
    这个函数检查鼠标指针在屏幕上的理论值和实际值之间的差异。
    
    参数：
    - self：MouseDataComm对象。
    - x：鼠标指针位置的x坐标。
    - y：鼠标指针位置的y坐标。
    
    返回：
    - difference_ratio：鼠标指针在屏幕上的理论值和实际值之间的差异。
    """

    def check_difference_ratio(self, x: int, y: int) -> float:
        # 创建一个MouseDataComm类的实例
        mouse = DataComm()
        # 调用send_data_absolute方法将鼠标指针移动到屏幕的中心
        mouse.send_data_absolute(int(self.X_MAX / 2), int(self.Y_MAX / 2))
        # 调用move_to方法，参数为(50,50)
        mouse.move_to_basic(x, y)
        # 计算鼠标的位置距离屏幕中心点的距离，并将距离输出到控制台上
        x_, y_ = pyautogui.position()
        distance = ((x_ - self.X_MAX / 2) ** 2 + (y_ - self.Y_MAX / 2) ** 2) ** 0.5
        difference_ratio = distance / (((x ** 2) + (y ** 2)) ** 0.5)
        print("理论值与实际值之间的差异：", (difference_ratio * 100), "%")
        return difference_ratio

    """
    功能：get_corrector
    
    描述：此函数从JSON文件中检索校正器值。如果文件不存在，则创建它并通过平均8个不同坐标的检查函数结果来计算校正器值。
    
    参数： 
    - self：对象实例
    
    返回：
    - value：校正器值
    """

    def get_corrector(self) -> float:
        file_path = os.path.join(os.getcwd(), 'corrector', 'information.json')
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                data = {'value': 0}
                json.dump(data, file)
            value_sum = 0
            for x, y in [(5, 20), (50, 25), (233, 233), (313, 212), (500, 10), (500, 100), (17, 587),
                         (666, 666)]:
                value_sum += self.check_difference_ratio(x, y)
            value = value_sum / 8
            with open(file_path, 'w') as file:
                data = {'value': value}
                json.dump(data, file)
            return value
        else:
            with open(file_path, 'r') as file:
                data = json.load(file)
                value = data['value']
                return value

    """
    将鼠标光标移动到指定的目标坐标。

    参数：
        dest_x (int)：目标的x坐标。
        dest_y (int)：目标的y坐标。
        ctrl (str, optional)：要发送到串口的控制字符。默认为''。
        port (serial, optional)：要使用的串口。默认为serial。

    返回：
        difference_ratio：鼠标指针实际移动量与目标移动量的比值（0 ~ 1）
    """
    
    def move_to(self, dest_x: int, dest_y: int, ctrl: str = '', port: serial = serial) -> None:
        start_x, start_y = pyautogui.position()
        correction_factor = self.get_corrector()
        corrected_x = dest_x * (1 / correction_factor)
        corrected_y = dest_y * (1 / correction_factor)
        self.move_to_basic(int(corrected_x), int(corrected_y), ctrl, port)
        end_x, end_y = pyautogui.position()
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        difference_ratio = distance / (((dest_x ** 2) + (dest_y ** 2)) ** 0.5)

        return difference_ratio

    """
    单击鼠标左键。
    
    参数：
        serial (Serial)：串行对象。
    
    返回：
        None
    """

    def click(self, port: serial = serial) -> None:
        self.send_data_relatively(0, 0, 'LE', port)
        time.sleep(random.uniform(0.1, 0.45))  # 100到450毫秒延迟
        self.send_data_relatively(0, 0, 'NU', port)

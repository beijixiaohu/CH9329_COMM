import random
import time
import serial

from BezierTrajectory import BezierTrajectory


class MouseDataComm:
    """
    属性：
        hex_dict (dict)：命令的十六进制值的字典。
    """

    def __init__(self):
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

    def send_data_absolute(self, x, y, ctrl='', port=serial):
        # 将字符转写为数据包
        HEAD = b'\x57\xAB'  # 帧头
        ADDR = b'\x00'  # 地址
        CMD = b'\x04'  # 命令
        LEN = b'\x07'  # 数据长度
        DATA = b''  # 数据

        # DATA固定码
        DATA += b'\x02'

        # 鼠标按键
        if ctrl == '':
            DATA += b'\x00'
        elif isinstance(ctrl, int):
            DATA += bytes([ctrl])
        else:
            DATA += self.hex_dict[ctrl]

        # 坐标
        X_MAX = 3840  # 注意！！！！！！！这里的X_MAX、Y_MAX需要改为自己的屏幕分辨率
        Y_MAX = 2160
        X_Cur = (4096 * x) // X_MAX
        Y_Cur = (4096 * y) // Y_MAX
        DATA += X_Cur.to_bytes(2, byteorder='little')
        DATA += Y_Cur.to_bytes(2, byteorder='little')

        if len(DATA) < 7:
            DATA += b'\x00' * (7 - len(DATA))
        else:
            DATA = DATA[:7]

        # 分离HEAD中的值，并计算和
        HEAD_hex_list = []
        for byte in HEAD:
            HEAD_hex_list.append(byte)
        HEAD_add_hex_list = 0
        for i in HEAD_hex_list:
            HEAD_add_hex_list += i

        # 分离DATA中的值，并计算和
        DATA_hex_list = []
        for byte in DATA:
            DATA_hex_list.append(byte)
        DATA_add_hex_list = 0
        for i in DATA_hex_list:
            DATA_add_hex_list += i

        #
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

    def send_data_relatively(self, x, y, ctrl='', port=serial):
        # 将字符转写为数据包
        HEAD = b'\x57\xAB'  # 帧头
        ADDR = b'\x00'  # 地址
        CMD = b'\x05'  # 命令
        LEN = b'\x05'  # 数据长度
        DATA = b''  # 数据

        # DATA固定码
        DATA += b'\x01'

        # 鼠标按键
        if ctrl == '':
            DATA += b'\x00'
        elif isinstance(ctrl, int):
            DATA += bytes([ctrl])
        else:
            DATA += self.hex_dict[ctrl]

        # x坐标
        if x == 0:
            DATA += b'\x00'
        elif x < 0:
            DATA += (0 - abs(x)).to_bytes(1, byteorder='big', signed=True)
        else:
            DATA += x.to_bytes(1, byteorder='big', signed=True)

        # y坐标，这里为了符合坐标系直觉，将<0改为向下，>0改为向上
        y = - y
        if y == 0:
            DATA += b'\x00'
        elif y < 0:
            DATA += (0 - abs(y)).to_bytes(1, byteorder='big', signed=True)
        else:
            DATA += y.to_bytes(1, byteorder='big', signed=True)

        if len(DATA) < 5:
            DATA += b'\x00' * (5 - len(DATA))
        else:
            DATA = DATA[:5]

        # 分离HEAD中的值，并计算和
        HEAD_hex_list = []
        for byte in HEAD:
            HEAD_hex_list.append(byte)
        HEAD_add_hex_list = 0
        for i in HEAD_hex_list:
            HEAD_add_hex_list += i

        # 分离DATA中的值，并计算和
        DATA_hex_list = []
        for byte in DATA:
            DATA_hex_list.append(byte)
        DATA_add_hex_list = 0
        for i in DATA_hex_list:
            DATA_add_hex_list += i

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

    def move_to(self, x, y, ctrl='', port=serial):
        coordinate = [x, y]
        number_list = int((((x ** 2) + (y ** 2)) ** 0.5))
        le = random.randint(4, 10)
        deviation = random.randint(0, int(min(abs(x) % 499, abs(y) % 499) / 5))
        bias = random.uniform(0, 0.8)
        type = 3
        bezierTrajectory = BezierTrajectory()
        bezier_array = bezierTrajectory.get_track([0, 0], coordinate, number_list, le, deviation, bias, type)

        # test
        print("====================参数信息=============================================")
        print("x=%d y=%d number_list=%d le=%d deviation=%d bias=%f type=%d" % (
        x, y, number_list, le, deviation, bias, type))

        # 将bezier_array数组转为整数
        for i in range(len(bezier_array)):
            bezier_array[i][0] = int(bezier_array[i][0])
            bezier_array[i][1] = int(bezier_array[i][1])

        # test
        # ac_x = 0
        # ac_y = 0
        # print("====================bezier_array======================================")
        # for i in range(len(bezier_array)):
        #     ac_x += bezier_array[i][0]
        #     ac_y += bezier_array[i][1]
        # print("x方向累加和= %d y方向累加和= %d" % (ac_x, ac_y))


        # 定义prefix_bezier_array数组，存放差值
        prefix_bezier_array = [[0, 0]]
        for i in range(len(bezier_array) - 1):
            prefix_bezier_array.append(
                [bezier_array[i + 1][0] - bezier_array[i][0], bezier_array[i + 1][1] - bezier_array[i][1]])

        # test
        # ac_x = 0
        # ac_y = 0
        # print("=====================prefix_bezier_array==============================")
        # for i in range(len(prefix_bezier_array)):
        #     ac_x += prefix_bezier_array[i][0]
        #     ac_y += prefix_bezier_array[i][1]
        # print("x方向累加和= %d y方向累加和= %d" % (ac_x, ac_y))


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
            
        # test
        ac_x = 0
        ac_y = 0
        print("=====================new_bezier_array==================================")
        for i in range(len(prefix_bezier_array)):
            ac_x += prefix_bezier_array[i][0]
            ac_y += prefix_bezier_array[i][1]
        print("x方向累加和= %d y方向累加和= %d" % (ac_x, ac_y))

        # 定义prefix_bezier_array数组，存放差值
        for i in range(len(prefix_bezier_array)):
            self.send_data_relatively(int(prefix_bezier_array[i][0]), int(prefix_bezier_array[i][1]), ctrl, port)
            time.sleep(0.002)

    """
    单击鼠标左键。
    
    参数：
        serial (Serial)：串行对象。
    
    返回：
        None
    """

    def click(port=serial):
        port.send_data_relatively(0, 0, 'LE')
        time.sleep(random.uniform(0.1, 0.45))  # 100到450毫秒延迟
        port.send_data_relatively(0, 0, 'NU')

import random
import time
import serial

class MouseDateComm:
    """
    初始化Mouse_DateComm类。
    
    属性：
        ser (serial.Serial)：通信的串行对象。
        hex_dict (dict)：命令的十六进制值的字典。
    """

    def __init__(self):
        self.hex_dict = {"ST": b'\x02',
                         "NU": b"\x00",
                         "LE": b"\x01",
                         "RI": b"\x02",
                         "CE": b"\x04"
                         }

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
        X_MAX = 3840
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
        ctrl (str)：鼠标的控制键。
        serial (Serial)：鼠标的串口。
    
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
        time.sleep(random.uniform(0.05, 0.2))  # 50~200毫秒延迟
        return True  # 如果成功，则返回True，否则引发异常

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

import serial


class DataComm:
    """
    此类初始化两个字典，control_button_hex_dict和normal_button_hex_dict，它们包含键盘上控制和普通按钮的十六进制值。
    如果你需要更多的按钮，请自行根据协议文档补充
    """

    def __init__(self):
        self.control_button_hex_dict = {"NULL": b'\x00',
                                        "R_WIN": b"\x80",
                                        "R_ALT": b"\x40",
                                        "R_SHIFT": b"\x20",
                                        "R_CTRL": b"\x10",
                                        "L_WIN": b"\x08",
                                        "L_ALT": b"\x04",
                                        "L_SHIFT": b"\x02",
                                        "L_CTRL": b"\x01"
                                        }
        self.normal_button_hex_dict = {"NU": b'\x00',
                                       "QQ": b"\x14",
                                       "WW": b"\x1A",
                                       "EE": b"\x08",
                                       "RR": b"\x15",
                                       "TT": b"\x17",
                                       "YY": b"\x1C",
                                       "UU": b"\x18",
                                       "II": b"\x0C",
                                       "OO": b"\x12",
                                       "PP": b"\x13",
                                       "AA": b"\x04",
                                       "SS": b"\x16",
                                       "DD": b"\x07",
                                       "FF": b"\x09",
                                       "GG": b"\x0A",
                                       "HH": b"\x0B",
                                       "JJ": b"\x0D",
                                       "KK": b"\x0E",
                                       "LL": b"\x0F",
                                       "ZZ": b"\x1D",
                                       "XX": b"\x1B",
                                       "CC": b"\x06",
                                       "VV": b"\x19",
                                       "BB": b"\x05",
                                       "NN": b"\x11",
                                       "MM": b"\x10"
                                       }

    """
    发送数据到串口。
    
    参数:
        data (str): 要发送的按键信息。
        ctrl (str): 要发送的控制键。
        port (serial): 要发送数据的串口。
    
    返回:
        bool: 如果数据成功发送，则为True，否则为False。
    """

    def send_data(self, data, ctrl='', port=serial):
        # 将字符转写为数据包
        HEAD = b'\x57\xAB'  # 帧头
        ADDR = b'\x00'  # 地址
        CMD = b'\x02'  # 命令
        LEN = b'\x08'  # 数据长度
        DATA = b''  # 数据

        # 控制键
        if ctrl == '':
            DATA += b'\x00'
        elif isinstance(ctrl, int):
            DATA += bytes([ctrl])
        else:
            DATA += self.control_button_hex_dict[ctrl]

        # DATA固定码
        DATA += b'\x00'

        # 读入data
        for i in range(0, len(data), 2):
            DATA += self.normal_button_hex_dict[data[i:i + 2]]
        if len(DATA) < 8:
            DATA += b'\x00' * (8 - len(DATA))
        else:
            DATA = DATA[:8]

        # 分离HEAD中的值，并计算和
        HEAD_hex_list = []
        for byte in HEAD:
            HEAD_hex_list.append(byte)
        HEAD_add_hex_list = sum(HEAD_hex_list)

        # 分离DATA中的值，并计算和
        DATA_hex_list = []
        for byte in DATA:
            DATA_hex_list.append(byte)
        DATA_add_hex_list = sum(DATA_hex_list)

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
    释放按钮。
    
    参数:
        serial (object): 用于发送数据的串行对象。
    
    返回:
        None
    """

    def release(serial):
        serial.send_data('')

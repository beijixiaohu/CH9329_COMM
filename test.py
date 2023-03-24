import serial
from ch9329Comm import keyboard
from ch9329Comm import mouse

serial.ser = serial.Serial('COM4', 115200)  # 开启串口

# # 键盘输出helloworld
# dc = KeyboardDataComm()
# dc.send_data('HHEELLLLOO')  # 按下HELLO
# dc.release()  # 松开
# dc.send_data('WWOORRLLDD')  # 按下WORLD
# dc.release()  # 松开


# （绝对）鼠标移动到屏幕的左上100*100的位置
# from MouseDataComm import MouseDataComm
#
# dc = MouseDataComm()
# dc.send_data_absolute(500,500)

# （相对）鼠标右移100px 下移100px
# dc2 = MouseDataComm()
# dc2.move_to(-100, -100)

# 校验
dc2 = MouseDataComm()
dc2.move_to(-230,-480)

serial.ser.close()  # 关闭串口

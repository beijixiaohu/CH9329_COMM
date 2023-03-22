import serial
from KeyboardDataComm import KeyboardDataComm
from MouseDataComm import MouseDataComm

serial.ser = serial.Serial('COM4', 9600)  # 开启串口

# 键盘输出helloworld
dc = KeyboardDataComm()
dc.send_data('HHEELLLLOO')  # 按下HELLO
dc.release()  # 松开
dc.send_data('WWOORRLLDD')  # 按下WORLD
dc.release()  # 松开


# （绝对）鼠标移动到屏幕的左上100*100的位置
# from MouseDateComm import Mouse_DateComm
#
# dc = MouseDateComm()
# dc.send_data_absolute(100,100)

# （相对）鼠标右移100px 下移100px
dc2 = MouseDataComm()
dc2.send_data_relatively(100, -100)
dc2.click()

serial.ser.close()  # 关闭串口

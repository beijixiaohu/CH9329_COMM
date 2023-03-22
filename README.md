# CH9329_COMM
基于CH9329芯片的键盘/鼠标串口通信类实现

## 发送键盘数据包

`KeyboardDataComm` 类提供了向串口快速发送键盘数据包的方法：`send_data()`

**语法：**

```python
send_data(data, [ctrl], [port])
```

参数:
- data (str): 要发送的按键信息，一次最多发送6个按键信息。<br>
  按键信息包含在字典中，默认仅包含了26个字母按键，比如按键`C`对应`CC`，如需要使用其它按键可以自行根据协议文档扩充
- ctrl (str): 可选，要发送的控制键，不填则默认不按下控制键。
- port (serial): 可选，要发送数据的串口，如果不填则默认为serial。

返回:
- bool: 如果数据成功发送，则为True，否则为False。
    
> 注意！
> 无法同时按下多个普通按键，后按下的按键会覆盖原来的按键，哪怕是一次发送多个按键

控制键的可选值：

| 可选值 | 含义      |
|------|---------|
| R_WIN  | 右Winodws键 |
| R_ALT    | 右Alt键 |
| R_SHIFT  | 右Shift键 |
| R_CTRL   | 右Ctrl键 |
| L_WIN     | 左Winodws键 |
| L_ALT      | 左Alt键 |
| L_SHIFT  | 左Shift键 |
| L_CTRL    | 左Ctrl键 |

你也可以传入一个16进制的数值以发送组合键，形如`0x00`，关于数值的定义与通信协议文档中相同

示例：

```python
dc = KeyboardDataComm()
dc.send_data('',0x03) # 按下ctrl+shift
```
**示例：**

```python
import serial
from KeyboardDataComm import KeyboardDataComm

serial.ser = serial.Serial('COM4', 9600)  # 开启串口

# 键盘输出helloworld
dc = KeyboardDataComm()
dc.send_data('HHEELLLLOO')  # 按下HELLO
dc.release()  # 松开
dc.send_data('WWOORRLLDD')  # 按下WORLD
dc.release()  # 松开

serial.ser.close()  # 关闭串口
```

## 发送鼠标数据包

`MouseDataComm` 类提供了向串口快速发送鼠标数据包的两个方法：`send_data_absolute()`、`send_data_relatively()`

### send_data_absolute()

该方法用于将鼠标移动到相对于屏幕左上角距离x,y的位置

**语法：**

```python
send_data_absolute(x, y, [ctrl], [port])
```

参数：
- x (int)：鼠标光标的x坐标。
- y (int)：鼠标光标的y坐标。
- ctrl (str)：可选，按下的控制键，如果省略则默认为NU，即只移动鼠标，不按下任何按键。
  > 注意！这表示按住鼠标控制键并移动鼠标，
- port (serial)：可选，要发送数据的串口，如果不填则默认为serial。

返回：
- 如果成功发送数据，则返回True，否则返回False。


控制键的可选值：

| 可选值 | 含义      |
|------|---------|
| NU  |  |
| LE  | 左键 |
| RI    | 右键 |
| CE  | 中键 |

你也可以传入一个16进制的数值以发送组合键，形如`0x00`，关于数值的定义与通信协议文档中相同

**示例：**

```python
import serial
from MouseDataComm import MouseDataComm

serial.ser = serial.Serial('COM4', 9600)  # 开启串口

# （绝对）鼠标移动到屏幕的左上100*100的位置
dc = MouseDataComm()
dc.send_data_absolute(100, 100)

serial.ser.close()  # 关闭串口
```

### send_data_relatively()

该方法用于将鼠标移动到以鼠标当前位置为原点的坐标系上点(x,y)的位置

**语法：**

```python
send_data_relatively(x, y, [ctrl], [port])
```
参数：
- x (int)：相对的x坐标。
- y (int)：相对的y坐标。
- ctrl (str)：可选，按下的控制键，如果省略则默认为NU，即只移动鼠标，不按下任何按键。
  > 注意！这表示按住鼠标控制键并移动鼠标，
- port (Serial)：可选，要发送数据的串口，如果不填则默认为serial。

返回：
- bool：如果成功发送数据，则返回True，否则返回False。

控制键的可选值：

| 可选值 | 含义      |
|------|---------|
| NU  |  |
| LE  | 左键 |
| RI    | 右键 |
| CE  | 中键 |

你也可以传入一个16进制的数值以发送组合键，形如`0x00`，关于数值的定义与通信协议文档中相同

**示例：**

```python
import serial
from MouseDataComm import MouseDataComm

serial.ser = serial.Serial('COM4', 9600)  # 开启串口

# （相对）鼠标右移100px 下移100px并单击左键
dc2 = MouseDataComm()
dc2.send_data_relatively(100, -100)
dc2.click()  # 单击左键

serial.ser.close()  # 关闭串口
```


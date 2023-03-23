# CH9329_COMM
基于CH9329芯片的键盘/鼠标串口通信类实现

结构介绍：

| 类                 | 说明         |
| ------------------ | ------------ |
| `KeyboardDataComm` | 键盘数据发送 |
| `MouseDataComm`    | 鼠标数据发送 |
| `BezierTrajectory` | 鼠标路径生成 |



> **注意！**
>
> 请将CH9329芯片按以下参数配置，否则某些方法不能正常工作：
>
> 波特率：`115200` 、串口包间隔：`1ms`
>
> （可以直接向串口发送数据包配置，也可以使用厂商的上位机软件配置，注意修改配置后在下一次上电时才会生效）

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

serial.ser = serial.Serial('COM4', 115200)  # 开启串口

# 键盘输出helloworld
dc = KeyboardDataComm()
dc.send_data('HHEELLLLOO')  # 按下HELLO
dc.release()  # 松开
dc.send_data('WWOORRLLDD')  # 按下WORLD
dc.release()  # 松开

serial.ser.close()  # 关闭串口
```

## 发送鼠标数据包

`MouseDataComm` 类提供了向串口快速发送鼠标数据包的三个方法：

- `send_data_absolute()`：绝对移动，将鼠标闪现到相对于屏幕左上角距离x,y的位置

- `send_data_relatively()`：相对移动，将鼠标闪现到以鼠标当前位置为原点的坐标系上点(x,y)的位置
- `move_to_basic()`：基于`send_data_relatively()`，其会自动生成随机路径，将鼠标指针沿轨迹移动到点(x,y)的位置
- `move_to()`（推荐）:对于 `move_to()` 的改进方法，添加了自动误差校正

### send_data_absolute()

该方法用于将鼠标闪现到相对于屏幕左上角距离x,y的位置

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

serial.ser = serial.Serial('COM4', 115200)  # 开启串口

# （绝对）鼠标移动到屏幕的左上100*100的位置
dc = MouseDataComm()
dc.send_data_absolute(100, 100)

serial.ser.close()  # 关闭串口
```

### send_data_relatively()

该方法用于将鼠标闪现到以鼠标当前位置为原点的坐标系上点(x,y)的位置

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

serial.ser = serial.Serial('COM4', 115200)  # 开启串口

# （相对）鼠标右移100px 下移100px并单击左键
dc2 = MouseDataComm()
dc2.send_data_relatively(100, -100)
dc2.click()  # 单击左键

serial.ser.close()  # 关闭串口
```

### move_to_basic()

该方法会调用`BezierTrajectory`类中的轨迹生成方法，自动生成随机路径，并将路径分解为步长 0 ~ 2px 的路径点的集合，

其以每 1.6ms 一个的频率发送数据包，因此指针每1.6ms最多会在屏幕上移动两个像素点（大部分时间只会移动1个像素点）

**语法：**

```python
move_to_basic(x, y, ctrl, port)
```

参数：
- x：目标的x坐标。
- y：目标的y坐标。
- ctrl：鼠标移动的控制字符（默认为空字符串）。
- port：串口（默认为serial）。

返回：
- None

控制键的可选值：

| 可选值 | 含义 |
| ------ | ---- |
| NU     |      |
| LE     | 左键 |
| RI     | 右键 |
| CE     | 中键 |

你也可以传入一个16进制的数值以发送组合键，形如`0x00`，关于数值的定义与通信协议文档中相同

### move_to()

该方法是对于 `move_to_basic()` 的改进方法，添加了自动误差校正

> **注意初始化：**
>
> 第一次调用该方法时，其会自动在项目路径下新建 `\corrector\information.json` 文件，
>
> 然后自动多次调用 `check_difference_ratio()` 方法，检查当前环境中鼠标指针在屏幕上的移动理论值和实际值之间的差异，
>
> 并根据差异的平均值对目标(x,y)进行修正，在此期间鼠标指针会自动在屏幕上跳跃或者移动，请不要触碰你的实际物理鼠标以免影响检查。
>
> 其会将在修正值存储在 `\corrector\information.json`中，以后调用该方法时会自动到文件中读取修正值，如果需要重新生成校正值，请手动删除 `\corrector\information.json` 文件

**语法：**

```python
move_to(dest_x, dest_y, ctrl, port)
```

参数：

- dest_x (int)：目标的x坐标。
- dest_y (int)：目标的y坐标。
- ctrl (str, optional)：要发送到串口的控制字符。默认为''。
- port (serial, optional)：要使用的串口。默认为serial。

返回：
    None

控制键的可选值：

| 可选值 | 含义 |
| ------ | ---- |
| NU     |      |
| LE     | 左键 |
| RI     | 右键 |
| CE     | 中键 |

你也可以传入一个16进制的数值以发送组合键，形如`0x00`，关于数值的定义与通信协议文档中相同

**示例：**

```python
import serial
from MouseDataComm import MouseDataComm

serial.ser = serial.Serial('COM4', 115200)  # 开启串口

dc2 = MouseDataComm()
dc2.move_to(-230,-480) # 生成路径并沿路径移动到(-230,-480)

serial.ser.close()  # 关闭串口
```






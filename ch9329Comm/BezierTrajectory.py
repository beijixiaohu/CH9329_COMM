import math
import random
import numpy as np


class BezierTrajectory:

    @staticmethod
    def _bztsg(data_trajectory):
        length_of_data = len(data_trajectory)

        def staer(x):
            t = ((x - data_trajectory[0][0]) / (data_trajectory[-1][0] - data_trajectory[0][0]))
            y = np.array([0, 0], dtype=np.float64)
            for s in range(length_of_data):
                y += data_trajectory[s] * ((math.factorial(length_of_data - 1) // (
                        math.factorial(s) * math.factorial(length_of_data - 1 - s))) * math.pow(t, s) * math.pow(
                    (1 - t), length_of_data - 1 - s))
            return y[1]

        return staer

    def _type(self, type_, x, number_list):
        number_list_re = []
        pin = (x[1] - x[0]) / number_list
        if type_ == 0:
            for i in range(number_list):
                number_list_re.append(i * pin)
            if pin >= 0:
                number_list_re = number_list_re[::-1]
        elif type_ == 1:
            for i in range(number_list):
                number_list_re.append(1 * ((i * pin) ** 2))
            number_list_re = number_list_re[::-1]
        elif type_ == 2:
            for i in range(number_list):
                number_list_re.append(1 * ((i * pin - x[1]) ** 2))

        elif type_ == 3:
            data_trajectory = [np.array([0, 0]), np.array([(x[1] - x[0]) * 0.8, (x[1] - x[0]) * 0.6]),
                               np.array([x[1] - x[0], 0])]
            fun = self._bztsg(data_trajectory)
            number_list_re = [0]
            for i in range(1, number_list):
                number_list_re.append(fun(i * pin) + number_list_re[-1])
            if pin >= 0:
                number_list_re = number_list_re[::-1]
        number_list_re = np.abs(np.array(number_list_re) - max(number_list_re))
        biao_number_list = ((number_list_re - number_list_re[number_list_re.argmin()]) / (
                number_list_re[number_list_re.argmax()] - number_list_re[number_list_re.argmin()])) * (x[1] - x[0]) + x[
                               0]
        biao_number_list[0] = x[0]
        biao_number_list[-1] = x[1]
        return biao_number_list

    def simulation(self, start, end, le=1, deviation=0, bias=0.5):
        """

        :param start:开始点的坐标 如 start = [0, 0]
        :param end:结束点的坐标 如 end = [100, 100]
        :param le:几阶贝塞尔曲线，越大越复杂 如 le = 4
        :param deviation:轨迹上下波动的范围 如 deviation = 10
        :param bias:波动范围的分布位置 如 bias = 0.5
        :return:返回一个字典equation对应该曲线的方程，P对应贝塞尔曲线的影响点
        """
        start = np.array(start)
        end = np.array(end)
        cbb = []
        if le != 1:
            e = (1 - bias) / (le - 1)
            cbb = [[bias + e * i, bias + e * (i + 1)] for i in range(le - 1)]

        data_trajectory_list = [start]

        t = random.choice([-1, 1])
        w = 0
        for i in cbb:
            px1 = start[0] + (end[0] - start[0]) * (random.random() * (i[1] - i[0]) + (i[0]))
            p = np.array([px1, self._bztsg([start, end])(px1) + t * deviation])
            data_trajectory_list.append(p)
            w += 1
            if w >= 2:
                w = 0
                t = -1 * t

        data_trajectory_list.append(end)
        return {"equation": self._bztsg(data_trajectory_list), "P": np.array(data_trajectory_list)}

    def get_track(self, start, end, number_list, le=1, deviation=0, bias=0.5, type_=0, cbb=0, yhh=10):
        """

        :param start:开始点的坐标 如 start = [0, 0]
        :param end:结束点的坐标 如 end = [100, 100]
        :param number_list:返回的数组的轨迹点的数量 number_list = 150
        :param le:几阶贝塞尔曲线，越大越复杂 如 le = 4
        :param deviation:轨迹上下波动的范围 如 deviation = 10
        :param bias:波动范围的分布位置 如 bias = 0.5
        :param type_:0表示均速滑动，1表示先慢后快，2表示先快后慢，3表示先慢中间快后慢 如 type_ = 1
        :param cbb:在终点来回摆动的次数
        :param yhh:在终点来回摆动的范围
        :return:返回一个字典trackArray对应轨迹数组，P对应贝塞尔曲线的影响点
        """
        s = []
        fun = self.simulation(start, end, le, deviation, bias)
        w = fun['P']
        fun = fun["equation"]
        if cbb != 0:
            number_list_of_cbb = round(number_list * 0.2 / (cbb + 1))
            number_list -= (number_list_of_cbb * (cbb + 1))

            x_track_array = self._type(type_, [start[0], end[0]], number_list)
            for i in x_track_array:
                s.append([i, fun(i)])
            dq = yhh / cbb
            kg = 0
            ends = np.copy(end)
            for i in range(cbb):
                if kg == 0:
                    d = np.array([end[0] + (yhh - dq * i),
                                  ((end[1] - start[1]) / (end[0] - start[0])) * (end[0] + (yhh - dq * i)) + (
                                          end[1] - ((end[1] - start[1]) / (end[0] - start[0])) * end[0])])
                    kg = 1
                else:
                    d = np.array([end[0] - (yhh - dq * i),
                                  ((end[1] - start[1]) / (end[0] - start[0])) * (end[0] - (yhh - dq * i)) + (
                                          end[1] - ((end[1] - start[1]) / (end[0] - start[0])) * end[0])])
                    kg = 0
                print(d)
                y = self.get_track(ends, d, number_list_of_cbb, le=2, deviation=0, bias=0.5, type_=0, cbb=0, yhh=10)
                s += list(y['trackArray'])
                ends = d
            y = self.get_track(ends, end, number_list_of_cbb, le=2, deviation=0, bias=0.5, type_=0, cbb=0, yhh=10)
            s += list(y['trackArray'])

        else:
            x_track_array = self._type(type_, [start[0], end[0]], number_list)
            for i in x_track_array:
                s.append([i, fun(i)])
        return s

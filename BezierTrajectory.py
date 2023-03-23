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
            for s in range(len(data_trajectory)):
                y += data_trajectory[s] * ((math.factorial(length_of_data - 1) / (
                        math.factorial(s) * math.factorial(length_of_data - 1 - s))) * math.pow(t, s) * math.pow(
                    (1 - t), length_of_data - 1 - s))
            return y[1]

        return staer

    def _type(self, type, x, number_list):
        numberListre = []
        pin = (x[1] - x[0]) / number_list
        if type == 0:
            for i in range(number_list):
                numberListre.append(i * pin)
            if pin >= 0:
                numberListre = numberListre[::-1]
        elif type == 1:
            for i in range(number_list):
                numberListre.append(1 * ((i * pin) ** 2))
            numberListre = numberListre[::-1]
        elif type == 2:
            for i in range(number_list):
                numberListre.append(1 * ((i * pin - x[1]) ** 2))

        elif type == 3:
            dataTrajectory = [np.array([0, 0]), np.array([(x[1] - x[0]) * 0.8, (x[1] - x[0]) * 0.6]),
                              np.array([x[1] - x[0], 0])]
            fun = self._bztsg(dataTrajectory)
            numberListre = [0]
            for i in range(1, number_list):
                numberListre.append(fun(i * pin) + numberListre[-1])
            if pin >= 0:
                numberListre = numberListre[::-1]
        numberListre = np.abs(np.array(numberListre) - max(numberListre))
        biaoNumberList = ((numberListre - numberListre[numberListre.argmin()]) / (
                numberListre[numberListre.argmax()] - numberListre[numberListre.argmin()])) * (x[1] - x[0]) + x[0]
        biaoNumberList[0] = x[0]
        biaoNumberList[-1] = x[1]
        return biaoNumberList

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

        dataTrajectoryList = [start]

        t = random.choice([-1, 1])
        w = 0
        for i in cbb:
            px1 = start[0] + (end[0] - start[0]) * (random.random() * (i[1] - i[0]) + (i[0]))
            p = np.array([px1, self._bztsg([start, end])(px1) + t * deviation])
            dataTrajectoryList.append(p)
            w += 1
            if w >= 2:
                w = 0
                t = -1 * t

        dataTrajectoryList.append(end)
        return {"equation": self._bztsg(dataTrajectoryList), "P": np.array(dataTrajectoryList)}

    def get_track(self, start, end, number_list, le=1, deviation=0, bias=0.5, type=0, cbb=0, yhh=10):
        """

        :param start:开始点的坐标 如 start = [0, 0]
        :param end:结束点的坐标 如 end = [100, 100]
        :param number_list:返回的数组的轨迹点的数量 numberList = 150
        :param le:几阶贝塞尔曲线，越大越复杂 如 le = 4
        :param deviation:轨迹上下波动的范围 如 deviation = 10
        :param bias:波动范围的分布位置 如 bias = 0.5
        :param type:0表示均速滑动，1表示先慢后快，2表示先快后慢，3表示先慢中间快后慢 如 type = 1
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

            xTrackArray = self._type(type, [start[0], end[0]], number_list)
            for i in xTrackArray:
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
                y = self.get_track(ends, d, number_list_of_cbb, le=2, deviation=0, bias=0.5, type=0, cbb=0, yhh=10)
                s += list(y['trackArray'])
                ends = d
            y = self.get_track(ends, end, number_list_of_cbb, le=2, deviation=0, bias=0.5, type=0, cbb=0, yhh=10)
            s += list(y['trackArray'])

        else:
            xTrackArray = self._type(type, [start[0], end[0]], number_list)
            for i in xTrackArray:
                s.append([i, fun(i)])
        return s

import math

#this file was written by Zach Peats
#A class used to simulate network traces

class NetworkTrace:


    def __init__(self, bandwidths):

        self.bwlist = bandwidths

    #returns the timesegment the time argument is within
    # 使用最小化函数 min 查找 bwlist 中与 cur_time 最接近的时间段
    # 其中 key 表达式计算每个时间段与 cur_time 的时间差
    # 如果 cur_time 在该时间段之后，返回时间差的绝对值
    # 如果 cur_time 在该时间段之前，返回无穷大 (math.inf)，
    # 从而确保找到的时间段是 cur_time 所在的或最近的过去的时间段
    def get_current_timesegment(self, cur_time):
        return min(self.bwlist, key= lambda x: abs(x[0] - cur_time) if cur_time > x[0] else math.inf )


    # 模拟从指定时间点开始下载指定大小的数据所需的时间
    # 输入参数 time 是开始下载的时间，size 是下载的数据大小（单位为字节）
    # 返回值是完成下载所需的总时间
    def simulate_download_from_time(self, time, size):

        cum_time = 0
        timeseg = self.get_current_timesegment(time)

        while(1):
            #find when next bw change is
            next_set = None
            try:
                #是的，Python 的列表（list）确实支持使用 .index(element) 这种用法来查找元素在列表中的位置。
                #.index(element) 方法的功能 
                #作用：.index(element) 方法用于返回指定元素在列表中第一次出现的索引位置。
                #语法：
                #list.index(element, start, end)
                #element：要查找的元素。
                #start（可选）：查找的起始位置（包含该位置）。
                #end（可选）：查找的结束位置（不包含该位置）。
                #返回值：如果列表中找到了这个 element，返回它的索引（即它在列表中的位置，从 0 开始）。
                #错误：如果没有找到该元素，Python 会抛出一个 ValueError，表示该元素不在列表中。

                next_set = self.bwlist[ self.bwlist.index(timeseg) + 1 ]
            except( IndexError ):
                pass

            #if no next bw change, calculate the remaining time
            if not next_set:
                cum_time += size / (timeseg[1] / 8)
                return cum_time

            #find time remaining on current bw, drain download by corresponding amt
            down_time = next_set[0] - time
            cum_time += down_time
            size -= down_time * (timeseg[1] / 8)

            if size <= 0:
                #refund unused time
                unused_time = -1 * size / (timeseg[1] / 8)
                cum_time -= unused_time
                return cum_time

            timeseg = next_set
            time = timeseg[0]


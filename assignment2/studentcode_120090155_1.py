import math
# {"Measured Bandwidth": 得到网络文件中当前时间最近的时间戳中的带宽信息，比如500000.0
# "prev_throughput": 之前的吞吐量，表明下载上一个chunk时的网络带宽，是一个数字，单位是bit/s
# "Buffer Occupancy" : 用户当前缓存是什么样的，如：
#                                                     # {
#                                                     #   "size":总的buffersize,
#                                                     #   "current":当前buffer中所有块的总size,
#                                                     #   "time":当前buffer中所有块的总time，
#                                                     # }
#"Available Bitrates": 当前chunk的一些信息，如：
#                                                         #（bitrate：size）
#                                                         # {
#                                                         #     500000: 126029, 
#                                                         #     1000000: 244250,
#                                                         #     5000000: 1259637
#                                                         # }
#"Video Time" : 当前时间，是一个数字
#"Chunk" : 当前chunk的一些信息如： # params = {  "left" : 30,
#                                        #     "time" :2,
#                                        #     "current" : 0
#                                        #  }
#"Rebuffering Time" : 上一个chunk在被下载的时候播放器挂空挡的持续时间
#"Preferred Bitrate" : #偏好的bitrate，是一个数字
#"exit" : 0})


# BOLA-BASIC 算法实现，提供一个入口点函数供 studentComm.py 调用。


def student_entrypoint(measured_bandwidth, prev_throughput, buffer_occupancy, available_bitrates, video_time, chunk, rebuffering_time, preferred_bitrate):
    # BOLA 参数初始化
    gamma = 5  # 调整流畅度和效用的平衡
    V = 100  # 效用权重，控制效用和缓冲之间的平衡

    # 获取缓冲区最大容量（字节），并将其转换为秒（假设以最低比特率填充）
    Q_max_bytes = buffer_occupancy["size"]  # 缓冲区最大容量（字节）
    lowest_bitrate = min([int(bitrate) for bitrate in available_bitrates])  # 获取最低的比特率（bps）
    Q_max = Q_max_bytes / (lowest_bitrate / 8)  # 用时间来描述Q_max
    
    Q_target = 0.9 * Q_max  # 目标缓冲区大小，通常设置为最大缓冲区的 90%
    Q_low = min(0.1 * Q_max, 10)  # 设置低阈值（通常是 Q_max 的 10% 或 10 秒）

    # 将可用比特率列表转换为有序的从低到高的整数列表
    sorted_bitrates = sorted([int(bitrate) for bitrate in available_bitrates])

    # 当前缓冲区状态
    buffer_level = buffer_occupancy["time"]  # 当前缓冲区时间（单位为秒）

    # 计算缓冲区效用，用于决定当前比特率的优先级
    def calculate_bola_score(bitrate, buffer_level):
        # 根据文献中的公式计算效用和缓冲安全因子
        utility = V * math.log(bitrate / sorted_bitrates[0])  # 计算比特率的效用值
        safety_factor = gamma * (buffer_level - Q_target)  # 安全因子，确保缓冲区在目标容量附近
        return utility + safety_factor  # BOLA 效用得分公式

    # 当前选择的默认比特率为最低比特率，以保证加载的安全性
    chosen_bitrate = sorted_bitrates[0]

    # 选择最优比特率
    max_score = float('-inf')
    for bitrate in sorted_bitrates:
        bola_score = calculate_bola_score(bitrate, buffer_level)
        if bola_score > max_score:
            max_score = bola_score
            chosen_bitrate = bitrate

    # 防止比特率切换过于频繁（仅在缓冲不足且之前的吞吐量低于所选比特率时降级）
    if prev_throughput < chosen_bitrate and buffer_level < Q_low:
        chosen_bitrate = sorted_bitrates[0]

    return chosen_bitrate  # 返回学生算法选择的比特率
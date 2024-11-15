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

# BOLA-BASIC 算法实现
def student_entrypoint(measured_bandwidth, prev_throughput, buffer_occupancy, available_bitrates, video_time, chunk, rebuffering_time, preferred_bitrate):
    # BOLA 参数初始化
    gamma = 5  # 调整流畅度和效用的平衡因子

    # 获取可用比特率及其对应的段大小
    sorted_bitrates = sorted(available_bitrates.items())  # 获取升序排列的比特率和段大小

    S1 = sorted_bitrates[0][1]  # 最低比特率对应的段大小 (bytes)
    S2 = sorted_bitrates[1][1]  # 第二低比特率对应的段大小 (bytes)
    SM = sorted_bitrates[-1][1] # 最大比特率对应的段大小（bytes）

    Q_max = buffer_occupancy["size"] / S1  # 计算缓冲区中可以容纳的段数

    Q_target = 0.9 * Q_max  # 目标缓冲区大小，通常设置为最大缓冲区的 90%
    Q_low = min(0.1 * Q_max, 10)  # 设置低阈值（通常是 Q_max 的 10% 或 10 秒）

    # 使用文献中关于参数选择的公式来计算 V 和 gamma_p
    v1 = 0.0  # 最低效用值，v1 = ln(S1/S1) = 0
    v2 = math.log(S2 / S1)  # 第二低效用值，v2 = ln(S2/S1)，通常为 ln(2)

    alpha = (S1 * v2 - S2 * v1) / (S2 - S1)  # 计算 alpha 值

    V = (Q_max - Q_low) / (v2 - alpha)  # 计算 V 的值
    gamma_p = (v2 * Q_low - alpha * Q_max) / (Q_max - Q_low)  # 计算 gamma_p 的值


    # 当前选择的默认比特率为最低比特率，以保证加载的安全性
    chosen_bitrate = sorted_bitrates[0][0]

    max_index = 0
    max_value = float('-inf')
    indicator_of_can_I_download_any_chunk=0  
    # if this value at the end is still zero, 
    # it means bola-basic algorithm suggests us not to download any chunk and wait for while
    for index, (key, value) in enumerate(available_bitrates.items(), start=0):
        Q= (buffer_occupancy["time"])/chunk["time"] # 当前缓冲区中的段数
        t=video_time #当前时间，是一个数字
        t_hat=max(t/2,3*chunk["time"]) #使用文献公式
        Q_max_hat=min(Q_max, t_hat/chunk["time"]) #使用文献公式
        S_index=sorted_bitrates[index][1] #使用文献公式，S_index是从小到大第index个chunk_size
        v_index=math.log(S_index/S1) #使用文献公式
        V_hat=(Q_max_hat-1)/(v_index+gamma_p) #使用文献公式
        if Q < V_hat * (v_index + gamma_p): #使用文献公式
            indicator_of_can_I_download_any_chunk=1
        if ((V_hat*v_index + V_hat*gamma_p - Q)/S_index) >0: 
            # according to 文献， here find the index that maximizes the ratio 
            # (V_hat*v_index + V_hat*gamma_p - Q)/S_index
            # among all m for which this ratio is positive.
            if ((V_hat*v_index + V_hat*gamma_p - Q)/S_index) > max_value:
                max_value = ((V_hat*v_index + V_hat*gamma_p - Q)/S_index)
                max_index=index        
    if indicator_of_can_I_download_any_chunk==0:
        # this means according to bola-basic algorithm, suggests us 
        # not to download any chunk and pause the playback and
        # wait for while and then redownload
        # but what is very pity is in this assignment we are not allowed to choose "not download any chunk" 
        # why this is not allowed in this assignment?: because the design of "simulator.py"
        # doesn't allow us to return a "pause for awhile". If you still dont understand it, go check simulator.py
        # the only way for me to simulate this behavior is just choosing the least bitrate chunk
        # that is the best I can do to simulate the behavior of bola-basic in this case.
        chosen_bitrate=sorted_bitrates[0][0]
    else:
        chosen_bitrate= sorted_bitrates[max_index][0]



  
    # # 当前缓冲区状态
    # buffer_level = buffer_occupancy["time"] / chunk["time"]  # 当前缓冲区中的段数
    # # 防止比特率切换过于频繁（仅在缓冲不足且之前的吞吐量低于所选比特率时降级）
    # if prev_throughput < chosen_bitrate and buffer_level < Q_low:
    #     chosen_bitrate = sorted_bitrates[0][0]

    return chosen_bitrate  # 返回学生算法选择的比特率

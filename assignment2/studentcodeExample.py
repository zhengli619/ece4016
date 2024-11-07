#Written by Nathan A-M =^)
#Buffer-based implementation using 
#A Buffer-based approach as a reference 

bitrate = 0 #used to save previous bitrate

def student_entrypoint(Measured_Bandwidth, Previous_Throughput, Buffer_Occupancy, Available_Bitrates, Video_Time, Chunk, Rebuffering_Time, Preferred_Bitrate ):
    #student can do whatever they want from here going forward
    global bitrate
    R_i = list(Available_Bitrates.items())
    R_i.sort(key=lambda tup: tup[1] , reverse=True)
    bitrate = bufferbased(rate_prev=bitrate, buf_now= Buffer_Occupancy, r=Chunk['time']+1,R_i= R_i ) 
    return bitrate

#helper function, to find the corresponding size of previous bitrate
def match(value, list_of_list): 
    for e in list_of_list:
        if value == e[1]:
            return e
            
#helper function, to find the corresponding size of previous bitrate
#if there's was no previous assume that it was the highest possible value
def prevmatch(value, list_of_list): 
    for e in list_of_list:
        if value == e[1]:
            return e
    value = max(i[1] for i in list_of_list)
    for e in list_of_list:
        if value == e[1]:
            return e
        



def bufferbased(rate_prev, buf_now, r, R_i , cu = 126):
    '''
    Input: 
    rate_prev: The previously used video rate
    Buf_now: The current buffer occupancy 
    r: The size of reservoir  //At least greater than Chunk Time
    cu: The size of cushion //between 90 to 216, paper used 126
    R_i: Array of bitrates of videos, key will be bitrate, and value will be the byte size of the chunk
    
    Output: 
    Rate_next: The next video rate
    '''
    
    R_max = max(i[1] for i in R_i)
    R_min = min(i[1] for i in R_i)
    # R_max 和 R_min 分别是 R_i 列表中的最大和最小分块大小。
    # 举例：    R_i = [
    #     (5000000, 1259637),  # 比特率为 5000000，分块大小为 1259637 字节
    #     (1000000, 244250),   # 比特率为 1000000，分块大小为 244250 字节
    #     (500000, 126029)     # 比特率为 500000，分块大小为 126029 字节
    # ]
    # R_max=1259637
    # R_min=126029
    rate_prev = prevmatch(rate_prev,R_i)
    #rate_prev现在是一个（5000000，1259637）样子的元组

    #set rate_plus to lowest reasonable rate
    # 将要选择的“略高于之前比特率”的可用比特率分块大小。
    # 如果当前比特率已经是最高可用比特率 R_max，则将 rate_plus 设为 R_max，因为没有更高的比特率可选。
    if rate_prev[1] == R_max:
        rate_plus = R_max
    else:
        # 如果当前比特率不是最高可用比特率，则尝试找到一个比当前比特率稍高的比特率。
        # more_rate_prev 是一个列表，包含了所有比 rate_prev[1] 更大的分块大小。这些分块大小是在 R_i 中的值（R_i 是比特率和对应分块大小的列表）。
        more_rate_prev = list(i[1] for i in R_i if i[1] > rate_prev[1])
        # 如果 more_rate_prev 是空的，表示没有比当前比特率更高的可选比特率，因此将 rate_plus 保持为当前比特率。
        # 如果 more_rate_prev 不是空的，说明存在更高的比特率，取其中最小的那个作为 rate_plus。这样可以在提升比特率时保持平滑，而不是直接跳到很高的比特率。
        if more_rate_prev == []:
            rate_plus = rate_prev[1]
        else: 
            rate_plus = min(more_rate_prev)
        
    #set rate_min to highest reasonable rate
    if rate_prev[1] == R_min:
        rate_mins = R_min
    else:
        less_rate_prev= list(i[1] for i in R_i if i[1] < rate_prev[1])
        if less_rate_prev == []:
            rate_mins = rate_prev[1]
        else: 
            rate_mins = max(less_rate_prev)


    
    #Buffer based Algorithm 
    if buf_now['time'] <= r: #1st check if buffer time is too small, set to R_min
        rate_next = R_min #如果buffer甚至小于两秒
        rate_next = match(R_min, R_i)[0]#在缓冲区时间接近耗尽的情况下，最重要的是快速下载下一个分块，以避免播放卡顿。
    elif buf_now['time'] >= (r + cu):  #too big, set R_max
        rate_next = R_max #如果buffer很满，选最大size的chunk
        rate_next = match(R_max, R_i)[0] 

    elif buf_now['current'] >= rate_plus: #check if big enough get a different reasonable rate
        #buf_now['current']是buffer中chunks总size
        #rate_plus 是“略高于之前比特率”的可用比特率分块大小
        #如果chunks总size比rate_plus大，那么：
        less_buff_now= list(i[1] for i in R_i if i[1] < buf_now['current'])
        if less_buff_now == []:
            #如果chunks总size比所有的可选分块的size都小
            rate_next = rate_prev[0]
        else: 
            rate_next = max(less_buff_now)
            rate_next = match(rate_next, R_i)[0]
    elif buf_now['current'] <= rate_mins: #check if small enough for a different reasonable rate
        more_buff_now= list(i[1] for i in R_i if i[1] > buf_now['current'])
        if more_buff_now == []:
            rate_next = rate_prev[0]
        else: 
            rate_next = min(more_buff_now)
            rate_next = match(rate_next, R_i)[0]
    else:
        rate_next = rate_prev[0] #else give up and try again next time

# 这段代码的逻辑是为了调节缓冲区中的数据量，使其既不过多（以免浪费带宽或造成不必要的等待），也不过少（以免导致播放卡顿）。
# 具体来说，这段代码通过动态选择比特率来平衡缓冲区数据量，确保播放体验的平滑和稳定。
# 判断缓冲区是否足够满（buf_now['current'] >= rate_plus）：

# 如果缓冲区内数据的总大小已经比 rate_plus（略高于前一次比特率的分块大小）大，意味着缓冲区比较充裕，播放过程短期内不会出现卡顿。
# 这时代码会寻找一个略低的合理比特率，避免缓冲区继续增长，以更好地平衡带宽利用。
# 判断缓冲区是否足够少（buf_now['current'] <= rate_mins）：

# 如果缓冲区内的数据总大小小于或等于 rate_mins，意味着缓冲区接近耗尽，可能出现播放中断的风险。
# 在这种情况下，代码会寻找一个稍高的比特率，以便增加数据输入，提升缓冲区的储备，避免播放过程中的卡顿。
# 默认保持前一次比特率：

# 如果以上条件均不满足，则说明缓冲区的填充状态适中，不需要调整比特率，直接保持上一次的比特率。
# 逻辑目标：平衡缓冲区
# 避免缓冲区太满：如果缓冲区太满（比 rate_plus 大），则可以选择更低的比特率，减少带宽消耗并控制缓冲区占用。
# 避免缓冲区太少：如果缓冲区太少（比 rate_mins 小），则可以选择略高的比特率，快速填充缓冲区，防止播放卡顿。

    return rate_next
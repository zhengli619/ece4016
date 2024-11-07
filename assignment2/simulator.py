import sys
import json
from Classes import SimBuffer, NetworkTrace, Scorecard, simulator_comm

#this file was written by Zach Peats
#This is the video download and playback simulator for an ABR algorithm lab.
#The program simulates a video stream over a network, using a network trace and a video manifest
#for more information regarding usage and file specifications, check out the readme



verbose = False


def loadtrace(tracefile):#从 tracefile 中读取网络带宽变化，并将其存储在 tracelog 列表中，随后实例化 NetworkTrace 类，用于管理追踪数据。
#返回值：NetworkTrace 对象，包含带宽追踪数据。

    with open(tracefile, 'r',encoding='utf-8') as infile:
        lines = infile.readlines()

    tracelog = []

    for line in lines:
        splitline = line.split(' ')
        if len(splitline) > 1:
            try:
                tracelog.append((float(splitline[0]), float(splitline[1])))

            except ValueError as e:
                print("Your trace file is poorly formed!")

    trace = NetworkTrace.NetworkTrace(tracelog)#创建一个NetworkTrace类的对象trace，并且用tracelog初始化
    
# 假设 lines 内容为：
#      lines = [
#     "0 5000000\n",
#     "15 1000000\n",
#     "30 100000\n",
#     "40 1000000\n",
#     "60 5000000\n"
#     ]
# 执行后的 tracelog 列表将是：

# [
#     (0.0, 5000000.0),
#     (15.0, 1000000.0),
#     (30.0, 100000.0),
#     (40.0, 1000000.0),
#     (60.0, 5000000.0)
# ]

    return trace





def loadmanifest(manifestfile):

# 假设 manifestfile 的内容如下：

# json

# {
#     "Video_Time": 60,
#     "Chunk_Count": 30,
#     "Chunk_Time": 2,
#     "Buffer_Size": 40000000,
#     "Available_Bitrates": [
#         500000,
#         1000000,
#         5000000
#     ],
#     "Preferred_Bitrate": "5000000",
#     "Chunks": {
#         "0": [126029, 244250, 1259637],
#         "1": [125208, 247724, 1239555],
#         "2": [125784, 252524, 1247158]
#     }
# }
# 在这种情况下，lines 的内容将是一个字符串，类似于：


# lines = '''{
#     "Video_Time": 60,
#     "Chunk_Count": 30,
#     "Chunk_Time": 2,
#     "Buffer_Size": 40000000,
#     "Available_Bitrates": [
#         500000,
#         1000000,
#         5000000
#     ],
#     "Preferred_Bitrate": "5000000",
#     "Chunks": {
#         "0": [126029, 244250, 1259637],
#         "1": [125208, 247724, 1239555],
#         "2": [125784, 252524, 1247158]
#     }
# }'''

# 2. manifest 的内容
# json.loads(lines) 会将 lines 中的 JSON 字符串解析为一个 Python 字典（dict），并将该字典赋值给 manifest。
# 所以，manifest 的内容将是一个字典，类似于：

# python
# manifest = {
#     "Video_Time": 60,
#     "Chunk_Count": 30,
#     "Chunk_Time": 2,
#     "Buffer_Size": 40000000,
#     "Available_Bitrates": [500000, 1000000, 5000000],
#     "Preferred_Bitrate": "5000000",
#     "Chunks": {
#         "0": [126029, 244250, 1259637],
#         "1": [125208, 247724, 1239555],
#         "2": [125784, 252524, 1247158]
#     }
# }

    with open(manifestfile, 'r', encoding='utf-8') as infile:
        lines = infile.read()

    manifest = json.loads(lines)
    return manifest





def prep_bitrates(available_rates, chunk):
    rates = dict(map(lambda x, y: (x, y), available_rates, chunk))
    return rates
# map(function, *iterables)。function 是应用于每组元素的函数，iterables 是可迭代对象。
# 这里，map() 会将 lambda x, y: (x, y) 函数应用于 available_rates 和 chunk 中的元素。
# dict() 函数将这些 (x, y) 元组转换为字典格式
# 假设 available_rates = [500000, 1000000, 5000000]，chunk = [126029, 244250, 1259637]，那么返回的 rates 字典将如下：

# python
# {
#     500000: 126029,
#     1000000: 244250,
#     5000000: 1259637
# }





def prep_chunk(chunks_rem, manifest, chunk_num):
    params = {  "left" : chunks_remaining,
                "time" : manifest["Chunk_Time"],
                "current" : chunk_num
                }
    return params


if __name__ == "__main__":

    #check arguments for relevant flags
    if "-v" in sys.argv or "--verbose" in sys.argv:
        verbose = True


    #Load in network trace from input file
    trace = loadtrace(sys.argv[1]) #所以第二个参数是一个tracefile，第一个参数一般是这个本身py文件的名字，也就是simulator

    #read video manifest
    manifest = loadmanifest(sys.argv[2])

    #create scorecard for logging
    logger = Scorecard.Scorecard(1, 1, 1)

    #simulator setup

    buffer = SimBuffer.SimBuffer(manifest["Buffer_Size"])
    #比如说"Buffer_Size": 40000000,把40000000给了simbuffer.py

    chunks_remaining = manifest["Chunk_Count"] #比如说30
    current_time = 0  #现在的时间戳
    prev_throughput = 0  #之前的吞吐量
    rebuff_time = 0  #还没缓冲过
    pref_bitrate = manifest["Preferred_Bitrate"]#获取偏好的bitrate

    stu_chunk_size = None  #还不知道是什么

    chunk_list = [(key, value) for key, value in manifest["Chunks"].items()]
    #等价代码： list(manifest["Chunks"].items())
    #manifest["Chunks"]是一个字典，比如
    #     manifest = {
    #     "Chunks": {
    #         "0": [126029, 244250, 1259637],
    #         "1": [125208, 247724, 1239555],
    #         "2": [125784, 252524, 1247158]
    #     }
    # }
    # manifest["Chunks"].items() 会返回一个键值对的视图对象，其中每个元素是一个 (key, value) 形式的元组
    #比如：
    #   dict_items([
    #     ('0', [126029, 244250, 1259637]),
    #     ('1', [125208, 247724, 1239555]),
    #     ('2', [125784, 252524, 1247158])
    # ])
    #为什么要这么写？：如果直接写chunk_list = manifest["Chunks"]的话
    #生成的结果是对原始 manifest["Chunks"] 字典的一个引用，
    #直接指向 manifest["Chunks"] 的数据。也就是说，chunk_list 和 manifest["Chunks"] 其实指向的是同一份数据
    #必须用.items()吗？是的，因为：直接对字典进行迭代哪怕使用for key, value也只能得到key吗？
    #最终，chunk_list 将包含所有分块信息的元组列表：
    # chunk_list = [
    #     ('0', [126029, 244250, 1259637]),
    #     ('1', [125208, 247724, 1239555]),
    #     ('2', [125784, 252524, 1247158])
    # ]



    chunk_iter = chunk_list.__iter__()

     #Communication loop with student (for all chunks):

    chunknum, chunk = next(chunk_iter, None)
    #chunknum代表了这是第几个chunk
    # 为什么要用迭代器和 next()？
    # 使用迭代器和 next() 可以按需逐个获取元素，这样在需要时才会请求下一个元素，而不必一次性读取所有内容。
    # 这是实现逐块下载和处理的核心操作，方便在处理完一个块后再获取下一个块。

    
    #while chunk这句话前面的这些行就是在提取manifest的各种信息，提取trace的各种信息
    #然后顺带把一些变量初始化为0
    while chunk:
        #calculate and pack info to be sent to student
        # todo ensure input types are correct

        m_band = trace.get_current_timesegment(current_time)[1]
        #得到网络文件中当前时间最近的时间戳中的带宽信息，告诉我们用户现在网络是什么情况
        buf_occ = buffer.get_student_params()
        #得到一个字典，告诉了我们用户现在缓存是什么情况{
        #   "size":总的buffersize,
        #   "current":当前buffer中所有块的总size,
        #   "time":当前buffer中所有块的总time，
        # }
        av_bitrates = prep_bitrates(manifest["Available_Bitrates"],chunk)
        #告诉我们当前chunk的一些信息
        # 于是av_bitrates是如下字典：
        # {
        #     500000: 126029,
        #     1000000: 244250,
        #     5000000: 1259637
        # }
        chunk_arg = prep_chunk(chunks_remaining, manifest, chunknum)
        #告诉我们当前chunk的一些信息
        # chunknum是这是第几个chunk，传递给current的值
        # manifest中的Chunk_Time，也就是2会被读取，作为time的值
        # chunks_remaining一开始是30，也就是chunk总数，后来逐渐减少，作为left的值
        # params = {  "left" : 30,
        #             "time" :2,
        #             "current" : 0
        #          }




        #send info to student, get response
        chosen_bitrate = simulator_comm.send_req_json(m_band, prev_throughput, buf_occ, av_bitrates, current_time, chunk_arg, rebuff_time, pref_bitrate)
        #返回由学生实现的算法文件（如 studentcodeExample.py）决定的比特率

        #bad response checking, ensure chunk fits in buffer
        try:
            stu_chunk_size = av_bitrates[int(chosen_bitrate)]
        except( KeyError ):
            print("Student returned invalid bitrate, exiting")
            break

        if stu_chunk_size > buffer.available_space():
            #chunk chosen does not fit in buffer, wait .5s and resend request
            buffer_time = buffer.burn_time(.5)
            current_time += .5
            continue #重新再来一次让学生算法选择合适的bitrate，合适的chunksize


        logger.log_bitrate_choice(current_time, chunknum, (chosen_bitrate, stu_chunk_size))

        #simulate download and playback
        time_elapsed = trace.simulate_download_from_time(current_time, stu_chunk_size)

        #round time to remove floating point errors
        #todo: this did not fix them
        time_elapsed = round(time_elapsed, 3)

        rebuff_time = buffer.sim_chunk_download(stu_chunk_size, chunk_arg["time"], time_elapsed)
        #下载时间是time_elapsed,这个过程中缓冲区可能空了，导致这一段时间播放器什么都放不出来，这里返回播放器空的时间
        
        #update state variables
        prev_throughput = (stu_chunk_size * 8) / time_elapsed
        current_time += time_elapsed
        chunks_remaining -= 1

        logger.log_rebuffer(current_time - rebuff_time, rebuff_time)
        #log actions



        #get next chunk
        chunknum, chunk = next(chunk_iter, (None, None))


    #cleanup and return
    simulator_comm.send_exit()

    if(verbose):
        logger.output_verbose()
    else:
        logger.output_results()
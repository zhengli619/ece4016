import socket
import json
import time

# Cut-the-corners TCP Client:
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_CLOEXEC)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.connect(('localhost', 6000))
#connect() 的作用
# connect() 用于建立一个面向连接的 TCP 会话。通过调用 connect()，客户端和服务器之间会建立一个可靠的连接通道。
# 一旦连接建立，客户端就不需要在每次发送数据时都指定服务器的 IP 和端口（例如 sendto(data, (ip, port)) 里必须指定 IP 和端口），
# 因为 connect() 已经明确指定了通信的目标。
# 通过 connect()，可以使用 send() 和 recv() 进行数据传输，这些方法提供了流式、面向连接的通信方式，确保了数据的顺序和可靠性。
# 2. 与sendto() 和 recvfrom() 的区别
# sendto() 和 recvfrom() 常用于无连接的 UDP 协议，允许每次发送时都指定目标 IP 和端口，因此更灵活。
# 由于没有建立连接，sendto() 和 recvfrom() 没有建立可靠的通道，因此无法保证数据包的顺序或送达。如果需要可靠传输，通常需要额外的逻辑处理。
# 在 TCP 使用场景中，虽然 sendto() 和 recvfrom() 也可以在连接后使用，但不常见，且使用时不会带来流式通信的优势。


def send_req_json(m_band, prev_throughput, buf_occ, av_bitrates, current_time, chunk_arg, rebuff_time, pref_bitrate ):

#pack message
#JSON（JavaScript Object Notation）是一种轻量级的数据交换格式，常用于在网络上进行数据传输。JSON 格式具有可读性好、兼容性强等优点，因此广泛用于服务器和客户端之间的数据传递。
# json.dumps() 是将 Python 数据结构（如字典、列表等）转换为 JSON 格式字符串的函数。在代码中：
#将包含多个键值对的 Python 字典转换成 JSON 格式字符串，并将其存储在 req 变量中。例如，假设传入的值如下：
# m_band = 5000
# prev_throughput = 4500
# buf_occ = 2000
# av_bitrates = [1000, 2000, 3000]
# current_time = 120
# chunk_arg = 5
# rebuff_time = 0
# pref_bitrate = 2000
# 调用 json.dumps 后，req 的内容将是这样的 JSON 字符串：
# {
#   "Measured Bandwidth": 5000,
#   "Previous Throughput": 4500,
#   "Buffer Occupancy": 2000,
#   "Available Bitrates": [1000, 2000, 3000],
#   "Video Time": 120,
#   "Chunk": 5,
#   "Rebuffering Time": 0,
#   "Preferred Bitrate": 2000,
#   "exit": 0
# }
    req = json.dumps({"Measured Bandwidth" : m_band, #用户当前时间戳中的带宽信息
                     "Previous Throughput" : prev_throughput,#之前的吞吐量，在simulator.py中一开始被初始化为0
                     "Buffer Occupancy" : buf_occ, #用户当前缓存是什么样的
                                                    # {
                                                    #   "size":总的buffersize,
                                                    #   "current":当前buffer中所有块的总size,
                                                    #   "time":当前buffer中所有块的总time，
                                                    # }
                     "Available Bitrates" : av_bitrates, #当前chunk的一些信息，是如下字典：
                                                        #（bitrate：size）
                                                        # {
                                                        #     500000: 126029, 
                                                        #     1000000: 244250,
                                                        #     5000000: 1259637
                                                        # }
                     "Video Time" : current_time,#当前时间戳
                     "Chunk" : chunk_arg,#当前chunk的一些信息 # params = {  "left" : 30,
                                                            #             "time" :2,
                                                            #             "current" : 0
                                                            #          }
                     "Rebuffering Time" : rebuff_time, #simulator.py中初始化一开始是0
                     "Preferred Bitrate" : pref_bitrate,#偏好的bitrate
                     "exit" : 0})
    # 此 req 请求是通过流式传输（如 TCP 套接字）发送的，接收方可能需要用换行符来区分每一条完整的消息。
    # 换行符作为消息的结束标志，帮助接收方准确识别每一条独立的 JSON 消息。
    req += '\n'

    s.sendall(req.encode()) #sendall() 方法会确保所有字节都被成功发送。与 send() 不同，
    #sendall() 会在网络不稳定时自动重试，直到所有数据被完全发送，
    #监听 6000 端口的服务（服务器）将接收 simulator_comm.py 发送的数据。

    message = ""
    while(1):
        messagepart = s.recv(2048).decode()

        #print(messagepart)
        message += messagepart
        if message[-1] == '\n':
            #print(message)

            response = json.loads(message)

            return response["bitrate"]
            # 返回由学生实现的算法文件（如 studentcodeExample.py）决定的比特率
            # simulator.py 接收到 studentComm.py 返回的 bitrate 后，
            # 会在模拟器中应用这个比特率，继续模拟视频播放过程。
def send_exit():#simulator.py中发完所有的chunk，会调用这个函数
    req = json.dumps({"exit" : 1})

    req += '\n'
    s.sendall(req.encode())


if __name__ == "__main__":
    pass

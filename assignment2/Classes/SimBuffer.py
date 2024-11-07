
#this file was written by Zach Peats
#A class that represents the video playback buffer.

class SimBuffer:

    def __init__(self, bufsize):
        self.size = bufsize #总的buffer size
        self.chunks = [] #each chunk object is a tuple (size, chunk_time)
        self.time = 0 #当前buffer中所有块的总time
        self.cur_size = 0 #当前buffer中所有块的总size
        self.mid_chunk_time = 0


    def get_student_params(self): 
        params = {}
        params["size"] = self.size
        params["current"] = self.cur_size
        params["time"] = self.time
        return params

    def available_space(self): #buffer中还没被块占据的size
        return self.size - self.cur_size
    
    

    def sim_chunk_download(self, chunk_size, chunk_time, playback_time):
        if chunk_size > self.size - self.cur_size:  #当前的chunk能不能fit in进来
            print("Error: Chunk being added is too large to fit into buffer")
            return False

        buffer_time = self.sim_playback(playback_time)#播放playback_time时长，耗chunks，看耗完之后整个buffer会处于没有任何缓冲块状态多少秒

        self.chunks.append((chunk_size,chunk_time)) #把当前的chunk加进chunks队尾
        self.calculate_occupancy() #刷新块总大小
        self.calculate_time() #刷新块总时长
        return buffer_time #返回耗完buffer之后整个buffer会处于没有任何缓冲块状态多少秒
    


    def calculate_occupancy(self):#刷新当前buffer中所有块的总大小
        self.cur_size = 0
        for chunk in self.chunks:
            self.cur_size += chunk[0]


    def burn_time(self, time):
        buffer_time = self.sim_playback(time) #播放time这么长时间，耗掉一部分chunks，返回耗完之后整个buffer会处于没有任何缓冲块状态多少秒
        self.calculate_occupancy()# 刷新所有块的总大小
        self.calculate_time()#刷新所有块的总时长
        return buffer_time#返回耗完之后整个buffer会处于没有任何缓冲块状态多少秒
    



    def sim_playback(self, playback_time): #输入一个playback_time，他会耗掉一部分buffer中的chunk，
                                            #输出的是耗完之后整个buffer会处于没有任何缓冲块状态多少秒
                                            #比如说buffer耗完了，还剩一段时间。 
                                            #0就代表了现存buffer中的chunks足够耗掉所有的playback_time，也就是不存在缓冲区是空的的状态
                                            
        while playback_time > 0:

            #if there are any chunks to be played
            if self.chunks:
                current_chunk = self.chunks.pop(0)

                chunk_time_remaining = current_chunk[1]#会删除并返回第一个元素

                playback_time -= chunk_time_remaining

                if playback_time < 0:
                    chunk_time_remaining = -1 * playback_time
                    self.chunks.insert(0, (current_chunk[0], chunk_time_remaining))
                    return 0


            #no chunks left to be played, buffering
            else:
                return playback_time

        #all playback was simulated, return 0 buffer time
        return 0
    



    def calculate_time(self):#刷新当前buffer中所有块的总time

        totaltime = 0
        for chunk in self.chunks:
            totaltime += chunk[1]

        self.time = totaltime
        return
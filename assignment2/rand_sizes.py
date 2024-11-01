import numpy as np
import json

CHUNK_TIME = 2
NUM_OF_CHUNKS = 30
low_BR = 500000
med_BR = 1000000
high_BR = 5000000
Buffer_Size = 40000000

# generate random chunk sizes for the manifest, WIP
low = np.random.normal(low_BR / 8, 5000 / 8, NUM_OF_CHUNKS) * CHUNK_TIME
med = np.random.normal(med_BR / 8, 10000 / 8, NUM_OF_CHUNKS) * CHUNK_TIME
high = np.random.normal(high_BR / 8, 50000 / 8, NUM_OF_CHUNKS) * CHUNK_TIME

data = {}
data['Video_Time'] = NUM_OF_CHUNKS * CHUNK_TIME
data['Chunk_Count'] = NUM_OF_CHUNKS
data['Chunk_Time'] = CHUNK_TIME
data['Buffer_Size'] = Buffer_Size
data['Available_Bitrates'] = [low_BR, med_BR, high_BR]
data['Chunks'] = {}

for i in range(30):
    data['Chunks'][str(i)] = [
        int(low[i]),
        int(med[i]),
        int(high[i])
    ]

print(json.dumps(data, indent=4))
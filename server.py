import asyncio
from funasr import AutoModel
import json
from datetime import datetime

MAX_CHUNK_SIZE = 3200
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2

model = AutoModel(model="iic/emotion2vec_base_finetuned", vad_model="fsmn-vad")


def get_most_likely_emotion(data):
    if len(data) == 0:
        return {}
    for entry in data:
        labels = entry['labels']
        scores = entry['scores']
        score_max = 0
        emo_max = ""
        for label, score in zip(labels, scores):
            if score > score_max:
                score_max = score
                emo_max = label
    return {"label": emo_max, "score": score_max}

def get_likely_emotions(data, prob=0.1):
    rt = []
    if len(data) > 0:
        for e in data:
            for l, s in zip(e['labels'], e['scores']):
                if s >= prob:
                    rt.append({'label': l, 'score': s})
    return rt

def get_angry_emotion(data):
    if len(data) == 0:
        return {}

    for entry in data:
        labels = entry['labels']
        scores = entry['scores']
        for label, score in zip(labels, scores):
            if label.endswith("/angry"):
                return {"label": label, "score": score}
    return {}


async def handle_client(reader, writer):
    
    addr = writer.get_extra_info('peername')
    print(f"Connected by {addr}")

    data = bytearray()

    try:
        while True:
            try:
                chunk = await asyncio.wait_for(reader.read(MAX_CHUNK_SIZE), timeout=2.0)
            except asyncio.TimeoutError:
                print("Connection timeout. Closing connection.")
                break
            
            if not chunk:
                print("Connection closed by client.")
                break
            
            data.extend(chunk)
            
            data_len = len(data)
            tick_len = SAMPLE_RATE * SAMPLE_WIDTH
            if data_len >= tick_len * 2: # 2s data detect
                rem = data_len % SAMPLE_WIDTH
                if rem > 0:
                    d = data[:-rem]
                else:
                    d = data
                    
                res = model.generate(bytes(d), output_dir="./outputs", granularity="utterance", extract_embedding=False)
                #print(get_most_likely_emotion(res))
                #print(get_angry_emotion(res))
                print(f'[DEBUG] [{datetime.now()}] data_len: {data_len}; res: {res}')
                res_json = json.dumps(res)
                writer.write(res_json.encode('utf-8')+b"\n")
                await writer.drain()

                if rem > 0:
                    print('[DEBUG] rem for next loop')
                    data = data[-(tick_len+rem):]
                else:
                    data = data[-tick_len:]  # Reset data buffer after processing
    finally:
        writer.close()


async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 8082)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())


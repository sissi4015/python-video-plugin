# 语音合成-----调用火山方舟语音合成大模型V3单向流式
# User: Sissi
# Date: 2025/09/04

import json
from sqlite3 import connect
import uuid
import logging
import websockets


# 用户认证
# 在https://console.volcengine.com/ark/region:ark+cn-beijing/tts/speechSynthesis获取
APPID = "5124948200"
ACCESS_TOKEN = "m-Icda-DQSWULS8t6SRlQNHxqAsWAIe1"
SECRET_KEY = "GelGpw5xKMaoSFiQnN_CpukAiJk9BpkK"

# 表示调用服务的资源信息 ID
""" 
大模型语音合成：
volc.service_type.10029
volc.service_type.10048(并发版)
声音复刻2.0:
volc.megatts.default(字符版)
volc.megatts.concurr(并发版)(不支持声音复刻1.0)
"""
RESOURCE_ID = "volc.service_type.10029"

# 声音类型
# 音色列表https://www.volcengine.com/docs/6561/1257544
VOICE_TYPE = "zh_male_yangguangqingnian_emo_v2_mars_bigtts"
# 业务集群
CLUSTER = "volcano_tts"
# 编码
ENCODING = "wav"
# WebSocket endpoint URL
""" 
V1:
wss://openspeech.bytedance.com/api/v1/tts/ws_binary (V1 单向流式)
https://openspeech.bytedance.com/api/v1/tts (V1 http非流式)
V3:
wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream (V3 wss单向流式)
wss://openspeech.bytedance.com/api/v3/tts/bidirection (V3 wss双向流式)
https://openspeech.bytedance.com/api/v3/tts/unidirectional (V3 http单向流式)
"""
ENDPOINT = "wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream"


# def get_resource_id(voice: str) -> str:
#     if voice.startswith("S_"):
#         return "volc.megatts.default"
#     return "volc.service_type.10029"

async def audio_generate(text: str, audio_file_url: str, audio_flag, timelines) -> str:

    logger = logging.getLogger("video_plugin")
    logger.debug("连接火山方舟语音合成大模型V3...")
    

    # Connect to server
    connect_id = str(uuid.uuid4())
    headers = {
        "X-Api-App-Key": APPID,
        "X-Api-Access-Key": ACCESS_TOKEN,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Connect-Id": connect_id,
    }

    logger.debug(
        f'headers = {{'
        f'"X-Api-App-Key": {APPID}, '
        f'"X-Api-Access-Key": {ACCESS_TOKEN}, '
        f'"X-Api-Resource-Id": {RESOURCE_ID}, '
        f'"X-Api-Connect-Id": {connect_id}'
        f'}}'
    )

    websocket = await websockets.connect(
        ENDPOINT, additional_headers=headers, max_size=10 * 1024 * 1024
    )


    try:
        # Prepare request payload
        request = {
            "user": {
                "uid": str(uuid.uuid4()),
            },
            "req_params": {
                "speaker": VOICE_TYPE,
                "audio_params": {
                    "format": ENCODING,
                    "sample_rate": 24000,
                    "enable_timestamp": True,
                },
                "text": text,
                "additions": json.dumps(
                    {
                        "disable_markdown_filter": False,
                    }
                ),
            },
        }

        # Send request
        from utils.audio_protocols import EventType, MsgType, full_client_request, receive_message
        await full_client_request(websocket, json.dumps(request).encode())

        # Receive audio data
        audio_data = bytearray()
        while True:
            msg = await receive_message(websocket)

            if msg.type == MsgType.FullServerResponse:
                
                if msg.event == EventType.TTSSentenceEnd:
                    # 获取 payload 里的 words 数组
                    words_json = msg.payload.decode('utf-8')
                    words = json.loads(words_json).get("words", [])
                    if words:
                        timelines.extend(words)

                if msg.event == EventType.SessionFinished:
                    break
            elif msg.type == MsgType.AudioOnlyServer:
                audio_data.extend(msg.payload)
            else:
                raise RuntimeError(f"TTS conversion failed: {msg}")

        # Check if we received any audio data
        if not audio_data:
            raise RuntimeError("No audio data received")

        # Save audio file
        # 音频文件地址(口播)
        with open(audio_file_url, "wb") as f:
            f.write(audio_data)

        # 有用！！！不能删！！！
        audio_flag = True
        return audio_data

    finally:
        await websocket.close()

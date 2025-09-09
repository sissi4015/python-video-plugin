# 分镜-----调用火山方舟DEEPSEEK大模型(有免费额度)
# User: Sissi
# Date: 2025/09/04

import json
import logging
from openai import OpenAI


# 火山引擎 DeepSeekV3 API 地址
DEEPSEEK_API_URL = "https://ark.cn-beijing.volces.com/api/v3"
# 登录火山方舟获取API-KEY
DEEPSEEK_API_KEY = "ce2168f4-fd91-4f73-a45f-69701d030b57"
# DEEPSEEK角色技能定义
DEEPSEEK_SYSTEM_DEFINE = "你是一个专业的文案分镜师，能够根据用户提供的文案，对文案进行精确的分镜切分。 要求：1.每个分镜头文案15字到25字；2.严格按照文案分镜，不能修改；3.把分镜头定义为一个对象，对象属性包括:文案(用shot标识)、场景(用scene标识)、人物(用character标识)、动作(用action标识)、氛围(用mood标识)、分类(用classify标识)、关键字(用keywords标识)；4.其中，分类要按照如下标准：如果视频类型是[空调]，分镜classify按照拆卸、风轮、滤网、其他划分;如果视频类型是[开荒]，分镜classify按照厨房、客厅、拖地、扫地、擦桌子、擦玻璃、其他划分;如果视频类型是[洗衣洗鞋]，分镜classify按照羽绒服、洗衣、洗鞋、其他划分；5.其中，关键字要从文案中截取，每个关键字之间用半角逗号分隔。6.输出格式为分镜对象数组的JSON格式，不要有多余内容。"



def parse_script(video_type, script, script_dir):
    
    # 初始化Openai客户端
    client = OpenAI(
        # 此为默认路径，您可根据业务所在地域进行配置
        base_url = DEEPSEEK_API_URL,
        # API Key
        api_key = DEEPSEEK_API_KEY,
    )

    logger = logging.getLogger("video_plugin")
    logger.info("连接DEEPSEEK-V3...")

    # Streaming:
    stream = client.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        model = "deepseek-v3-1-250821",
        messages = [
            {"role": "system", "content": DEEPSEEK_SYSTEM_DEFINE},
            {"role": "user", "content": f"你好，视频类型是{video_type}，文案如下：{script}"},
        ],
        # 响应内容是否流式返回
        stream = True,
    )

    logger.info("处理deepseek响应结果...")

    # 收集AI的响应
    ai_response = ""
    # 逐块处理流式响应
    for chunk in stream:
        if not chunk.choices:
            continue
        chunk_content = chunk.choices[0].delta.content
        ai_response += chunk_content

    shots = json.loads(ai_response)
    logger.info("分镜数组:\n%s", json.dumps(shots, ensure_ascii=False, indent=4))
    
    try:
        # 保存文案到本地
        with open(script_dir + "script.txt", "w", encoding="utf-8") as f:
            f.write(script)
        # 保存分镜结果到本地
        with open(script_dir + "shots.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(shots, ensure_ascii=False, indent=4))
    except Exception as e:
        logger.warning(f"保存文案或者分镜结果失败，但不影响后续操作: {e}")


    return shots


# 示例调用
# parse_script("一冬天都没开过的空调，你都想象不到有多脏。今天58到家9块9洗空调")








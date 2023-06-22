from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from fastapi import FastAPI, Form
import json

app = FastAPI()

# Cookie文件路径
COOKIES_PATH: str = "./cookies.json"
# Prompt文件路径（不用修改）
PROMPT_PATH: str = "./prompt.txt"
# 用于远程访问的验证码（请必须填入，建议大小写字母+数字）
VERIFY_CODE: str = "answer"

# Bing机器人的对话风格（默认精确模式）
CONVERSATION_STYLE_TYPE = ConversationStyle.precise

BOT: Chatbot = None
COOKIES: dict = None
FIRST_PROMPT: str = None

# 启动时读取缓存数据
@app.on_event("startup")
async def startup_event():
    global COOKIES, FIRST_PROMPT, VERIFY_CODE
    with open(COOKIES_PATH, "r", encoding="utf-8") as f:
        COOKIES = json.loads(f.read())
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        FIRST_PROMPT = f.read()

# 关闭时关闭Bot（其实没啥卵用）
@app.on_event("shutdown")
async def startup_event():
    global BOT
    try:
        await BOT.close()
    except:
        pass

# 询问接口
@app.post("/chat")
async def chat(verify: str = Form(...), msg: str = Form(...)):
    global VERIFY_CODE, BOT, CONVERSATION_STYLE_TYPE
    try:
        if verify == VERIFY_CODE:
            out_data: str = None
            data = await BOT.ask(
                prompt              = msg,
                conversation_style  = CONVERSATION_STYLE_TYPE,
                wss_link            = "wss://sydney.bing.com/sydney/ChatHub"
            )
            for sig_data in data['item']['messages']:
                try:
                    if sig_data["adaptiveCards"][0]["body"][0]["type"] == "TextBlock":
                        out_data = sig_data['text']
                        break
                except:
                    pass
            try:
                return {"code": 0, "msg": json.loads(out_data)}
            except:
                return {"code": 1, "msg": out_data}
        else:
            return {"code": 2, "msg": "AUTH ERROR"}
    except:
        return {"code": 1, "msg": "ERROR"}

# 重置接口
@app.post("/clean")
async def clean(verify: str = Form(...)):
    global VERIFY_CODE, BOT, COOKIES, FIRST_PROMPT
    try:
        if verify == VERIFY_CODE:
            try:
                await BOT.close()
            except:
                pass
            BOT = Chatbot(cookies=COOKIES)
            return {"code": 0, "msg": "Clean"}
        else:
            return {"code": 2, "msg": "AUTH ERROR"}
    except Exception as error:
        return {"code": 1, "msg": error}

# 加载配置接口
@app.post("/first_prompt")
async def first_prompt(verify: str = Form(...)):
    global VERIFY_CODE, BOT, CONVERSATION_STYLE_TYPE, FIRST_PROMPT
    try:
        if verify == VERIFY_CODE:
            out_data: str = None
            data = await BOT.ask(
                prompt              = FIRST_PROMPT,
                conversation_style  = CONVERSATION_STYLE_TYPE,
                wss_link            ="wss://sydney.bing.com/sydney/ChatHub"
            )
            for sig_data in data['item']['messages']:
                try:
                    if sig_data["adaptiveCards"][0]["body"][0]["type"] == "TextBlock":
                        out_data = sig_data['text']
                        break
                except:
                    pass
            try:
                return {"code": 0, "msg": json.loads(out_data)["msg"]}
            except:
                return {"code": 1, "msg": out_data}
        else:
            return {"code": 2, "msg": "AUTH ERROR"}
    except:
        return {"code": 1, "msg": "ERROR"}
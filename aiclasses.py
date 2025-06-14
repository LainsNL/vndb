import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 加载环境变量
load_dotenv()

class OpenAiProvider:

    def __init__(self):

        # 初始化环境变量
        self.apikey = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL")
        self.base_url = os.getenv("OPENAI_BASE_URL")

    # 发送请求
    def sendRequests(self,prompt,content):

        client = OpenAI(
            api_key= self.apikey,
            base_url= self.base_url,
            )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"{prompt}"},
                {"role": "user", "content": f"{content}"},
                ],
                stream=True
            )

        ai_output = ''

        for chunk in response:

            content = chunk.choices[0].delta.content
            if content !=None:
                ai_output += content
                print(content, end="", flush=True)

            if chunk.choices[0].finish_reason is not None: 
                print("\n\n输入Token:", chunk.usage.prompt_tokens)
                print("输出Token:", chunk.usage.completion_tokens)

            pattern = r'(?:<think>((?:.*\n)+)<\/think>)?\n*((?:.*\n?)+)'
            match = re.search(pattern,ai_output)

        try:
            output = match.group(2)

        except Exception as e:

            print(f'{ai_output}: {e}')


        data_list_str = output.replace('```json', '').replace('```', '').strip()
        data_list = json.loads(data_list_str)

        return data_list

class GoogleProvider:

    def __init__(self):

        # 初始化环境变量

        self.apikey = os.getenv("GOOGLE_API_KEY")
        self.model = os.getenv("GOOGLE_MODEL")

    def sendRequests(self,prompt,content):

        answer = ""

        client = genai.Client(api_key=f"{self.apikey}")

        response = client.models.generate_content_stream(
            model=self.model,
            config=types.GenerateContentConfig(    
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True
                ),
                system_instruction=prompt),
            contents=content
        )

        # 每次传回的数据
        for chunk in response:

            for part in chunk.candidates[0].content.parts:

                # 非文本，进行循环
                if not part.text:
                    continue

                # 打印思考内容
                elif part.thought:
                    print(part.text)

                else:

                    answer += part.text

        data_list_str = answer.replace('```json', '').replace('```', '').strip()
        print(data_list_str)

        data_list = json.loads(data_list_str)
        
        return data_list

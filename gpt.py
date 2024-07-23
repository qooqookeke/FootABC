# import os
# import re
# import sqlite3

# import openai
# from dotenv import load_dotenv

# load_dotenv()

# OPENAI_KEY = os.getenv("OPENAI_API_KEY")
# MODEL = "gpt-3.5-turbo"

# # 프롬프트 작성 
# def post_gpt(system_content:str, user_content:str) -> str:
#     try:
#         openai.api_key = OPENAI_KEY
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": system_content},
#                 {"role": "user", "content": user_content}
#             ],
#             # max_tokens=3000,
#             stop=None,
#             temperature=0.5
#         )
#         answer = response['choices'][0]['message']['content']
#         print("gpt 답변: " + answer)
#         return answer
    
#     except Exception as e:
#         print(e)
#         return None
        
# def create_prompt(prompt:str) -> str:
#     system_content = "You are a helpful assistant."
#     pre_prompt = "한국어로 답변해줘; \n\n"
#     answer = post_gpt(system_content, pre_prompt + prompt)

#     return answer
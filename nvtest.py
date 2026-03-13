import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
    model=os.getenv("NVIDIA_MODEL", "deepseek-ai/deepseek-v3.1"),
)
print(llm.invoke("Reply exactly: OK").content)
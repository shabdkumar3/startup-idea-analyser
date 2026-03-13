import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY  = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL    = os.getenv("NVIDIA_MODEL",    "deepseek-ai/deepseek-v3.1")
TAVILY_API_KEY  = os.getenv("TAVILY_API_KEY",  "")
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key, default=""):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

NVIDIA_API_KEY  = get_secret("NVIDIA_API_KEY")
NVIDIA_BASE_URL = get_secret("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL    = get_secret("NVIDIA_MODEL", "deepseek-ai/deepseek-v3.1")
TAVILY_API_KEY  = get_secret("TAVILY_API_KEY")
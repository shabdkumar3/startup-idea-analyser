import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key, default=""):
    if key in st.secrets:
        return st.secrets[key]
    val = os.getenv(key)
    if val:
        return val
    return default


NVIDIA_API_KEY  = get_secret("NVIDIA_API_KEY")
NVIDIA_BASE_URL = get_secret("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL    = get_secret("NVIDIA_MODEL", "deepseek-ai/deepseek-v3.1")
TAVILY_API_KEY  = get_secret("TAVILY_API_KEY")
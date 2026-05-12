import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key, default=None):
  
    val = os.getenv(key)
    if val:
        return val

    
    try:
        return st.secrets[key]
    except Exception:
        return default

NVIDIA_API_KEY  = get_secret("NVIDIA_API_KEY")
NVIDIA_BASE_URL = get_secret("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL    = get_secret("NVIDIA_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1")
TAVILY_API_KEY  = get_secret("TAVILY_API_KEY")
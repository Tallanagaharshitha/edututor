
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import streamlit as st

@st.cache_resource(show_spinner="🔄 Loading AI model...")
def load_model_and_tokenizer(model_name="ibm-granite/granite-3.3-2b-instruct"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return model, tokenizer, device

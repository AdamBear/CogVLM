"""
This is a demo using the chat version about CogAgent and CogVLM in WebDEMO
Make sure you have installed the vicuna-7b-v1.5 tokenizer model (https://huggingface.co/lmsys/vicuna-7b-v1.5), a full checkpoint of vicuna-7b-v1.5 LLM is not required.
Mention that only one image can be processed in a conversation, which means you cannot replace or insert another image during the conversation.


The models_info parameter is explained as follows
   tokenizer: tokenizer model using vicuna-7b-v1.5 model
   agent_chat: Use the CogAgent-chat-18B model to complete the conversation task
   vlm_chat: Use the CogVLM-chat-17B model to complete the conversation task
   vlm_grounding: Use CogVLM-grounding-17B model to complete the Grounding task

Web Demo user operation logic is as follows:
    CogVLM -> grounding? - yes -> CogVLM-grounding-17B
                         - no  -> CogVLM-chat-17B

    CogAgent -> CogAgent-chat-18B
             -> Choose a template -> grounding? - yes -> prompt + (with grounding)
                                                - no  -> prompt

"""

import streamlit as st
from enum import Enum

from utils import encode_file_to_base64, templates
import demo_vlm, demo_agent

st.markdown("<h3>CogAgent & CogVLM Chat Demo</h3>", unsafe_allow_html=True)
st.markdown(
    "<sub>更多使用方法请参考文档: https://lslfd0slxc.feishu.cn/wiki/WvQbwIJ9tiPAxGk8ywDck6yfnof </sub> \n\n",
    unsafe_allow_html=True)


class Mode(str, Enum):
    CogVLM, CogAgent = '💬CogVLM', '🧑‍💻 CogAgent'


with st.sidebar:
    top_p = st.slider(
        'top_p', 0.0, 1.0, 0.8, step=0.01
    )
    temperature = st.slider(
        'temperature', 0.01, 1.0, 0.90, step=0.01
    )
    top_k = st.slider(
        'top_k', 1, 20, 5, step=1
    )
    max_new_token = st.slider(
        'Output length', 1, 2048, 2048, step=1
    )
    grounding = st.checkbox("Grounding")

    uploaded_file = st.file_uploader("Choose an image...", type=['.jpg', '.png', '.jpeg'], accept_multiple_files=False)

    cols = st.columns(2)
    export_btn = cols[0]
    clear_history = cols[1].button("Clear History", use_container_width=True)
    retry = export_btn.button("Retry", use_container_width=True)

prompt_text = st.chat_input(
    'Chat with CogAgent | CogVLM',
    key='chat_input',
)

tab = st.radio(
    'Mode',
    [mode.value for mode in Mode],
    horizontal=True,
    label_visibility='hidden',
)
if tab == Mode.CogAgent.value:
    with st.sidebar:
        selected_template = st.selectbox("Select a Template", templates)

if clear_history or retry:
    prompt_text = ""

match tab:
    case Mode.CogVLM:
        if uploaded_file is not None:
            demo_vlm.main(
                retry=retry,
                top_p=top_p,
                top_k=top_k,
                temperature=temperature,
                prompt_text=prompt_text,
                metadata=encode_file_to_base64(uploaded_file),
                max_new_tokens=max_new_token,
                grounding=grounding
            )
        else:
            st.error(f'Please upload an image to start')
    case Mode.CogAgent:
        if uploaded_file is not None:
            demo_agent.main(
                retry=retry,
                top_p=top_p,
                top_k=top_k,
                temperature=temperature,
                prompt_text=prompt_text,
                metadata=encode_file_to_base64(uploaded_file),
                max_new_tokens=max_new_token,
                grounding=grounding,
                template=selected_template  # only used in CogAgent
            )
        else:
            st.error(f'Please upload an image to start')
    case _:
        st.error(f'Unexpected tab: {tab}')

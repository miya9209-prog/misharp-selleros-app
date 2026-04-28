import os
import sys
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pages import page_psd_use, page_psd_create, page_create, page_guide


def run():
    tabs = st.tabs([
        "① 템플릿 불러오기",
        "② PSD 템플릿 생성",
        "③ JPG 템플릿 생성",
        "④ 사용 가이드",
    ])

    with tabs[0]:
        page_psd_use.render()

    with tabs[1]:
        page_psd_create.render()

    with tabs[2]:
        page_create.render()

    with tabs[3]:
        page_guide.render()


def render():
    run()


def main():
    run()


def app():
    run()


if __name__ == "__main__":
    run()


# fix
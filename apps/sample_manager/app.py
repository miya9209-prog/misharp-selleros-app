
import importlib.util
import os
import sys
import streamlit as st

def render():
    base = os.path.dirname(__file__)
    target = os.path.join(base, 'app_orig.py')
    old_sys_path = list(sys.path)
    original = getattr(st, 'set_page_config', None)
    def _noop(*args, **kwargs):
        return None
    try:
        sys.path.insert(0, base)
        if original:
            st.set_page_config = _noop
        spec = importlib.util.spec_from_file_location('sample_manager_wrapped', target)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
    finally:
        if original:
            st.set_page_config = original
        sys.path = old_sys_path

if __name__ == '__main__':
    render()

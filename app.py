import streamlit as st
from pathlib import Path

from short_factory.config import load_config
from short_factory.generator import ShortFactory
from short_factory.presets import FREQUENCY_PRESETS, THEME_PRESETS

st.set_page_config(page_title="SynchroVault Short Factory", page_icon="◈", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1200px; padding-top: 2rem;}
.hero {padding: 1.5rem 0 1rem;}
.hero h1 {font-size: 2.4rem; margin-bottom: .25rem;}
.hero p {color: #777; font-size: 1.05rem;}
.card {border: 1px solid #e7e7e7; border-radius: 18px; padding: 18px; background: #fff;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>◈ SynchroVault Short Factory</h1><p>주파수 → 콘텐츠 전략 → 비주얼 → 오디오 → Shorts 렌더링</p></div>', unsafe_allow_html=True)

config = load_config()

with st.sidebar:
    st.header("Generation")
    frequency = st.selectbox("Frequency", list(FREQUENCY_PRESETS.keys()), index=1)
    theme = st.selectbox("Theme", list(THEME_PRESETS.keys()), index=0)
    count = st.slider("Number of Shorts", 1, 10, 3)
    duration = st.selectbox("Duration", [15, 30, 45], index=1)
    language = st.selectbox("Language", ["English", "Korean"], index=0)
    generate_visual = st.checkbox("Generate AI visual", value=True)
    st.caption("AI visual generation uses Gemini 3.1 Flash Image when enabled.")

preset = FREQUENCY_PRESETS[frequency]

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Frequency", f"{frequency} Hz")
with c2:
    st.metric("Visual", preset["visual"])
with c3:
    st.metric("Target", preset["angle"])

st.divider()

if st.button("GENERATE SHORT PACK", type="primary", use_container_width=True):
    factory = ShortFactory(config)
    progress = st.progress(0)
    status = st.empty()
    results = []

    for i in range(count):
        status.write(f"Generating {i + 1}/{count} …")
        try:
            result = factory.generate(
                frequency=frequency,
                theme=theme,
                duration=duration,
                language=language,
                generate_visual=generate_visual,
                variant=i + 1,
            )
            results.append(result)
        except Exception as exc:
            st.error(f"#{i + 1} failed: {exc}")
        progress.progress((i + 1) / count)

    status.success(f"Completed {len(results)} short(s).")

    for result in results:
        st.subheader(result["title"])
        st.video(str(result["video_path"]))
        st.code(result["metadata_path"].read_text(encoding="utf-8"), language="json")
        st.download_button(
            "Download MP4",
            data=result["video_path"].read_bytes(),
            file_name=result["video_path"].name,
            mime="video/mp4",
        )
else:
    st.info("Start with 888 Hz × Abundance × 30 sec. The system will create the hook, script, visual prompt, audio and final MP4 automatically.")

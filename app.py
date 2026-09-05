import streamlit as st

from short_factory.config import load_config
from short_factory.generator import ShortFactory
from short_factory.presets import FREQUENCY_PRESETS, THEME_PRESETS

st.set_page_config(page_title="SynchroVault Short Factory", page_icon="◈", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1200px; padding-top: 2rem;}
.hero {padding: 1.5rem 0 1rem;}
.hero h1 {font-size: 2.5rem; margin-bottom: .25rem; letter-spacing: -.04em;}
.hero p {color: #777; font-size: 1.05rem;}
.metric-card {border: 1px solid #e8e8e8; border-radius: 18px; padding: 16px; min-height: 112px;}
.small {color:#777; font-size:.85rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>◈ SynchroVault Short Factory</h1><p>AI content strategy → cinematic visual → frequency + voice → timed captions → 9:16 Short</p></div>', unsafe_allow_html=True)

config = load_config()

with st.sidebar:
    st.header("SHORT SETTINGS")
    frequency = st.selectbox("Frequency", list(FREQUENCY_PRESETS.keys()), index=1)
    theme = st.selectbox("Theme", list(THEME_PRESETS.keys()), index=0)
    count = st.slider("Number of Shorts", 1, 10, 3)
    duration = st.selectbox("Duration", [15, 30, 45], index=1)
    language = st.selectbox("Language", ["English", "Korean"], index=0)
    st.divider()
    generate_visual = st.checkbox("AI Visual", value=True)
    use_tts = st.checkbox("AI Voice / TTS", value=True)
    st.caption("If a provider is unavailable, the factory falls back to local visual/frequency audio so a render can still be produced.")

preset = FREQUENCY_PRESETS[frequency]

c1, c2, c3, c4 = st.columns(4)
for col, label, value in [
    (c1, "FREQUENCY", f"{frequency} Hz"),
    (c2, "THEME", theme),
    (c3, "VISUAL", preset["visual"]),
    (c4, "ANGLE", preset["angle"]),
]:
    with col:
        st.markdown(f'<div class="metric-card"><div class="small">{label}</div><b>{value}</b></div>', unsafe_allow_html=True)

st.divider()

if st.button("GENERATE SHORT PACK", type="primary", use_container_width=True):
    factory = ShortFactory(config)
    progress = st.progress(0)
    status = st.empty()
    results = []

    for i in range(count):
        status.write(f"Creating Short {i + 1}/{count}: creative brief → visual → audio → captions → render")
        try:
            result = factory.generate(
                frequency=frequency,
                theme=theme,
                duration=duration,
                language=language,
                generate_visual=generate_visual,
                variant=i + 1,
                use_tts=use_tts,
            )
            results.append(result)
        except Exception as exc:
            st.error(f"Short #{i + 1} failed: {exc}")
        progress.progress((i + 1) / count)

    if results:
        status.success(f"Generated {len(results)} Short(s).")
        for result in results:
            quality = result.get("quality", {})
            st.subheader(result["title"])
            st.video(str(result["video_path"]))
            m1, m2, m3 = st.columns(3)
            m1.metric("Overall", quality.get("overall", "—"))
            m2.metric("Hook", quality.get("hook", "—"))
            m3.metric("Loop", quality.get("loop", "—"))
            st.download_button(
                "Download MP4",
                data=result["video_path"].read_bytes(),
                file_name=result["video_path"].name,
                mime="video/mp4",
                key=result["video_path"].name,
            )
            with st.expander("Creative brief / metadata"):
                st.json(result["brief"])
    else:
        status.error("No Short was generated. Check the error above.")
else:
    st.info("Recommended first test: 888 Hz × Abundance × 30 sec × AI Visual + AI Voice.")

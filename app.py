import streamlit as st
import whisper
import os
import sys

# 1. MANUALLY REBUILD CRITICAL ENVIRONMENT PATHS (Fixes Windows system path breaks)
if sys.platform == "win32":
    ffmpeg_path = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"
    system32_path = r"C:\Windows\System32"
    
    current_paths = os.environ.get("PATH", "").split(os.pathsep)
    if os.path.exists(ffmpeg_path) and ffmpeg_path not in current_paths:
        os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]
    if os.path.exists(system32_path) and system32_path not in current_paths:
        os.environ["PATH"] = system32_path + os.pathsep + os.environ["PATH"]

# 2. CACHE WHISPER MODEL (Prevents reloading the model on every app rerun)
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

st.set_page_config(page_title="Tamil Voice Summarizer", page_icon="🎙️", layout="centered")

st.title("🎙️ Tamil Voice Summarizer")
st.markdown("### தமிழ் குரல் → ஆங்கில சுருக்கம்")
st.write("Record your voice in Tamil, and get a transcript, English translation, and a concise summary.")

# Load model safely
with st.spinner("Loading Whisper model... please wait"):
    model = load_whisper_model()

st.divider()

# 3. NATIVE RECORDER WIDGET
st.write("### 1. Speak in Tamil:")
audio_file = st.audio_input("Click the microphone to record")

if audio_file:
    # Read and store audio bytes
    audio_bytes = audio_file.read()
    
    if st.button("✨ Transcribe & Summarize", type="primary"):
        save_path = "temp_recording.wav"
        
        # Save the audio bytes locally for Whisper to scan
        with open(save_path, "wb") as f:
            f.write(audio_bytes)
            
        with st.spinner("Processing audio... This might take 10-30 seconds"):
            try:
                # Pass 1: Tamil transcript
                tamil_result = model.transcribe(save_path, language="ta")
                tamil_text = tamil_result.get("text", "").strip()

                # Pass 2: English translation
                english_result = model.transcribe(save_path, task="translate", language="ta")
                english_text = english_result.get("text", "").strip()

                # Summary logic
                sentences = [s.strip() for s in english_text.split(".") if s.strip()]
                if len(sentences) <= 2:
                    summary = english_text
                else:
                    summary = f"{sentences[0]}. {sentences[-1]}."

                # 4. DISPLAY OUTPUTS
                st.success("🎉 Processing Complete!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🔴 Tamil Transcript")
                    st.text_area(label="Tamil Out", value=tamil_text, height=150, label_visibility="collapsed")
                    
                with col2:
                    st.subheader("🔵 English Translation")
                    st.text_area(label="English Out", value=english_text, height=150, label_visibility="collapsed")
                    
                st.divider()
                st.subheader("🟢 English Summary")
                st.info(summary)

            except Exception as e:
                st.error(f"Processing Error: {str(e)}")
                
            finally:
                # Clean up local temporary file safely
                if os.path.exists(save_path):
                    try:
                        os.remove(save_path)
                    except:
                        pass
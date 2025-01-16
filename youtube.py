import streamlit as st
import yt_dlp
import os
import requests
from PIL import Image
from io import BytesIO

def get_video_info(url):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return info
    except Exception as e:
        st.error(f"Failed to retrieve video info: {e}")
        return None

def download_video(url, resolution):
    info = get_video_info(url)
    if not info:
        return None
    
    thumbnail_url = info.get("thumbnail", "")
    if thumbnail_url:
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption=f"Downloading: {info['title']}", use_column_width=True)
    
    ydl_opts = {
        'format': f'best[height<={resolution}][ext=mp4]',  # Ensures progressive video (no FFmpeg needed)
        'outtmpl': '%(title)s.%(ext)s'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return f"{info['title']}.mp4"

def download_playlist(url, resolution):
    try:
        ydl_opts = {'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
        
        st.write(f"Downloading Playlist: {playlist_info['title']}")
        for entry in playlist_info['entries']:
            download_video(entry['url'], resolution)
        
        st.success("Playlist Downloaded Successfully!")
    except Exception as e:
        st.error(f"Error: {e}")

# Streamlit UI
st.title("YouTube Video/Playlist Downloader")
url = st.text_input("Enter YouTube Video or Playlist URL:")
resolution = st.selectbox("Choose Quality:", ["1080", "720", "480", "360", "240", "144"])

download_type = st.radio("Select Download Type:", ["Single Video", "Playlist"])

if st.button("Download") and url:
    if download_type == "Single Video":
        file_path = download_video(url, resolution)
        if file_path:
            st.success(f"Downloaded Successfully: {file_path}")
    else:
        download_playlist(url, resolution)

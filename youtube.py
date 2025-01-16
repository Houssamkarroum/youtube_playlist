import streamlit as st
import yt_dlp
import os
import requests
from PIL import Image
from io import BytesIO

# Get video information
def get_video_info(url):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return info
    except Exception as e:
        st.error(f"Failed to retrieve video info: {e}")
        return None

# Update download function to handle folder path
def download_video(url, resolution, folder_path):
    info = get_video_info(url)
    if not info:
        return None
    
    # Display thumbnail image
    thumbnail_url = info.get("thumbnail", "")
    if thumbnail_url:
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption=f"Downloading: {info['title']}", use_column_width=True)
    
    # yt-dlp options for video download
    ydl_opts = {
        'format': f'best[height<={resolution}][ext=mp4]',  # Ensures progressive video (no FFmpeg needed)
        'outtmpl': os.path.join(folder_path, '%(title)s.%(ext)s'),  # Save to the user-selected folder
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return f"{info['title']}.mp4"

# Download playlist function with the correct arguments
def download_playlist(url, resolution, folder_path):
    try:
        ydl_opts = {'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
        
        st.write(f"Downloading Playlist: {playlist_info['title']}")
        for entry in playlist_info['entries']:
            download_video(entry['url'], resolution, folder_path)
        
        st.success("Playlist Downloaded Successfully!")
        st.balloons()  # Optional: Display Streamlit balloons after successful download
    except Exception as e:
        st.error(f"Error: {e}")

# Streamlit UI
st.title("YouTube Video/Playlist Downloader")

# Folder path input by user
folder_path = st.text_input("Enter Folder Path to Save Videos:")

# Make sure the folder exists
if folder_path and not os.path.exists(folder_path):
    st.error(f"Folder path does not exist: {folder_path}")
else:
    url = st.text_input("Enter YouTube Video or Playlist URL:")
    resolution = st.selectbox("Choose Quality:", ["1080", "720", "480", "360", "240", "144"])

    download_type = st.radio("Select Download Type:", ["Single Video", "Playlist"])

    if st.button("Download") and url and folder_path:
        if download_type == "Single Video":
            file_path = download_video(url, resolution, folder_path)
            if file_path:
                st.success(f"Downloaded Successfully: {file_path}")
                st.balloons()  # Optional: Show balloons for download success
                st.write("Thank you for using the downloader!")
        else:
            download_playlist(url, resolution, folder_path)  # Corrected function call
            st.write("Thank you for using the downloader!")

import yt_dlp
import tkinter
import os
import sys
from tkinter import PhotoImage, filedialog, ttk
import threading

def start_download_thread():
    # Butonu geçici olarak devre dışı bırakalım ki üst üste basılmasın
    download_button.config(state="disabled")
    t = threading.Thread(target=download_youtube_video)
    t.daemon = True # Program kapanırsa indirme de dursun
    t.start()

def center_screen(window):
    width = 400
    height = 450
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

screen = tkinter.Tk()
screen.title("Youtube Downloader")
screen.iconbitmap(resource_path("assets/youtube.ico"))
screen.resizable(False, False)

image_path = resource_path("assets/youtube.png")
image = PhotoImage(file=image_path)

image_label = tkinter.Label(image=image)
image_label.pack(pady=(10,0))

target_dir = ""
str_var = tkinter.StringVar()

def select_path():
    global target_dir
    target_dir = filedialog.askdirectory()
    screen.update_idletasks()
    str_var.set(target_dir)
    path_entry.config(textvariable=str_var)
    path_entry.config(state="readonly")

path_text_label = tkinter.Label(text="Select a folder to save the download", font=("Arial Bold", 12, "bold"))
path_text_label.pack(pady=(25,0))
select_path_button = tkinter.Button(text="Select path", width=18, height=1, font=("Arial Bold", 8), command=select_path)
select_path_button.pack(pady=(5,0))
path_entry = tkinter.Entry(width=30, font=("Arial Bold", 10))
path_entry.pack(pady=(5,0))

url_text_label = tkinter.Label(text="Copy and paste the URL ", font=("Arial Bold", 15, "bold"))
url_text_label.pack(pady=(25,0))
url_entry = tkinter.Entry(width=30, font=("Arial Bold", 10))
url_entry.pack(pady=(5,0))


def update_text(word):
    str_var.set(word)

def progress_hook(d):
    if d['status'] == 'downloading':
        # Yüzde bilgisini alıp temizliyoruz
        p = d.get('_percent_str', '0%').replace('%','')
        try:
            current_percent = float(p)
            progress_bar['value'] = current_percent
            # Yüzdeyi status_label'da da gösterebiliriz
            status_label.config(text=f"Downloading... %{current_percent:.1f}")
            screen.update_idletasks()
        except ValueError:
            pass
    if d['status'] == 'finished':
        progress_bar['value'] = 100

def download_youtube_video():
    url = url_entry.get()
    ydl_opts = {
        # 'bestvideo+bestaudio' FFmpeg yüklü olduğu için artık sorunsuz çalışacak
        # Bu satır 1080p, 2K veya 4K hangisi varsa onu indirir
        #'format': 'bestvideo+bestaudio/best',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',

        # Çıktı dosyasının formatı mp4 olsun (birleştirme sonrası)
        'merge_output_format': 'mp4',

        # İlerleme durumunu terminalde gösterir
        'quiet': False,
        'no_warnings': False,
        'progress_hooks': [progress_hook],
        'noplaylist': True,
    }
    if target_dir != "":
        ydl_opts['outtmpl'] = os.path.join(target_dir, '%(title)s.%(ext)s')
    else:
        ydl_opts['outtmpl'] = '%(title)s.%(ext)s'
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown Video')

            status_label.config(text=f"Downloading: \n{video_title}", fg="blue")
            screen.update_idletasks()

            ydl.download([url])

            full_path = ydl.prepare_filename(info)
            folder_path = os.path.abspath(os.path.dirname(full_path))

            status_label.config(text=f"Download finished: \n{folder_path}", fg="green")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        download_button.config(state="normal")  # Hata olsa da olmasa da buton geri gelsin

download_button = tkinter.Button(text="Download", width=18, height=1, font=("Arial Bold", 8), command=start_download_thread)
download_button.pack(pady=(20,5))

status_label = tkinter.Label(font=("Arial Bold", 10, "bold"))
status_label.pack(pady=(10,5))

progress_bar = ttk.Progressbar(screen, orient="horizontal", length=250, mode="determinate")
progress_bar.pack(pady=(5, 0))

center_screen(screen)
screen.mainloop()
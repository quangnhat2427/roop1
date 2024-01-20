from typing import Tuple, Optional
import gradio

import facefusion.globals
from facefusion import wording
from facefusion.face_store import clear_static_faces, clear_reference_faces
from facefusion.uis.typing import File
from facefusion.filesystem import is_image, is_video
from facefusion.uis.core import register_ui_component

TARGET_FILE: Optional[gradio.File] = None
TARGET_IMAGE: Optional[gradio.Image] = None
TARGET_VIDEO: Optional[gradio.Video] = None
TARGET_TEXT: Optional[gradio.Textbox] = None
OUTPUT_PATH_TEXTBOX: Optional[gradio.Textbox] = None
CHOOSE_BUTTON: Optional[gradio.Button] = None
CHOOSE_BUTTON1: Optional[gradio.Button] = None
CHOOSE_BUTTON2: Optional[gradio.Button] = None


def render() -> None:
    global TARGET_FILE
    global TARGET_IMAGE
    global TARGET_VIDEO
    global TARGET_TEXT
    global CHOOSE_BUTTON
    global CHOOSE_BUTTON1
    global CHOOSE_BUTTON2
    global OUTPUT_PATH_TEXTBOX

    is_target_image = is_image(facefusion.globals.target_path)
    is_target_video = is_video(facefusion.globals.target_path)

    TARGET_FILE = gradio.File(
        label=wording.get('target_file_label'),
        file_count='single',
        file_types=['.png', '.jpg', '.webp', '.mp4'],
        value=facefusion.globals.target_path if is_target_image or is_target_video else None
    )

    TARGET_IMAGE = gradio.Image(
        value=TARGET_FILE.value['name'] if is_target_image else None,
        visible=is_target_image,
        show_label=False
    )

    TARGET_VIDEO = gradio.Video(
        value=TARGET_FILE.value['name'] if is_target_video else None,
        visible=is_target_video,
        show_label=False
    )

    TARGET_TEXT = gradio.Textbox(
        lines=1,
        label="Nhập văn bản"
    )

    OUTPUT_PATH_TEXTBOX = gradio.Textbox(
        label=wording.get('output_path_textbox_label'),
        max_lines=1
    )

    CHOOSE_BUTTON = gradio.Button(
        label="Chọn ngay",
        type="button"
    )
    CHOOSE_BUTTON1 = gradio.Button(
        label="Download",
        type="button"
    )
    CHOOSE_BUTTON2 = gradio.Button(
        label="Button 2",
        type="button"
    )

    register_ui_component('target_image', TARGET_IMAGE)
    register_ui_component('target_video', TARGET_VIDEO)


def listen() -> None:
    TARGET_FILE.change(update, inputs=[TARGET_FILE], outputs=[TARGET_IMAGE, TARGET_VIDEO])
    CHOOSE_BUTTON.click(update_path, inputs=[TARGET_TEXT], outputs=[TARGET_IMAGE, TARGET_VIDEO])
    CHOOSE_BUTTON1.click(download, inputs=[OUTPUT_PATH_TEXTBOX], outputs=[])
    CHOOSE_BUTTON2.click(delete, inputs=[], outputs=[])
import os
import urllib.request
def delete():
    folder_path = "/content/gg"

    # Kiểm tra xem thư mục tồn tại hay không
    if os.path.exists(folder_path):
        # Lấy danh sách các tệp tin trong thư mục
        file_list = os.listdir(folder_path)

        # Xóa từng tệp tin trong thư mục
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
    
        print("Đã xóa thành công các tệp tin trong thư mục /content/gg.")
    else:
        print("Thư mục /content/gg không tồn tại.")
def download(input_links: str):
    folder_path = "/content/gg"
    os.makedirs(folder_path, exist_ok=True)  # Tạo thư mục nếu chưa có
    links = input_links.split("\n")
    for link in links:
        link = link.strip()
        if link.startswith("http://") or link.startswith("https://"):
            file_name = link.split("/")[-1]
            save_directory = "/content/gg"
            save_path = os.path.join(save_directory, file_name)
            try:
                urllib.request.urlretrieve(link, save_path)
                print("Downloaded:", file_name)
            except Exception as e:
                print("Error downloading:", file_name, "-", str(e))
        else:
            print("Invalid URL:", link)
            
def update_path(target_text: str):
    print(target_text)
    facefusion.globals.target_path = target_text
    try:
        with open(target_text, "rb") as file:
            # Truyền đối tượng tệp tin thay vì dữ liệu bytes
            result = update(file)
            TARGET_FILE.change()
            
        # Thực hiện xử lý kết quả từ hàm update ở đây
        # Ví dụ: hiển thị hình ảnh hoặc video

    except FileNotFoundError:
        print("Không tìm thấy tệp tin.")
    except Exception as e:
        print("Đã xảy ra lỗi:", str(e))
    return result


def update(file: File) -> Tuple[gradio.Image, gradio.Video]:
    clear_reference_faces()
    clear_static_faces()
    if file and is_image(file.name):
        facefusion.globals.target_path = file.name
        return gradio.Image(value=file.name, visible=True), gradio.Video(value=None, visible=False)
    if file and is_video(file.name):
        facefusion.globals.target_path = file.name
        return gradio.Image(value=None, visible=False), gradio.Video(value=file.name, visible=True)
    facefusion.globals.target_path = None
    return gradio.Image(value=None, visible=False), gradio.Video(value=None, visible=False)
import flet as ft
import google.generativeai as genai
import PIL.Image

import time
import os
from dotenv import load_dotenv

from elevenlabs import tts
from context import create_context
from formatting import chat_format, output_path_format, spacy_text_format


class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type


class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str) -> str:
        return user_name[:1].capitalize()

    def get_avatar_color(self, user_name: str) -> ft.colors:
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.BLACK,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


def main(page: ft.Page):

    # Configure page appearance
    page.title = "English chatbot"
    page.horizontal_alignment = "stretch"
    page.theme_mode = ft.ThemeMode.DARK

    # Configure gemini models
    try:
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    except Exception as e:
        print("No api-key file:", e)

    model_text = genai.GenerativeModel("gemini-pro")
    chat_text = model_text.start_chat(history=[])
    model_vision = genai.GenerativeModel("gemini-pro-vision")

    # Join validation
    def join_chat_click(e):
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()

        elif not select_english_level.value:
            select_english_level.error_text = "Select an English level!"
            select_english_level.update()
        else:
            page.session.set("user_name", join_user_name.value)
            page.dialog.open = False
            new_message.prefix = ft.Text(
                f"{join_user_name.value} - {select_english_level.value}:  "
            )
            page.update()

    def send_message_click(e):
        new_message.disabled = True
        if new_message.value != "":
            page.pubsub.send_all(
                Message(
                    page.session.get("user_name"),
                    new_message.value,
                    message_type="chat_message",
                )
            )
            page.update()

            generate_gemini_response(
                model="pro", user_message=new_message.value.strip(), images=None
            )
            new_message.value = ""
            new_message.focus()

    def send_images(e: ft.FilePickerResultEvent):
        new_message.disabled = True

        images = []
        image_names = []

        for file in e.files:
            print(file.path)  #!
            image = PIL.Image.open(file.path)

            images.append(image)
            image_names.append(file.name)

            user_upload_message = f"Upload: {' | '.join(image_names)}"

        page.pubsub.send_all(
            Message(
                user_name=page.session.get("user_name"),
                text=user_upload_message,
                message_type="chat_message",
            )
        )

        page.update()

        generate_gemini_response(
            model="pro_vision", user_message=user_upload_message, images=images
        )

    def generate_gemini_response(model: str, user_message: str, images):

        context = create_context(
            selected_english_level=select_english_level.value,
            user_name=join_user_name.value,
            user_message=user_message,
            model=model,
        )

        if images is None:
            response = chat_text.send_message(content=context)

        else:
            print(images)  #!
            response = model_vision.generate_content([context, *images])

        print(f"context:\n{context}")  #!
        print(f"reponse:\n {response}")  #!
        print(f"response.text:\n{response.text}")  #!

        gemini_response = chat_format(response.text)

        spacy_proccessing(gemini_response)

        audio_path = output_path_format()

        tts(text=gemini_response, output_path=audio_path)

        play_audio(audio_path)

        page.update()
        page.pubsub.send_all(
            Message("Gemini:", gemini_response, message_type="chat_message")
        )
        new_message.disabled = False
        page.update()

    def play_audio(audio_path: str):
        audio.src = audio_path
        page.add(audio)
        time.sleep(2)
        audio.play()

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.BLACK45, size=12)
        else:
            print("Received an unknown message type:", message)
            return

        if m is not None:
            chat.controls.append(m)
            page.update()

    audio = ft.Audio(
        autoplay=False,
        volume=1,
        balance=0,
        on_loaded=lambda _: print("Loaded"),
        on_duration_changed=lambda e: print("Duration changed:", e.data),
        on_position_changed=lambda e: print("Position changed:", e.data),
        on_state_changed=lambda e: print("State changed:", e.data),
        on_seek_complete=lambda _: print("Seek complete"),  #!
    )

    def spacy_proccessing(text: str):
        import spacy

        nlp = spacy.load("en_core_web_sm")

        orginal_text = ft.Text(text, size=24)
        text = spacy_text_format(text)
        doc = nlp(text=text)

        unique_words = set()
        for word in doc:
            unique_words.add(word.text.lower())
        table_rows = []

        for word_text in unique_words:
            word = nlp(text=word_text)
            lemma = word[0].lemma_
            pos = word[0].pos_

            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(word_text)),  # Word
                        ft.DataCell(ft.Text(lemma)),  # Base form
                        ft.DataCell(ft.Text(pos)),  # TAG
                    ]
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Word")),
                ft.DataColumn(ft.Text("Base form")),
                ft.DataColumn(ft.Text("TAG")),
            ],
            rows=table_rows,
        )

        lv.controls.append(orginal_text)
        lv.controls.append(table)
        page.update()

    page.pubsub.subscribe(on_message)

    join_user_name = ft.TextField(
        label="Enter your name",
        autofocus=True,
        width=300,
        height=65,
        on_submit=join_chat_click,
    )

    english_levels = [
        ft.dropdown.Option("A1"),
        ft.dropdown.Option("A2"),
        ft.dropdown.Option("B1"),
        ft.dropdown.Option("B2"),
        ft.dropdown.Option("C1"),
        ft.dropdown.Option("C2"),
    ]

    select_english_level = ft.Dropdown(
        label="Select your english level",
        width=300,
        height=65,
        options=english_levels,
    )

    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column(
            [join_user_name, select_english_level],
            width=260,
            height=150,
            tight=True,
            spacing=15,
        ),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_chat_click)],
        actions_alignment="end",
        content_padding=30,
    )

    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    file_picker = ft.FilePicker(on_result=send_images)
    page.add(file_picker)

    chat_bot_container = ft.Container(
        content=ft.Column(
            [
                chat,
                ft.Row(
                    [
                        new_message,
                        ft.IconButton(
                            icon=ft.icons.SEND_ROUNDED,
                            tooltip="Send message",
                            on_click=send_message_click,
                            disabled=False,
                        ),
                        ft.IconButton(
                            icon=ft.icons.UPLOAD,
                            tooltip="Upload image",
                            on_click=lambda _: file_picker.pick_files(
                                allow_multiple=True,
                                allowed_extensions=["jpg", "jpeg", "png", "webp"],
                            ),
                        ),
                    ]
                ),
            ]
        ),
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=5,
        padding=10,
        expand=True,
    )

    lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)

    second_tab_content = ft.Container(content=lv)

    t = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="English chat bot", content=chat_bot_container),
            ft.Tab(text="Text analysis table", content=second_tab_content),
        ],
        expand=1,
    )

    page.add(t)


ft.app(target=main)
# ft.app(target=main, view=ft.AppView.WEB_BROWSER)

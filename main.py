from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarListItem, ImageLeftWidget
from bookdb import BookDB
from pdfviewer import PDFViewer
from epubviewer import EPUBViewer
from utils import extract_epub_cover, save_cover
import os
from plyer import filechooser, tts

Window.size = (360, 640)

KV = """
ScreenManager:
    LibraryScreen:
    PDFScreen:
    EPUBScreen:
    BrowserScreen:
    SettingsScreen:

<LibraryScreen>:
    name: "library"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "My Library"
            left_action_items: [["menu", lambda x: None]]
            right_action_items: [["plus", lambda x: app.import_book()]]
        MDTextField:
            id: search_field
            hint_text: "Search books..."
            on_text: app.filter_books(self.text)
        ScrollView:
            MDList:
                id: book_list

<PDFScreen>:
    name: "pdf"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "PDF Reader"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            right_action_items: [["volume-high", lambda x: app.speak_pdf()]]
        ScrollView:
            id: pdf_scroll

<EPUBScreen>:
    name: "epub"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "EPUB Reader"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            right_action_items: [["volume-high", lambda x: app.speak_epub()]]
        BoxLayout:
            id: epub_scroll

<BrowserScreen>:
    name: "browser"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Browser"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
        BoxLayout:
            size_hint_y: None
            height: "50dp"
            MDTextField:
                id: browser_input
                hint_text: "Enter URL or search"
            MDRaisedButton:
                text: "Go"
                on_release: app.load_browser()
        WebView:
            id: webview

<SettingsScreen>:
    name: "settings"
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Settings"
        MDRaisedButton:
            text: "Toggle Theme"
            pos_hint: {"center_x":0.5}
            on_release: app.toggle_theme()
"""

class LibraryScreen(Screen): pass
class PDFScreen(Screen): pass
class EPUBScreen(Screen): pass
class BrowserScreen(Screen): pass
class SettingsScreen(Screen): pass

class BookApp(MDApp):
    def build(self):
        self.db = BookDB()
        self.sm = Builder.load_string(KV)
        self.current_file = None
        self.load_books()
        return self.sm

    def load_books(self):
        books = self.db.get_books()
        book_list = self.sm.get_screen("library").ids.book_list
        book_list.clear_widgets()
        for book in books:
            cover_path = None
            if book[2].endswith(".epub"):
                img_bytes = extract_epub_cover(book[2])
                if img_bytes:
                    cover_path = save_cover(img_bytes)
            item = OneLineAvatarListItem(
                text=book[1],
                on_release=lambda x, path=book[2]: self.open_book(path)
            )
            if cover_path:
                item.add_widget(ImageLeftWidget(source=cover_path))
            book_list.add_widget(item)

    def filter_books(self, query):
        books = self.db.get_books()
        filtered = [b for b in books if query.lower() in b[1].lower()]
        book_list = self.sm.get_screen("library").ids.book_list
        book_list.clear_widgets()
        for book in filtered:
            item = OneLineAvatarListItem(
                text=book[1],
                on_release=lambda x, path=book[2]: self.open_book(path)
            )
            book_list.add_widget(item)

    def import_book(self):
        paths = filechooser.open_file(title="Select PDF or EPUB", filters=[("PDF/EPUB","*.pdf;*.epub")])
        if paths:
            path = paths[0]
            title = os.path.basename(path)
            self.db.add_book(title, path)
            self.load_books()

    def open_book(self, path):
        self.current_file = path
        if path.endswith(".pdf"): self.show_pdf(path)
        elif path.endswith(".epub"): self.show_epub(path)

    def show_pdf(self, path):
        screen = self.sm.get_screen("pdf")
        scroll = screen.ids.pdf_scroll
        scroll.clear_widgets()
        scroll.add_widget(PDFViewer(path))
        self.sm.current = "pdf"

    def show_epub(self, path):
        screen = self.sm.get_screen("epub")
        scroll = screen.ids.epub_scroll
        scroll.clear_widgets()
        scroll.add_widget(EPUBViewer(path))
        self.sm.current = "epub"

    def speak_pdf(self):
        if self.current_file and self.current_file.endswith(".pdf"):
            import fitz
            text = "".join([p.get_text() for p in fitz.open(self.current_file)])
            tts.speak(text)

    def speak_epub(self):
        if self.current_file and self.current_file.endswith(".epub"):
            from ebooklib import epub
            book = epub.read_epub(self.current_file)
            text = ""
            for item in book.get_items():
                if item.get_type() == epub.EpubHtml:
                    text += item.get_body_content().decode('utf-8')
            tts.speak(text)

    def toggle_theme(self):
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style=="Light" else "Light"

    def change_screen(self, name):
        self.sm.current = name

    def go_back(self):
        self.sm.current = "library"

    def load_browser(self):
        url = self.sm.get_screen("browser").ids.browser_input.text
        if not url.startswith("http"):
            url = "https://www.google.com/search?q=" + url.replace(" ","+")
        self.sm.get_screen("browser").ids.webview.url = url

if __name__ == "__main__":
    BookApp().run()
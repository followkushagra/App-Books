from kivy.uix.boxlayout import BoxLayout
from kivy_garden.cefpython import WebView
from ebooklib import epub

class EPUBViewer(BoxLayout):
    def __init__(self, filepath, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.webview = WebView()
        self.add_widget(self.webview)

        book = epub.read_epub(filepath)
        html_content = ""
        for item in book.get_items():
            if item.get_type() == epub.EpubHtml:
                html_content += item.get_body_content().decode('utf-8')

        html_full = f"""
        <html>
        <head><meta charset="UTF-8"><style>
        body {{ font-family: sans-serif; padding:10px; color:#000; background:#fff; }}
        img {{ max-width:100%; height:auto; }}
        </style></head>
        <body>{html_content}</body>
        </html>
        """
        self.webview.html = html_full
import fitz
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

class PDFViewer(BoxLayout):
    def __init__(self, filepath, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.doc = fitz.open(filepath)
        for page in self.doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2,2))
            texture = Texture.create(size=(pix.width,pix.height))
            texture.blit_buffer(pix.samples, colorfmt="RGBA", bufferfmt="ubyte")
            img = Image(texture=texture, size_hint_y=None, height=pix.height)
            self.add_widget(img)
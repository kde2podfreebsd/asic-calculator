import os
from pyhtml2pdf import converter


if __name__ == "__main__":
    path = os.path.abspath('tech/index.html')
    converter.convert(f'file:///{path}', 'static/1223.pdf')
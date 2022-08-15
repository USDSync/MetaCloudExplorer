import glob
from PIL import Image, ImageDraw, ImageFont
import requests
import io

def draw_text_on_image_at_position(input_image_path:str,  output_path:str, textToDraw:str, x:int, y:int, fillColor:str):
    image = Image.open(input_image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("temp\\BebasNeue-Regular.ttf", size=28)
    draw.text((x, y), textToDraw, font_size=44, font=font, fill=fillColor)
    image.save(output_path)

def create_image_with_text(output_path:str, textToDraw:str, x:int, y:int, h:int, w:int, color:str, alignment:str, fillColor:str, fontPath:str, fontSize:int):    
    image = Image.new("RGB", (h, w), color)
    draw = ImageDraw.Draw(image)
    # Load font from URI
    truetype_url = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true'
    r = requests.get(truetype_url, allow_redirects=True)
    font = ImageFont.truetype(io.BytesIO(r.content), size=24)

    #font = ImageFont.truetype(fontPath, layout_engine=ImageFont.LAYOUT_BASIC, size=fontSize)
    draw.text((x, y), textToDraw, font=font, align=alignment, fill=fillColor)
    image.save(output_path)


if __name__ == "__main__":
    create_image_with_text("temp\\output2.jpg", "Mmmuuuurrrrrrrrrr", 10.0,525,575,575,"white", "left", "black", "temp\\airstrike.ttf", 44)
    draw_text_on_image_at_position("temp\\grid.png", "temp\\grid_test.png", "defaultresourcegroup_ea", 25,385, "yellow")



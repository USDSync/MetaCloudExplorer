import glob
from PIL import Image, ImageDraw, ImageFont
import requests
import io

def draw_text_on_image_at_position(
    input_image_path:str, 
    output_image_path:str, 
    textToDraw:str, 
    x:int, y:int,
    fillColor:str, fontSize:int):    

    image = Image.open(input_image_path)

    image = image.rotate(270, expand=1)

    draw = ImageDraw.Draw(image)
    
    font1 = "https://github.com/googlefonts/Arimo/raw/main/fonts/ttf/Arimo-Regular.ttf"
    truetype_url = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true'
    font = load_font_from_uri(fontSize, font1)


    draw.text((x, y), textToDraw, font_size=fontSize, font=font, fill=fillColor)
    image = image.rotate(-270, expand=1)

    image.save(output_image_path)


def create_image_with_text(output_image_path:str, textToDraw:str, x:int, y:int, h:int, w:int, color:str, alignment:str, fillColor:str, fontPath:str, fontSize:int):    
    image = Image.new("RGB", (h, w), color)
    draw = ImageDraw.Draw(image)

    # Load font from URI
    font1 = "https://github.com/googlefonts/Arimo/raw/main/fonts/ttf/Arimo-Regular.ttf"
    truetype_url = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true'
    font = load_font_from_uri(fontSize, font1)

    #font = ImageFont.truetype(fontPath, layout_engine=ImageFont.LAYOUT_BASIC, size=fontSize)
    draw.text((x, y), textToDraw, font=font, align=alignment, fill=fillColor)
    image.save(output_image_path)


def load_font_from_uri(size:int, url:str):
    # Load font from URI
    truetype_url = url
    r = requests.get(truetype_url, allow_redirects=True)
    return ImageFont.truetype(io.BytesIO(r.content), size=size)


#angled text 
#https://stackoverflow.com/questions/245447/how-do-i-draw-text-at-an-angle-using-pythons-pil
def draw_text_90_into(text: str, into, at):

    # Measure the text area
    font = ImageFont.truetype (r'C:\Windows\Fonts\Arial.ttf', 16)
    wi, hi = font.getsize (text)

    # Copy the relevant area from the source image
    img = into.crop ((at[0], at[1], at[0] + hi, at[1] + wi))

    # Rotate it backwards
    img = img.rotate (270, expand = 1)

    # Print into the rotated area
    d = ImageDraw.Draw (img)
    d.text ((0, 0), text, font = font, fill = (0, 0, 0))

    # Rotate it forward again
    img = img.rotate (90, expand = 1)

    # Insert it back into the source image
    # Note that we don't need a mask
    into.paste (img, at)









if __name__ == "__main__":
    #create_image_with_text("temp\\output2.jpg", "Mmmuuuurrrrrrrrrr", 10.0,525,575,575,"white", "left", "black", "temp\\airstrike.ttf", 44)
    draw_text_on_image_at_position("temp\\tron_grid.png", "temp\\grid_test.png", "defaultresourcegroup_ea", 25,420, "yellow", 36)

#'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true'

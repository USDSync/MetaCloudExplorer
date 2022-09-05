import glob
from PIL import Image, ImageDraw, ImageFont, ImageDraw
import io
import asyncio
import os
import time
import sys
import os.path as path
from pathlib import Path
import omni.kit.pipapi
from datetime import datetime, timedelta

#Create and draw images in async contexxt
async def draw_text_on_image_at_position_async (
    input_image_path:str, 
    output_image_path:str, 
    textToDraw:str, 
    costToDraw:str,
    x:int, y:int,
    fillColor:str,
    font:str,
    fontSize:int):    

    await draw_text_on_image_at_position(
        input_image_path, 
        output_image_path, 
        textToDraw, 
        costToDraw,
        x, y, fillColor, font, fontSize
    )


def is_file_older_than_x_days(file, days=1): 
    file_time = path.getmtime(file) 
    # Check against 24 hours 
    return ((time.time() - file_time) / 3600 > 24*days)

#Create a new image with text
def draw_text_on_image_at_position(
    input_image_path:str, 
    output_image_path:str, 
    textToDraw:str, 
    costToDraw:str,
    x:int, y:int,
    fillColor:str, font:str, fontSize:int):    

    makeFile = False

    if not os.path.exists(input_image_path):
        print("No src file: " + str(input_image_path))
        return

    if os.path.exists(output_image_path):
        if is_file_older_than_x_days(output_image_path, 1):
            makeFile = True
    else: 
        makeFile = True

    if makeFile:

        print("Refreshing Image " + str(output_image_path) + " with text: "  + textToDraw + " cst: " + costToDraw) 

        #font = ImageFont.load(str(font))
        font = ImageFont.truetype(str(font), fontSize, encoding="unic")

        print("Loading src file: " + str(input_image_path))
        image = Image.open(input_image_path)
        image = image.rotate(270, expand=1)
        draw = ImageDraw.Draw(image)
        textW, textH = draw.textsize(textToDraw, font) # how big is our text
        costW, costH = draw.textsize(costToDraw, font) # how big is cost text

        if costToDraw != "":
            costToDraw = str(costToDraw) + " /month"
            draw.text((x,y-75), textToDraw, font_size=fontSize,anchor="ls", font=font, fill=fillColor)
            draw.text((x,y+75), costToDraw, font_size=(fontSize-50), anchor="ls", font=font, fill="red")
        else:
            draw.text((x, y-50), textToDraw, font_size=fontSize,anchor="ls", font=font, fill=fillColor)

        image = image.rotate(-270, expand=1)

        with open(output_image_path, 'wb') as out_file:
            image.save(out_file, 'PNG')

    #image.save(output_image_path)

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
    draw_text_on_image_at_position("temp\\tron_grid_test.png", "temp\\output_test.png", "defaultresourcegroup_ea","$299.00", 200,1800, "yellow", 110)

#'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true'
    # input_image_path:str, 
    # output_image_path:str, 
    # textToDraw:str, 
    # costToDraw:str,
    # x:int, y:int,
    # fillColor:str, fontSize:int):    


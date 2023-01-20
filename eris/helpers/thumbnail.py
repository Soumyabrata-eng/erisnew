import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


async def gen_thumb(videoid):
    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)
    for result in (await results.next())["result"]:
       try:
        title = result["title"]
        title = re.sub("\W+", " ", title)
        title = title.title()
       except:
        title = "No Title"
    thumbnail = result["thumbnails"][0]["url"].split("?")[0]

    async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

    image1 = Image.open(f"cache/thumb{videoid}.png")
    image2 = Image.open("./eris/resources/cover.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save(f"cache/temp{videoid}.png")
    img = Image.open(f"cache/temp{videoid}.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('./eris/resources/default.ttf', 60)
    draw.text(
        (25, 609),
        f"{title}",
        fill="black",
        font=font,
    )   
    img.save(f"cache/final{videoid}.png")
    os.remove(f"cache/temp{videoid}.png")
    os.remove(f"cache/thumb{videoid}.png")
    final = f"cache/final{videoid}.png"
    return final

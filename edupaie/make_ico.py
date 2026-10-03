from PIL import Image

img = Image.open("src/assets/logo.png").convert("RGBA")
sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
resized = [img.resize(s, Image.LANCZOS) for s in sizes]
resized[0].save(
    "src/assets/edupaie.ico",
    format="ICO",
    sizes=sizes,
    append_images=resized[1:]
)
print("edupaie.ico cree avec succes")

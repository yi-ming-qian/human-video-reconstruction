import os
import glob
import html_snippets

video_name = "FigureSkater"
image_list = glob.glob(f"./{video_name}/*_mask.png")
rows = ""
for i in range(len(image_list)):
    name = f"{i:04}"
    frame_path = f"./{name}.png"
    mask_path = f"./{name}_mask.png"
    model_path = f"./results/{name}.glb"
    tex_model_path = f"./results/{name}_tex.glb"
    rows += html_snippets.row.format(frame_path, mask_path, model_path, tex_model_path)

with open(f"./{video_name}/{video_name}.html", 'w') as f:
    f.write(html_snippets.preample.format(video_name, rows))
exit()


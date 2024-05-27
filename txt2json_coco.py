# 文件路径: txt2json_coco.py

import os
import json
import glob
from PIL import Image
import fire
from collections import defaultdict
from rich.progress import track
from rich.console import Console
from rich.table import Table

console = Console()

def get_image_info(image_id, file_name, image_size):
    """获取图像信息的字典格式"""
    return {
        "id": image_id,
        "file_name": file_name,
        "width": image_size[0],
        "height": image_size[1],
    }

def get_annotation_info(annotation_id, image_id, category_id, bbox, iscrowd=0):
    """获取标注信息的字典格式"""
    x, y, w, h = bbox
    return {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "segmentation": [],  # 简单处理，这里留空
        "area": w * h,
        "bbox": [x, y, w, h],
        "iscrowd": iscrowd,
    }

def convert_annotations(base_dir, mode):
    """
    将注释转换为COCO格式

    参数:
    base_dir (str): 数据集主路径
    mode (str): 模式，train 或 valid
    """
    image_dir = os.path.join(base_dir, mode)
    label_dir = os.path.join(base_dir, mode)
    output_json = os.path.join(base_dir, mode, "_annotations.coco.json")
    
    images = []
    annotations = []
    categories = [{"id": 1, "name": "object", "supercategory": "object"}]
    category_count = defaultdict(int)
    bbox_count = 0
    
    image_files = glob.glob(os.path.join(image_dir, "*.jpg"))
    image_id = 0
    annotation_id = 0
    
    for image_file in track(image_files, description=f"Processing {mode} images"):
        image_id += 1
        file_name = os.path.basename(image_file)
        image = Image.open(image_file)
        width, height = image.size
        
        images.append(get_image_info(image_id, file_name, (width, height)))
        
        label_file = os.path.join(label_dir, os.path.splitext(file_name)[0] + ".txt")
        if not os.path.exists(label_file):
            continue

        with open(label_file, "r") as f:
            for line in f.readlines():
                parts = line.strip().split()
                category_id = int(parts[0])
                x_center, y_center, w, h = map(float, parts[1:])
                
                # 转换为绝对坐标
                x_center *= width
                y_center *= height
                w *= width
                h *= height
                x = x_center - w / 2
                y = y_center - h / 2
                
                annotations.append(get_annotation_info(annotation_id, image_id, category_id, [x, y, w, h]))
                category_count[category_id] += 1
                bbox_count += 1
                annotation_id += 1
    
    coco_format = {
        "info": {
            "description": "COCO format dataset",
            "url": "",
            "version": "1.0",
            "year": 2024,
            "contributor": "",
            "date_created": "2024/05/24"
        },
        "licenses": [
            {
                "id": 1,
                "name": "Unknown",
                "url": ""
            }
        ],
        "images": images,
        "annotations": annotations,
        "categories": categories
    }
    
    with open(output_json, "w") as f:
        json.dump(coco_format, f, indent=4)
    
    console.print(f"COCO format annotations saved to [green]{output_json}[/green]")
    
    # 打印总结报告
    print_summary_report(category_count, bbox_count, len(images))

def print_summary_report(category_count, bbox_count, image_count):
    """
    打印总结报告

    参数:
    category_count (dict): 类别数及其数量分布
    bbox_count (int): bbox框总数
    image_count (int): 图片文件总数
    """
    table = Table(title="Summary Report")

    table.add_column("Category ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="magenta")
    
    for category_id, count in category_count.items():
        table.add_row(str(category_id), str(count))
    
    console.print(table)
    console.print(f"Total bounding boxes: [bold]{bbox_count}[/bold]")
    console.print(f"Total images: [bold]{image_count}[/bold]")

def main(base_dir, mode):
    """
    主函数，处理指定路径和模式的文件

    参数:
    base_dir (str): 数据集主路径
    mode (str): 模式，train 或 valid
    """
    if mode not in ["train", "valid"]:
        console.print("[red]Error: Mode must be 'train' or 'valid'[/red]")
        return

    convert_annotations(base_dir, mode)

if __name__ == "__main__":
    fire.Fire(main)

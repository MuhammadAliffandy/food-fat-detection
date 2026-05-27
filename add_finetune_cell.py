import json

with open('train_yolov8.ipynb', 'r') as f:
    nb = json.load(f)

new_cell = {
  "cell_type": "code",
  "execution_count": None,
  "metadata": {},
  "outputs": [],
  "source": [
    "# 5.5 Continue Training (Fine-Tuning)\n",
    "# Jika kamu merasa mAP masih bisa naik dan ingin menambah epoch.\n",
    "# Kita akan me-load 'best.pt' sebelumnya, lalu melatihnya lagi.\n",
    "from ultralytics import YOLO\n",
    "import os\n",
    "\n",
    "best_weights = os.path.join(yolo_runs_path, 'yolov8_food_model_v2/weights/best.pt')\n",
    "if os.path.exists(best_weights):\n",
    "    print(\"Loading best weights to continue training...\")\n",
    "    fine_tune_model = YOLO(best_weights)\n",
    "    \n",
    "    # Lanjutkan training untuk 50 epoch lagi.\n",
    "    # Disimpan di folder baru '_finetune' agar tidak menimpa versi sebelumnya.\n",
    "    fine_tune_model.train(\n",
    "        data=yaml_path,\n",
    "        epochs=50,  # Set berapa epoch tambahan yang kamu inginkan\n",
    "        imgsz=640,\n",
    "        batch=16,\n",
    "        device=0,\n",
    "        project=yolo_runs_path,\n",
    "        name='yolov8_food_model_v2_finetune',\n",
    "        exist_ok=True,\n",
    "    )\n",
    "else:\n",
    "    print(\"Model utama belum selesai di-train!\")\n"
  ]
}

# Find index of Cell 5 (Train the Model)
insert_idx = -1
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and "5. Train the Model" in "".join(cell['source']):
        insert_idx = i + 1
        break

if insert_idx != -1:
    nb['cells'].insert(insert_idx, new_cell)
else:
    nb['cells'].append(new_cell)

with open('train_yolov8.ipynb', 'w') as f:
    json.dump(nb, f, indent=2)

print("Notebook updated with fine-tuning cell.")

import json

with open('train_yolov8.ipynb', 'r') as f:
    nb = json.load(f)

# Find index of Cell 3 (Paths setup)
insert_idx = 0
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and "3. Paths Definition" in "".join(cell['source']):
        insert_idx = i + 1
        break

new_cell = {
  "cell_type": "code",
  "execution_count": None,
  "metadata": {},
  "outputs": [],
  "source": [
    "# 3.5 Optional Data Augmentation & Calibration\n",
    "import random\n",
    "import shutil\n",
    "import os\n",
    "\n",
    "val_images_dir = os.path.join(dataset_path, 'valid/images')\n",
    "val_labels_dir = os.path.join(dataset_path, 'valid/labels')\n",
    "train_images_dir = os.path.join(dataset_path, 'train/images')\n",
    "train_labels_dir = os.path.join(dataset_path, 'train/labels')\n",
    "\n",
    "if os.path.exists(val_images_dir) and os.path.exists(train_images_dir):\n",
    "    val_images = os.listdir(val_images_dir)\n",
    "    # Select 25% for calibration mixing\n",
    "    sample_size = int(len(val_images) * 0.25)\n",
    "    selected_images = random.sample(val_images, sample_size)\n",
    "    \n",
    "    for img_name in selected_images:\n",
    "        # Get matching label\n",
    "        lbl_name = img_name.rsplit('.', 1)[0] + '.txt'\n",
    "        \n",
    "        # Copy to train\n",
    "        img_src = os.path.join(val_images_dir, img_name)\n",
    "        img_dst = os.path.join(train_images_dir, img_name)\n",
    "        if os.path.exists(img_src):\n",
    "            shutil.copy(img_src, img_dst)\n",
    "            \n",
    "        lbl_src = os.path.join(val_labels_dir, lbl_name)\n",
    "        lbl_dst = os.path.join(train_labels_dir, lbl_name)\n",
    "        if os.path.exists(lbl_src):\n",
    "            shutil.copy(lbl_src, lbl_dst)\n",
    "\n",
    "    print(f\"Data calibration complete: {sample_size} samples mixed.\")\n"
  ]
}

nb['cells'].insert(insert_idx, new_cell)

with open('train_yolov8.ipynb', 'w') as f:
    json.dump(nb, f, indent=2)

print("Notebook updated with calibration cell.")

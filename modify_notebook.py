import json

with open('train_yolov8.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        
        # 1. Fix the initialization cell to always start fresh
        if "checkpoint_path = os.path.join" in source and "Found checkpoint. Resuming training" in source:
            cell['source'] = [
                "from ultralytics import YOLO\n",
                "import os\n",
                "\n",
                "# 4. Initialize Fresh YOLOv8 Model\n",
                "# We DO NOT resume from the old checkpoint because the old checkpoint was trained on broken data.\n",
                "print(\"Starting fresh from yolov8n.pt...\")\n",
                "model = YOLO('yolov8n.pt')\n"
            ]
            
        # 2. Fix the training cell to remove manual hyperparameters and change project name
        if "results = model.train(" in source:
            cell['source'] = [
                "# 5. Train the Model\n",
                "results = model.train(\n",
                "    data=yaml_path,\n",
                "    epochs=50,\n",
                "    imgsz=640,\n",
                "    batch=16,\n",
                "    device=0,\n",
                "    project=yolo_runs_path,\n",
                "    name='yolov8_food_model_v2', # Menggunakan nama baru agar tidak menimpa yang lama\n",
                "    exist_ok=True,\n",
                "    # Menghapus manual hyperparameter (lr0, optimizer, dll) agar YOLOv8 menggunakan settingan Auto-Optimizer bawaan yang lebih stabil.\n",
                ")\n"
            ]
            
        # 3. Fix the evaluation cell to load from the new project name
        if "best_weights_path = os.path.join(yolo_runs_path, 'yolov8_food_model/weights/best.pt')" in source:
            new_source = []
            for line in cell['source']:
                if "'yolov8_food_model/weights/best.pt'" in line:
                    new_source.append(line.replace("'yolov8_food_model/weights/best.pt'", "'yolov8_food_model_v2/weights/best.pt'"))
                else:
                    new_source.append(line)
            cell['source'] = new_source

with open('train_yolov8.ipynb', 'w') as f:
    json.dump(nb, f, indent=2)

print("Notebook updated successfully.")

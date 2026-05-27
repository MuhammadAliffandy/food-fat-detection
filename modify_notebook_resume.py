import json

with open('train_yolov8.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        
        # 1. Update Cell 4 (Initialization)
        if "4. Initialize Fresh YOLOv8 Model" in source:
            cell['source'] = [
                "from ultralytics import YOLO\n",
                "import os\n",
                "\n",
                "# 4. Initialize YOLOv8 Model (with Resume Capability for v2)\n",
                "# We check if the NEW v2 checkpoint exists to resume. We DO NOT resume from the old broken v1.\n",
                "checkpoint_path = os.path.join(yolo_runs_path, 'yolov8_food_model_v2/weights/last.pt')\n",
                "\n",
                "if os.path.exists(checkpoint_path):\n",
                "    print(\"Found v2 checkpoint. Resuming training...\")\n",
                "    model = YOLO(checkpoint_path)\n",
                "    resume_status = True\n",
                "else:\n",
                "    print(\"No v2 checkpoint found. Starting fresh from yolov8n.pt...\")\n",
                "    model = YOLO('yolov8n.pt')\n",
                "    resume_status = False\n"
            ]
            
        # 2. Update Cell 5 (Train)
        if "5. Train the Model" in source:
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
                "    resume=resume_status,\n",
                "    # Menghapus manual hyperparameter (lr0, optimizer, dll) agar YOLOv8 menggunakan settingan Auto-Optimizer bawaan yang lebih stabil.\n",
                ")\n"
            ]

with open('train_yolov8.ipynb', 'w') as f:
    json.dump(nb, f, indent=2)

print("Notebook updated with resume functionality.")

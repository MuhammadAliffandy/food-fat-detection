# YOLOv8 Food Detection Web App

A Flask-based web application that utilizes a custom-trained YOLOv8 model (`best.pt`) to detect multiple food items in uploaded images, automatically fetches nutritional data from the FatSecret API, and provides a daily nutrition dashboard.

## Features
- **YOLOv8 Inference**: Upload an image to get bounding boxes and labels for detected foods.
- **FatSecret API Integration**: Automatically fetches Calories, Protein, Carbs, and Fat based on detected labels.
- **Session-Based Storage**: No login required. Data is stored securely using device/session IDs.
- **Clinical Dashboard**: Minimalist, high-contrast UI to track daily macros against targets.

## Setup Instructions

1. **Navigate to the app directory**:
   ```bash
   cd web_app
   ```

2. **Activate the Virtual Environment**:
   - Mac/Linux: `source venv/bin/activate`
   - Windows: `venv\\Scripts\\activate`

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory and add your FatSecret API credentials:
   ```env
   FATSECRET_CLIENT_ID=your_client_id_here
   FATSECRET_CLIENT_SECRET=your_client_secret_here
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your web browser.

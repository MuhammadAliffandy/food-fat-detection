import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# Import our custom modules
import database
import yolo_inference
import fatsecret_api

app = Flask(__name__)
app.secret_key = os.urandom(24) # Used for securely signing the session cookie

# Configuration for image uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Database
database.init_db()

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def ensure_session():
    """Ensure every user gets a unique session ID tied to their browser."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@app.route('/')
def dashboard():
    """
    Main dashboard view.
    Displays daily nutrition progress, today's food history, and target settings.
    """
    session_id = session['session_id']
    
    # 1. Get User Targets
    target = database.get_user_target(session_id)
    
    # 2. Get Today's History
    daily_logs = database.get_daily_history(session_id)
    
    # 3. Calculate Current Totals
    total_cal = sum(log['calories'] for log in daily_logs)
    total_pro = sum(log['protein'] for log in daily_logs)
    total_car = sum(log['carbs'] for log in daily_logs)
    total_fat = sum(log['fat'] for log in daily_logs)
    
    current_macros = {
        'calories': total_cal,
        'protein': total_pro,
        'carbs': total_car,
        'fat': total_fat
    }
    
    # Pass data to the template
    return render_template('dashboard.html', 
                           target=target, 
                           current=current_macros, 
                           logs=daily_logs)

import subprocess

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload, run YOLO inference, fetch nutrition, and log it."""
    if 'file' not in request.files:
        flash("Tidak ada file pada permintaan.", "error")
        return redirect(url_for('dashboard'))
        
    file = request.files['file']
    
    if file.filename == '':
        flash("Tidak ada file yang dipilih.", "error")
        return redirect(url_for('dashboard'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Handle macOS HEIC conversion natively using 'sips'
        if filepath.lower().endswith('.heic'):
            jpg_filepath = filepath.rsplit('.', 1)[0] + '.jpg'
            try:
                subprocess.run(['sips', '-s', 'format', 'jpeg', filepath, '--out', jpg_filepath], check=True, capture_output=True)
                os.remove(filepath) # Remove original HEIC
                filepath = jpg_filepath
            except Exception as e:
                flash(f"Gagal mengkonversi gambar HEIC: {e}", "error")
                return redirect(url_for('dashboard'))
        
        # 1. Run YOLOv8 Inference
        detected_foods, annotated_image_path = yolo_inference.run_inference(filepath, app.config['UPLOAD_FOLDER'])
        
        # ALWAYS store the path so the user can see the image, even if no food is detected
        if annotated_image_path:
            session['last_annotated_image'] = os.path.basename(annotated_image_path)
            
        # Clear previous latest foods
        if 'latest_foods' in session:
            session.pop('latest_foods')
        
        if not detected_foods:
            flash("Tidak ada makanan yang terdeteksi pada gambar. Coba gambar lain!", "warning")
            return redirect(url_for('dashboard'))
            
        session_id = session['session_id']
        foods_added = 0
        latest_foods = []
        
        # 2. For each detected food, fetch nutrition and save to DB
        for food_name in detected_foods:
            nutrition_data = fatsecret_api.fetch_nutrition_for_food(food_name)
            
            if nutrition_data:
                database.add_food_log(
                    session_id=session_id,
                    food_name=nutrition_data['food_name'],
                    calories=nutrition_data['calories'],
                    protein=nutrition_data['protein'],
                    carbs=nutrition_data['carbs'],
                    fat=nutrition_data['fat']
                )
                foods_added += 1
                latest_foods.append(nutrition_data)
            else:
                flash(f"Tidak dapat mengambil data nutrisi untuk '{food_name}'.", "warning")
                
        if latest_foods:
            session['latest_foods'] = latest_foods
                
        if foods_added > 0:
            flash(f"Berhasil memproses dan menambahkan {foods_added} makanan ke catatan harian Anda!", "success")
            
        return redirect(url_for('dashboard'))
        
    else:
        flash("Tipe file tidak valid. Harap unggah gambar yang valid (png, jpg, jpeg, heic).", "error")
        return redirect(url_for('dashboard'))

@app.route('/settings', methods=['POST'])
def update_settings():
    """Update user's daily nutritional targets."""
    session_id = session['session_id']
    
    try:
        cal = int(request.form.get('calories', 2000))
        pro = int(request.form.get('protein', 50))
        car = int(request.form.get('carbs', 250))
        fat = int(request.form.get('fat', 70))
        
        database.set_user_target(session_id, cal, pro, car, fat)
        flash("Target harian berhasil diperbarui.", "success")
    except ValueError:
        flash("Input tidak valid. Harap masukkan angka yang benar.", "error")
        
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    """Delete a specific food history log."""
    session_id = session['session_id']
    database.delete_food_log(session_id, log_id)
    flash("Riwayat makanan dihapus.", "success")
    return redirect(url_for('history'))

@app.route('/history')
def history():
    """
    View all food consumption history for the current session.
    Since get_daily_history filters by date, we'll fetch everything for the session.
    We'll bypass the date filter by extending database.py or using raw query here.
    For simplicity, let's execute a raw query or we can update database.py.
    """
    session_id = session['session_id']
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM food_history 
        WHERE session_id = ? 
        ORDER BY consumed_at DESC
    ''', (session_id,))
    all_logs = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', logs=all_logs)

if __name__ == '__main__':
    # Run the Flask application in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5001)

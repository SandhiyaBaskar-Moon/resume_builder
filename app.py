from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import io

# ✅ FIRST create app
app = Flask(__name__)

# Upload folder config
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ THEN routes
@app.route('/')
def home():
    return render_template('form.html')

@app.route('/preview', methods=['POST'])
def preview():
    data = request.form.to_dict()

    photo = request.files.get('photo')
    photo_filename = None

    if photo and photo.filename != "":
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    return render_template('resume.html', data=data, photo=photo_filename)

@app.route('/download', methods=['POST'])
def download():
    data = request.form

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    # Photo
    photo_filename = data.get('photo')
    if photo_filename:
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
        if os.path.exists(photo_path):
            pdf.drawImage(photo_path, width - 150, height - 150,
                          width=100, height=100, mask='auto')

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, data.get('name', ''))

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name="resume.pdf",
                     mimetype="application/pdf")

# ✅ LAST
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

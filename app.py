from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import io

# Create Flask app
app = Flask(__name__)

# Upload folder config
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home page (Form)
@app.route('/')
def home():
    return render_template('form.html')

# Preview Resume
@app.route('/preview', methods=['POST'])
def preview():
    data = request.form.to_dict()

    photo = request.files.get('photo')
    photo_filename = None

    if photo and photo.filename != "":
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    return render_template(
        'resume.html',
        data=data,
        photo=photo_filename
    )

# Download Resume as PDF
@app.route('/download', methods=['POST'])
def download():
    data = request.form.to_dict()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    # Add Photo (top right)
    photo_filename = data.get('photo')
    if photo_filename:
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
        if os.path.exists(photo_path):
            pdf.drawImage(
                photo_path,
                width - 150,
                height - 150,
                width=100,
                height=100,
                mask='auto'
            )

    # Name
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, data.get('name', ''))

    y -= 30
    pdf.setFont("Helvetica", 12)

    # Contact details
    if data.get('email'):
        pdf.drawString(50, y, f"Email: {data.get('email')}")
        y -= 18

    if data.get('phone'):
        pdf.drawString(50, y, f"Phone: {data.get('phone')}")
        y -= 18

    if data.get('linkedin'):
        pdf.drawString(50, y, f"LinkedIn: {data.get('linkedin')}")
        y -= 25

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="resume.pdf",
        mimetype="application/pdf"
    )

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

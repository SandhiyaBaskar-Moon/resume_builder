from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import io

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home Page – Form
@app.route("/")
def home():
    return render_template("form.html")

# Preview Resume
@app.route("/preview", methods=["POST"])
def preview():
    data = request.form.to_dict()

    # Photo upload
    photo = request.files.get("photo")
    photo_filename = ""
    if photo and photo.filename:
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

    # Signature upload
    signature = request.files.get("signature")
    sign_filename = ""
    if signature and signature.filename:
        sign_filename = secure_filename(signature.filename)
        signature.save(os.path.join(app.config["UPLOAD_FOLDER"], sign_filename))

    return render_template(
        "resume.html",
        data=data,
        photo=photo_filename,
        signature=sign_filename
    )

# Download PDF
@app.route("/download", methods=["POST"])
def download():
    data = request.form

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    # Name
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, y, data.get("name", ""))
    y -= 30

    pdf.setFont("Helvetica", 11)

    # Contact details
    if data.get("email"):
        pdf.drawString(50, y, f"Email: {data.get('email')}")
        y -= 15

    if data.get("phone"):
        pdf.drawString(50, y, f"Phone: {data.get('phone')}")
        y -= 15

    if data.get("linkedin"):
        pdf.drawString(50, y, f"LinkedIn: {data.get('linkedin')}")
        y -= 25

    # Helper function for sections
    def draw_section(title, content):
        nonlocal y
        if content and content.strip():
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y, title)
            y -= 18
            pdf.setFont("Helvetica", 11)
            for line in content.split("\n"):
                pdf.drawString(60, y, line)
                y -= 14
            y -= 10

    draw_section("Education", data.get("education", ""))
    draw_section("Skills", data.get("skills", ""))
    draw_section("Certifications", data.get("certifications", ""))
    draw_section("Internships", data.get("internships", ""))
    draw_section("Projects", data.get("projects", ""))

    # Photo (Top Right)
    photo = data.get("photo")
    if photo:
        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo)
        if os.path.exists(photo_path):
            pdf.drawImage(photo_path, width - 150, height - 150, 90, 90, mask="auto")

    # Signature (Bottom Left)
    signature = data.get("signature")
    if signature:
        sign_path = os.path.join(app.config["UPLOAD_FOLDER"], signature)
        if os.path.exists(sign_path):
            pdf.drawImage(sign_path, 50, 50, 120, 40, mask="auto")
            pdf.drawString(50, 40, "Signature")

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="resume.pdf",
        mimetype="application/pdf"
    )

# Run App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

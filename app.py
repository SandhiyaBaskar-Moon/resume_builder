from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("form.html")


@app.route("/preview", methods=["POST"])
def preview():
    data = {}
    fields = [
        "name", "email", "phone", "linkedin",
        "education", "skills", "projects",
        "internships", "certifications"
    ]

    for f in fields:
        value = request.form.get(f, "").strip()
        if value:
            if f == "skills":
                data[f] = [s.strip() for s in value.split(",") if s.strip()]
            else:
                data[f] = value

    # photo
    photo = request.files.get("photo")
    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        photo.save(photo_path)
        data["photo"] = photo_path

    # signature
    sign = request.files.get("signature")
    if sign and sign.filename:
        filename = secure_filename(sign.filename)
        sign_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        sign.save(sign_path)
        data["signature"] = sign_path

    app.config["DATA"] = data
    return render_template("resume.html", data=data)


@app.route("/download")
def download_pdf():
    data = app.config.get("DATA")

    file_path = "resume.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, data.get("name", ""))

    y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"{data.get('email','')} | {data.get('phone','')}")

    y -= 30
    c.setFont("Helvetica-Bold", 14)

    def section(title, content):
        nonlocal y
        if content:
            c.drawString(50, y, title)
            y -= 18
            c.setFont("Helvetica", 11)
            if isinstance(content, list):
                for i in content:
                    c.drawString(60, y, f"- {i}")
                    y -= 14
            else:
                c.drawString(60, y, content)
                y -= 18
            c.setFont("Helvetica-Bold", 14)
            y -= 10

    section("Education", data.get("education"))
    section("Skills", data.get("skills"))
    section("Projects", data.get("projects"))
    section("Internships", data.get("internships"))
    section("Certifications", data.get("certifications"))

    if "photo" in data:
        c.drawImage(data["photo"], width - 150, height - 180, 100, 120)

    if "signature" in data:
        c.drawImage(data["signature"], width - 200, 80, 120, 40)

    c.save()
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

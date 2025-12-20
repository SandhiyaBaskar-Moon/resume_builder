from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))

TEAL = colors.HexColor("#358597")
PEACH = colors.HexColor("#F4A896")

def ultra_clean(text):
    return text.encode("ascii", "ignore").decode("ascii") if text else ""

def clean(text, mode="normal"):
    if not text:
        return []
    if mode == "education":
        return [l.strip() for l in text.split("\n") if l.strip()]
    return [l.strip() for l in text.replace(".", "\n").split("\n") if l.strip()]

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/preview", methods=["POST"])
def preview():
    data = {}
    fields = ["name","email","phone","linkedin","education","projects","internships","certifications"]

    for f in fields:
        v = request.form.get(f, "").strip()
        if v:
            data[f] = ultra_clean(v)

    skills = request.form.get("skills","")
    if skills:
        data["skills"] = [ultra_clean(s.strip()) for s in skills.split(",") if s.strip()]

    photo = request.files.get("photo")
    if photo and photo.filename:
        p = secure_filename(photo.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], p)
        photo.save(path)
        data["photo"] = path

    sign = request.files.get("signature")
    if sign and sign.filename:
        s = secure_filename(sign.filename)
        spath = os.path.join(app.config["UPLOAD_FOLDER"], s)
        sign.save(spath)
        data["signature"] = spath

    app.config["DATA"] = data
    return render_template("resume.html", data=data)

@app.route("/download")
def download_pdf():
    data = app.config.get("DATA", {})
    file_path = "resume_final.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    LEFT_W = 190
    RIGHT_X = LEFT_W + 25

    # LEFT PANEL
    c.setFillColor(TEAL)
    c.rect(0, 0, LEFT_W, height, fill=1)

    if "photo" in data:
        c.drawImage(data["photo"], 35, height - 200, 120, 140, mask="auto")

    y_left = height - 230

    c.setFont("DejaVu", 16)
    c.setFillColor(colors.white)
    c.drawCentredString(LEFT_W / 2, y_left, data.get("name", "").upper())
    y_left -= 26

    c.setFont("DejaVu", 9)
    for k in ["email", "phone"]:
        if data.get(k):
            c.drawCentredString(LEFT_W / 2, y_left, data[k])
            y_left -= 14

    if data.get("linkedin"):
        link = data["linkedin"]
        MAX = 26
        if len(link) <= MAX:
            c.drawCentredString(LEFT_W / 2, y_left, link)
            y_left -= 14
        else:
            c.drawCentredString(LEFT_W / 2, y_left, link[:MAX])
            y_left -= 12
            c.drawCentredString(LEFT_W / 2, y_left, link[MAX:])
            y_left -= 14

    if data.get("skills"):
        y_left -= 18
        c.setFont("DejaVu", 13)
        c.setFillColor(PEACH)
        c.drawCentredString(LEFT_W / 2, y_left, "SKILLS")
        y_left -= 18

        c.setFont("DejaVu", 10)
        c.setFillColor(colors.white)
        for s in data["skills"]:
            c.drawString(30, y_left, f"• {s}")
            y_left -= 14

    # RIGHT CONTENT
    y = height - 80

    def section(title, content, mode="normal"):
        nonlocal y
        lines = clean(content, mode)
        if not lines:
            return

        c.setFont("DejaVu", 14)
        c.setFillColor(TEAL)
        c.drawString(RIGHT_X, y, title.upper())
        y -= 14

        c.setFont("DejaVu", 11)
        c.setFillColor(colors.black)

        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = "DejaVu"
        style.fontSize = 11
        style.leading = 14

        max_width = width - RIGHT_X - 30

        for l in lines:
            p = Paragraph("&bull;&nbsp;" + l, style)
            w, h = p.wrap(max_width, height)
            p.drawOn(c, RIGHT_X + 15, y - h)
            y -= h + 6

        y -= 18

    # ✅ SECTION CALLS — FUNCTION VELIYA
    section("Education", data.get("education"), "education")
    section("Projects", data.get("projects"))
    section("Internships", data.get("internships"))
    section("Certifications", data.get("certifications"))

    if data.get("signature"):
        c.drawImage(data["signature"], RIGHT_X, 60, 120, 40, mask="auto")

    c.save()
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run()


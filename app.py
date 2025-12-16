from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

# Home page – Resume form
@app.route('/')
def home():
    return render_template('form.html')

# Preview resume
@app.route('/preview', methods=['POST'])
def preview():
    data = request.form
    return render_template('resume.html', data=data)

# Download resume as PDF
@app.route('/download', methods=['POST'])
def download():
    data = request.form

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    # Name
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, data.get('name', ''))
    y -= 30

    # Contact details
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Email: {data.get('email', '')}")
    y -= 15
    pdf.drawString(50, y, f"Phone: {data.get('phone', '')}")
    y -= 15
    pdf.drawString(50, y, f"LinkedIn: {data.get('linkedin', '')}")
    y -= 25

    # Helper function for sections
    def draw_section(title, content):
        nonlocal y
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(50, y, title)
        y -= 15

        pdf.setFont("Helvetica", 11)
        for line in content.split('\n'):
            pdf.drawString(60, y, line)
            y -= 14
        y -= 10

    # Education
    education = (
        f"Masters Degree: {data.get('masters', '')}\n"
        f"Bachelors Degree: {data.get('bachelors', '')}\n"
        f"HSC: {data.get('hsc', '')}\n"
        f"SSLC: {data.get('sslc', '')}"
    )
    draw_section("Education Qualification", education)

    # Professional details
    draw_section("Skills", data.get('skills', ''))
    draw_section("Certifications", data.get('certifications', ''))
    draw_section("Internships", data.get('internships', ''))
    draw_section("Projects", data.get('projects', ''))

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="resume.pdf",
        mimetype="application/pdf"
    )

if __name__ == '__main__':
    app.run(debug=True)

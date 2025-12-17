@app.route('/download', methods=['POST'])
def download():
    data = request.form

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    # 👉 PHOTO
    photo_filename = data.get('photo')
    if photo_filename:
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
        if os.path.exists(photo_path):
            pdf.drawImage(photo_path, width - 150, height - 150,
                          width=100, height=100, mask='auto')

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

    def draw_section(title, content):
        nonlocal y
        if not content:
            return
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(50, y, title)
        y -= 15
        pdf.setFont("Helvetica", 11)
        for line in content.split('\n'):
            pdf.drawString(60, y, line)
            y -= 14
        y -= 10

    education = (
        f"Masters Degree: {data.get('masters', '')}\n"
        f"Bachelors Degree: {data.get('bachelors', '')}\n"
        f"HSC: {data.get('hsc', '')}\n"
        f"SSLC: {data.get('sslc', '')}"
    )

    draw_section("Education Qualification", education)
    draw_section("Skills", data.get('skills', ''))
    draw_section("Certifications", data.get('certifications', ''))
    draw_section("Internships", data.get('internships', ''))
    draw_section("Projects", data.get('projects', ''))

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name="resume.pdf",
                     mimetype="application/pdf")

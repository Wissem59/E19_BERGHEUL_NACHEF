from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_evaluation_report(evaluation):
    # Create the filename
    filename = f"evaluation_report_{evaluation.employee.name}_{evaluation.date}.pdf"

    # Initialize the PDF canvas
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title section
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "Employee Evaluation Report")

    # Subtitle
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 70, f"{evaluation.employee.name} - {evaluation.date.strftime('%Y-%m-%d')}")

    # Horizontal line
    c.setLineWidth(1)
    c.setStrokeColor(colors.grey)
    c.line(50, height - 80, width - 50, height - 80)

    # Employee details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 110, "Employee Details")
    c.setFont("Helvetica", 12)
    c.drawString(70, height - 130, f"Name: {evaluation.employee.name}")
    c.drawString(70, height - 145, f"Evaluation Date: {evaluation.date.strftime('%Y-%m-%d')}")
    c.drawString(70, height - 160, f"Evaluation Type: {evaluation.get_evaluation_type_display()}")
    c.drawString(70, height - 175, f"Performance Rating: {evaluation.performance_rating}")
    c.drawString(70, height - 190, f"Skills Developed: {evaluation.skills_developed}")

    # Manager's comments
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 220, "Manager's Comments")
    c.setFont("Helvetica", 12)
    c.drawString(70, height - 240, f"{evaluation.comments}")

    # Evaluation criteria
    if evaluation.criteria:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 270, "Evaluation Criteria")
        
        # Assuming evaluation.criteria is a dictionary
        criteria = evaluation.criteria
        y_position = height - 290
        c.setFont("Helvetica", 12)

        for key, value in criteria.items():
            c.drawString(70, y_position, f"{key}:")
            c.drawString(200, y_position, str(value))
            y_position -= 15

            if y_position < 50:  # Handle page overflow
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 50

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 30, "Page 1")

    # Save the PDF
    c.save()
    return filename

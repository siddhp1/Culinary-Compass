from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf(file_name):
    # Create a PDF document
    pdf_canvas = canvas.Canvas(file_name, pagesize=letter)

    # Set font and size for the heading
    pdf_canvas.setFont("Helvetica-Bold", 16)

    # Calculate the width of the page and the center point
    page_width, page_height = letter
    heading = "Your Culinary Mapped"
    heading_width = pdf_canvas.stringWidth(heading, "Helvetica-Bold", 16)
    center_x = (page_width - heading_width) / 2

    # Draw the centered heading
    pdf_canvas.drawString(center_x, page_height - 50, heading)

    # Set font and size for the subheadings
    pdf_canvas.setFont("Helvetica", 12)

    # Draw three subheadings
    subheadings = ["Name Here", "Favourite Resturants", "Favourite Genres"]
    y_position = page_height - 100

    for subheading in subheadings:
        subheading_width = pdf_canvas.stringWidth(subheading, "Helvetica", 12)
        center_x = (page_width - subheading_width) / 2
        pdf_canvas.drawString(center_x, y_position, subheading)
        y_position -= 250

    # Save the PDF file
    pdf_canvas.save()

if __name__ == "__main__":
    create_pdf("centered_heading.pdf")

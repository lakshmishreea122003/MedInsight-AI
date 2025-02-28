from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io


class PDFGenerator:
    def __init__(self, text_data, file_path_pdf):
        self.text_data = text_data
        self.file_path_pdf = file_path_pdf

    def create_pdf(self):
        # Create a buffer to hold the PDF data
        buffer = io.BytesIO()

        # Create a PDF with reportlab
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Define a title
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 50, "Clinical Data Report")

        # Define the starting position
        text = c.beginText(50, height - 100)
        text.setFont("Helvetica", 10)
        max_width = width - 100  # Set the max width for text wrapping

        # Split the text into lines
        lines = self.text_data.split('\n')

        for line in lines:
            # Wrap text to fit within the page width
            wrapped_lines = self.wrap_text(line, max_width, c)
            for wrapped_line in wrapped_lines:
                text.textLine(wrapped_line)
                # Check if the text exceeds the page height
                if text.getY() < 50:
                    c.drawText(text)
                    c.showPage()
                    text = c.beginText(50, height - 50)
                    text.setFont("Helvetica", 10)

        c.drawText(text)
        c.showPage()
        c.save()

        # Move buffer position to the beginning
        buffer.seek(0)

        # Save the PDF to a file
        with open(r"D:\h1\AIHealthCare\AIHealthCare\data\R.pdf", 'wb') as f:
            f.write(buffer.getvalue())

        return buffer

    @staticmethod
    def wrap_text(text, max_width, canvas):
        """Wrap text to fit within a specified width."""
        lines = []
        words = text.split(' ')
        line = ''
        for word in words:
            test_line = f"{line} {word}".strip()
            if canvas.stringWidth(test_line, "Helvetica", 10) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)  # Add the last line
        return lines
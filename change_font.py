import fitz  # PyMuPDF

def extract_text_with_default_font(pdf_path, default_font='Arial'):
    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    extracted_text = ""

    # Iterate through each page
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)

        # Extract text from the page
        text = page.get_text()

        # Check if the text contains any fonts that are not available
        if page.get_fonts():
            for font in page.get_fonts():
                print(font)
                # if font != default_font:
                    # Replace non-default fonts with the default font
                text = text.replace(font[3], default_font)

        # Append the extracted text to the result
        extracted_text += text

    # Close the PDF
    pdf_document.close()

    return extracted_text


# Example usage
pdf_path = 'sample.pdf'
default_font = 'Arial'
extracted_text = extract_text_with_default_font(pdf_path, default_font)
print(extracted_text)

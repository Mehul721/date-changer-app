
import streamlit as st
import re
from datetime import datetime
from docx import Document
from io import BytesIO
import tempfile

st.set_page_config(page_title="Date Changer", layout="centered")

st.title("📅 Date Format Replacer for .docx Files")

uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"])
target_date = st.date_input("Choose the new target date")

# Convert datetime object to various formats
def generate_formats(new_date):
    return {
        "dd-mm-yyyy": new_date.strftime("%d-%m-%Y"),
        "dd/mm/yyyy": new_date.strftime("%d/%m/%Y"),
        "d Month yyyy": new_date.strftime("%d %B %Y"),
        "ddMONyyyy": new_date.strftime("%d%b%Y").upper(),
        "Month/d": new_date.strftime("%B/%d"),
        "dMonth": new_date.strftime("%d%B"),
        "Monthd": new_date.strftime("%B%d")
    }

# Date matching regex patterns
date_patterns = {
    r"\b\d{2}[/-]\d{2}[/-]\d{4}\b": "dd/mm/yyyy or dd-mm-yyyy",
    r"\b\d{2}[A-Z]{3}\d{4}\b": "ddMONyyyy",
    r"\b\d{1,2} [A-Z][a-z]+ \d{4}\b": "d Month yyyy",
    r"\b[A-Z][a-z]+/\d{2}\b": "Month/dd",
    r"\b\d{1,2}[A-Z][a-z]+\b": "dMonth",
    r"\b[A-Z][a-z]+\d{1,2}\b": "Monthd"
}

def replace_dates_in_text(text, new_date):
    new_values = generate_formats(new_date)
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Format-preserving logic
            if re.match(r"\d{2}/\d{2}/\d{4}", match):
                text = text.replace(match, new_values["dd/mm/yyyy"])
            elif re.match(r"\d{2}-\d{2}-\d{4}", match):
                text = text.replace(match, new_values["dd-mm-yyyy"])
            elif re.match(r"\d{2}[A-Z]{3}\d{4}", match):
                text = text.replace(match, new_values["ddMONyyyy"])
            elif re.match(r"\d{1,2} [A-Z][a-z]+ \d{4}", match):
                text = text.replace(match, new_values["d Month yyyy"])
            elif re.match(r"[A-Z][a-z]+/\d{2}", match):
                text = text.replace(match, new_values["Month/d"])
            elif re.match(r"\d{1,2}[A-Z][a-z]+", match):
                text = text.replace(match, new_values["dMonth"])
            elif re.match(r"[A-Z][a-z]+\d{1,2}", match):
                text = text.replace(match, new_values["Monthd"])
    return text

if uploaded_file:
    doc = Document(uploaded_file)
    for para in doc.paragraphs:
        para.text = replace_dates_in_text(para.text, target_date)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                cell.text = replace_dates_in_text(cell.text, target_date)

    # Save to BytesIO
    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)

    st.success("✅ Dates replaced successfully!")
    st.download_button("📥 Download Modified .docx", output_stream, file_name="updated_dates.docx")

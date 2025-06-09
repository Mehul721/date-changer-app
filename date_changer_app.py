import streamlit as st
import re
from datetime import datetime
from docx import Document
from io import BytesIO
import os

st.set_page_config(page_title="Date Changer", layout="centered")
st.title("📅 Date Format Replacer for .docx Files")

uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"])
target_date = st.date_input("Choose the new target date")

# Convert datetime to multiple format styles
def generate_formats(new_date):
    return {
        "YYYY-MM-DD": new_date.strftime("%Y-%m-%d"),
        "YYYY/MM/DD": new_date.strftime("%Y/%m/%d"),
        "YYYY-MM": new_date.strftime("%Y-%m"),
        "YYYY/MM": new_date.strftime("%Y/%m"),
        "dd-mm-yyyy": new_date.strftime("%d-%m-%Y"),
        "dd/mm/yyyy": new_date.strftime("%d/%m/%Y"),
        "d Month yyyy": new_date.strftime("%d %B %Y"),
        "ddMONyyyy": new_date.strftime("%d%b%Y").upper(),
        "Month/d": new_date.strftime("%B/%d"),
        "dMonth": new_date.strftime("%d%B"),
        "Monthd": new_date.strftime("%B%d")
    }

# Regex patterns for detecting dates
date_patterns = {
    r"\b\d{4}-\d{2}-\d{2}\b": "YYYY-MM-DD",
    r"\b\d{4}/\d{2}/\d{2}\b": "YYYY/MM/DD",
    r"\b\d{4}-\d{2}\b": "YYYY-MM",
    r"\b\d{4}/\d{2}\b": "YYYY/MM",
    r"\b\d{2}/\d{2}/\d{4}\b": "dd/mm/yyyy",
    r"\b\d{2}-\d{2}-\d{4}\b": "dd-mm-yyyy",
    r"\b\d{2}[A-Z]{3}\d{4}\b": "ddMONyyyy",
    r"\b\d{1,2} [A-Z][a-z]+ \d{4}\b": "d Month yyyy",
    r"\b[A-Z][a-z]+/\d{2}\b": "Month/d",
    r"\b\d{1,2}[A-Z][a-z]+\b": "dMonth",
    r"\b[A-Z][a-z]+\d{1,2}\b": "Monthd"
}

# Replace matching dates in the text
def replace_dates_in_text(text, new_date):
    new_values = generate_formats(new_date)
    for pattern, label in date_patterns.items():
        matches = re.findall(pattern, text)
        for match in matches:
            text = text.replace(match, new_values[label])
    return text

# Process uploaded file
if uploaded_file:
    doc = Document(uploaded_file)
    original_name = os.path.splitext(uploaded_file.name)[0]

    for para in doc.paragraphs:
        para.text = replace_dates_in_text(para.text, target_date)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                cell.text = replace_dates_in_text(cell.text, target_date)

    # Save to memory stream
    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)

    st.success("✅ Dates replaced successfully!")
    st.download_button(
        "📥 Download Modified .docx",
        output_stream,
        file_name=f"{original_name}-updated.docx"
    )

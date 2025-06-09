import streamlit as st
import re
import os
from datetime import datetime
from io import BytesIO
from docx import Document

st.set_page_config(page_title="📅 Date Changer", layout="centered")
st.title("📁 Date Replacer for .docx and .txt Files")

def build_flexible_date_regex():
    months = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|" \
             r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|" \
             r"Nov(?:ember)?|Dec(?:ember)?)"
    patterns = [
        r"\d{1,2}/\d{1,2}/\d{4}",
        r"\d{1,2}-\d{1,2}-\d{4}",
        r"\d{1,2}\.\d{1,2}\.\d{4}",
        rf"\d{{1,2}} ?{months} ?\d{{4}}",
        rf"\d{{1,2}}{months}\d{{4}}",
        rf"{months}/\d{{1,2}}",
        rf"{months}\d{{2}}",
        rf"\d{{2}}{months}",
    ]
    return "|".join(patterns)

def format_preserving_replace(match, new_date_obj):
    old = match.group(0)
    day = new_date_obj.strftime('%d')
    month = new_date_obj.strftime('%B')
    mon_abbr = new_date_obj.strftime('%b')
    mon_number = new_date_obj.strftime('%m')
    year = new_date_obj.strftime('%Y')

    if re.match(r"\d{1,2}/\d{1,2}/\d{4}", old):
        return f"{day}/{mon_number}/{year}"
    elif re.match(r"\d{1,2}-\d{1,2}-\d{4}", old):
        return f"{day}-{mon_number}-{year}"
    elif re.match(r"\d{1,2}\.\d{1,2}\.\d{4}", old):
        return f"{day}.{mon_number}.{year}"
    elif re.match(r"\d{1,2}(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\d{4}", old, re.IGNORECASE):
        return f"{day}{mon_abbr}{year}"
    elif re.match(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\d{2}", old, re.IGNORECASE):
        return f"{mon_abbr}{day}"
    elif re.match(r"(January|February|March|April|May|June|July|August|September|October|November|December)/\d{1,2}", old, re.IGNORECASE):
        return f"{month}/{day}"
    elif re.match(r"\d{1,2}(January|February|March|April|May|June|July|August|September|October|November|December)\d{4}", old, re.IGNORECASE):
        return f"{day}{month}{year}"
    elif re.match(r"\d{1,2} ?(January|February|March|April|May|June|July|August|September|October|November|December) ?\d{4}", old, re.IGNORECASE):
        return f"{day} {month} {year}"
    else:
        return new_date_obj.strftime('%Y-%m-%d')

def replace_in_runs(paragraph, new_date_obj, date_pattern):
    combined_text = ''.join(run.text for run in paragraph.runs)
    matches = list(date_pattern.finditer(combined_text))
    if not matches:
        return 0

    for match in reversed(matches):
        start, end = match.span()
        replacement = format_preserving_replace(match, new_date_obj)
        combined_text = combined_text[:start] + replacement + combined_text[end:]

    char_index = 0
    for run in paragraph.runs:
        run_len = len(run.text)
        run.text = combined_text[char_index:char_index + run_len]
        char_index += run_len

    return len(matches)

def process_file(uploaded_file, new_date_obj, filename):
    ext = os.path.splitext(filename)[1].lower()
    pattern = re.compile(build_flexible_date_regex(), flags=re.IGNORECASE)

    if ext == ".txt":
        content = uploaded_file.read().decode("utf-8", errors="replace")
        updated_content = pattern.sub(lambda m: format_preserving_replace(m, new_date_obj), content)
        return BytesIO(updated_content.encode("utf-8")), filename.replace(ext, "_updated.txt")

    elif ext == ".docx":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            replace_in_runs(para, new_date_obj, pattern)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        replace_in_runs(para, new_date_obj, pattern)

        for section in doc.sections:
            for part in [section.header, section.footer]:
                for para in part.paragraphs:
                    replace_in_runs(para, new_date_obj, pattern)

        output_stream = BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream, filename.replace(ext, "_updated.docx")

    else:
        raise ValueError("Unsupported file type")

# Streamlit UI
uploaded_file = st.file_uploader("Upload a .docx or .txt file", type=["docx", "txt"])
target_date = st.date_input("Select the new date", datetime.today())

if uploaded_file:
    filename = uploaded_file.name
    if st.button("🔁 Replace Dates"):
        with st.spinner("Processing..."):
            try:
                buffer, updated_name = process_file(uploaded_file, target_date, filename)
                st.success("✅ Dates replaced successfully!")
                st.download_button(
                    "📥 Download Updated File",
                    data=buffer,
                    file_name=updated_name,
                    mime="application/octet-stream"
                )
            except Exception as e:
                st.error(f"Error: {e}")


import pymupdf
import os

base = "/Users/namitshastry/Desktop/Airfare Index"
output_dir = os.path.join(base, ".extracted")
os.makedirs(output_dir, exist_ok=True)

pdfs = [
    "AeroIndex .pdf",
    "AeroIndex_FareOS_Venture_and_Technical_Specification.pdf",
    "SIH26056.pdf",
    "Topics Study Guide.pdf"
]

for pdf_name in pdfs:
    pdf_path = os.path.join(base, pdf_name)
    if not os.path.exists(pdf_path):
        print(f"MISSING: {pdf_name}")
        continue
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    out_name = pdf_name.replace(".pdf", ".txt").replace(" ", "_")
    out_path = os.path.join(output_dir, out_name)
    with open(out_path, "w") as f:
        f.write(text)
    print(f"Extracted {pdf_name}: {len(text)} chars, {len(doc)} pages -> {out_name}")
    doc.close()

import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd

from text_parser import parse_receipt
from validation_ui import validate_receipt
from queries import save_receipt, receipt_exists


# ===== SECTION HEADER HELPER =====
def _section_header(title, subtitle=""):
    """Renders a styled section header consistent with app.py theme."""
    subtitle_html = f'<div style="font-size:0.85rem;color:#64748b;margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:1rem;padding-bottom:0.625rem;border-bottom:2px solid #e2e8f0;">
        <div style="font-size:1.15rem;font-weight:700;color:#1e293b;letter-spacing:-0.025em;">{title}</div>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


# ===== STATUS BADGE HELPER =====
def _status_badge(text, variant="info"):
    """Renders an inline status badge."""
    colors = {
        "success": ("#059669", "rgba(5,150,105,0.08)", "#d1fae5"),
        "error":   ("#dc2626", "rgba(220,38,38,0.08)", "#fee2e2"),
        "info":    ("#2563eb", "rgba(37,99,235,0.08)", "#dbeafe"),
        "warning": ("#d97706", "rgba(217,119,6,0.08)", "#fef3c7"),
    }
    fg, bg, border_c = colors.get(variant, colors["info"])
    st.markdown(f"""
    <div style="
        display:inline-block;
        background:{bg};
        color:{fg};
        border:1px solid {border_c};
        border-radius:8px;
        padding:0.35rem 0.85rem;
        font-size:0.82rem;
        font-weight:600;
        letter-spacing:0.02em;
        margin-bottom:0.5rem;
    ">{text}</div>
    """, unsafe_allow_html=True)


def render_upload_ui():
    # ===== PAGE-LEVEL STYLES (scoped to upload section) =====
    st.markdown("""
    <style>
        /* Card wrapper */
        .upload-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.5rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            margin-bottom: 1rem;
        }

        /* Primary action button override */
        .extract-btn .stButton > button {
            background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.01em;
            box-shadow: 0 4px 14px rgba(59,130,246,0.3) !important;
            transition: all 0.25s ease !important;
        }

        .extract-btn .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(59,130,246,0.4) !important;
        }

        /* Summary table styling */
        .summary-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.2rem;
        }

        .summary-value {
            font-size: 1.05rem;
            font-weight: 700;
            color: #1e293b;
        }

        .summary-cell {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            text-align: center;
        }

        /* Image viewer styling */
        .image-viewer {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 0.75rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }

        .image-viewer img {
            border-radius: 10px;
        }

        .image-label {
            text-align: center;
            font-size: 0.8rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid #f1f5f9;
        }

        /* Extraction method badge */
        .method-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.3rem 0.75rem;
            border-radius: 20px;
        }

        .method-ai {
            background: rgba(99,102,241,0.1);
            color: #6366f1;
            border: 1px solid rgba(99,102,241,0.2);
        }

        .method-ocr {
            background: rgba(245,158,11,0.1);
            color: #d97706;
            border: 1px solid rgba(245,158,11,0.2);
        }
    </style>
    """, unsafe_allow_html=True)

    # ===== SECTION HEADER =====
    _section_header("Upload Receipt", "Upload a receipt image or PDF to extract and save transaction data")

    # ===== FILE UPLOADER =====
    uploaded = st.file_uploader(
        "Upload receipt image or PDF",
        type=["png", "jpg", "jpeg", "pdf"],
        label_visibility="collapsed",
    )

    if not uploaded:
        # Empty state card
        st.markdown("""
        <div style="
            background:#ffffff;
            border:2px dashed #cbd5e1;
            border-radius:14px;
            padding:3rem 2rem;
            text-align:center;
            margin-top:0.5rem;
        ">
            <div style="font-size:2.5rem;margin-bottom:0.75rem;">&#128196;</div>
            <div style="font-size:1rem;font-weight:600;color:#334155;margin-bottom:0.35rem;">
                No file uploaded yet
            </div>
            <div style="font-size:0.85rem;color:#94a3b8;">
                Drag and drop a receipt image or PDF above, or click "Browse files" to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ================= IMAGE PROCESSING =================
    if uploaded.type == "application/pdf":
        from pdf_processor import pdf_to_images
        with st.spinner("Converting PDF to image..."):
            try:
                pdf_images = pdf_to_images(uploaded.read())
                if not pdf_images:
                    st.error("Could not convert PDF to image")
                    return
                img = pdf_images[0]  # Take first page
            except Exception as e:
                st.error(f"PDF Processing Error: {e}")
                st.info("Ensure Poppler is installed and path is correct in `ocr/pdf_processor.py`.")
                return
    else:
        img = Image.open(uploaded)

    # ===== IMAGE PREVIEW (side by side in cards) =====
    _section_header("Image Preview", "Original and processed views of the uploaded receipt")

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown('<div class="image-viewer">', unsafe_allow_html=True)
        st.image(img, use_container_width=True)
        st.markdown('<div class="image-label">Original Image</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        gray = img.convert("L")
        st.markdown('<div class="image-viewer">', unsafe_allow_html=True)
        st.image(gray, use_container_width=True)
        st.markdown('<div class="image-label">Processed (Grayscale)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ===== EXTRACT BUTTON =====
    st.markdown('<div class="extract-btn">', unsafe_allow_html=True)
    extract_clicked = st.button("Extract & Save Receipt", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    if not extract_clicked:
        return

    # ================= OCR + PARSE =================
    data = None
    items = []

    api_key = st.session_state.get("GEMINI_API_KEY")
    use_ai = bool(api_key)
    extraction_method = None

    with st.spinner("Extracting receipt data..."):
        if use_ai:
            from gemini_client import GeminiClient
            try:
                client = GeminiClient(api_key)
                result = client.extract_receipt(img)
                if result:
                    items = result.pop("items", [])
                    data = result
                    extraction_method = "ai"
            except Exception as e:
                st.error(f"AI Extraction failed: {e}. Falling back to OCR.")
                use_ai = False

        if not data:
            # Fallback to Tesseract
            import numpy as np
            import cv2
            from image_preprocessing import preprocess_image
            gray_preprocessed = preprocess_image(img)
            text = pytesseract.image_to_string(gray_preprocessed)
            if not text.strip():
                st.error("No readable text detected from the image.")
                return
            data, items = parse_receipt(text)
            extraction_method = "ocr"

    st.session_state["LAST_EXTRACTED_RECEIPT"] = data

    # ===== EXTRACTION METHOD INDICATOR =====
    if extraction_method == "ai":
        st.markdown('<span class="method-badge method-ai">AI Extraction</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="method-badge method-ocr">OCR Extraction</span>', unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ================= RECEIPT SUMMARY =================
    _section_header("Receipt Summary", "Key details extracted from the receipt")

    # Summary as styled metric cards
    m1, m2, m3, m4 = st.columns(4, gap="medium")
    with m1:
        st.metric(label="Bill ID", value=data.get("bill_id", "N/A"))
    with m2:
        st.metric(label="Vendor", value=data.get("vendor", "Unknown"))
    with m3:
        st.metric(label="Category", value=data.get("category", "Uncategorized"))
    with m4:
        st.metric(label="Date", value=data.get("date", "N/A"))

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3, gap="medium")
    with f1:
        st.metric(label="Subtotal", value=f"\u20b9 {round(data.get('subtotal', 0.0), 2):,.2f}")
    with f2:
        st.metric(label="Tax", value=f"\u20b9 {round(data.get('tax', 0.0), 2):,.2f}")
    with f3:
        st.metric(label="Total Amount", value=f"\u20b9 {round(data.get('amount', 0.0), 2):,.2f}")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ================= ITEM-WISE DETAILS =================
    _section_header("Item-wise Details", "Individual line items detected from the receipt")

    if items and len(items) > 0:
        st.dataframe(
            items,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.markdown("""
        <div style="
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:12px;
            padding:2rem;
            text-align:center;
        ">
            <div style="font-size:0.9rem;color:#94a3b8;font-weight:500;">
                No item-wise details detected from this receipt.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ================= DUPLICATE CHECK =================
    _section_header("Status", "Duplicate check and validation results")

    if receipt_exists(data["bill_id"]):
        _status_badge("Duplicate Detected -- Receipt NOT saved to database", "error")
        return
    else:
        _status_badge("No duplicate found", "success")

    # ================= VALIDATION =================
    validation = validate_receipt(data)
    st.session_state["LAST_VALIDATION_REPORT"] = validation

    # ================= SAVE (EVEN IF VALIDATION FAILS) =================
    save_receipt(data)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if validation["passed"]:
        st.success("Receipt passed validation and was saved successfully.")
    else:
        st.error("Receipt failed validation but was saved to the database.")

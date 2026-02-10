import streamlit as st
from datetime import datetime
from queries import fetch_all_receipts, receipt_exists

EXPECTED_TAX_RATE = 0.08   # 8%
TOLERANCE = 0.05           # 5% tolerance


# ===================================================================
#  SCOPED CSS  --  matches app.py slate / blue / Inter theme
# ===================================================================
VALIDATION_CSS = """
<style>
    /* ---------- Section Header ---------- */
    .val-section-hdr {
        margin-bottom: 0.25rem;
    }
    .val-section-hdr h2 {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
        letter-spacing: -0.03em;
    }
    .val-section-hdr p {
        font-size: 0.85rem;
        color: #64748b;
        margin: 0.15rem 0 0.75rem 0;
    }
    .val-section-hdr .hdr-line {
        height: 3px;
        width: 48px;
        background: linear-gradient(135deg, #3b82f6, #818cf8);
        border-radius: 4px;
        margin-bottom: 1.25rem;
    }

    /* ---------- Result Card ---------- */
    .val-card {
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.65rem;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .val-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07);
    }
    .val-card.pass {
        background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
        border-left: 4px solid #22c55e;
    }
    .val-card.fail {
        background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
        border-left: 4px solid #ef4444;
    }
    .val-card .icon {
        font-size: 1.25rem;
        flex-shrink: 0;
        width: 28px;
        text-align: center;
        padding-top: 2px;
    }
    .val-card .content {
        flex: 1;
        min-width: 0;
    }
    .val-card .title {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-weight: 700;
        font-size: 0.88rem;
        color: #1e293b;
        margin-bottom: 2px;
    }
    .val-card .msg {
        font-size: 0.82rem;
        color: #475569;
        line-height: 1.45;
    }

    /* ---------- Overall Verdict Banner ---------- */
    .verdict-banner {
        border-radius: 14px;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-top: 0.75rem;
        margin-bottom: 0.5rem;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    .verdict-banner.pass {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: #ffffff;
        box-shadow: 0 4px 14px rgba(34, 197, 94, 0.3);
    }
    .verdict-banner.fail {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: #ffffff;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3);
    }
    .verdict-banner .v-icon {
        font-size: 1.35rem;
    }
    .verdict-banner .v-text {
        font-size: 0.95rem;
        font-weight: 700;
    }

    /* ---------- Empty State Card ---------- */
    .empty-state-card {
        background: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 14px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        color: #94a3b8;
        margin-bottom: 1rem;
    }
    .empty-state-card .es-icon {
        font-size: 2.25rem;
        margin-bottom: 0.5rem;
    }
    .empty-state-card .es-title {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 0.25rem;
    }
    .empty-state-card .es-msg {
        font-size: 0.82rem;
        color: #94a3b8;
    }

    /* ---------- Search / Filter Panel ---------- */
    .filter-panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem 1.5rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
    }
    .filter-panel .fp-title {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-weight: 700;
        font-size: 0.82rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.75rem;
    }

    /* ---------- Divider ---------- */
    .styled-divider {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 2rem 0 1.5rem 0;
    }
</style>
"""


# ===================================================================
#  HELPERS  --  render HTML components
# ===================================================================

def _section_header(title: str, subtitle: str = "") -> str:
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    return (
        f'<div class="val-section-hdr">'
        f'  <h2>{title}</h2>{sub}'
        f'  <div class="hdr-line"></div>'
        f'</div>'
    )


def _result_card(title: str, message: str, passed: bool) -> str:
    cls = "pass" if passed else "fail"
    icon = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>' if passed else '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'
    return (
        f'<div class="val-card {cls}">'
        f'  <div class="icon">{icon}</div>'
        f'  <div class="content">'
        f'    <div class="title">{title}</div>'
        f'    <div class="msg">{message}</div>'
        f'  </div>'
        f'</div>'
    )


def _verdict_banner(passed: bool, label: str = "") -> str:
    if passed:
        icon_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
        text = label or "Receipt passed all validation checks"
        cls = "pass"
    else:
        icon_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'
        text = label or "Receipt failed validation"
        cls = "fail"

    return (
        f'<div class="verdict-banner {cls}">'
        f'  <div class="v-icon">{icon_svg}</div>'
        f'  <div class="v-text">{text}</div>'
        f'</div>'
    )


def _empty_state(icon: str, title: str, message: str) -> str:
    return (
        f'<div class="empty-state-card">'
        f'  <div class="es-icon">{icon}</div>'
        f'  <div class="es-title">{title}</div>'
        f'  <div class="es-msg">{message}</div>'
        f'</div>'
    )


# ===================================================================
#  CORE VALIDATION LOGIC  --  unchanged
# ===================================================================

def validate_receipt(data, skip_duplicate=False):
    results = []
    passed = True

    # ---------- Required Fields ----------
    required = ["bill_id", "vendor", "date", "amount", "tax"]
    missing = [f for f in required if data.get(f) is None]

    if missing:
        results.append({
            "title": "Required Fields",
            "status": "error",
            "message": f"Missing fields: {', '.join(missing)}"
        })
        passed = False
        return {"passed": passed, "results": results}
    else:
        results.append({
            "title": "Required Fields",
            "status": "success",
            "message": "All required fields present"
        })

    # ---------- Date Format ----------
    try:
        datetime.strptime(str(data["date"]), "%Y-%m-%d")
        results.append({
            "title": "Date Format",
            "status": "success",
            "message": f"Valid date: {data['date']}"
        })
    except Exception:
        results.append({
            "title": "Date Format",
            "status": "error",
            "message": f"Invalid date format: {data['date']}"
        })
        passed = False

    try:
        amount = float(data["amount"])
    except (ValueError, TypeError):
        amount = 0.0

    try:
        tax = float(data["tax"])
    except (ValueError, TypeError):
        tax = 0.0

    # ---------- Total Validation ----------
    if amount > 0:
        results.append({
            "title": "Total Validation",
            "status": "success",
            "message": f"Amount detected: \u20b9{amount:.2f}"
        })
    else:
        results.append({
            "title": "Total Validation",
            "status": "error",
            "message": "Invalid amount value"
        })
        passed = False

    # ---------- Tax Rate Validation ----------
    if tax == 0:
        results.append({
            "title": "Tax Rate Validation",
            "status": "success",
            "message": "No tax applied (valid)"
        })
    else:
        subtotal_option_1 = amount - tax
        subtotal_option_2 = amount

        valid = False
        used_subtotal = 0.0
        actual_rate = 0.0

        for subtotal in [subtotal_option_1, subtotal_option_2]:
            if subtotal <= 0:
                continue
            rate = tax / subtotal
            if abs(rate - EXPECTED_TAX_RATE) <= TOLERANCE:
                valid = True
                used_subtotal = subtotal
                actual_rate = rate
                break

        if valid:
            results.append({
                "title": "Tax Rate Validation",
                "status": "success",
                "message": (
                    f"Tax rate OK "
                    f"({actual_rate*100:.2f}%, Subtotal \u20b9{used_subtotal:.2f})"
                )
            })
        else:
            results.append({
                "title": "Tax Rate Validation",
                "status": "error",
                "message": (
                    f"Tax mismatch. Expected ~{EXPECTED_TAX_RATE*100:.1f}% "
                    f"but got \u20b9{tax:.2f} on amount \u20b9{amount:.2f}"
                )
            })
            passed = False

    # ---------- Duplicate Detection ----------
    if not skip_duplicate:
        if receipt_exists(data["bill_id"]):
            results.append({
                "title": "Duplicate Detection",
                "status": "error",
                "message": "Duplicate receipt found"
            })
            passed = False
        else:
            results.append({
                "title": "Duplicate Detection",
                "status": "success",
                "message": "No duplicate found"
            })

    return {"passed": passed, "results": results}


# ===================================================================
#  RENDER VALIDATION RESULTS  --  reusable
# ===================================================================

def _render_results(report: dict, context_label: str = ""):
    cards_html = ""
    for r in report["results"]:
        is_pass = r["status"] == "success"
        cards_html += _result_card(r["title"], r["message"], is_pass)
    st.markdown(cards_html, unsafe_allow_html=True)

    verdict_label = (
        f"{context_label} passed all validation checks" if report["passed"]
        else f"{context_label} failed validation"
    ) if context_label else ""
    st.markdown(_verdict_banner(report["passed"], verdict_label), unsafe_allow_html=True)


# ===================================================================
#  VALIDATION PAGE  --  UI only rewritten, logic unchanged
# ===================================================================

def validation_ui():
    # Inject scoped CSS
    st.markdown(VALIDATION_CSS, unsafe_allow_html=True)

    # ================= CURRENT UPLOADED RECEIPT =================
    st.markdown(
        _section_header("Current Uploaded Receipt", "Validation results for the most recently uploaded receipt"),
        unsafe_allow_html=True,
    )

    data = st.session_state.get("LAST_EXTRACTED_RECEIPT")
    report = st.session_state.get("LAST_VALIDATION_REPORT")

    if data and report:
        _render_results(report, "Receipt")
    else:
        st.markdown(
            _empty_state(
                '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
                "No receipt uploaded yet",
                "Upload a receipt from the Upload tab to see validation results here.",
            ),
            unsafe_allow_html=True,
        )

    # ================= DIVIDER =================
    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ================= STORED RECEIPT VALIDATION =================
    st.markdown(
        _section_header("Validate Stored Receipt", "Search and validate any previously saved receipt"),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="filter-panel"><div class="fp-title">Search Filters</div></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    bill_id = c1.text_input("Bill ID", placeholder="e.g. INV-001")
    vendor = c2.text_input("Vendor", placeholder="e.g. Amazon")
    amount = c3.text_input("Amount", placeholder="e.g. 1500")
    tax = c4.text_input("Tax", placeholder="e.g. 120")

    if st.button("Run Validation", use_container_width=True, type="primary"):
        receipts = fetch_all_receipts()
        match = None

        for r in receipts:
            if bill_id and bill_id not in r["bill_id"]:
                continue
            if vendor and vendor.lower() not in r["vendor"].lower():
                continue
            if amount:
                try:
                    if float(amount) != r["amount"]:
                        continue
                except ValueError:
                    pass
            if tax:
                try:
                    if float(tax) != r["tax"]:
                        continue
                except ValueError:
                    pass
            match = r
            break

        if not match:
            st.markdown(
                _empty_state(
                    '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
                    "No matching receipt found",
                    "Try adjusting your search filters above.",
                ),
                unsafe_allow_html=True,
            )
            return

        st.markdown(
            _section_header(f"Results for {match['bill_id']}"),
            unsafe_allow_html=True,
        )

        stored_report = validate_receipt(match, skip_duplicate=True)
        _render_results(stored_report, f"Receipt {match['bill_id']}")

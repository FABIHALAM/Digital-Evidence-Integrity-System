import hashlib
import os
import datetime
import difflib
import requests
import json
import qrcode
import exifread
from PIL import Image
import pytesseract
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ===============================
# 1️⃣ HASH FILE (SHA-256)
# ===============================
def hash_file(path):
    sha = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha.update(chunk)
    return sha.hexdigest()

# ===============================
# 2️⃣ METADATA EXTRACTION
# ===============================
def extract_metadata(path):
    stat = os.stat(path)
    return {
        "size": stat.st_size,
        "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
    }

# ===============================
# 3️⃣ BLOCK (HASH CHAIN)
# ===============================
def build_block(path, previous_hash):
    current_hash = hash_file(path)
    block = {
        "file": os.path.basename(path),
        "hash": current_hash,
        "previous_hash": previous_hash,
        "time": datetime.datetime.now()
    }
    return block

# ===============================
# 4️⃣ INTEGRITY VERIFICATION
# ===============================
def verify_integrity(chain, path):
    new_hash = hash_file(path)

    # Duplicate detection
    for block in chain:
        if block["hash"] == new_hash:
            return "DUPLICATE"

    if not chain:
        return "VALID"

    last_hash = chain[-1]["hash"]

    # Exact match
    if new_hash == last_hash:
        return "VALID"

    # Minor change detection
    ratio = difflib.SequenceMatcher(
        None, new_hash, last_hash
    ).ratio()

    if ratio > 0.85:
        return "MINOR_CHANGE"

    return "TAMPERED"

# ===============================
# 5️⃣ QR CODE GENERATION
# ===============================
def generate_qr(block):
    qr_data = f"""
    FILE: {block['file']}
    HASH: {block['hash']}
    TIME: {block['time']}
    PREVIOUS: {block['previous_hash']}
    """
    qr = qrcode.make(qr_data)
    qr_path = f"static/qr_{block['hash'][:10]}.png"
    qr.save(qr_path)
    return "/" + qr_path

# ===============================
# 6️⃣ AI-STYLE TAMPER PREDICTION
# (Rule-based intelligence)
# ===============================
def ai_tamper_predict(path):
    meta = extract_metadata(path)
    now = datetime.datetime.now()

    # File modified too quickly
    modified_time = datetime.datetime.fromisoformat(meta["modified"])
    if (now - modified_time).total_seconds() < 5:
        return True

    # Suspicious extension
    suspicious_ext = [".exe", ".bat", ".js"]
    if any(path.lower().endswith(ext) for ext in suspicious_ext):
        return True

    return False

# ===============================
# 7️⃣ GEOLOCATION FROM IP
# ===============================

def get_location_from_ip(ip):
    try:
        response = requests.get(f'http://ipapi.co/{ip}/json/', timeout=5)
        data = response.json()
        if data.get('error'):
            return f"{ip} (Unknown)"
        city = data.get('city', 'Unknown')
        country = data.get('country_name', 'Unknown')
        return f"{city}, {country}"
    except:
        return f"{ip} (Error)"

def analyze_file_content(path):
    """
    Perform deep file analysis including EXIF extraction, text analysis, and basic steganography detection.
    """
    analysis = {
        "exif_data": {},
        "text_content": "",
        "steganography_detected": False,
        "file_type": "",
        "anomalies": []
    }

    try:
        # Determine file type
        import mimetypes
        analysis["file_type"] = mimetypes.guess_type(path)[0] or "unknown"

        # EXIF extraction for images
        if analysis["file_type"] and analysis["file_type"].startswith("image/"):
            with open(path, 'rb') as f:
                tags = exifread.process_file(f)
                analysis["exif_data"] = {tag: str(value) for tag, value in tags.items()}

        # Text extraction using OCR for images or direct text for text files
        if analysis["file_type"] and (analysis["file_type"].startswith("image/") or analysis["file_type"] == "text/plain"):
            try:
                if analysis["file_type"].startswith("image/"):
                    img = Image.open(path)
                    analysis["text_content"] = pytesseract.image_to_string(img)
                else:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        analysis["text_content"] = f.read()[:1000]  # Limit to first 1000 chars
            except Exception as e:
                analysis["anomalies"].append(f"Text extraction failed: {str(e)}")

        # Basic steganography detection (simple heuristic)
        file_size = os.path.getsize(path)
        if file_size > 1000000:  # Large files might hide data
            analysis["steganography_detected"] = True
            analysis["anomalies"].append("Large file size may indicate hidden data")

        # Additional anomaly checks
        if len(analysis["text_content"]) > 0 and "suspicious" in analysis["text_content"].lower():
            analysis["anomalies"].append("Suspicious keywords detected in content")

    except Exception as e:
        analysis["anomalies"].append(f"Analysis error: {str(e)}")

    return analysis

def generate_forensic_pdf(case, output_path):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []

    elements.append(Paragraph("<b>Digital Forensic Evidence Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    table_data = [
        ["Case ID", case["case_id"]],
        ["File Name", case["file"]],
        ["Integrity Status", case["status"]],
        ["SHA-256 Hash", case["hash"]],
        ["Timestamp", str(case["time"])],
        ["File Size", f'{case["metadata"]["size"]} bytes']
    ]

    table = Table(table_data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Right align labels
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),   # Left align values
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Bold labels
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        "This report certifies that the above digital evidence was processed "
        "using cryptographic hashing and integrity verification techniques. "
        "Any modification to the evidence would invalidate this report.",
        styles["Normal"]
    ))

    doc.build(elements)

# ===============================
# 8️⃣ ANOMALY DETECTION
# ===============================
def detect_anomaly(path):
    """
    Detect anomalies in the file using basic heuristics.
    """
    try:
        file_size = os.path.getsize(path)
        if file_size == 0:
            return True  # Empty files are anomalous

        # Check for suspicious file extensions
        suspicious_ext = [".exe", ".bat", ".scr", ".pif", ".com", ".vbs", ".js", ".jar"]
        if any(path.lower().endswith(ext) for ext in suspicious_ext):
            return True

        # Check for large files (potential malware carriers)
        if file_size > 50 * 1024 * 1024:  # 50MB
            return True

        return False
    except Exception:
        return True  # If we can't analyze, assume anomaly

# ===============================
# 9️⃣ VIRUSTOTAL CHECK
# ===============================
def check_virustotal(file_hash):
    """
    Check file hash against VirusTotal (mock implementation).
    In production, integrate with actual VirusTotal API.
    """
    try:
        # Mock response - in real implementation, call VirusTotal API
        # For demo purposes, return a mock result
        return {
            "detected": False,
            "positives": 0,
            "total": 70,
            "permalink": f"https://www.virustotal.com/gui/file/{file_hash}"
        }
    except Exception as e:
        return {
            "error": str(e),
            "detected": False,
            "positives": 0,
            "total": 0
        }

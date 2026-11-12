"""Visual assets for the research interface. No patient images or fake predictions."""
from PIL import Image, ImageDraw, ImageFont

STYLES = """
<style>
:root { --ink:#172b3b; --muted:#65788a; --teal:#087f75; --line:#e0e7ec; }
.stApp { background:#f5f7fa; }
.block-container { max-width:1400px; padding:2.5rem 3rem 3rem; }
h1,h2,h3 { color:var(--ink); letter-spacing:-.035em; }
h1 { font-size:2.5rem !important; line-height:1.15 !important; font-weight:750 !important; }
h2 { font-size:1.45rem !important; }
h3 { font-size:1.15rem !important; }
p { line-height:1.65; }
[data-testid="stSidebar"] { background:#102737; border-right:0; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#b8cbd7; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color:#f4f8fb; }
[data-testid="stSidebar"] a { color:#87d9cc; text-decoration:none; }
[data-testid="stSidebar"] button { color:#e3eef3; border-color:#3d5362; background:transparent; }
[data-testid="stSidebar"] [data-testid="stLinkButton"] a { background:transparent; border-color:#3d5362; }
[data-testid="stSidebar"] [data-testid="stLinkButton"] p { color:#e3eef3; }
.st-key-access_card, .st-key-input_panel, .st-key-review_panel,
.st-key-method_implementation, .st-key-method_privacy, .st-key-method_limits { background:white; border-color:var(--line); border-radius:18px; }
[data-testid="stToolbar"], .stDeployButton, #MainMenu { display:none !important; }
[data-testid="stFileUploaderDropzone"] { background:#f6fafb; border:1px dashed #a9c5cd; border-radius:12px; }
[data-testid="stMetric"] { padding:.6rem 0; }
[data-testid="stMetricValue"] { color:var(--ink); font-size:1.9rem; font-weight:700; }
[data-testid="stTabs"] [role="tablist"] { gap:1.75rem; border-bottom:1px solid var(--line); }
[data-testid="stTabs"] [role="tab"] { height:48px; font-weight:600; }
.brand { display:flex; align-items:center; gap:12px; padding:12px 0 24px; }
.brand svg { width:34px; height:34px; color:#80d5c6; }
.brand strong { color:#fff; font-size:23px; letter-spacing:-.7px; }
.brand small { display:block; color:#a7c1ce; font-size:12px; margin-top:2px; }
.side-section { color:#7fa4b6; font-size:11px; font-weight:700; letter-spacing:1.8px; margin:22px 0 10px; }
.side-line { border-top:1px solid #304958; margin:24px 0; }
.eyebrow { font-size:11px; font-weight:750; letter-spacing:2px; color:var(--teal); margin:0 0 12px; }
.lead { color:var(--muted); font-size:16px; max-width:720px; margin:0 0 22px; }
.research-note { background:#fff6e9; color:#785124; border:1px solid #f0dfc4; padding:12px 17px; border-radius:12px; font-size:13px; margin:0 0 22px; }
.workflow { display:flex; gap:24px; padding:16px 0 26px; }
.workflow-item { display:flex; align-items:center; gap:10px; color:var(--muted); font-size:13px; }
.step { width:28px; height:28px; display:grid; place-items:center; border-radius:50%; background:#e2f3ee; color:var(--teal); font-size:11px; font-weight:750; }
.panel-kicker { color:var(--muted); font-size:11px; font-weight:700; letter-spacing:1.4px; margin-bottom:8px; }
.review-title { color:var(--ink); font-size:24px; line-height:1.25; font-weight:700; letter-spacing:-.7px; margin:12px 0; }
.review-copy { color:var(--muted); font-size:14px; margin-bottom:20px; }
.check-row { border-top:1px solid var(--line); padding:12px 0; }
.check-row strong { font-size:13px; color:var(--ink); }
.check-row span { display:block; font-size:12px; color:var(--muted); margin-top:4px; }
.status-label { display:inline-block; padding:5px 10px; background:#e7f5f0; color:#176955; border-radius:7px; font-size:11px; font-weight:700; }
.fine-print { color:var(--muted); font-size:12px; margin-top:18px; }
.login-brand { color:var(--teal); font-size:14px; font-weight:750; letter-spacing:1.4px; margin-bottom:30px; }
@media (max-width:760px) {
 .block-container { padding:1.5rem 1rem 2rem; }
 h1 { font-size:1.9rem !important; }
 .workflow { gap:12px; flex-wrap:wrap; }
 .workflow-item { font-size:12px; }
}
</style>
"""

BRAND = """<div class="brand"><svg viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M4 20s6-10 16-10 16 10 16 10-6 10-16 10S4 20 4 20Z" stroke="currentColor" stroke-width="2.3"/><circle cx="20" cy="20" r="5" stroke="currentColor" stroke-width="2.3"/></svg><div><strong>Conjunctiva</strong><small>Anaemia screening research</small></div></div>"""

WORKFLOW = """<div class="workflow"><div class="workflow-item"><span class="step">01</span>Choose an image</div><div class="workflow-item"><span class="step">02</span>Run research analysis</div><div class="workflow-item"><span class="step">03</span>Review the limitations</div></div>"""


def illustration():
    """Draw a schematic example. It is never submitted for medical classification."""
    image = Image.new("RGB", (1000, 520), "#edf5f5")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((42, 38, 958, 482), radius=30, fill="#ffffff")
    draw.ellipse((200, 112, 805, 352), fill="#f1b7ae")
    draw.ellipse((200, 90, 805, 306), fill="#ffffff", outline="#254a60", width=5)
    draw.ellipse((433, 124, 577, 268), fill="#4f9c94", outline="#254a60", width=4)
    draw.ellipse((474, 165, 536, 227), fill="#163c4c")
    draw.ellipse((487, 168, 506, 187), fill="#ffffff")
    draw.arc((193, 106, 811, 350), 0, 180, fill="#b46a65", width=5)
    draw.line((725, 326, 837, 378), fill="#56798a", width=2)
    draw.text((640, 387), "Conjunctival region", fill="#36596c", font=ImageFont.load_default(size=21))
    draw.text((88, 438), "ILLUSTRATION / NOT PATIENT DATA", fill="#6f8591", font=ImageFont.load_default(size=17))
    return image


def favicon():
    image = Image.new("RGB", (64, 64), "#087f75")
    draw = ImageDraw.Draw(image)
    draw.ellipse((7, 18, 57, 46), outline="white", width=4)
    draw.ellipse((24, 24, 40, 40), fill="white")
    return image


def class_label(label):
    normal = label.lower().replace("_", "-")
    return {"anemic": "Anaemic class", "non-anemic": "Non-anaemic class"}.get(normal, label)

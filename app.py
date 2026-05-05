import re
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from collections import Counter

app = Flask(__name__)
app.secret_key = "ats_scanner_2025_secret"

# ── Stop words ──────────────────────────────────────────────────────────────
STOP_WORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","was","are","were","be","been","being","have","has",
    "had","do","does","did","will","would","shall","should","may","might",
    "can","could","not","no","nor","so","yet","both","either","neither",
    "each","few","more","most","other","some","such","than","too","very",
    "just","about","above","after","before","between","during","under",
    "again","further","then","once","here","there","when","where","why",
    "how","all","any","this","that","these","those","i","me","my","we",
    "our","you","your","he","him","his","she","her","it","its","they",
    "them","their","what","which","who","as","if","while","because",
    "since","unless","until","into","through","including","throughout",
    "despite","upon","up","out","over","per","s","t","d","m","re","ve",
    "ll","also","etc","ie","eg","vs","via","within","without","using",
    "used","use","uses","need","needs","strong","work","working","ability",
    "experience","knowledge","skills","skill","team","teams","role","roles",
}

TECH_MARKERS = {
    "python","java","javascript","typescript","react","angular","vue","node",
    "django","flask","spring","sql","nosql","mongodb","postgresql","mysql",
    "redis","docker","kubernetes","aws","gcp","azure","git","linux",
    "machine","learning","deep","neural","tensorflow","pytorch","scikit",
    "pandas","numpy","spark","hadoop","kafka","rest","graphql","html","css",
    "c++","c#","ruby","php","swift","kotlin","rust","go","scala","r",
    "matlab","excel","tableau","power","bi","api","ci/cd","devops","agile",
    "scrum","jira","jenkins","terraform","ml","ai","nlp","opencv","data",
    "analysis","visualization","cloud","microservices","fastapi","celery",
    "rabbitmq","elasticsearch","firebase","next","vercel","figma","selenium",
    "pytest","junit","postman","swagger","airflow","dbt","looker","snowflake",
    "redshift","bigquery","sagemaker","keras","xgboost","lightgbm","opencv",
    "streamlit","dash","flask","fastapi","spring","hibernate","maven","gradle",
}
SOFT_MARKERS = {
    "communication","leadership","teamwork","collaboration","management",
    "problem","solving","analytical","creativity","presentation",
    "negotiation","adaptability","time","critical","thinking","interpersonal",
    "motivated","detail","oriented","proactive","initiative","mentoring",
    "organised","organized","multitask","multitasking","decision","making",
    "planning","coordination","supervision","customer","service","research",
    "reporting","documentation","stakeholder","cross-functional",
}

# ── Job Role Keyword Profiles ─────────────────────────────────────────────────
# Each role maps to a list of expected keywords an ATS would look for
JOB_PROFILES = {
    "python developer": [
        "python","django","flask","fastapi","rest","api","sql","postgresql","mysql",
        "git","docker","linux","agile","scrum","pandas","numpy","pytest","celery",
        "redis","aws","microservices","oop","ci/cd","problem solving","communication",
        "debugging","unit testing","json","html","css","javascript","sqlalchemy",
    ],
    "data scientist": [
        "python","r","machine learning","deep learning","tensorflow","pytorch","keras",
        "scikit","pandas","numpy","sql","statistics","data analysis","visualization",
        "tableau","power bi","matplotlib","seaborn","nlp","feature engineering",
        "model deployment","aws","gcp","spark","big data","a/b testing","research",
        "jupyter","xgboost","lightgbm","hypothesis testing","communication","reporting",
    ],
    "data analyst": [
        "sql","excel","python","r","tableau","power bi","data visualization",
        "data analysis","statistics","reporting","pandas","numpy","mysql","postgresql",
        "google analytics","looker","business intelligence","dashboards","kpi",
        "data cleaning","data modeling","stakeholder","presentation","communication",
        "critical thinking","problem solving","pivot tables","vlookup","bi tools",
    ],
    "web developer": [
        "html","css","javascript","typescript","react","angular","vue","node",
        "rest","api","git","responsive design","sql","mongodb","docker","aws",
        "agile","scrum","webpack","sass","figma","ui","ux","accessibility",
        "performance","seo","testing","jest","debugging","problem solving","communication",
    ],
    "frontend developer": [
        "html","css","javascript","typescript","react","angular","vue","next",
        "redux","tailwind","sass","figma","responsive","git","webpack","vite",
        "jest","cypress","accessibility","performance","ui","ux","rest","api",
        "agile","problem solving","communication","attention to detail","animation",
    ],
    "backend developer": [
        "python","java","node","c#","go","rust","django","spring","express",
        "rest","api","graphql","sql","postgresql","mysql","mongodb","redis",
        "docker","kubernetes","aws","gcp","microservices","ci/cd","git","linux",
        "agile","scrum","authentication","security","performance","testing","communication",
    ],
    "full stack developer": [
        "html","css","javascript","typescript","react","node","python","django","flask",
        "sql","mongodb","postgresql","rest","api","git","docker","aws","ci/cd",
        "agile","scrum","responsive","testing","jest","figma","problem solving",
        "communication","leadership","microservices","authentication","deployment",
    ],
    "machine learning engineer": [
        "python","machine learning","deep learning","tensorflow","pytorch","scikit",
        "mlops","model deployment","docker","kubernetes","aws","gcp","sql","spark",
        "feature engineering","nlp","computer vision","rest","api","git","ci/cd",
        "pandas","numpy","statistics","a/b testing","airflow","sagemaker","monitoring",
        "research","communication","problem solving","experiment tracking","mlflow",
    ],
    "devops engineer": [
        "docker","kubernetes","aws","gcp","azure","ci/cd","jenkins","terraform",
        "ansible","linux","bash","python","git","monitoring","grafana","prometheus",
        "nginx","helm","microservices","networking","security","agile","scrum",
        "infrastructure","automation","cloud","problem solving","communication",
        "reliability","scalability","deployment","configuration management",
    ],
    "software engineer": [
        "python","java","c++","c#","javascript","algorithms","data structures",
        "oop","design patterns","git","sql","rest","api","docker","agile","scrum",
        "testing","debugging","linux","problem solving","communication","teamwork",
        "ci/cd","code review","documentation","performance","scalability","microservices",
    ],
    "ui ux designer": [
        "figma","sketch","adobe xd","prototyping","wireframing","user research",
        "usability testing","ui","ux","design systems","typography","color theory",
        "responsive design","accessibility","html","css","animation","interaction design",
        "information architecture","personas","user flows","a/b testing","presentation",
        "communication","collaboration","creativity","attention to detail","adobe",
    ],
    "business analyst": [
        "requirements","stakeholder","sql","excel","tableau","power bi","reporting",
        "data analysis","process improvement","agile","scrum","jira","documentation",
        "business intelligence","kpi","gap analysis","use cases","user stories",
        "communication","presentation","analytical","problem solving","critical thinking",
        "project management","visio","powerpoint","negotiation","leadership",
    ],
    "cloud engineer": [
        "aws","gcp","azure","terraform","kubernetes","docker","ci/cd","linux",
        "networking","security","iam","s3","ec2","lambda","cloudformation","ansible",
        "python","bash","monitoring","grafana","prometheus","git","microservices",
        "infrastructure","automation","cloud","problem solving","communication","devops",
        "high availability","disaster recovery","cost optimization","scalability",
    ],
    "android developer": [
        "kotlin","java","android","android studio","rest","api","mvvm","jetpack",
        "compose","sqlite","room","retrofit","git","firebase","google play",
        "ui","ux","testing","junit","espresso","gradle","xml","coroutines",
        "problem solving","agile","scrum","communication","debugging","performance",
    ],
    "ios developer": [
        "swift","objective-c","xcode","ios","swiftui","uikit","rest","api","mvvm",
        "core data","firebase","git","app store","testing","xctest","cocoapods",
        "spm","combine","reactive","ui","ux","problem solving","agile","debugging",
        "performance","communication","teamwork","instruments","push notifications",
    ],
    "cybersecurity analyst": [
        "network security","firewall","siem","penetration testing","vulnerability",
        "threat analysis","incident response","python","linux","bash","aws","compliance",
        "iso 27001","nist","gdpr","authentication","encryption","git","sql","reporting",
        "analytical","problem solving","communication","critical thinking","documentation",
        "malware analysis","intrusion detection","wireshark","splunk","nessus",
    ],
    "project manager": [
        "project management","agile","scrum","jira","ms project","stakeholder",
        "risk management","budget","planning","reporting","leadership","communication",
        "teamwork","problem solving","documentation","kpi","milestones","pmp",
        "excel","powerpoint","negotiation","coordination","critical thinking",
        "resource management","timeline","delivery","cross-functional","presentation",
    ],
    "data engineer": [
        "python","sql","spark","hadoop","kafka","airflow","dbt","etl","postgresql",
        "mysql","mongodb","aws","gcp","azure","snowflake","redshift","bigquery",
        "docker","kubernetes","git","ci/cd","data modeling","data pipeline",
        "linux","bash","pandas","numpy","problem solving","communication","analytical",
        "data warehouse","data lake","streaming","batch processing","monitoring",
    ],
    "react developer": [
        "react","javascript","typescript","redux","hooks","next","html","css",
        "rest","api","git","jest","cypress","webpack","vite","node","npm","yarn",
        "responsive","ui","ux","figma","agile","scrum","testing","debugging",
        "performance","accessibility","problem solving","communication","teamwork",
    ],
    "java developer": [
        "java","spring","spring boot","hibernate","maven","gradle","sql","postgresql",
        "mysql","rest","api","microservices","docker","kubernetes","aws","git",
        "agile","scrum","junit","testing","linux","oop","design patterns","ci/cd",
        "multithreading","jvm","problem solving","communication","debugging","kafka",
    ],
}

# Lowercase sorted list for display in dropdown
ALL_ROLES = sorted(JOB_PROFILES.keys())


# ── Text processing ──────────────────────────────────────────────────────────
def preprocess(text: str) -> list:
    text = text.lower()
    text = re.sub(r"[^a-z0-9/\s\-]", " ", text)
    return [t for t in text.split() if t not in STOP_WORDS and len(t) > 1]


def extract_resume_keywords(text: str) -> set:
    tokens = preprocess(text)
    expanded = set(tokens)
    # also add bigrams
    for i in range(len(tokens) - 1):
        expanded.add(f"{tokens[i]} {tokens[i+1]}")
    return expanded


# ── ATS scoring ──────────────────────────────────────────────────────────────
def calculate_ats_score(resume_text: str, job_role: str) -> dict:
    role_key = job_role.strip().lower()

    # Find best matching profile (exact or partial)
    profile_keywords = None
    matched_role_name = None
    if role_key in JOB_PROFILES:
        profile_keywords = JOB_PROFILES[role_key]
        matched_role_name = role_key.title()
    else:
        # partial match
        for role, kws in JOB_PROFILES.items():
            if role_key in role or role in role_key:
                profile_keywords = kws
                matched_role_name = role.title()
                break

    if not profile_keywords:
        # fallback: treat role as custom keywords
        profile_keywords = preprocess(job_role) or [role_key]
        matched_role_name = job_role.title()

    job_kw_set = set(profile_keywords)
    resume_kw  = extract_resume_keywords(resume_text)

    matched_kw = set()
    missing_kw = set()

    for kw in job_kw_set:
        # check if keyword (possibly multi-word) appears in resume
        kw_tokens = set(kw.split())
        if kw_tokens.issubset(set(preprocess(resume_text))) or kw in resume_kw:
            matched_kw.add(kw)
        else:
            missing_kw.add(kw)

    score = min(round((len(matched_kw) / max(len(job_kw_set), 1)) * 100, 1), 100.0)

    if score >= 80:
        grade = "Excellent"; grade_css = "excellent"
        recommendation = (
            "Your resume is strongly aligned for a {} role. "
            "You are very likely to pass ATS screening.".format(matched_role_name)
        )
    elif score >= 60:
        grade = "Good"; grade_css = "good"
        recommendation = (
            "Good match for {}. Adding a few more keywords "
            "can push you into the top tier.".format(matched_role_name)
        )
    elif score >= 40:
        grade = "Fair"; grade_css = "fair"
        recommendation = (
            "Moderate alignment for {}. Incorporate the missing keywords "
            "naturally in your experience and skills sections.".format(matched_role_name)
        )
    else:
        grade = "Needs Work"; grade_css = "poor"
        recommendation = (
            "Your resume needs significant work to pass ATS filters for {}. "
            "Review missing keywords and restructure your resume.".format(matched_role_name)
        )

    def categorise(kw_set):
        tech  = sorted([k for k in kw_set if any(t in k for t in TECH_MARKERS)])
        soft  = sorted([k for k in kw_set if any(t in k for t in SOFT_MARKERS) and k not in tech])
        other = sorted([k for k in kw_set if k not in tech and k not in soft])
        return tech, soft, other

    m_tech, m_soft, m_other = categorise(matched_kw)
    x_tech, x_soft, x_other = categorise(missing_kw)

    # top missing (first 12)
    top_missing = list(missing_kw)[:12]

    dash_offset = round(352 - (352 * score / 100), 1)

    return {
        "score":          score,
        "dash_offset":    dash_offset,
        "grade":          grade,
        "grade_css":      grade_css,
        "recommendation": recommendation,
        "matched_count":  len(matched_kw),
        "missing_count":  len(missing_kw),
        "total_job_kw":   len(job_kw_set),
        "matched_tech":   m_tech,
        "matched_soft":   m_soft,
        "matched_other":  m_other,
        "missing_tech":   x_tech,
        "missing_soft":   x_soft,
        "missing_other":  x_other,
        "top_missing":    top_missing,
        "resume_words":   len(resume_text.split()),
        "job_role":       matched_role_name,
    }


# ── File text extraction ──────────────────────────────────────────────────────
def extract_text_from_file(file_obj, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_obj)
            return " ".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            raise ValueError(f"Could not read PDF: {e}")
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_obj)
            return " ".join(para.text for para in doc.paragraphs)
        except Exception as e:
            raise ValueError(f"Could not read DOCX: {e}")
    elif ext in (".txt", ".text"):
        raw = file_obj.read()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", roles=ALL_ROLES)


@app.route("/analyze", methods=["POST"])
def analyze():
    job_role_custom = request.form.get("job_role_custom", "").strip()
    job_role_select = request.form.get("job_role", "").strip()
    job_role = job_role_custom if job_role_custom else job_role_select
    if not job_role:
        flash("Please select or type a job role.", "error")
        return redirect(url_for("index"))

    file = request.files.get("resume_file")
    if not file or file.filename == "":
        flash("Please upload your resume file (PDF, DOCX, or TXT).", "error")
        return redirect(url_for("index"))

    try:
        resume_text = extract_text_from_file(file.stream, file.filename)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("index"))

    if len(resume_text.strip()) < 50:
        flash("Could not extract enough text. Please try a different file.", "error")
        return redirect(url_for("index"))

    result = calculate_ats_score(resume_text, job_role)
    result["filename"] = file.filename
    return render_template("results.html", r=result)


@app.route("/health")
def health():
    from flask import jsonify
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

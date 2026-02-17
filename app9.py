from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB
import openai
import os
import time
import uuid
import smtplib
from email.mime.text import MIMEText
from xml.etree.ElementTree import Element, SubElement, ElementTree
from datetime import date



# -------------------------------
# CONFIG
# -------------------------------

DATABASE_URL = "postgresql://job_portal_db:job_portal_db@jobportaldb.c1swawyaiteb.us-east-2.rds.amazonaws.com:5432/postgres"

openai.api_key = 'openapikey'

app = Flask(__name__)
CORS(app)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -------------------------------
# MODELS
# -------------------------------

class JobProfile(Base):
    __tablename__ = "job_profiles_new"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)

    description = relationship("JobDescription", back_populates="profile", uselist=False)


class JobDescription(Base):
    __tablename__ = "job_descriptions_new"

    id = Column(Integer, primary_key=True, index=True)
    job_profile_id = Column(Integer, ForeignKey("job_profiles_new.id"))

    vertical = Column(Text)
    division = Column(Text)
    subdivision = Column(Text)

    purpose = Column(Text)
    responsibilities = Column(Text)
    manager = Column(Text)
    travel = Column(Text)
    physical = Column(Text)
    workconditions = Column(Text)
    minqualifications = Column(Text)
    preferredqualifications = Column(Text)
    mineducation = Column(Text)
    preferrededucation = Column(Text)
    minexperience = Column(Text)
    certifications = Column(Text)
    competencies = Column(Text)
    whatYoullDo = Column(Text)
    whatWeLookFor = Column(Text)
    qualitiesThatStir = Column(Text)

    profile = relationship("JobProfile", back_populates="description")


class PendingJobDescription(Base):
    __tablename__ = "pending_job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, unique=True, nullable=False)
    profile_name = Column(Text, nullable=False)
    payload = Column(JSONB, nullable=False)


# -------------------------------
# PROMPTS
# -------------------------------

PROMPTS = {
    "purpose": """Craft a formal, three-sentence 'Position Purpose' paragraph for the {Job_Title} role. Maintain a professional, formal, and outcome-driven tone appropriate for a Fortune 50 job description.""",

    "responsibilities": """Generate 6-8 clear, action-driven bullet points for 'Key Responsibilities' for the {Job_Title} role. Use professional, results-focused language appropriate for a Fortune 50 company.""",

    "manager": """Create a brief, formal description for 'Direct Manager/Direct Reports' for the {Job_Title}. Indicate reporting structure and whether there are direct reports.""",

    "travel": """Write a formal, one-sentence 'Travel Requirements' statement for the {Job_Title}.""",

    "physical": """Generate an ADA-compliant 'Physical Requirements' paragraph for the {Job_Title}. Include standard office-based expectations.""",

    "workconditions": """Craft a professional 'Working Conditions' paragraph for the {Job_Title}, describing environment and pace.""",

    "minqualifications": """Create a formal 'Minimum Qualifications' list for the {Job_Title}, listing required skills and experience.""",

    "preferredqualifications": """Generate a 'Preferred Qualifications' list for the {Job_Title}, listing additional desirable skills and experiences.""",

    "mineducation": """Write a concise statement for 'Minimum Education' required for the {Job_Title}.""",

    "preferrededucation": """Draft a short, formal sentence for 'Preferred Education' for the {Job_Title}.""",

    "minexperience": """State the 'Minimum Years of Work Experience' required for the {Job_Title} role.""",

    "certifications": """List any 'Certifications' required or preferred for the {Job_Title} in the {Vertical}.""",

    "competencies": """Generate a list of 6-8 professional 'Competencies' for the {Job_Title}.""",

    "whatYoullDo": """Write a brief, compelling 2-3 sentence paragraph summarizing key tasks and responsibilities of the {Job_Title}. Also add a section below titled 'Duties' and generate 6-8 action-driven bullet points.""",

    "whatWeLookFor": """Draft a professional 'What We Look For' section with 6 to 8 bullets highlighting the core attributes and skills desired in candidates for the {Job_Title}.""",

    "qualitiesThatStir": """Create a professional yet inspiring section with 4 bullets listing “nice to have” skills and personal qualities for the {Job_Title}."""
}

# -------------------------------
# GPT CALL
# -------------------------------

def query_chatgpt(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        if "rate limit" in str(e).lower():
            time.sleep(30)
            return query_chatgpt(prompt)
        print("GPT Error:", e)
        return f"Error: {str(e)}"

# -------------------------------
# GENERATE DESCRIPTION
# -------------------------------

def generate_description(profile):
    vertical = "General"
    division = vertical + " Division"
    subdivision = vertical + " Subdivision"

    data = {}
    for field, prompt_template in PROMPTS.items():
        prompt = prompt_template.format(
            Job_Title=profile.title,
            Vertical=vertical
        )
        result = query_chatgpt(prompt)
        data[field] = result

    jd_dict = {
        "vertical": vertical,
        "division": division,
        "subdivision": subdivision,
        **data
    }

    return jd_dict

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/api/job-profiles', methods=['GET'])
def list_profiles():
    db = SessionLocal()
    profiles = db.query(JobProfile).all()
    result = []
    for p in profiles:
        result.append({
            "id": p.id,
            "title": p.title,
            "approved": False
        })
    db.close()
    return jsonify(result)


@app.route('/api/job-description/<int:job_id>', methods=['GET'])
def get_description(job_id):
    db = SessionLocal()
    profile = db.query(JobProfile).filter(JobProfile.id == job_id).first()

    if not profile:
        db.close()
        return jsonify({"error": "Job profile not found."}), 404

    jd = profile.description

    if jd:
        # already saved
        result = {
            "vertical": jd.vertical,
            "division": jd.division,
            "subdivision": jd.subdivision,
            "internal": {
                "purpose": jd.purpose,
                "responsibilities": jd.responsibilities,
                "manager": jd.manager,
                "travel": jd.travel,
                "physical": jd.physical,
                "workconditions": jd.workconditions,
                "minqualifications": jd.minqualifications,
                "preferredqualifications": jd.preferredqualifications,
                "mineducation": jd.mineducation,
                "preferrededucation": jd.preferrededucation,
                "minexperience": jd.minexperience,
                "certifications": jd.certifications,
                "competencies": jd.competencies,
            },
            "external": {
                "whatYoullDo": jd.whatYoullDo,
                "whatWeLookFor": jd.whatWeLookFor,
                "qualitiesThatStir": jd.qualitiesThatStir
            }
        }
    else:
        # generate fresh but do NOT save
        jd_dict = generate_description(profile)
        result = {
            "vertical": jd_dict["vertical"],
            "division": jd_dict["division"],
            "subdivision": jd_dict["subdivision"],
            "internal": {k: jd_dict[k] for k in [
                "purpose", "responsibilities", "manager", "travel",
                "physical", "workconditions", "minqualifications",
                "preferredqualifications", "mineducation", "preferrededucation",
                "minexperience", "certifications", "competencies"
            ]},
            "external": {k: jd_dict[k] for k in [
                "whatYoullDo", "whatWeLookFor", "qualitiesThatStir"
            ]}
        }

    db.close()
    return jsonify(result)


@app.route('/api/job-description/<int:job_id>', methods=['POST'])
def save_description(job_id):
    db = SessionLocal()
    profile = db.query(JobProfile).filter(JobProfile.id == job_id).first()

    if not profile:
        db.close()
        return jsonify({"error": "Job profile not found."}), 404

    payload = request.get_json()

    # delete old JD if exists
    if profile.description:
        db.delete(profile.description)
        db.commit()

    jd = JobDescription(
        job_profile_id=job_id,
        vertical=payload.get("vertical"),
        division=payload.get("division"),
        subdivision=payload.get("subdivision"),
        purpose=payload["internal"].get("purpose"),
        responsibilities=payload["internal"].get("responsibilities"),
        manager=payload["internal"].get("manager"),
        travel=payload["internal"].get("travel"),
        physical=payload["internal"].get("physical"),
        workconditions=payload["internal"].get("workconditions"),
        minqualifications=payload["internal"].get("minqualifications"),
        preferredqualifications=payload["internal"].get("preferredqualifications"),
        mineducation=payload["internal"].get("mineducation"),
        preferrededucation=payload["internal"].get("preferrededucation"),
        minexperience=payload["internal"].get("minexperience"),
        certifications=payload["internal"].get("certifications"),
        competencies=payload["internal"].get("competencies"),
        whatYoullDo=payload["external"].get("whatYoullDo"),
        whatWeLookFor=payload["external"].get("whatWeLookFor"),
        qualitiesThatStir=payload["external"].get("qualitiesThatStir"),
    )

    db.add(jd)
    db.commit()
    db.close()

    return jsonify({"message": "Job description saved successfully."})

# --------------------------------------
# NEW ROUTE: generate-job-description
# --------------------------------------

@app.route('/api/generate-job-description', methods=['POST'])
def generate_or_fetch_description():
    db = SessionLocal()
    payload = request.get_json()
    profile_name = payload.get("profileName")

    if not profile_name:
        db.close()
        return jsonify({"error": "profileName is required"}), 400

    profile = db.query(JobProfile).filter(
        JobProfile.title.ilike(profile_name)
    ).first()

    if profile:
        jd = profile.description

        if jd:
            result = {
                "vertical": jd.vertical,
                "division": jd.division,
                "subdivision": jd.subdivision,
                "internal": {
                    "purpose": jd.purpose,
                    "responsibilities": jd.responsibilities,
                    "manager": jd.manager,
                    "travel": jd.travel,
                    "physical": jd.physical,
                    "workconditions": jd.workconditions,
                    "minqualifications": jd.minqualifications,
                    "preferredqualifications": jd.preferredqualifications,
                    "mineducation": jd.mineducation,
                    "preferrededucation": jd.preferrededucation,
                    "minexperience": jd.minexperience,
                    "certifications": jd.certifications,
                    "competencies": jd.competencies,
                },
                "external": {
                    "whatYoullDo": jd.whatYoullDo,
                    "whatWeLookFor": jd.whatWeLookFor,
                    "qualitiesThatStir": jd.qualitiesThatStir
                }
            }
        else:
            jd_dict = generate_description(profile)
            result = {
                "vertical": jd_dict["vertical"],
                "division": jd_dict["division"],
                "subdivision": jd_dict["subdivision"],
                "internal": {k: jd_dict[k] for k in [
                    "purpose", "responsibilities", "manager", "travel",
                    "physical", "workconditions", "minqualifications",
                    "preferredqualifications", "mineducation", "preferrededucation",
                    "minexperience", "certifications", "competencies"
                ]},
                "external": {k: jd_dict[k] for k in [
                    "whatYoullDo", "whatWeLookFor", "qualitiesThatStir"
                ]}
            }
    else:
        profile = JobProfile(title=profile_name)
        db.add(profile)
        db.commit()

        jd_dict = generate_description(profile)
        result = {
            "vertical": jd_dict["vertical"],
            "division": jd_dict["division"],
            "subdivision": jd_dict["subdivision"],
            "internal": {k: jd_dict[k] for k in [
                "purpose", "responsibilities", "manager", "travel",
                "physical", "workconditions", "minqualifications",
                "preferredqualifications", "mineducation", "preferrededucation",
                "minexperience", "certifications", "competencies"
            ]},
            "external": {k: jd_dict[k] for k in [
                "whatYoullDo", "whatWeLookFor", "qualitiesThatStir"
            ]}
        }

    db.close()
    return jsonify(result)

# --------------------------------------
# NEW ROUTE: save description by title
# --------------------------------------

@app.route('/api/job-description/by-title', methods=['POST'])
def save_description_by_title():
    db = SessionLocal()
    payload = request.get_json()
    profile_name = payload.get("profileName")

    if not profile_name:
        db.close()
        return jsonify({"error": "profileName is required"}), 400

    profile = db.query(JobProfile).filter(
        JobProfile.title.ilike(profile_name)
    ).first()

    if not profile:
        db.close()
        return jsonify({"error": "Job profile not found."}), 404

    if profile.description:
        db.delete(profile.description)
        db.commit()

    jd = JobDescription(
        job_profile_id=profile.id,
        vertical=payload.get("vertical"),
        division=payload.get("division"),
        subdivision=payload.get("subdivision"),
        purpose=payload["internal"].get("purpose"),
        responsibilities=payload["internal"].get("responsibilities"),
        manager=payload["internal"].get("manager"),
        travel=payload["internal"].get("travel"),
        physical=payload["internal"].get("physical"),
        workconditions=payload["internal"].get("workconditions"),
        minqualifications=payload["internal"].get("minqualifications"),
        preferredqualifications=payload["internal"].get("preferredqualifications"),
        mineducation=payload["internal"].get("mineducation"),
        preferrededucation=payload["internal"].get("preferrededucation"),
        minexperience=payload["internal"].get("minexperience"),
        certifications=payload["internal"].get("certifications"),
        competencies=payload["internal"].get("competencies"),
        whatYoullDo=payload["external"].get("whatYoullDo"),
        whatWeLookFor=payload["external"].get("whatWeLookFor"),
        qualitiesThatStir=payload["external"].get("qualitiesThatStir"),
    )

    db.add(jd)
    db.commit()
    db.close()

    return jsonify({"message": "Job description saved successfully."})


@app.route('/api/job-description/send-link', methods=['POST'])
def send_approval_link():
    db = SessionLocal()
    payload = request.get_json()

    profile_name = payload.get("profileName")
    recipient_email = payload.get("recipientEmail")

    if not profile_name or not recipient_email:
        db.close()
        return jsonify({"error": "profileName and recipientEmail are required"}), 400

    token = str(uuid.uuid4())

    pending = PendingJobDescription(
        token=token,
        profile_name=profile_name,
        payload=payload
    )
    db.add(pending)
    db.commit()

    # # build link
    # approval_link = f"http://localhost:5174/approve-job-description/{token}"

    # # send email
    # send_email(
    #     recipient_email,
    #     f"Approve Job Description for {profile_name}",
    #     f"Please click the link below to approve the job description:\n\n{approval_link}"
    # )

    xml_file_path = create_job_profile_xml(profile_name, payload)


    db.close()

    return jsonify({"message": "Approval link sent successfully."})


import os
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.dom import minidom
from datetime import date


def prettify_xml(element):
    """
    Convert ElementTree to a nicely formatted XML string.
    """
    from xml.etree.ElementTree import tostring
    rough_string = tostring(element, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ", encoding="UTF-8").decode("utf-8")


def create_job_profile_xml(profile_name, payload):
    """
    Generates and saves a Workday-style Job Profile XML with all fields
    from internal + external included inside <wd:Job_Description>.
    """
    namespaces = {
        "env": "http://schemas.xmlsoap.org/soap/envelope/",
        "xsd": "http://www.w3.org/2001/XMLSchema",
        "wd": "urn:com.workday/bsvc"
    }

    # Root envelope setup
    env = Element("env:Envelope", {
        "xmlns:env": namespaces["env"],
        "xmlns:xsd": namespaces["xsd"]
    })
    body = SubElement(env, "env:Body")

    submit_req = SubElement(body, "wd:Submit_Job_Profile_Request", {
        "xmlns:wd": namespaces["wd"],
        "wd:Add_Only": "true",
        "wd:version": "v44.1"
    })

    bp_params = SubElement(submit_req, "wd:Business_Process_Parameters")
    SubElement(bp_params, "wd:Auto_Complete").text = "true"
    SubElement(bp_params, "wd:Run_Now").text = "true"
    SubElement(bp_params, "wd:Discard_On_Exit_Validation_Error").text = "true"

    job_profile_data = SubElement(submit_req, "wd:Job_Profile_Data")
    job_req_data = SubElement(job_profile_data, "wd:Job_Profile_Request_Data")

    job_code = profile_name.upper().replace(" ", "_")
    effective_date = date.today().strftime("%Y-%m-%d")

    SubElement(job_req_data, "wd:Job_Code").text = job_code
    SubElement(job_req_data, "wd:Effective_Date").text = effective_date

    job_basic_data = SubElement(job_req_data, "wd:Job_Profile_Basic_Data")
    SubElement(job_basic_data, "wd:Inactive").text = "false"
    SubElement(job_basic_data, "wd:Job_Title").text = profile_name

    # -------------------------------
    # Collect all Job Description fields
    # -------------------------------
    internal = payload.get("internal", {})
    external = payload.get("external", {})

    description_parts = []

    def add_field(label, value):
        if value and str(value).strip():
            description_parts.append(f"{label}: {value.strip()}")

    add_field("Purpose", internal.get("purpose"))
    add_field("Key Responsibilities", internal.get("responsibilities"))
    add_field("Direct Manager/Reports", internal.get("manager"))
    add_field("Travel Requirements", internal.get("travel"))
    add_field("Physical Requirements", internal.get("physical"))
    add_field("Working Conditions", internal.get("workconditions"))
    add_field("Minimum Qualifications", internal.get("minqualifications"))
    add_field("Preferred Qualifications", internal.get("preferredqualifications"))
    add_field("Minimum Education", internal.get("mineducation"))
    add_field("Preferred Education", internal.get("preferrededucation"))
    add_field("Minimum Experience", internal.get("minexperience"))
    add_field("Certifications", internal.get("certifications"))
    add_field("Competencies", internal.get("competencies"))
    add_field("What You'll Do", external.get("whatYoullDo"))
    add_field("What We Look For", external.get("whatWeLookFor"))
    add_field("Qualities That Stir Our Souls", external.get("qualitiesThatStir"))

    # Combine all fields into one large block
    combined_description = "Approved .. " + "\n\n".join(description_parts)
    SubElement(job_basic_data, "wd:Job_Description").text = combined_description

    # Static references
    mgmt_ref = SubElement(job_basic_data, "wd:Management_Level_Reference")
    mgmt_id = SubElement(mgmt_ref, "wd:ID", {"wd:type": "Management_Level_ID"})
    mgmt_id.text = "MANAGEMENT_LEVEL-3-30"

    job_family_data = SubElement(job_basic_data, "wd:Job_Family_Data")
    job_family_ref = SubElement(job_family_data, "wd:Job_Family_Reference")
    jf_id = SubElement(job_family_ref, "wd:ID", {"wd:type": "Job_Family_ID"})
    jf_id.text = "EMPLOYEE_RELATIONS"

    # -------------------------------
    # Save to file
    # -------------------------------
    pretty_xml_str = prettify_xml(env)
    os.makedirs("exports/job_profiles", exist_ok=True)
    file_path = os.path.join("exports/job_profiles", f"{job_code}.xml")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml_str)

    return os.path.abspath(file_path)



def send_email(to_email, subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "srinath97gr@gmail.com"
    smtp_password = "vxbidrzxhxkqklcd"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to_email], msg.as_string())

@app.route('/api/job-description/approve/<token>', methods=['POST'])
def approve_job_description(token):
    db = SessionLocal()

    pending = db.query(PendingJobDescription).filter(
        PendingJobDescription.token == token
    ).first()

    if not pending:
        db.close()
        return jsonify({"error": "Invalid or expired approval link."}), 404

    payload = pending.payload
    profile_name = pending.profile_name

    profile = db.query(JobProfile).filter(
        JobProfile.title.ilike(profile_name)
    ).first()

    if not profile:
        db.close()
        return jsonify({"error": "Job profile not found."}), 404

    if profile.description:
        db.delete(profile.description)
        db.commit()

    jd = JobDescription(
        job_profile_id=profile.id,
        vertical=payload.get("vertical"),
        division=payload.get("division"),
        subdivision=payload.get("subdivision"),
        purpose=payload["internal"].get("purpose"),
        responsibilities=payload["internal"].get("responsibilities"),
        manager=payload["internal"].get("manager"),
        travel=payload["internal"].get("travel"),
        physical=payload["internal"].get("physical"),
        workconditions=payload["internal"].get("workconditions"),
        minqualifications=payload["internal"].get("minqualifications"),
        preferredqualifications=payload["internal"].get("preferredqualifications"),
        mineducation=payload["internal"].get("mineducation"),
        preferrededucation=payload["internal"].get("preferrededucation"),
        minexperience=payload["internal"].get("minexperience"),
        certifications=payload["internal"].get("certifications"),
        competencies=payload["internal"].get("competencies"),
        whatYoullDo=payload["external"].get("whatYoullDo"),
        whatWeLookFor=payload["external"].get("whatWeLookFor"),
        qualitiesThatStir=payload["external"].get("qualitiesThatStir"),
    )

    db.add(jd)
    db.commit()

    # delete pending
    db.delete(pending)
    db.commit()

    db.close()

    return jsonify({"message": "Job description approved and saved successfully."})

@app.route('/api/job-description/pending/<token>', methods=['GET'])
def fetch_pending_description(token):
    db = SessionLocal()

    pending = db.query(PendingJobDescription).filter(
        PendingJobDescription.token == token
    ).first()

    if not pending:
        db.close()
        return jsonify({"error": "Invalid or expired token."}), 404

    db.close()
    return jsonify(pending.payload)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app.run(port=5000, debug=True)

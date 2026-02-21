from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import openai
import io
import os

app = Flask(__name__)
CORS(app)

# Configuration
openai.api_key = 'api_key'
SAVE_FOLDER = r"C:\Users\srina\Documents\HR application\processed"
PROMPTS = {
    "internal_with_sources": """Reformat the following two Job descriptions into Desired format:

{desc_1}
{desc_2}

Desired format:
     Position Purpose:
     Key Responsibilities:
     Direct Manager/Direct Reports:
     Travel Requirements:
     Physical Requirements:
     Working Conditions:
     Minimum Qualifications:
     Preferred Qualifications:
     Minimum Education:
     Preferred Education:
     Minimum Years of Work Experience:
     Certifications:
     Competencies:""",

    "external_with_sources": """Reformat the following two Job descriptions into Desired format:

{desc_1}
{desc_2}

Desired format:
What You’ll Do:  
• 2-3 sentence high level summary of role itself PLUS 6 -8 bullets max with DUTIES  
What We Look For:    
• 6-8 bullets max with key requirements
Qualities that Stir our Souls (and make you stand out):   
• 4 bullets with “nice to have” experience, skills, and/or attributes.""",

    "internal_fallback": """generate Job description for {job_profile} in a {vertical} distribution company in the desired format below:

Desired format:
     Position Purpose:
     Key Responsibilities:
     Direct Manager/Direct Reports:
     Travel Requirements:
     Physical Requirements:
     Working Conditions:
     Minimum Qualifications:
     Preferred Qualifications:
     Minimum Education:
     Preferred Education:
     Minimum Years of Work Experience:
     Certifications:
     Competencies:""",

    "external_fallback": """generate Job description for {job_profile} in a {vertical} distribution company in the desired format below:

Desired format:
What You’ll Do:  
• 2-3 sentence high level summary of role itself PLUS 6 -8 bullets max with DUTIES  
What We Look For:    
• 6-8 bullets max with key requirements
Qualities that Stir our Souls (and make you stand out):   
• 4 bullets with “nice to have” experience, skills, and/or attributes."""
} 

os.makedirs(SAVE_FOLDER, exist_ok=True)

def query_chatgpt(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def generate_outputs(job_profile,  vertical, desc_1="", desc_2=""):
    if desc_1 or desc_2:
        prompt_1 = PROMPTS["internal_with_sources"].format(desc_1=desc_1, desc_2=desc_2)
        prompt_2 = PROMPTS["external_with_sources"].format(desc_1=desc_1, desc_2=desc_2)
    else:
        prompt_1 = PROMPTS["internal_fallback"].format(job_profile=job_profile, vertical=vertical)
        prompt_2 = PROMPTS["external_fallback"].format(job_profile=job_profile, vertical=vertical)


    output_1 = query_chatgpt(prompt_1)
    # output_2 = query_chatgpt(prompt_2)

    # return output_1, output_2
    print(output_1)
    return output_1


def process_excel(df):
  
    required_columns = {'ID', 'Job Profile'}
    if not required_columns.issubset(df.columns):
        raise ValueError("Missing required columns like 'ID' or 'Job Profile'.")

    df.columns = [col.strip() for col in df.columns]
    output_rows = []

    print(df.columns.tolist())

    for _, row in df.iterrows():
        row_dict = row.to_dict()
        job_profile = row_dict.get('Job Profile', '')
        job_profile_Name = str(row_dict.get('Job Profile Name', ''))


        sources1 = [
            row_dict.get("Source 1 ( Job Summary)", ""),
            row_dict.get("Source 2 ( Job Description)", "")
        ]
        sources2 = [
            row_dict.get("Source 3(Additional Job Description)", ""),
            row_dict.get("Source 4(Recruiting)", "")
        ]


        vertical = row_dict.get("Vertical", "distribution")



        if any([pd.notna(src) and str(src).strip() for src in sources1]):
            desc_1 = f"Job description: {sources1[0]}" if pd.notna(sources1[0]) else ""
            desc_2 = f"Job description: {sources1[1]}" if pd.notna(sources1[1]) else ""
        elif any([pd.notna(src) and str(src).strip() for src in sources2]):
            desc_1 = f"Job description: {sources2[0]}" if pd.notna(sources2[0]) else ""
            desc_2 = f"Job description: {sources2[1]}" if pd.notna(sources2[1]) else ""
        else:
            desc_1, desc_2 = "", ""

        output_1 = generate_outputs(job_profile_Name, vertical, desc_1, desc_2)

        row_dict["Internal (Output 1)"] = output_1
        # row_dict["External (Output 2)"] = output_2
        output_rows.append(row_dict)

    return pd.DataFrame(output_rows)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        file = request.files['file']
        df = pd.read_excel(file, sheet_name="Sheet1", header=0)


        df.columns = [col.strip() for col in df.columns]


        lower_columns = {col.lower(): col for col in df.columns}
        if 'id' not in lower_columns or 'job profile' not in lower_columns:
            raise ValueError("Missing required columns: 'ID' or 'Job Profile'")

        processed_df = process_excel(df)

        output = io.BytesIO()
        save_path = os.path.join(SAVE_FOLDER, "processed_file.xlsx")

        with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
            processed_df.to_excel(writer, index=False)

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            processed_df.to_excel(writer, index=False)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name="processed_file.xlsx"
        )

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

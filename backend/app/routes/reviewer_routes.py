from flask import Blueprint, request, jsonify
from backend.app.models.job_profiles import JobProfile
from backend.app.models.reviewer import Reviewer
from backend.app import db
from flask_jwt_extended import jwt_required


reviewer_bp = Blueprint('reviewer_routes', __name__, url_prefix='/api')

@reviewer_bp.route('/reviewers-list', methods=['GET'])
@jwt_required()
def get_reviewers_list():
    profiles = JobProfile.query.all()

    profile_primary_reviewers = [p.primary_reviewer for p in profiles if p.primary_reviewer]
    profile_hr_reviewers = [p.hr_reviewer for p in profiles if p.hr_reviewer]
    profile_hiring_managers = [p.hiring_manager for p in profiles if p.hiring_manager]

    reviewers = Reviewer.query.all()

    new_primary_reviewers = [r.primary_reviewer for r in reviewers if r.primary_reviewer]
    new_hr_reviewers = [r.hr_reviewer for r in reviewers if r.hr_reviewer]
    new_hiring_managers = [r.hiring_manager for r in reviewers if r.hiring_manager]

    primary_reviewers = list(set(profile_primary_reviewers + new_primary_reviewers))
    hr_reviewers = list(set(profile_hr_reviewers + new_hr_reviewers))
    hiring_managers = list(set(profile_hiring_managers + new_hiring_managers))

    return jsonify({
        'primaryReviewers': primary_reviewers,
        'hrReviewers': hr_reviewers,
        'managers': hiring_managers
    })

@reviewer_bp.route('/admin-reviewers/add', methods=['POST'])
@jwt_required()
def add_admin_reviewer():
    data = request.get_json()
    name = data.get('name')
    reviewer_type = data.get('type')

    if not name or not reviewer_type:
        return jsonify({'error': 'Name and type are required'}), 400

    if reviewer_type not in ['primary', 'hr', 'manager']:
        return jsonify({'error': 'Invalid reviewer type'}), 400

    new_reviewer = Reviewer(
        primary_reviewer=name if reviewer_type == 'primary' else None,
        hr_reviewer=name if reviewer_type == 'hr' else None,
        hiring_manager=name if reviewer_type == 'manager' else None
    )

    db.session.add(new_reviewer)
    db.session.commit()

    return jsonify({'message': f'{reviewer_type.capitalize()} reviewer added successfully'}), 200

@reviewer_bp.route('/admin-review/update', methods=['POST'])
@jwt_required()
def update_admin_review():
    try:
        data = request.get_json()

        profile_name = data.get('profile')
        updated_data = data.get('updatedData')

        if not profile_name or not updated_data:
            return jsonify({'error': 'Profile name and updated data are required'}), 400

        job = JobProfile.query.filter_by(job_profile=profile_name).first()


        if not job:
            return jsonify({'error': 'Job profile not found'}), 404

        job.primary_reviewer = updated_data.get('primaryReviewer')
        job.hr_reviewer = updated_data.get('hrReviewer')
        job.hiring_manager = updated_data.get('hiringManager')
        job.vertical = updated_data.get('vertical')
        job.division = updated_data.get('division')
        job.subdivision = updated_data.get('subdivision')
        
        job.saved_position_purpose = updated_data.get('purpose')
        job.saved_key_responsibilities = updated_data.get('responsibilities')
        job.saved_direct_manager_direct_reports = updated_data.get('manager')
        job.saved_travel_requirements = updated_data.get('travel')
        job.saved_physical_requirements = updated_data.get('physical')
        job.saved_working_conditions = updated_data.get('workconditions')
        job.saved_minimum_qualifications = updated_data.get('minqualifications')
        job.saved_preferred_qualifications = updated_data.get('preferredqualifications')
        job.saved_minimum_education = updated_data.get('mineducation')
        job.saved_preferred_education = updated_data.get('preferrededucation')
        job.saved_minimum_years_of_work_experience = updated_data.get('minexperience')
        job.saved_certifications = updated_data.get('certifications')
        job.saved_competencies = updated_data.get('competencies')

        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    

@reviewer_bp.route('/recuriter_reviewers-list', methods=['GET'])
@jwt_required()
def get_recruiter_reviewers_list():
    profiles = JobProfile.query.all()

    profile_recruiter_reviewers = [p.primary_reviewer for p in profiles if p.primary_reviewer]

    reviewers = Reviewer.query.all()


    new_primary_reviewers = [r.primary_reviewer for r in reviewers if r.primary_reviewer]

    primary_reviewers = list(set(profile_recruiter_reviewers + new_primary_reviewers))


    return jsonify({
        'recruiterReviewers': list(set(primary_reviewers)),
    })

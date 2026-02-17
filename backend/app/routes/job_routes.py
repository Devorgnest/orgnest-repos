from flask import Blueprint, request, jsonify
from backend.app.models.job_profiles import JobProfile
from backend.app import db
from flask_jwt_extended import jwt_required
from datetime import datetime
import pytz


job_bp = Blueprint('job_routes', __name__, url_prefix='/api')

cst = pytz.timezone('US/Central')


@job_bp.route('/all-job-profiles', methods=['GET'])
@jwt_required()
def get_all_job_profiles():
    profiles = JobProfile.query.all()

    profiles_data = {}

    for p in profiles:
        profiles_data[p.job_profile] = {
            'primaryReviewer': p.primary_reviewer,
            'hrReviewer': p.hr_reviewer,
            'hiringManager': p.hiring_manager,
            'vertical': p.vertical,
            'division': p.division,
            'subdivision': p.subdivision,
            'description': {
                'purpose': p.saved_position_purpose or p.position_purpose,
                'responsibilities': p.saved_key_responsibilities or p.key_responsibilities,
                'manager': p.saved_direct_manager_direct_reports or p.direct_manager_direct_reports,
                'travel': p.saved_travel_requirements or p.travel_requirements,
                'physical': p.saved_physical_requirements or p.physical_requirements,
                'workconditions': p.saved_working_conditions or p.working_conditions,
                'minqualifications': p.saved_minimum_qualifications or p.minimum_qualifications,
                'preferredqualifications': p.saved_preferred_qualifications or p.preferred_qualifications,
                'mineducation': p.saved_minimum_education or p.minimum_education,
                'preferrededucation': p.saved_preferred_education or p.preferred_education,
                'minexperience': p.saved_minimum_years_of_work_experience or p.minimum_years_of_work_experience,
                'certifications': p.saved_certifications or p.certifications,
                'competencies': p.saved_competencies or p.competencies
            }
        }

    return jsonify(profiles_data)

@job_bp.route('/internal/all-job-profiles', methods=['GET'])
@jwt_required()
def get_all_job_profiles_internal():
    profiles = JobProfile.query.all()

    profiles_data = {}

    for p in profiles:
        profiles_data[p.job_profile] = {
            'primaryReviewer': p.primary_reviewer,
            'hrReviewer': p.hr_reviewer,
            'hiringManager': p.hiring_manager,
            'vertical': p.vertical,
            'division': p.division,
            'subdivision': p.subdivision,
            'description': {
                'purpose': p.saved_position_purpose or p.position_purpose,
                'responsibilities': p.saved_key_responsibilities or p.key_responsibilities,
                'manager': p.saved_direct_manager_direct_reports or p.direct_manager_direct_reports,
                'travel': p.saved_travel_requirements or p.travel_requirements,
                'physical': p.saved_physical_requirements or p.physical_requirements,
                'workconditions': p.saved_working_conditions or p.working_conditions,
                'minqualifications': p.saved_minimum_qualifications or p.minimum_qualifications,
                'preferredqualifications': p.saved_preferred_qualifications or p.preferred_qualifications,
                'mineducation': p.saved_minimum_education or p.minimum_education,
                'preferrededucation': p.saved_preferred_education or p.preferred_education,
                'minexperience': p.saved_minimum_years_of_work_experience or p.minimum_years_of_work_experience,
                'certifications': p.saved_certifications or p.certifications,
                'competencies': p.saved_competencies or p.competencies,
            },
            'approved_internal': p.approved_internal,
        }

    return jsonify(profiles_data)


@job_bp.route('/internal-review/save', methods=['POST'])
@jwt_required()
def save_internal_review():
    try:
        data = request.get_json()

        profile_name = data.get('profile')
        updated_data = data.get('updatedData')

        if not profile_name or not updated_data:
            return jsonify({'error': 'Profile name and updated data are required'}), 400

        job = JobProfile.query.filter_by(job_profile=profile_name).first()

        if not job:
            return jsonify({'error': 'Job profile not found'}), 404

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
    

@job_bp.route('/internal-review/approve', methods=['POST'])
@jwt_required()
def approve_internal_review():
    try:
        data = request.get_json()

        profile_name = data.get('profile')
        updated_data = data.get('updatedData')

        if not profile_name or not updated_data:
            return jsonify({'error': 'Profile name and updated data are required'}), 400

        job = JobProfile.query.filter_by(job_profile=profile_name).first()

        if not job:
            return jsonify({'error': 'Job profile not found'}), 404

        # print(updated_data)
        
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
        job.approved_internal = updated_data.get('approved_internal')
        job.approved_internal_time = datetime.now(cst).replace(tzinfo=None)

        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    

@job_bp.route('/external/all-job-profiles', methods=['GET'])
@jwt_required()
def get_all_job_profiles_external():
    profiles = JobProfile.query.all()

    profiles_data = {}

    for p in profiles:
        profiles_data[p.job_profile] = {
            'primaryReviewer': p.primary_reviewer,
            'hrReviewer': p.hr_reviewer,
            'hiringManager': p.hiring_manager,
            'vertical': p.vertical,
            'division': p.division,
            'subdivision': p.subdivision,
            'recruiterReviewer': p.recruiter_reviewer,
            'description': {
                'purpose': p.saved_position_purpose or p.position_purpose,
                'responsibilities': p.saved_key_responsibilities or p.key_responsibilities,
                'manager': p.saved_direct_manager_direct_reports or p.direct_manager_direct_reports,
                'travel': p.saved_travel_requirements or p.travel_requirements,
                'physical': p.saved_physical_requirements or p.physical_requirements,
                'workconditions': p.saved_working_conditions or p.working_conditions,
                'minqualifications': p.saved_minimum_qualifications or p.minimum_qualifications,
                'preferredqualifications': p.saved_preferred_qualifications or p.preferred_qualifications,
                'mineducation': p.saved_minimum_education or p.minimum_education,
                'preferrededucation': p.saved_preferred_education or p.preferred_education,
                'minexperience': p.saved_minimum_years_of_work_experience or p.minimum_years_of_work_experience,
                'certifications': p.saved_certifications or p.certifications,
                'competencies': p.saved_competencies or p.competencies,
                'whatYoullDo' : p.saved_what_you_will_do or p.what_you_will_do,
                'whatWeLookFor': p.saved_what_we_look_for or p.what_we_look_for,
                'qualitiesThatStir': p.saved_qualities_that_stir_our_souls or p.qualities_that_stir_our_souls
            },
            'approved_internal': p.approved_internal,
            'approved_external': p.approved_external
        }

    return jsonify(profiles_data)


@job_bp.route('/external-review/save', methods=['POST'])
@jwt_required()
def save_external_review():
    try:
        data = request.get_json()

        profile_name = data.get('profile')
        updated_data = data.get('updatedRecruiterDescription')

        print(profile_name)
        print(updated_data)

        if not profile_name or not updated_data:
            return jsonify({'error': 'Profile name and updated data are required'}), 400

        job = JobProfile.query.filter_by(job_profile=profile_name).first()

        if not job:
            return jsonify({'error': 'Job profile not found'}), 404

        job.saved_what_you_will_do = updated_data.get('whatYoullDo')
        job.saved_what_we_look_for = updated_data.get('whatWeLookFor')
        job.saved_qualities_that_stir_our_souls = updated_data.get('qualitiesThatStir')

        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    

@job_bp.route('/external-review/approve', methods=['POST'])
@jwt_required()
def approve_external_review():
    try:
        data = request.get_json()

        profile_name = data.get('profile')
        updated_data = data.get('updatedRecruiterDescription')

        if not profile_name or not updated_data:
            return jsonify({'error': 'Profile name and updated data are required'}), 400

        job = JobProfile.query.filter_by(job_profile=profile_name).first()

        if not job:
            return jsonify({'error': 'Job profile not found'}), 404

        
        job.saved_what_you_will_do = updated_data.get('whatYoullDo')
        job.saved_what_we_look_for = updated_data.get('whatWeLookFor')
        job.saved_qualities_that_stir_our_souls = updated_data.get('qualitiesThatStir')
        job.approved_external = updated_data.get('approved_external')
        job.approved_external_time = datetime.now(cst).replace(tzinfo=None)

        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


@job_bp.route('/job-profile/<job_profile>', methods=['GET'])
@jwt_required()
def get_job_profile_by_name(job_profile):
    job = JobProfile.query.filter_by(job_profile=job_profile).first()

    if not job:
        return jsonify({'error': 'Job Profile not found'}), 404

    response_data = {
        'id': job.id,
        'job_profile': job.job_profile,
        'job_code': job.job_code,
        'job_category': job.job_category,
        'job_profile_name': job.job_profile_name,
        'vertical': job.vertical,
        'division': job.division,
        'subdivision': job.subdivision,
        'primary_reviewer': job.primary_reviewer,
        'hr_reviewer': job.hr_reviewer,
        'hiring_manager': job.hiring_manager
    }

    field_names = [
        'position_purpose',
        'key_responsibilities',
        'direct_manager_direct_reports',
        'travel_requirements',
        'physical_requirements',
        'working_conditions',
        'minimum_qualifications',
        'preferred_qualifications',
        'minimum_education',
        'preferred_education',
        'minimum_years_of_work_experience',
        'certifications',
        'competencies',
        'what_you_will_do',
        'what_we_look_for',
        'qualities_that_stir_our_souls'
    ]

    for field in field_names:
        saved_field = f"saved_{field}"  

        saved_value = getattr(job, saved_field)
        final_value = getattr(job, field)

        if saved_value and saved_value.strip():
            response_data[field] = saved_value
        else:
            response_data[field] = final_value

    return jsonify(response_data)


@job_bp.route('/job-profile-approvals', methods=['GET'])
@jwt_required()
def get_job_profile_approvals():
    profiles = JobProfile.query.all()
    result = []

    for p in profiles:
        result.append({
            'id': p.id,
            'jobProfile': p.job_profile,
            'jobProfileName': p.job_profile_name,
            'approvalInternal': p.approved_internal,
            'approvalInternalTime': p.approved_internal_time if p.approved_internal_time else None,
            'approvalExternal': p.approved_external,
            'approvalExternalTime': p.approved_external_time if p.approved_external_time else None,
            'primaryReviewer': p.primary_reviewer,
            'hrReviewer': p.hr_reviewer,
            'hiringManager': p.hiring_manager,
            'recruiterReviewer': p.recruiter_reviewer,
        })

    return jsonify(result), 200


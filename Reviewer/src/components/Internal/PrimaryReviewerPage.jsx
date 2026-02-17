import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import './PrimaryReviewer.css'; 
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const PrimaryReviewerPage = () => {
  const [profilesData, setProfilesData] = useState({});
  const [loading, setLoading] = useState(true);
  const token = sessionStorage.getItem('token1') || '';

  const [selectedReviewer, setSelectedReviewer] = useState('');
  const [selectedHRReviewer, setSelectedHRReviewer] = useState('');
  const [selectedHiringManager, setSelectedHiringManager] = useState(''); 
  const [reviewersList, setReviewersList] = useState({
    primaryReviewers: [],
    hrReviewers: [],
    managers: []
  });
  const [approvalFilter, setApprovalFilter] = useState('all');
  const [selectedProfile, setSelectedProfile] = useState('');
  const [mainEditable, setMainEditable] = useState(false);
  const [selectedRole, setSelectedRole] = useState('');

  const [formState, setFormState] = useState({
    purpose: '',
    responsibilities: '',
    manager: '',
    travel: '',
    physical: '',
    workconditions: '',
    minqualifications: '',
    preferredqualifications: '',
    mineducation: '',
    preferrededucation: '',
    minexperience: '',
    certifications: '',
    competencies: '',
    approved_internal: ''
  });

  const [editBuffer, setEditBuffer] = useState({});
  const [sectionEditable, setSectionEditable] = useState({
    purpose: false,
    responsibilities: false,
    manager: false,
    travel: false,
    physical: false,
    workconditions: false,
    minqualifications: false,
    preferredqualifications: false,
    mineducation: false,
    preferrededucation: false,
    minexperience: false,
    certifications: false,
    competencies: false
  });

  useEffect(() => {
    fetchProfiles();
  }, [selectedReviewer, selectedHRReviewer, selectedHiringManager]);

  const fetchProfiles = async () => {
    try {
      const [profilesResponse, reviewersResponse] = await Promise.all([
        fetch('http://127.0.0.1:5000/api/internal/all-job-profiles', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }),
        fetch('http://127.0.0.1:5000/api/reviewers-list', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        })
      ]);

      const profilesData = await profilesResponse.json();
      const reviewersData = await reviewersResponse.json();
      setProfilesData(profilesData);
      setReviewersList(reviewersData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching profiles:', error);
      setLoading(false);
    }
  };

  const handleProfileSelect = (profile) => {
    const profileData = profilesData[profile];
    const descData = profileData.description;
    const newState = {
      vertical: profileData.vertical,
      division: profileData.division,
      subdivision: profileData.subdivision,
      purpose: descData.purpose,
      responsibilities: descData.responsibilities,
      manager: descData.manager,
      travel: descData.travel,
      physical: descData.physical,
      workconditions: descData.workconditions,
      minqualifications: descData.minqualifications,
      preferredqualifications: descData.preferredqualifications,
      mineducation: descData.mineducation,
      preferrededucation: descData.preferrededucation,
      minexperience: descData.minexperience,
      certifications: descData.certifications,
      competencies: descData.competencies,
      approved_internal: profileData.approved_internal
    };
    setFormState(newState);
    setSelectedProfile(profile);
    setMainEditable(false);
    setSectionEditable(Object.keys(sectionEditable).reduce((acc, key) => ({ ...acc, [key]: false }), {}));
  };

  const toggleSectionEdit = (section) => {
    setSectionEditable(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const handleSave = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/internal-review/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ profile: selectedProfile, updatedData: editBuffer })
      });
      if (response.ok) {
        setFormState(editBuffer);
        setMainEditable(false);
        setSectionEditable(Object.keys(sectionEditable).reduce((acc, key) => ({ ...acc, [key]: false }), {}));
        await fetchProfiles();
        toast.success("Changes saved successfully!");
      } else {
        toast.error("Failed to save changes.");
      }
    } catch (error) {
      console.error('Error saving changes:', error);
      toast.error("Failed to save changes.");
    }
  };

  const handleApprove = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/internal-review/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          profile: selectedProfile,
          updatedData: {
            ...editBuffer,
            'approved_internal': 'yes'
          }
        })
      });
      if (response.ok) {
        setFormState(editBuffer);
        setMainEditable(false);
        setSectionEditable(Object.keys(sectionEditable).reduce((acc, key) => ({ ...acc, [key]: false }), {}));
        setSelectedProfile('');
        await fetchProfiles();
        toast.success("Changes approved successfully!");
      } else {
        toast.error("Failed to approve changes.");
      }
    } catch (error) {
      console.error('Error approving profile:', error);
      toast.error("Failed to approve changes.");
    }
  };

  const loggedInUser = sessionStorage.getItem('username') || '';
  const filteredProfiles = Object.keys(profilesData).filter(profile => {
    const data = profilesData[profile];
    const matches = data.primaryReviewer === loggedInUser || data.hrReviewer === loggedInUser || data.hiringManager === loggedInUser;
    const isApproved = data.approved_internal === 'yes';
    const matchesApproval = approvalFilter === 'all' ? true : approvalFilter === 'approved' ? isApproved : !isApproved;
    return matches && matchesApproval;
  });

  const getLabelWithCheck = (profile) => {
    const isApproved = profilesData[profile]?.approved_internal === 'yes';
    return isApproved ? `${profile} ✅` : profile;
  };

  if (loading) {
    return <div>Loading profiles...</div>;
  }
  

  return (


<div className="primary-page-wrapper">


    <div className="primary-review-container">
      <h2 className="page-heading">Primary Review</h2>


    <div className="combined-dropdown-group">

      <div className="dropdown-group">

        <div>
          <label>Approval Status</label>
          <select
            value={approvalFilter}
            onChange={(e) => { setApprovalFilter(e.target.value); setSelectedProfile('');}}  // Reset Profile Selection When Changing Filters
            className="dropdown"
          >
            <option value="all">All Profiles</option>
            <option value="approved">Approved</option>
            <option value="unapproved">Unapproved</option>
          </select>
        </div>

      </div>
<div className= "dropdown-group-2">

<div className = "profile-dropdown">   
  <label className="job-profile-label">Job Profile</label>       
<Select
  className="react-select-container"
  classNamePrefix="react-select"
  isSearchable
  // isDisabled={!selectedRole}
  options={filteredProfiles.map(profile => ({
    value: profile,
    label: profilesData[profile].approved_internal
      ? `${profile} ✅`
      : profile
  }))}
  value={
  selectedProfile
    ? filteredProfiles
        .map(profile => ({
          value: profile,
          label: profilesData[profile]?.approved_internal
            ? `${profile} ✅`
            : profile
        }))
        .find(option => option.value === selectedProfile)
    : null
}

  onChange={(selectedOption) => handleProfileSelect(selectedOption.value)}
  placeholder="Select Job Profile"
/>
</div>
        

        <div>
  <button
    onClick={() => {
      setSelectedReviewer('');
      setSelectedHRReviewer('');
      setSelectedHiringManager('');
      setSelectedRole('');
      setSelectedProfile('');
    }}
    className="reset-button"
  >
    Reset Selection
  </button>
  </div>

  </div>
  </div>


{selectedProfile && (
        <>


<div className="readonly-combined-box">
      {selectedRole !== 'primary' && (
        <div><strong>Primary Reviewer:</strong> {profilesData[selectedProfile]?.primaryReviewer}</div>
      )}
      {selectedRole !== 'hr' && (
        <div><strong>HR Reviewer:</strong> {profilesData[selectedProfile]?.hrReviewer}</div>
      )}
      {selectedRole !== 'manager' && (
        <div><strong>Hiring Manager:</strong> {profilesData[selectedProfile]?.hiringManager}</div>
      )}
    </div>


    <div className="readonly-combined-box">
      <div>
        <strong>Vertical:</strong> {formState.vertical}
      </div>
      <div>
        <strong>Division:</strong> {formState.division}
      </div>
      <div>
        <strong>Sub Division:</strong> {formState.subdivision}
      </div>
    </div>
        </>
)}



      {selectedProfile && (
        <>

          <div className="job-description-header">
            <h3>Job Description</h3>
            
  <div className="edit-button-wrapper">
  <button
    className="edit-button"
    onClick={() => {


      const newMainEditable = !mainEditable;
      setMainEditable(newMainEditable);

      if (newMainEditable) {
        setEditBuffer(formState); 
      }

      const updatedSections = {};
      Object.keys(sectionEditable).forEach(section => {
        updatedSections[section] = newMainEditable;
      });
      setSectionEditable(updatedSections);
    }}


  >
    {mainEditable ? 'Cancel Edit' : 'Edit'}
  </button>
</div>

          </div>

          {[
            "purpose", "responsibilities", "manager", "travel",
            "physical", "workconditions", "minqualifications",
            "preferredqualifications", "mineducation", "preferrededucation",
            "minexperience", "certifications", "competencies"
          ].map((key) => (
            <div key={key} className="description-section">
              <div className="section-header">
                <h4>{{
                  purpose: "Position Purpose",
                  responsibilities: "Key Responsibilities",
                  manager: "Direct Manager/Direct Reports",
                  travel: "Travel Requirements",
                  physical: "Physical Requirements",
                  workconditions: "Working Conditions",
                  minqualifications: "Minimum Qualifications",
                  preferredqualifications: "Preferred Qualifications",
                  mineducation: "Minimum Education",
                  preferrededucation: "Preferred Education",
                  minexperience: "Minimum Experience",
                  certifications: "Certifications",
                  competencies: "Competencies"
                }[key]}</h4>

                {mainEditable && (
                  <button
                    className="section-edit-button"
                    onClick={() => {
                      if (sectionEditable[key]) {
                        
                        setEditBuffer(prev => ({
                          ...prev,
                          [key]: formState[key]
                        }));
                      }
                      toggleSectionEdit(key)
                    }}
                  >
                    {sectionEditable[key] ? 'Cancel' : 'Edit'}
                  </button>
                )}
              </div>

              {!sectionEditable[key] ? (
                <p>
                {formState[key]?.split('\n').map((line, index) => (
                  <React.Fragment key={index}>
                    {line}
                    <br />
                  </React.Fragment>
                ))}
              </p>
              ) : (
                <textarea
                  value={editBuffer[key]}
                  onChange={(e) =>
                    setEditBuffer(prev => ({ ...prev, [key]: e.target.value }))
                  }
                  rows={4}
                  className="editable-textarea"
                />
              )}

            </div>
          ))}

          {mainEditable && (
            <div style={{ marginTop: '20px' }}>
              <button className="save-button" onClick={handleSave}>
                Save Changes
              </button>
            </div>
          )}

{selectedProfile && profilesData[selectedProfile]?.primaryReviewer === loggedInUser && (
  <div className="approve-button-container">
    <button
      className="approve-button"
      onClick={() => handleApprove()}
    >
      Approve
    </button>
  </div>
)}

        </>
      )}
    </div>

      <ToastContainer position="top-center" autoClose={3000} hideProgressBar />


</div>


  );
};

export default PrimaryReviewerPage;

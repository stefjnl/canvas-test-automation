// Request form functionality
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const stepScenario = document.getElementById('step-scenario');
    const stepConfiguration = document.getElementById('step-configuration');
    const stepPreview = document.getElementById('step-preview');
    const scenarioCards = document.querySelectorAll('.scenario-card');
    const backToScenarios = document.getElementById('back-to-scenarios');
    const previewButton = document.getElementById('preview-request');
    const backToForm = document.getElementById('back-to-form');
    const submitButton = document.getElementById('submit-request');
    
    let selectedScenario = null;
    
    // Scenario selection
    scenarioCards.forEach(card => {
        card.addEventListener('click', function() {
            selectedScenario = this.dataset.scenario;
            scenarioCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            
            // Load scenario defaults
            loadScenarioDefaults(selectedScenario);
            
            // Move to configuration
            stepScenario.style.display = 'none';
            stepConfiguration.style.display = 'block';
            window.scrollTo(0, 0);
        });
    });
    
    // Navigation
    backToScenarios.addEventListener('click', () => {
        stepConfiguration.style.display = 'none';
        stepScenario.style.display = 'block';
    });
    
    previewButton.addEventListener('click', () => {
        generatePreview();
        stepConfiguration.style.display = 'none';
        stepPreview.style.display = 'block';
        window.scrollTo(0, 0);
    });
    
    backToForm.addEventListener('click', () => {
        stepPreview.style.display = 'none';
        stepConfiguration.style.display = 'block';
    });
    
    // Dynamic form elements
    document.getElementById('create-subaccount').addEventListener('change', function() {
        document.getElementById('subaccount-details').style.display = 
            this.checked ? 'block' : 'none';
    });
    
    document.getElementById('add-apps').addEventListener('change', function() {
        document.getElementById('app-details').style.display = 
            this.checked ? 'block' : 'none';
    });
    
    // Add course functionality
    document.getElementById('add-course').addEventListener('click', () => {
        const container = document.getElementById('courses-container');
        const courseDiv = document.createElement('div');
        courseDiv.className = 'course-config';
        courseDiv.innerHTML = `
            <div class="form-row">
                <div class="form-group flex-2">
                    <label>Course Name *</label>
                    <input type="text" class="course-name" placeholder="Course name">
                </div>
                <div class="form-group">
                    <label>Sections</label>
                    <input type="number" class="course-sections" value="1" min="1">
                </div>
                <button type="button" class="btn-icon remove-course" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Test Students</label>
                    <input type="number" class="test-students" value="5" min="0">
                </div>
                <div class="form-group">
                    <label>Test Teachers</label>
                    <input type="number" class="test-teachers" value="1" min="0">
                </div>
            </div>
        `;
        container.appendChild(courseDiv);
    });
    
    // Load scenario defaults
    function loadScenarioDefaults(scenario) {
        const defaults = {
            'app-integration': {
                subaccount: true,
                subaccountName: 'App Integration Test',
                courses: [{name: 'Test Course with App', sections: 2, students: 20, teachers: 1}],
                apps: true,
                appNames: 'Peerceptiv'
            },
            'department-structure': {
                subaccount: true,
                subaccountName: 'Test Faculty',
                courses: [
                    {name: 'Introduction Course', sections: 1, students: 10, teachers: 1},
                    {name: 'Advanced Course', sections: 1, students: 5, teachers: 1}
                ]
            },
            'bulk-testing': {
                subaccount: true,
                subaccountName: 'Bulk Testing',
                courses: [{name: 'Large Test Course', sections: 4, students: 50, teachers: 3}]
            },
            'assignment-workflow': {
                subaccount: false,
                courses: [{name: 'Assignment Test Course', sections: 1, students: 10, teachers: 1}]
            }
        };
        
        if (defaults[scenario]) {
            const config = defaults[scenario];
            
            // Set form values
            document.getElementById('create-subaccount').checked = config.subaccount || false;
            document.getElementById('subaccount-details').style.display = config.subaccount ? 'block' : 'none';
            
            if (config.subaccountName) {
                document.getElementById('subaccount-name').value = config.subaccountName;
            }
            
            if (config.apps) {
                document.getElementById('add-apps').checked = true;
                document.getElementById('app-details').style.display = 'block';
                document.getElementById('app-names').value = config.appNames || '';
            }
            
            // Set courses
            if (config.courses) {
                const container = document.getElementById('courses-container');
                container.innerHTML = ''; // Clear existing
                
                config.courses.forEach(course => {
                    const courseDiv = document.createElement('div');
                    courseDiv.className = 'course-config';
                    courseDiv.innerHTML = `
                        <div class="form-row">
                            <div class="form-group flex-2">
                                <label>Course Name *</label>
                                <input type="text" class="course-name" value="${course.name}">
                            </div>
                            <div class="form-group">
                                <label>Sections</label>
                                <input type="number" class="course-sections" value="${course.sections}" min="1">
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Test Students</label>
                                <input type="number" class="test-students" value="${course.students}" min="0">
                            </div>
                            <div class="form-group">
                                <label>Test Teachers</label>
                                <input type="number" class="test-teachers" value="${course.teachers}" min="0">
                            </div>
                        </div>
                    `;
                    container.appendChild(courseDiv);
                });
            }
        }
    }
    
    // Generate preview
    function generatePreview() {
        const preview = {
            requester: document.getElementById('requester-name').value,
            topdesk: document.getElementById('topdesk-number').value,
            environment: document.getElementById('environment').value,
            jiraEpic: document.getElementById('jira-epic').value,
            startDate: document.getElementById('start-date').value,
            endDate: document.getElementById('end-date').value,
            adminUsers: document.getElementById('admin-users').value,
            createSubaccount: document.getElementById('create-subaccount').checked,
            subaccountName: document.getElementById('subaccount-name').value,
            courses: [],
            options: {
                terms: document.getElementById('configure-terms').checked,
                apps: document.getElementById('add-apps').checked,
                appNames: document.getElementById('app-names').value,
                developerKeys: document.getElementById('developer-keys').checked,
                integrationAccounts: document.getElementById('integration-accounts').checked
            },
            notes: document.getElementById('special-notes').value
        };
        
        // Collect courses
        document.querySelectorAll('.course-config').forEach(config => {
            preview.courses.push({
                name: config.querySelector('.course-name').value,
                sections: config.querySelector('.course-sections').value,
                students: config.querySelector('.test-students').value,
                teachers: config.querySelector('.test-teachers').value
            });
        });
        
        // Generate HTML preview (matching menukaart format)
        const previewHtml = `
            <table class="menukaart-preview">
                <tr class="section-header">
                    <td colspan="3">Inrichting en afspraken testomgeving</td>
                </tr>
                <tr>
                    <td>Aanvrager</td>
                    <td colspan="2">${preview.requester}</td>
                </tr>
                <tr>
                    <td>Topdesk nr.</td>
                    <td colspan="2">${preview.topdesk || '-'}</td>
                </tr>
                <tr>
                    <td>Jira epic nr.</td>
                    <td colspan="2">${preview.jiraEpic || '-'}</td>
                </tr>
                <tr>
                    <td>Omgeving</td>
                    <td colspan="2">${preview.environment.toUpperCase()}</td>
                </tr>
                <tr>
                    <td rowspan="3">Toegang/bewaartermijn</td>
                    <td>Datum vanaf</td>
                    <td>${formatDate(preview.startDate)}</td>
                </tr>
                <tr>
                    <td>Datum tot</td>
                    <td>${formatDate(preview.endDate)}</td>
                </tr>
                <tr>
                    <td>Datum opschoning</td>
                    <td>${formatDate(preview.endDate)}</td>
                </tr>
                <tr class="section-divider"><td colspan="3"></td></tr>
                ${preview.createSubaccount ? `
                <tr>
                    <td>Nieuw sub-account</td>
                    <td colspan="2">${preview.subaccountName}</td>
                </tr>
                ` : ''}
                <tr>
                    <td>Admin toegang</td>
                    <td colspan="2">${preview.adminUsers}</td>
                </tr>
                ${preview.courses.map((course, i) => `
                <tr>
                    <td>${i === 0 ? 'Cursus' : ''}</td>
                    <td colspan="2">${course.name} (${course.sections} secties)</td>
                </tr>
                <tr>
                    <td>Studenten</td>
                    <td colspan="2">${course.students} teststudenten</td>
                </tr>
                <tr>
                    <td>Docenten</td>
                    <td colspan="2">${course.teachers} docent(en)</td>
                </tr>
                `).join('')}
                ${preview.options.terms ? `
                <tr>
                    <td>Terms</td>
                    <td colspan="2">Ja</td>
                </tr>
                ` : ''}
                ${preview.options.apps ? `
                <tr class="section-divider"><td colspan="3">Koppelingen</td></tr>
                <tr>
                    <td>Apps</td>
                    <td colspan="2">${preview.options.appNames}</td>
                </tr>
                ` : ''}
                ${preview.notes ? `
                <tr class="section-divider"><td colspan="3">Overig</td></tr>
                <tr>
                    <td colspan="3">${preview.notes}</td>
                </tr>
                ` : ''}
            </table>
        `;
        
        document.getElementById('preview-content').innerHTML = previewHtml;
    }
    
    // Format date
    function formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        const months = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
        return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
    }
    
    // Submit request
    submitButton.addEventListener('click', async () => {
        // Show loading
        submitButton.disabled = true;
        submitButton.querySelector('.btn-text').style.display = 'none';
        submitButton.querySelector('.spinner').style.display = 'inline-block';
        
        // Collect all form data
        const requestData = collectFormData();
        
        try {
            const response = await fetch('/api/submit-request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (response.ok) {
                const result = await response.json();
                showToast('Request submitted successfully!', 'success');
                
                // Redirect to dashboard or show success page
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                throw new Error('Failed to submit request');
            }
        } catch (error) {
            showToast('Error submitting request: ' + error.message, 'error');
        } finally {
            // Reset button
            submitButton.disabled = false;
            submitButton.querySelector('.btn-text').style.display = 'inline';
            submitButton.querySelector('.spinner').style.display = 'none';
        }
    });
    
    function collectFormData() {
        // Collect all form data for submission
        const courses = [];
        document.querySelectorAll('.course-config').forEach(config => {
            courses.push({
                name: config.querySelector('.course-name').value,
                sections: parseInt(config.querySelector('.course-sections').value),
                students: parseInt(config.querySelector('.test-students').value),
                teachers: parseInt(config.querySelector('.test-teachers').value)
            });
        });
        
        return {
            scenario: selectedScenario,
            requester: document.getElementById('requester-name').value,
            topdesk_number: document.getElementById('topdesk-number').value,
            environment: document.getElementById('environment').value,
            jira_epic: document.getElementById('jira-epic').value,
            start_date: document.getElementById('start-date').value,
            end_date: document.getElementById('end-date').value,
            admin_users: document.getElementById('admin-users').value.split(',').map(u => u.trim()),
            subaccount: {
                create: document.getElementById('create-subaccount').checked,
                name: document.getElementById('subaccount-name').value
            },
            courses: courses,
            options: {
                configure_terms: document.getElementById('configure-terms').checked,
                add_apps: document.getElementById('add-apps').checked,
                app_names: document.getElementById('app-names').value.split(',').map(a => a.trim()),
                developer_keys: document.getElementById('developer-keys').checked,
                integration_accounts: document.getElementById('integration-accounts').checked
            },
            special_notes: document.getElementById('special-notes').value
        };
    }
});
document.addEventListener('DOMContentLoaded', function() {
    const setupBtn = document.getElementById('setup-btn');
    const cleanupBtn = document.getElementById('cleanup-btn');
    const resultsSection = document.getElementById('results');
    const resultsContent = document.getElementById('results-content');
    const environmentSelect = document.getElementById('environment-select');
    
    // Toggle switches
    const subaccountsToggle = document.getElementById('create-subaccounts');
    const coursesToggle = document.getElementById('create-courses');
    
    // Config sections
    const subaccountsConfig = document.getElementById('subaccounts-config');
    const coursesConfig = document.getElementById('courses-config');
    
    // Enable/disable buttons based on environment selection
    environmentSelect.addEventListener('change', function() {
        const hasEnvironment = this.value !== '';
        setupBtn.disabled = !hasEnvironment;
        cleanupBtn.disabled = !hasEnvironment;
    });
    
    // Toggle configuration sections
    subaccountsToggle.addEventListener('change', function() {
        subaccountsConfig.style.display = this.checked ? 'block' : 'none';
    });
    
    coursesToggle.addEventListener('change', function() {
        coursesConfig.style.display = this.checked ? 'block' : 'none';
    });
    
    // Add subaccount functionality
    document.querySelector('.add-subaccount').addEventListener('click', function() {
        const list = document.getElementById('subaccount-list');
        const newItem = document.createElement('div');
        newItem.className = 'subaccount-item';
        newItem.innerHTML = `
            <input type="text" class="subaccount-name" placeholder="e.g., Department of Testing">
            <button class="btn-icon remove-subaccount">×</button>
        `;
        list.appendChild(newItem);
        updateRemoveButtons();
    });
    
    // Add course functionality
    document.querySelector('.add-course').addEventListener('click', function() {
        const list = document.getElementById('course-list');
        const newItem = document.createElement('div');
        newItem.className = 'course-item';
        newItem.innerHTML = `
            <input type="text" class="course-name" placeholder="Course name">
            <input type="text" class="course-code" placeholder="Course code">
            <button class="btn-icon remove-course">×</button>
        `;
        list.appendChild(newItem);
        updateRemoveButtons();
    });
    
    // Remove functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-subaccount')) {
            e.target.parentElement.remove();
            updateRemoveButtons();
        }
        if (e.target.classList.contains('remove-course')) {
            e.target.parentElement.remove();
            updateRemoveButtons();
        }
    });
    
    // Update remove button visibility
    function updateRemoveButtons() {
        const subaccounts = document.querySelectorAll('.subaccount-item');
        const courses = document.querySelectorAll('.course-item');
        
        subaccounts.forEach((item, index) => {
            const removeBtn = item.querySelector('.remove-subaccount');
            removeBtn.style.display = subaccounts.length > 1 ? 'flex' : 'none';
        });
        
        courses.forEach((item, index) => {
            const removeBtn = item.querySelector('.remove-course');
            removeBtn.style.display = courses.length > 1 ? 'flex' : 'none';
        });
    }
    
    // Setup button click
    setupBtn.addEventListener('click', async () => {
        const environment = environmentSelect.value;
        if (!environment) {
            alert('Please select an environment');
            return;
        }
        
        const config = {
            environment: environment,
            subaccounts: [],
            courses: []
        };
        
        // Collect subaccounts
        if (subaccountsToggle.checked) {
            const subaccountItems = document.querySelectorAll('.subaccount-item');
            subaccountItems.forEach((item, index) => {
                const name = item.querySelector('.subaccount-name').value.trim();
                if (name) {
                    config.subaccounts.push({
                        name: name,
                        parent_account_id: 1
                    });
                }
            });
        }
        
        // Collect courses
        if (coursesToggle.checked) {
            const courseItems = document.querySelectorAll('.course-item');
            courseItems.forEach((item, index) => {
                const name = item.querySelector('.course-name').value.trim();
                const code = item.querySelector('.course-code').value.trim();
                if (name && code) {
                    config.courses.push({
                        name: name,
                        course_code: code,
                        account_id: 1
                    });
                }
            });
        }
        
        // Show loading state
        setupBtn.disabled = true;
        setupBtn.querySelector('.btn-text').style.display = 'none';
        setupBtn.querySelector('.spinner').style.display = 'inline-block';
        
        try {
            const response = await fetch('/api/setup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            displayResults(data);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to set up environment: ' + error.message);
        } finally {
            // Reset button state
            setupBtn.disabled = false;
            setupBtn.querySelector('.btn-text').style.display = 'inline';
            setupBtn.querySelector('.spinner').style.display = 'none';
        }
    });
    
    function displayResults(data) {
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
        let html = '<div class="results-summary">';
        
        if (data.subaccounts.length > 0) {
            html += `<h3>✅ Subaccounts Created (${data.subaccounts.length})</h3><ul>`;
            data.subaccounts.forEach(acc => {
                html += `<li>${acc.name} (ID: ${acc.id})</li>`;
            });
            html += '</ul>';
        }
        
        if (data.courses.length > 0) {
            html += `<h3>✅ Courses Created (${data.courses.length})</h3><ul>`;
            data.courses.forEach(course => {
                html += `<li>${course.name} - ${course.course_code} (ID: ${course.id})</li>`;
            });
            html += '</ul>';
        }
        
        if (data.errors && data.errors.length > 0) {
            html += `<h3>⚠️ Errors (${data.errors.length})</h3><ul class="error-list">`;
            data.errors.forEach(error => {
                html += `<li>${error}</li>`;
            });
            html += '</ul>';
        }
        
        html += '</div>';
        resultsContent.innerHTML = html;
    }
    
    // Initialize
    updateRemoveButtons();
});
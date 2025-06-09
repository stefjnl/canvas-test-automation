document.addEventListener('DOMContentLoaded', function() {
    loadRequests();
});

async function loadRequests() {
    try {
        const response = await fetch('/api/requests');
        const requests = await response.json();
        displayRequests(requests);
    } catch (error) {
        console.error('Failed to load requests:', error);
    }
}

function displayRequests(requests) {
    const grid = document.getElementById('requests-grid');
    
    if (requests.length === 0) {
        grid.innerHTML = '<p class="no-requests">No active requests found</p>';
        return;
    }
    
    grid.innerHTML = requests.map(req => {
        const isExpired = new Date(req.end_date) < new Date();
        const status = req.cleaned ? 'cleaned' : (isExpired ? 'expired' : 'active');
        
        return `
            <div class="request-card ${status}">
                <div class="request-header">
                    <h3>${req.scenario_name || req.scenario}</h3>
                    <span class="request-status status-${status}">${status}</span>
                </div>
                <div class="request-info">
                    <p><strong>Request ID:</strong> ${req.id}</p>
                    <p><strong>Requester:</strong> ${req.requester}</p>
                    <p><strong>Environment:</strong> ${req.environment}</p>
                    <p><strong>Period:</strong> ${formatDate(req.start_date)} - ${formatDate(req.end_date)}</p>
                    <p><strong>Created:</strong></p>
                    <ul>
                        ${req.created_resources.subaccounts.length > 0 ? 
                            `<li>${req.created_resources.subaccounts.length} subaccounts</li>` : ''}
                        ${req.created_resources.courses.length > 0 ? 
                            `<li>${req.created_resources.courses.length} courses</li>` : ''}
                        ${req.created_resources.users.length > 0 ? 
                            `<li>${req.created_resources.users.length} users</li>` : ''}
                    </ul>
                </div>
                <div class="request-actions">
                    <button class="btn-small btn-secondary" onclick="viewRequestDetails('${req.id}')">
                        View Details
                    </button>
                    ${!req.cleaned ? `
                        <button class="btn-small btn-danger" onclick="cleanupRequest('${req.id}')">
                            Cleanup
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

async function cleanupRequest(requestId) {
    if (!confirm('Are you sure you want to cleanup this request? This will delete all created resources.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/requests/${requestId}/cleanup`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(`Cleaned up: ${result.deleted_courses} courses, ${result.deleted_users} users`, 'success');
            loadRequests(); // Reload the list
        } else {
            throw new Error('Cleanup failed');
        }
    } catch (error) {
        showToast('Failed to cleanup request: ' + error.message, 'error');
    }
}

function viewRequestDetails(requestId) {
    window.location.href = `/request/${requestId}`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('nl-NL');
}
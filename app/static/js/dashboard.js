// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check status of each environment
    checkEnvironmentStatus();
    
    // Refresh every 30 seconds
    setInterval(checkEnvironmentStatus, 30000);
});

async function checkEnvironmentStatus() {
    const environments = ['acceptatie', 'test', 'development'];
    
    for (const env of environments) {
        try {
            // For now, we'll simulate the status check
            // Later, this will call your actual API
            const status = await getEnvironmentStatus(env);
            updateEnvironmentCard(env, status);
        } catch (error) {
            console.error(`Error checking ${env}:`, error);
            updateEnvironmentCard(env, { error: true });
        }
    }
}

async function getEnvironmentStatus(environment) {
    // TODO: Replace with actual API call
    // Simulated data for now
    const mockData = {
        acceptatie: {
            subaccounts: Math.floor(Math.random() * 5),
            courses: Math.floor(Math.random() * 10),
            lastActivity: new Date(Date.now() - Math.random() * 86400000).toISOString(),
            status: 'clean'
        },
        test: {
            subaccounts: Math.floor(Math.random() * 3),
            courses: Math.floor(Math.random() * 15),
            lastActivity: new Date(Date.now() - Math.random() * 172800000).toISOString(),
            status: 'in-use'
        },
        development: {
            subaccounts: 2,
            courses: 0,
            lastActivity: new Date().toISOString(),
            status: 'in-use'
        }
    };
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return mockData[environment];
}

function updateEnvironmentCard(environment, data) {
    const card = document.querySelector(`[data-env="${environment}"]`);
    if (!card) return;
    
    const statusElement = card.querySelector('.env-status');
    const subaccountsElement = document.getElementById(`${environment}-subaccounts`);
    const coursesElement = document.getElementById(`${environment}-courses`);
    const activityElement = document.getElementById(`${environment}-activity`);
    
    if (data.error) {
        statusElement.className = 'env-status status-error';
        statusElement.innerHTML = '<span class="status-dot"></span> Error';
        return;
    }
    
    // Update counts
    subaccountsElement.textContent = data.subaccounts || 0;
    coursesElement.textContent = data.courses || 0;
    
    // Update last activity
    if (data.lastActivity) {
        const date = new Date(data.lastActivity);
        const now = new Date();
        const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
        
        if (diffHours < 1) {
            activityElement.textContent = 'Just now';
        } else if (diffHours < 24) {
            activityElement.textContent = `${diffHours} hours ago`;
        } else {
            const diffDays = Math.floor(diffHours / 24);
            activityElement.textContent = `${diffDays} days ago`;
        }
    }
    
    // Update status
    let statusClass = 'status-clean';
    let statusText = 'Clean';
    
    if (data.subaccounts > 0 || data.courses > 0) {
        statusClass = 'status-in-use';
        statusText = 'In Use';
    }
    
    if (data.status === 'needs-cleanup') {
        statusClass = 'status-needs-cleanup';
        statusText = 'Needs Cleanup';
    }
    
    statusElement.className = `env-status ${statusClass}`;
    statusElement.innerHTML = `<span class="status-dot"></span> ${statusText}`;
}

function viewDetails(environment) {
    // TODO: Implement view details modal
    alert(`View details for ${environment} - Coming soon!`);
}

function cleanupEnvironment(environment) {
    if (confirm(`Are you sure you want to cleanup the ${environment} environment?`)) {
        // TODO: Implement cleanup
        alert(`Cleanup ${environment} - Coming soon!`);
    }
}
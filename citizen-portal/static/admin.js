document.addEventListener('DOMContentLoaded', () => {
    const loginOverlay = document.getElementById('login-overlay');
    const dashboardContent = document.getElementById('dashboard-content');
    const loginForm = document.getElementById('admin-login-form');
    const loginError = document.getElementById('login-error');
    
    const totalEngagements = document.getElementById('total-engagements');
    const activityTableBody = document.getElementById('activity-table-body');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const exportBtnNav = document.getElementById('export-btn-nav');
    const logoutBtn = document.getElementById('logout-btn');
    const refreshBtn = document.getElementById('refresh-btn');

    let interestChart = null;

    // 1. Session Check
    const token = localStorage.getItem('adminToken');
    if (token) {
        showDashboard();
    }

    // 2. Login Logic
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('admin-username').value;
        const password = document.getElementById('admin-password').value;

        try {
            const response = await fetch('/api/admin/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('adminToken', data.token);
                showDashboard();
            } else {
                loginError.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    });

    // 3. Dashboard Initialization
    function showDashboard() {
        loginOverlay.classList.add('hidden');
        dashboardContent.classList.remove('hidden');
        loadDashboardData();
    }

    async function loadDashboardData() {
        const token = localStorage.getItem('adminToken');
        try {
            const response = await fetch('/api/admin/dashboard-stats', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.status === 401) {
                logout();
                return;
            }

            const data = await response.json();
            
            // Update Stats
            totalEngagements.textContent = data.total_engagements;
            
            // Update Chart
            updateChart(data.categories);
            
            // Update Table
            updateTable(data.recent_activity);

        } catch (error) {
            console.error('Data error:', error);
        }
    }

    function updateChart(categories) {
        const ctx = document.getElementById('interestChart').getContext('2d');
        const labels = categories.map(c => c._id || 'Uncategorized');
        const counts = categories.map(c => c.count);

        if (interestChart) {
            interestChart.destroy();
        }

        interestChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Engagement by Interest',
                    data: counts,
                    backgroundColor: '#007bff',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }

    function updateTable(activity) {
        activityTableBody.innerHTML = '';
        activity.forEach(item => {
            const tr = document.createElement('tr');
            const time = new Date(item.timestamp).toLocaleString();
            tr.innerHTML = `
                <td>${time}</td>
                <td>${item.age}</td>
                <td>${item.job}</td>
                <td>${item.interest}</td>
            `;
            activityTableBody.appendChild(tr);
        });
    }

    // 4. Export Feature
    async function exportCSV() {
        const token = localStorage.getItem('adminToken');
        try {
            const response = await fetch('/api/admin/export', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'citizen_engagements.csv';
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                alert('No data available to export.');
            }
        } catch (error) {
            console.error('Export error:', error);
        }
    }

    exportCsvBtn.addEventListener('click', exportCSV);
    exportBtnNav.addEventListener('click', exportCSV);

    // Logout & Refresh
    logoutBtn.addEventListener('click', logout);
    refreshBtn.addEventListener('click', loadDashboardData);

    function logout() {
        localStorage.removeItem('adminToken');
        window.location.reload();
    }
});

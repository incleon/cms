/**
 * Enterprise CMS — Client-Side JavaScript
 * =========================================
 * Premium utility functions for the frontend.
 */

// ── Flash Messages ──────────────────────────────────────────

function showFlash(message, type = 'info') {
    const container = document.getElementById('flash-messages');
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.style.animation = 'slideInRight 0.3s ease-out';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    container.appendChild(alert);

    setTimeout(() => {
        if (alert.parentNode) {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(20px)';
            alert.style.transition = 'all 0.3s ease';
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

// ── Sidebar Toggle (Mobile) ────────────────────────────────

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    sidebar.classList.toggle('show');
    if (backdrop) backdrop.classList.toggle('show');
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    sidebar.classList.remove('show');
    if (backdrop) backdrop.classList.remove('show');
}

// ── Logout ──────────────────────────────────────────────────

async function logout() {
    try {
        await fetch('/auth/logout', { method: 'POST' });
    } catch (e) { /* ignore */ }
    window.location.href = '/login';
}

// ── Generic Delete ──────────────────────────────────────────

async function deleteItem(resource, id) {
    if (!confirm(`Are you sure you want to delete this ${resource.slice(0, -1)}?`)) return;

    try {
        const res = await fetch(`/api/${resource}/${id}`, { method: 'DELETE' });
        if (res.ok) {
            showFlash('Deleted successfully', 'success');
            setTimeout(() => window.location.reload(), 500);
        } else {
            const err = await res.json();
            showFlash(err.detail || 'Delete failed', 'danger');
        }
    } catch (e) {
        showFlash('Connection error', 'danger');
    }
}

// ── Generic Create Form Handler ─────────────────────────────

async function handleCreate(event, apiUrl, redirectUrl) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = {};

    for (const [key, value] of formData.entries()) {
        if (value === '') continue;
        if (key.endsWith('_id') || key === 'semester' || key === 'experience_years' || key === 'credits') {
            data[key] = parseInt(value) || value;
        } else {
            data[key] = value;
        }
    }

    try {
        const res = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (res.ok) {
            window.location.href = redirectUrl;
        } else {
            const err = await res.json();
            showFlash(err.detail || 'Operation failed', 'danger');
        }
    } catch (e) {
        showFlash('Connection error', 'danger');
    }
}

// ── Close sidebar on mobile when clicking outside ───────────

document.addEventListener('click', function(e) {
    const sidebar = document.getElementById('sidebar');
    if (sidebar && sidebar.classList.contains('show')) {
        if (!sidebar.contains(e.target) && !e.target.closest('.sidebar-toggle')) {
            closeSidebar();
        }
    }
});

// ── Staggered Animation on Scroll ───────────────────────────

document.addEventListener('DOMContentLoaded', function() {
    // Add staggered animation to stat cards on page load
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, i) => {
        card.style.animationDelay = `${i * 0.06}s`;
    });
});

document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
    setInterval(fetchStatus, 5000); // Poll every 5 seconds
});

async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        updateStats(data.stats);
        updateDeviceList(data.computers);
    } catch (error) {
        console.error('Error fetching status:', error);
    }
}

function updateStats(stats) {
    document.getElementById('total-devices').textContent = stats.total;
    document.getElementById('online-devices').textContent = stats.online;
    document.getElementById('offline-devices').textContent = stats.offline;
}

function updateDeviceList(computers) {
    const listContainer = document.getElementById('device-list');

    if (computers.length === 0) {
        listContainer.innerHTML = '<div class="glass" style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">Устройств не найдено</div>';
        return;
    }

    const html = computers.map(pc => {
        const isOnline = pc.is_online;
        const statusClass = isOnline ? 'online' : 'offline';
        const statusText = isOnline ? 'ONLINE' : 'OFFLINE';
        const badgeClass = isOnline ? 'status-badge-online' : 'status-badge-offline';

        const lastSeenDate = new Date(pc.last_seen);
        const formattedDate = lastSeenDate.toLocaleString('ru-RU', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });

        return `
            <div class="glass device-card ${statusClass}">
                <div class="device-header">
                    <div class="device-name">${pc.name}</div>
                    <div class="device-status ${badgeClass}">${statusText}</div>
                </div>
                <div class="device-info">
                    <div>Последняя активность:</div>
                    <div class="device-last-seen">${formattedDate}</div>
                </div>
            </div>
        `;
    }).join('');

    listContainer.innerHTML = html;
}

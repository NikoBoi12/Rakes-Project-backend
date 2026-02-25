document.addEventListener('DOMContentLoaded', () => {
  const statusEl = document.getElementById('status');
  const pingBtn = document.getElementById('ping-btn');

  async function pingServer() {
    statusEl.textContent = 'Pinging...';
    try {
      const response = await fetch('/api/hello');
      const data = await response.json();
      statusEl.textContent = `✅ ${data.message}`;
    } catch (err) {
      statusEl.textContent = '❌ Could not reach the server.';
    }
  }

  pingBtn.addEventListener('click', pingServer);

  // Auto-ping on load
  pingServer();
});

function formatEvent(event) {
    const { author, to_branch, from_branch, action, timestamp } = event;

    if (action === 'push') {
        return `${author} pushed to ${to_branch} on ${timestamp}`;
    }
    if (action === 'pull_request') {
        return `${author} submitted a pull request from ${from_branch} to ${to_branch} on ${timestamp}`;
    }
    if (action === 'merge') {
        return `${author} merged branch ${from_branch} to ${to_branch} on ${timestamp}`;
    }
    return '';
}

async function fetchEvents() {
    const response = await fetch('/events');
    const events = await response.json();
    const list = document.getElementById('eventList');
    list.innerHTML = '';
    events.forEach(event => {
        const li = document.createElement('li');
        li.textContent = formatEvent(event);
        list.appendChild(li);
    });
}

setInterval(fetchEvents, 15000);
window.onload = fetchEvents;

function startListening() {
    const command = document.getElementById('voiceCommand').value;

    fetch('/process_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('output').innerText = data.response;
    })
    .catch(error => {
        document.getElementById('output').innerText = 'Error: ' + error;
    });
}
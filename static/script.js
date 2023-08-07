var player;
var userHasIntervened = false;

document.addEventListener('DOMContentLoaded', function() {
    player = videojs('scene-3');

    player.on('ended', function() {
        if (!userHasIntervened) {
            // User did not press the intervene button, save a default value of 180 seconds (total video length)
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/trainee/save_responsetime', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log('Default response time saved successfully.');
                    // Redirect to the feedback page after the request has completed
                    window.location.href = "/trainee/feedback"
                }
            };
            xhr.send(JSON.stringify({ timestamp: 180 }));
        }
        else {
            window.location.href = "/trainee/feedback";
        }
    });

    var interveneButton = document.querySelector('#intervene-button');
    interveneButton.disabled = false;
});

function saveResponsetime(session_id) {
    // Get the current timestamp of the video
    var currentTime = player.currentTime();
    userHasIntervened = true;

    // Send an AJAX request to the server to save the timestamp
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/trainee/save_responsetime', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log('Response time saved successfully.');
        }
    };
    xhr.send(JSON.stringify({ timestamp: currentTime, session_id: session_id }));
    document.getElementById('intervene-button').disabled = true;
}

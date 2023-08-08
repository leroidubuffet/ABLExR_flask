var player;
var userHasIntervened = false;
var saveResponseTimeUrl = '/trainee/save_responsetime';
document.addEventListener('DOMContentLoaded', initializePlayer);
function initializePlayer() {
    player = videojs('scene-3');
    player.on('ended', handleVideoEnded);
    var interveneButton = document.querySelector('#intervene-button');
    interveneButton.disabled = false;
}
function handleVideoEnded() {
    if (!userHasIntervened) {
        saveResponseTime(180, handleDefaultResponseTimeSaved);
    } else {
        redirectToFeedbackPage();
    }
}
function saveResponseTime(timestamp, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', saveResponseTimeUrl, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            callback();
} };
    xhr.send(JSON.stringify({ timestamp: timestamp }));
}
function handleDefaultResponseTimeSaved() {
    console.log('Default response time saved successfully.');
    redirectToFeedbackPage();
}
function redirectToFeedbackPage() {
    window.location.href = "/trainee/feedback";
}
function saveResponsetime(session_id) {
    var currentTime = player.currentTime();
    userHasIntervened = true;
    saveResponseTime(currentTime, handleResponseTimeSaved);
    document.getElementById('intervene-button').disabled = true;
}
function handleResponseTimeSaved() {
    console.log('Response time saved successfully.');
}
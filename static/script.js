var player;
var userHasIntervened = false;

function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.ENDED) {
        if (!userHasIntervened) {
            // User did not press the intervene button, save the default value
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/save_responsetime', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log('Default response time saved successfully.');
                    // Redirect to the feedback page after the request has completed
                    window.location.href = "/feedback";
                }
            };
            xhr.send(JSON.stringify({ timestamp: 180 }));
        }
		window.location.href = "/feedback";
    }
}

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '600',
        width: '800',
        videoId: '3-kP8i9Lwbg',
        playerVars: {
            'controls': 1,
            'autoplay': 1,
            'disablekb': 1,
            'rel': 0,
            'showinfo': 0,
            'modestbranding': 1
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

function onPlayerReady(event) {
    // Player is ready, enable the button
    var interveneButton = document.querySelector('button');
    interveneButton.disabled = false;
}

function saveResponsetime() {
    // Get the current timestamp of the video
    var currentTime = player.getCurrentTime();

    // Send an AJAX request to the server to save the timestamp
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/save_responsetime', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log('Response time saved successfully.');
        }
    };
    xhr.send(JSON.stringify({ timestamp: currentTime }));
	document.getElementById('intervene-button').disabled = true;
	userHasIntervened = true;
}

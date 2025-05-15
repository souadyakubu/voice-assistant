const robotVideo = document.getElementById('robotVideo');

// Speech recognition setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = 'en-US';
recognition.interimResults = false;

// Speech synthesis setup
const synth = window.speechSynthesis;

recognition.addEventListener('result', (e) => {
    let last = e.results.length - 1;
    let text = e.results[last][0].transcript;

    console.log('Received voice input: ', text);

    // Example response handling
    let responseText = "Sorry, I didn't catch that.";
    if (text.includes("hello")) {
        responseText = "Hi there! How can I help you today?";
    }

    // Speak the response
    speak(responseText);
});

recognition.addEventListener('speechend', () => {
    recognition.stop();
});

// Automatically restart recognition when it ends
recognition.addEventListener('end', recognition.start);

function speak(text) {
    if (synth.speaking) {
        console.error('SpeechSynthesis is already speaking.');
        return;
    }

    const utterThis = new SpeechSynthesisUtterance(text);
    utterThis.onstart = function(event) {
        robotVideo.play();
    };
    utterThis.onend = function(event) {
        robotVideo.pause();
    };

    synth.speak(utterThis);
}

// Start the voice recognition
function processQuery(query) {
    fetch("/process_query", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.response);
        speak(data.response);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
recognition.start();
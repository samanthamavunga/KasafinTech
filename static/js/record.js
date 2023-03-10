var rec;
var audio = document.querySelector('audio');
var recordButton = document.getElementById('record-btn');
var stopButton = document.getElementById('stop-btn');
var recordedText = document.getElementById('recorded-text');
var processButton = document.getElementById('process-btn');

function startRecording() {
  var constraints = { audio: true, video: false };

  navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
    rec = new Recorder(stream);
    rec.record();
    recordButton.disabled = true;
    stopButton.disabled = false;
    processButton.disabled = true;
  }).catch(function(err) {
    console.error('Error starting recording', err);
  });
}

function stopRecording() {
  rec.stop();
  rec.exportWAV(function(blob) {
    audio.src = URL.createObjectURL(blob);
    audio.play();
    var reader = new FileReader();
    reader.onloadend = function() {
      recordedText.innerHTML = reader.result;
      processButton.disabled = false;
    };
    reader.readAsText(blob);
  });
  recordButton.disabled = false;
  stopButton.disabled = true;
}

recordButton.addEventListener('click', startRecording);
stopButton.addEventListener('click', stopRecording);

processButton.addEventListener('click', function() {
  var text = recordedText.innerHTML.trim();
  if (text.length > 0) {
    // Process the text here
    console.log('Text to process:', text);
    alert('Text processed!');
  } else {
    alert('Please record some text first');
  }
});
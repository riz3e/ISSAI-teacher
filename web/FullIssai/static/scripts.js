document
  .getElementById("text-to-speech-form")
  .addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    const response = await fetch("/text-to-speech", {
      method: "POST",
      body: formData,
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.getElementById("download-link");
    a.href = url;
    a.download = "output.wav";
    a.style.display = "block";
  });

document
  .getElementById("speech-to-text-form")
  .addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    const response = await fetch("/speech-to-text", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();
    document.getElementById("transcription-result").innerText = result.text;
  });

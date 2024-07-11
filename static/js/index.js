window.onload = function() {
    const textBtn = document.getElementById('text-btn');
    const fileBtn = document.getElementById('file-btn');
    const textArea = document.getElementById('content');
    const fileUpload = document.getElementById('file-upload');

    textBtn.addEventListener('click', () => {
        fileUpload.value = "";
        textArea.hidden = false;
        fileUpload.hidden = true;
    });

    fileBtn.addEventListener('click', () => {
        textArea.value = "";
        textArea.hidden = true;
        fileUpload.hidden = false;
    });
}
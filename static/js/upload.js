document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById('mainVideo');
    const dropZone = document.querySelector('.main-video-upload');
    const filenameDisplay = document.getElementById('filename-display');
    const statusText = document.getElementById('statusText');
    const form = document.getElementById('uploadForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const uploadBtn = document.getElementById('uploadBtn');

    // 1. Handle File Selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            updateUI(e.target.files[0]);
        }
    });

    // 2. Drag & Drop Visuals
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#2b7cdd';
        dropZone.style.backgroundColor = '#f0f7ff';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#d2e3f5';
        dropZone.style.backgroundColor = '#f5f9ff';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#d2e3f5';
        dropZone.style.backgroundColor = '#f5f9ff';
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateUI(e.dataTransfer.files[0]);
        }
    });

    function updateUI(file) {
        filenameDisplay.textContent = file.name;
        filenameDisplay.style.color = "#2b7cdd";
        statusText.textContent = "Ready: " + file.name;
    }

    // 3. Handle Form Submit (Loading Spinner)
    form.addEventListener('submit', () => {
        loadingOverlay.style.display = 'flex';
        uploadBtn.textContent = "Uploading...";
        uploadBtn.disabled = true;
    });
});
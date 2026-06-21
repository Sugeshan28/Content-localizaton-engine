document.addEventListener("DOMContentLoaded", function() {
    
    const fileInput = document.getElementById('mainVideo');
    const uploadZone = document.getElementById('uploadZone');
    const fileLabel = document.getElementById('file-label');
    const filenameDisplay = document.getElementById('filename-display');
    const form = document.getElementById('uploadForm');
    const loading = document.getElementById('loadingOverlay');

    // Handle clicking on the upload zone to trigger file input
    if (uploadZone) {
        uploadZone.addEventListener('click', function() {
            fileInput.click();
        });
    }

    // Handle File Selection Change
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const name = this.files[0].name;
                fileLabel.textContent = "Selected";
                fileLabel.style.color = "green";
                fileLabel.style.fontWeight = "bold";
                filenameDisplay.textContent = name;
            }
        });
    }

    // Handle Form Submit (Show Loading Screen)
    if (form) {
        form.addEventListener('submit', function() {
            loading.style.display = 'flex';
        });
    }
});
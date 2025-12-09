document.addEventListener('DOMContentLoaded', function() {
    const videoPlayer = document.getElementById('mainVideoPlayer');
    const audioPlayer = document.getElementById('dubbedAudio');
    const audioSelector = document.getElementById('audioSelector');
    const dynamicText = document.getElementById('dynamicText');

    // 1. Populate the Audio Selector Dropdown
    if (typeof contentMap !== 'undefined' && contentMap) {
        // Language Names Mapping
        const langNames = {
            'ta': 'Tamil (தமிழ்)',
            'hi': 'Hindi (हिंदी)',
            'te': 'Telugu (తెలుగు)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)'
        };

        for (const [langCode, data] of Object.entries(contentMap)) {
            // Only add if there is an audio file available
            if (data.audio_file) {
                const option = document.createElement('option');
                option.value = langCode;
                option.textContent = langNames[langCode] || langCode.toUpperCase();
                audioSelector.appendChild(option);
            }
        }
    }

    // 2. Handle Language Selection Change
    audioSelector.addEventListener('change', function() {
        const selectedLang = this.value;

        if (selectedLang === 'original') {
            // Restore Original
            videoPlayer.muted = false;
            audioPlayer.pause();
            audioPlayer.src = "";
            dynamicText.textContent = window.ORIGINAL_DESCRIPTION;
        } else {
            // Switch to Dubbed
            const langData = contentMap[selectedLang];
            if (langData && langData.audio_file) {
                // Set audio source (matches the Flask route /audio/<filename>)
                audioPlayer.src = `/audio/${langData.audio_file}`;
                
                // Mute video, Unmute audio
                videoPlayer.muted = true;
                
                // Sync time instantly
                audioPlayer.currentTime = videoPlayer.currentTime;
                
                // If video is playing, play audio
                if (!videoPlayer.paused) {
                    audioPlayer.play();
                }

                // Update text description
                if (langData.text) {
                    dynamicText.textContent = langData.text;
                }
            }
        }
    });

    // 3. SYNCHRONIZATION LOGIC (The Magic Part)
    // When video plays, audio plays
    videoPlayer.addEventListener('play', () => {
        if (audioSelector.value !== 'original' && audioPlayer.src) {
            audioPlayer.play();
        }
    });

    // When video pauses, audio pauses
    videoPlayer.addEventListener('pause', () => {
        if (audioSelector.value !== 'original') {
            audioPlayer.pause();
        }
    });

    // When video seeks (user drags slider), sync audio
    videoPlayer.addEventListener('seeking', () => {
        if (audioSelector.value !== 'original') {
            audioPlayer.currentTime = videoPlayer.currentTime;
        }
    });

    // Determine if audio is loading/buffering
    videoPlayer.addEventListener('waiting', () => {
        if (audioSelector.value !== 'original') {
            audioPlayer.pause();
        }
    });

    videoPlayer.addEventListener('playing', () => {
        if (audioSelector.value !== 'original' && audioPlayer.src) {
            audioPlayer.play();
        }
    });
});
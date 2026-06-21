document.addEventListener('DOMContentLoaded', function() {
    const videoPlayer = document.getElementById('mainVideoPlayer');
    const audioPlayer = document.getElementById('dubbedAudio');
    const audioSelector = document.getElementById('audioSelector');
    const dynamicText = document.getElementById('dynamicText');

    // Use the correct variable name from HTML
    const contentMap = window.VIDEO_CONTENT_MAP;

    // 1. Populate the Audio Selector Dropdown
    if (typeof contentMap !== 'undefined' && contentMap) {
        const langNames = {
            'ta': 'Tamil (தமிழ்)',
            'hi': 'Hindi (हिंदी)',
            'te': 'Telugu (తెలుగు)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)'
        };

        for (const [langCode, data] of Object.entries(contentMap)) {
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
                console.log('Loading audio:', langData.audio_file);
                
                // Set audio source
                audioPlayer.src = `/audio/${langData.audio_file}`;
                
                // CRITICAL: Load the audio file
                audioPlayer.load();
                
                // Mute video
                videoPlayer.muted = true;
                
                // Wait for audio to be ready before playing
                audioPlayer.addEventListener('canplay', function onCanPlay() {
                    // Remove this listener after first trigger
                    audioPlayer.removeEventListener('canplay', onCanPlay);
                    
                    // Sync time
                    audioPlayer.currentTime = videoPlayer.currentTime;
                    
                    // If video is playing, play audio
                    if (!videoPlayer.paused) {
                        audioPlayer.play().catch(err => {
                            console.error('Audio play failed:', err);
                        });
                    }
                }, { once: true });

                // Update text description
                if (langData.text) {
                    dynamicText.textContent = langData.text;
                }
            }
        }
    });

    // 3. SYNCHRONIZATION LOGIC
    videoPlayer.addEventListener('play', () => {
        if (audioSelector.value !== 'original' && audioPlayer.src) {
            audioPlayer.play().catch(err => {
                console.error('Audio play on video play failed:', err);
            });
        }
    });

    videoPlayer.addEventListener('pause', () => {
        if (audioSelector.value !== 'original') {
            audioPlayer.pause();
        }
    });

    videoPlayer.addEventListener('seeking', () => {
        if (audioSelector.value !== 'original' && audioPlayer.src) {
            audioPlayer.currentTime = videoPlayer.currentTime;
        }
    });

    videoPlayer.addEventListener('waiting', () => {
        if (audioSelector.value !== 'original') {
            audioPlayer.pause();
        }
    });

    videoPlayer.addEventListener('playing', () => {
        if (audioSelector.value !== 'original' && audioPlayer.src) {
            audioPlayer.play().catch(err => {
                console.error('Audio play on video playing failed:', err);
            });
        }
    });

    // Error handling for audio
    audioPlayer.addEventListener('error', (e) => {
        console.error('Audio error:', e);
        console.error('Audio src:', audioPlayer.src);
        console.error('Error code:', audioPlayer.error?.code);
        console.error('Error message:', audioPlayer.error?.message);
    });
});

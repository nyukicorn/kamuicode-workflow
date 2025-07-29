// Audio-Reactive System for Three.js Viewers
// Shared component for music analysis and audio-reactive effects

// Audio analysis variables
let audioElement = null;
let musicPlaying = false;
let audioContext = null;
let microphoneSource = null;
let musicAnalyser = null;
let micAnalyser = null;
let musicDataArray = null;
let micDataArray = null;
let audioReactiveEnabled = false;
let microphoneEnabled = false;
let currentVolumeLevel = 0;
let volumeSmoothing = 0.3; // Improved responsiveness (was 0.8)

// Frequency band analysis with enhanced settings
let frequencyBands = {
    bass: 0,      // 60-250Hz (adjusted for better bass detection)
    mid: 0,       // 250-2000Hz
    treble: 0     // 2000-8000Hz (extended for better clarity)
};
let audioMode = 'music'; // 'music' or 'voice'
let dynamicModeEnabled = false; // Independent dynamic mode toggle

// Enhanced audio analysis system
let adaptiveSystem = {
    // Dynamic thresholds based on audio history
    frequencyThresholds: {
        bass: 0.08,   // Lowered for better microphone sensitivity
        mid: 0.06,    // Lowered for better microphone sensitivity  
        treble: 0.04  // Lowered for better microphone sensitivity
    },
    volumeThreshold: 0.08, // Lowered for better microphone sensitivity
    // Human auditory perception weights
    perceptualWeight: { 
        bass: 0.8,   // Lower weight as humans are less sensitive to bass
        mid: 1.2,    // Higher weight for speech/melody range
        treble: 1.0  // Standard weight
    },
    // Audio history for adaptive thresholds
    history: {
        bass: [],
        mid: [], 
        treble: [],
        volume: [],
        maxHistoryLength: 120 // 2 seconds at 60fps
    }
};

// Effect decay system for natural fade-out
let effectDecay = {
    size: 0.95,       // 5% decay per frame
    brightness: 0.92, // 8% decay per frame  
    color: 0.90,      // 10% decay per frame
    movement: 0.88    // 12% decay per frame
};

// Current effect intensities for decay tracking
let currentEffects = {
    sizeMultiplier: 1.0,
    brightnessMultiplier: 1.0,
    colorIntensity: 1.0,
    movementIntensity: 0.0
};

// Audio analysis functions
function initializeAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        console.log('🎵 Audio context initialized');
    }
    return audioContext;
}

// Initialize external audio (microphone/BlackHole) automatically
function initializeExternalAudio() {
    // Wait a moment for page to fully load, then try to setup microphone
    setTimeout(() => {
        setupMicrophoneAnalysis().then(success => {
            if (success) {
                console.log('🎧 External audio initialized - Ready for BlackHole/external music!');
                
                // Update button to show microphone is active
                const micButton = document.getElementById('microphoneToggle');
                if (micButton) {
                    micButton.innerHTML = '🎤 External Audio ON';
                    micButton.title = 'External audio is ON (BlackHole/microphone input active)';
                }
                
                // Update audio reactive button
                const audioButton = document.getElementById('audioReactiveToggle');
                if (audioButton) {
                    audioButton.innerHTML = '🎵 Audio React ON';
                    audioButton.title = 'Audio reactive is ON - particles will respond to external music';
                }
            } else {
                console.log('💡 To use external music: Allow microphone access and select BlackHole as input device');
            }
        });
    }, 1000); // 1 second delay to ensure page is ready
}

function setupMusicAnalysis(audioElement) {
    if (!audioElement || musicAnalyser) return;
    
    try {
        const context = initializeAudioContext();
        const source = context.createMediaElementSource(audioElement);
        musicAnalyser = context.createAnalyser();
        musicAnalyser.fftSize = 256;
        musicDataArray = new Uint8Array(musicAnalyser.frequencyBinCount);
        
        source.connect(musicAnalyser);
        musicAnalyser.connect(context.destination);
        
        console.log('🎵 Music analysis setup complete');
    } catch (error) {
        console.error('❌ Music analysis setup failed:', error);
    }
}

function setupMicrophoneAnalysis() {
    if (micAnalyser) return Promise.resolve();
    
    return navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const context = initializeAudioContext();
            microphoneSource = context.createMediaStreamSource(stream);
            micAnalyser = context.createAnalyser();
            micAnalyser.fftSize = 256;
            micDataArray = new Uint8Array(micAnalyser.frequencyBinCount);
            
            microphoneSource.connect(micAnalyser);
            microphoneEnabled = true;
            
            console.log('🎤 Microphone analysis setup complete - External audio ready!');
            return true;
        })
        .catch(error => {
            console.warn('⚠️ Microphone access denied - External audio will not work:', error.message);
            console.log('💡 To use external audio: Allow microphone access and select BlackHole as input');
            return false;
        });
}

function getVolumeLevel() {
    let volume = 0;
    let hasAudioSource = false;
    
    // Check microphone input first (external audio via BlackHole)
    if (microphoneEnabled && micAnalyser) {
        micAnalyser.getByteFrequencyData(micDataArray);
        const micVolume = getAverageVolume(micDataArray);
        volume = Math.max(volume, micVolume);
        hasAudioSource = true;
        
        // Analyze frequency bands for microphone
        analyzeFrequencyBands(micDataArray, micAnalyser.context.sampleRate);
    }
    
    // Check page music (if playing and no strong microphone signal)
    if (audioReactiveEnabled && musicAnalyser && musicPlaying) {
        musicAnalyser.getByteFrequencyData(musicDataArray);
        const musicVolume = getAverageVolume(musicDataArray);
        
        // Use page music if no microphone or microphone is quiet
        if (!microphoneEnabled || volume < 0.1) {
            volume = Math.max(volume, musicVolume);
            hasAudioSource = true;
            
            // Analyze frequency bands for page music
            analyzeFrequencyBands(musicDataArray, musicAnalyser.context.sampleRate);
        }
    }
    
    // Apply smoothing
    currentVolumeLevel = currentVolumeLevel * volumeSmoothing + volume * (1 - volumeSmoothing);
    return currentVolumeLevel;
}

function getAverageVolume(dataArray) {
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
    }
    return (sum / dataArray.length) / 255; // Normalize to 0-1
}

function analyzeFrequencyBands(dataArray, sampleRate) {
    // FFT size is 256, so we have 128 frequency bins
    // Each bin represents (sampleRate / 2) / 128 Hz
    const binSize = (sampleRate / 2) / dataArray.length;
    
    // Enhanced frequency ranges based on musical perception
    let bassEnd, midEnd;
    if (audioMode === 'voice') {
        // Voice mode: focus on speech frequencies (500-2000Hz for clarity)
        bassEnd = Math.floor(500 / binSize);
        midEnd = Math.floor(2000 / binSize);
    } else {
        // Music mode: improved frequency separation (60-250Hz, 250-2000Hz, 2000-8000Hz)
        bassEnd = Math.floor(250 / binSize);
        midEnd = Math.floor(2000 / binSize);
    }
    
    // Calculate average volume for each band
    let bassSum = 0, midSum = 0, trebleSum = 0;
    let bassCount = 0, midCount = 0, trebleCount = 0;
    
    for (let i = 0; i < dataArray.length; i++) {
        if (i <= bassEnd) {
            bassSum += dataArray[i];
            bassCount++;
        } else if (i <= midEnd) {
            midSum += dataArray[i];
            midCount++;
        } else {
            trebleSum += dataArray[i];
            trebleCount++;
        }
    }
    
    // Improved smoothing for better responsiveness
    const smoothing = 0.4; // Reduced from 0.7 for better responsiveness
    let newBass = Math.min(1.0, (bassSum / bassCount / 255));
    let newMid = Math.min(1.0, (midSum / midCount / 255));
    let newTreble = Math.min(1.0, (trebleSum / trebleCount / 255));
    
    // Apply perceptual weighting with microphone boost
    const isMicrophoneInput = microphoneEnabled && currentVolumeLevel > 0;
    const micBoost = isMicrophoneInput ? 2.5 : 1.0; // 2.5x boost for microphone input
    
    newBass *= adaptiveSystem.perceptualWeight.bass * micBoost;
    newMid *= adaptiveSystem.perceptualWeight.mid * micBoost;
    newTreble *= adaptiveSystem.perceptualWeight.treble * micBoost;
    
    frequencyBands.bass = frequencyBands.bass * smoothing + newBass * (1 - smoothing);
    frequencyBands.mid = frequencyBands.mid * smoothing + newMid * (1 - smoothing);
    frequencyBands.treble = frequencyBands.treble * smoothing + newTreble * (1 - smoothing);
    
    // Update adaptive history
    updateAdaptiveHistory();
    
    // Update dynamic thresholds
    updateDynamicThresholds();
    
    // Peak detection for enhanced responsiveness
    detectAudioPeaks();
}

// Update adaptive history for dynamic thresholds
function updateAdaptiveHistory() {
    const history = adaptiveSystem.history;
    const maxLength = history.maxHistoryLength;
    
    // Add current values to history
    history.bass.push(frequencyBands.bass);
    history.mid.push(frequencyBands.mid);
    history.treble.push(frequencyBands.treble);
    history.volume.push(currentVolumeLevel);
    
    // Keep history within max length
    if (history.bass.length > maxLength) history.bass.shift();
    if (history.mid.length > maxLength) history.mid.shift();
    if (history.treble.length > maxLength) history.treble.shift();
    if (history.volume.length > maxLength) history.volume.shift();
}

// Update dynamic thresholds based on audio history
function updateDynamicThresholds() {
    const history = adaptiveSystem.history;
    
    if (history.bass.length < 30) return; // Wait for enough history
    
    // Calculate adaptive thresholds (80% of recent average)
    const getAverage = (arr) => arr.slice(-60).reduce((a, b) => a + b, 0) / Math.min(arr.length, 60);
    
    adaptiveSystem.frequencyThresholds.bass = Math.max(0.05, getAverage(history.bass) * 0.8);
    adaptiveSystem.frequencyThresholds.mid = Math.max(0.05, getAverage(history.mid) * 0.8);
    adaptiveSystem.frequencyThresholds.treble = Math.max(0.05, getAverage(history.treble) * 0.8);
    adaptiveSystem.volumeThreshold = Math.max(0.1, getAverage(history.volume) * 0.8);
}

// Detect audio peaks for enhanced response
function detectAudioPeaks() {
    const history = adaptiveSystem.history;
    if (history.bass.length < 5) return;
    
    // Simple peak detection (current > 150% of recent average)
    const recent = 5;
    const getRecentAvg = (arr) => arr.slice(-recent).reduce((a, b) => a + b, 0) / recent;
    
    const bassAvg = getRecentAvg(history.bass.slice(0, -1));
    const midAvg = getRecentAvg(history.mid.slice(0, -1));
    const trebleAvg = getRecentAvg(history.treble.slice(0, -1));
    
    // Apply peak boost for immediate response
    if (frequencyBands.bass > bassAvg * 1.5) frequencyBands.bass *= 1.2;
    if (frequencyBands.mid > midAvg * 1.5) frequencyBands.mid *= 1.2;
    if (frequencyBands.treble > trebleAvg * 1.5) frequencyBands.treble *= 1.2;
}

function toggleAudioReactive() {
    audioReactiveEnabled = !audioReactiveEnabled;
    const button = document.getElementById('audioReactiveToggle');
    
    if (audioReactiveEnabled) {
        if (button) {
            button.innerHTML = '🎵 Audio React ON';
            button.title = 'Audio reactive is ON (click to disable)';
        }
        console.log('🎵 Audio-reactive mode enabled');
        // Setup audio analysis for the music element if it exists
        if (audioElement && !musicAnalyser) {
            setupMusicAnalysis(audioElement);
        }
    } else {
        if (button) {
            button.innerHTML = '🔇 Audio React OFF';
            button.title = 'Audio reactive is OFF (click to enable)';
        }
        console.log('🔇 Audio-reactive mode disabled');
        
        // Reset to normal state when disabling audio reactive
        resetToNormalState();
    }
}

function toggleMicrophone() {
    if (!microphoneEnabled) {
        setupMicrophoneAnalysis().then(success => {
            const button = document.getElementById('microphoneToggle');
            if (success) {
                // microphoneEnabled is already set to true in setupMicrophoneAnalysis
                if (button) {
                    button.innerHTML = '🎤 Mic ON';
                    button.title = 'Microphone is ON (click to disable)';
                }
                console.log('🎤 Microphone enabled');
            } else {
                // Failed to setup microphone, ensure flag remains false
                microphoneEnabled = false;
                if (button) {
                    button.innerHTML = '🎙️ Mic Failed';
                    button.title = 'Microphone access failed';
                }
                console.log('🎤 Microphone setup failed');
            }
        });
    } else {
        microphoneEnabled = false;
        if (microphoneSource) {
            microphoneSource.disconnect();
        }
        const button = document.getElementById('microphoneToggle');
        if (button) {
            button.innerHTML = '🎙️ Mic OFF';
            button.title = 'Microphone is OFF (click to enable)';
        }
        console.log('🎤 Microphone disabled');
        
        // Reset to normal state when disabling microphone (if audio reactive is also off)
        if (!audioReactiveEnabled) {
            resetToNormalState();
        }
    }
}

function toggleAudioMode() {
    audioMode = audioMode === 'music' ? 'voice' : 'music';
    const button = document.getElementById('audioModeToggle');
    
    // Reset frequency bands when switching modes to prevent residual effects
    frequencyBands.bass = 0;
    frequencyBands.mid = 0;
    frequencyBands.treble = 0;
    
    if (button) {
        if (audioMode === 'music') {
            button.innerHTML = '🎵 Music Mode ON';
            button.title = 'Currently in music mode (bass/mid/treble separation)';
            console.log('🎵 Switched to music mode');
        } else {
            button.innerHTML = '🎤 Voice Mode ON';
            button.title = 'Currently in voice mode (speech frequency focus)';
            console.log('🎤 Switched to voice mode');
        }
    }
}

function toggleDynamicMode() {
    dynamicModeEnabled = !dynamicModeEnabled;
    const button = document.getElementById('dynamicModeToggle');
    
    if (button) {
        if (dynamicModeEnabled) {
            button.innerHTML = '🚀 Dynamic ON';
            button.title = 'Dynamic enhancement is ON (40% boost)';
            console.log('🚀 Dynamic mode enabled');
        } else {
            button.innerHTML = '🚀 Dynamic OFF';
            button.title = 'Dynamic enhancement is OFF';
            console.log('🚀 Dynamic mode disabled');
        }
    }
}

// Apply audio-reactive effects (called from main animation loop)
function applyAudioReactiveEffects() {
    const volumeLevel = getVolumeLevel();
    
    // Use adaptive thresholds instead of fixed ones
    const shouldTrigger = volumeLevel > adaptiveSystem.volumeThreshold || 
                         frequencyBands.bass > adaptiveSystem.frequencyThresholds.bass || 
                         frequencyBands.mid > adaptiveSystem.frequencyThresholds.mid || 
                         frequencyBands.treble > adaptiveSystem.frequencyThresholds.treble;
    
    if (shouldTrigger) {
        // Calculate new effect intensities
        let newSizeMultiplier, newBrightnessMultiplier, newColorIntensity;
        
        // Enhanced volume-responsive system
        if (volumeLevel > adaptiveSystem.volumeThreshold) {
            // Volume-level based effects with improved mapping
            if (volumeLevel < 0.25) {
                // Low volume: subtle pulse
                newSizeMultiplier = 1.0 + (volumeLevel * 0.8);
                newBrightnessMultiplier = 1.0 + (volumeLevel * 0.6);
                newColorIntensity = 1.0 + (volumeLevel * 0.4);
            } else if (volumeLevel < 0.6) {
                // Medium volume: wave ripple
                newSizeMultiplier = 1.0 + (frequencyBands.bass * 1.8);
                newBrightnessMultiplier = 1.0 + (frequencyBands.mid * 1.6);
                newColorIntensity = 1.0 + (frequencyBands.treble * 1.4);
            } else {
                // High volume: dramatic expansion
                newSizeMultiplier = 1.0 + (frequencyBands.bass * 2.2);
                newBrightnessMultiplier = 1.0 + (frequencyBands.mid * 2.0);
                newColorIntensity = 1.0 + (frequencyBands.treble * 1.8);
            }
        } else {
            // Frequency-only effects (when volume is low but frequencies detected)
            newSizeMultiplier = 1.0 + (frequencyBands.bass * 1.2);
            newBrightnessMultiplier = 1.0 + (frequencyBands.mid * 1.0);
            newColorIntensity = 1.0 + (frequencyBands.treble * 0.8);
        }
        
        // Apply dynamic mode boost
        if (dynamicModeEnabled) {
            const boost = 1.4;
            newSizeMultiplier = (newSizeMultiplier - 1.0) * boost + 1.0;
            newBrightnessMultiplier = (newBrightnessMultiplier - 1.0) * boost + 1.0;
            newColorIntensity = (newColorIntensity - 1.0) * boost + 1.0;
        }
        
        // Update current effects (for decay system)
        currentEffects.sizeMultiplier = Math.max(currentEffects.sizeMultiplier, newSizeMultiplier);
        currentEffects.brightnessMultiplier = Math.max(currentEffects.brightnessMultiplier, newBrightnessMultiplier);
        currentEffects.colorIntensity = Math.max(currentEffects.colorIntensity, newColorIntensity);
    }
    
    // Apply decay to all effects for natural fade-out
    currentEffects.sizeMultiplier = Math.max(1.0, currentEffects.sizeMultiplier * effectDecay.size);
    currentEffects.brightnessMultiplier = Math.max(1.0, currentEffects.brightnessMultiplier * effectDecay.brightness);
    currentEffects.colorIntensity = Math.max(1.0, currentEffects.colorIntensity * effectDecay.color);
    currentEffects.movementIntensity *= effectDecay.movement;
    
    // Apply effects to visual elements (requires external functions)
    if (typeof applyVisualEffects === 'function') {
        applyVisualEffects();
    }
    
    // Apply movement effects (requires external functions)
    if (typeof applyMovementEffects === 'function') {
        applyMovementEffects();
    }
    
    // Enhanced debug logging
    if (Math.random() < 0.01) {
        const modeIcon = audioMode === 'music' ? '🎵' : '🎤';
        const dynamicSuffix = dynamicModeEnabled ? ' +Dynamic' : '';
        console.log(`${modeIcon} ${audioMode} mode${dynamicSuffix}: vol=${(volumeLevel * 100).toFixed(1)}% bass=${(frequencyBands.bass * 100).toFixed(1)}% mid=${(frequencyBands.mid * 100).toFixed(1)}% treble=${(frequencyBands.treble * 100).toFixed(1)}% → size=${currentEffects.sizeMultiplier.toFixed(2)}x bright=${currentEffects.brightnessMultiplier.toFixed(2)}x color=${currentEffects.colorIntensity.toFixed(2)}x`);
    }
}

function resetToNormalState() {
    // Reset audio analysis values
    currentVolumeLevel = 0;
    frequencyBands.bass = 0;
    frequencyBands.mid = 0;
    frequencyBands.treble = 0;
    
    // Reset effect values
    currentEffects.sizeMultiplier = 1.0;
    currentEffects.brightnessMultiplier = 1.0;
    currentEffects.colorIntensity = 1.0;
    currentEffects.movementIntensity = 0.0;
    
    console.log('🔄 Audio reactive system reset to normal state');
}

// Export functions to global scope for HTML events
window.toggleAudioReactive = toggleAudioReactive;
window.toggleMicrophone = toggleMicrophone;
window.toggleAudioMode = toggleAudioMode;
window.toggleDynamicMode = toggleDynamicMode;
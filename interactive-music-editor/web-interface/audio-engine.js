/**
 * 🎵 Audio Engine for Interactive Music Editor
 * Web Audio API based real-time music synthesis
 */

class AudioEngine {
    constructor() {
        this.audioContext = null;
        this.masterGain = null;
        this.tracks = new Map();
        this.isPlaying = false;
        this.currentTime = 0;
        this.tempo = 120; // BPM
        
        this.init();
    }

    async init() {
        try {
            // Initialize Audio Context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Create master gain node
            this.masterGain = this.audioContext.createGain();
            this.masterGain.connect(this.audioContext.destination);
            this.masterGain.gain.value = 0.7;
            
            console.log('🎵 Audio Engine initialized successfully');
            return true;
        } catch (error) {
            console.error('❌ Audio Engine initialization failed:', error);
            return false;
        }
    }

    // Resume audio context (required for user interaction)
    async resume() {
        if (this.audioContext && this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
        }
    }

    // Create different instrument sounds
    createOscillator(frequency, type = 'sine', startTime = null, duration = 1.0) {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.frequency.setValueAtTime(frequency, startTime || this.audioContext.currentTime);
        oscillator.type = type;
        
        // ADSR Envelope
        const now = startTime || this.audioContext.currentTime;
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(0.3, now + 0.01); // Attack
        gainNode.gain.exponentialRampToValueAtTime(0.1, now + 0.1); // Decay
        gainNode.gain.setValueAtTime(0.1, now + duration - 0.1); // Sustain
        gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration); // Release
        
        oscillator.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        return { oscillator, gainNode };
    }

    // Note to frequency conversion
    noteToFrequency(note) {
        const notes = {
            'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6,
            'E': -5, 'F': -4, 'F#': -3, 'Gb': -3, 'G': -2, 'G#': -1, 'Ab': -1,
            'A': 0, 'A#': 1, 'Bb': 1, 'B': 2
        };
        
        const octave = parseInt(note.slice(-1));
        const noteName = note.slice(0, -1);
        
        if (notes[noteName] === undefined) return 440; // Default to A4
        
        const semitone = notes[noteName] + (octave - 4) * 12;
        return 440 * Math.pow(2, semitone / 12);
    }

    // Play a single note
    playNote(note, instrument = 'piano', duration = 1.0, velocity = 0.7, startTime = null) {
        const frequency = this.noteToFrequency(note);
        const actualStartTime = startTime || this.audioContext.currentTime;
        
        let oscillatorType = 'sine';
        let effectGain = velocity;
        
        // Different instrument characteristics
        switch (instrument) {
            case 'piano':
                oscillatorType = 'triangle';
                effectGain *= 0.8;
                break;
            case 'violin':
                oscillatorType = 'sawtooth';
                effectGain *= 0.6;
                break;
            case 'drums':
                // Use noise for drums
                return this.playDrumHit(actualStartTime, velocity);
            case 'bass':
                oscillatorType = 'square';
                effectGain *= 1.2;
                break;
        }
        
        const { oscillator, gainNode } = this.createOscillator(frequency, oscillatorType, actualStartTime, duration);
        gainNode.gain.value *= effectGain;
        
        oscillator.start(actualStartTime);
        oscillator.stop(actualStartTime + duration);
        
        return oscillator;
    }

    // Special drum sound
    playDrumHit(startTime, velocity = 0.7) {
        const bufferSize = this.audioContext.sampleRate * 0.1;
        const buffer = this.audioContext.createBuffer(1, bufferSize, this.audioContext.sampleRate);
        const data = buffer.getChannelData(0);
        
        // Generate noise for drum sound
        for (let i = 0; i < bufferSize; i++) {
            data[i] = (Math.random() * 2 - 1) * velocity * Math.exp(-i / (bufferSize * 0.1));
        }
        
        const source = this.audioContext.createBufferSource();
        const gainNode = this.audioContext.createGain();
        
        source.buffer = buffer;
        source.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        gainNode.gain.value = velocity;
        source.start(startTime);
        
        return source;
    }

    // Play a sequence of notes
    playSequence(notes, instrument = 'piano', timing = null, durations = null, velocities = null) {
        if (!timing) timing = notes.map((_, i) => i * 0.5);
        if (!durations) durations = notes.map(() => 0.4);
        if (!velocities) velocities = notes.map(() => 0.7);
        
        const startTime = this.audioContext.currentTime + 0.1;
        
        notes.forEach((note, i) => {
            if (note && note !== 'rest') {
                this.playNote(
                    note, 
                    instrument, 
                    durations[i], 
                    velocities[i], 
                    startTime + timing[i]
                );
            }
        });
        
        console.log(`🎵 Playing ${instrument} sequence:`, notes);
    }

    // Play chord
    playChord(notes, instrument = 'piano', duration = 2.0, velocity = 0.5) {
        const startTime = this.audioContext.currentTime + 0.1;
        
        notes.forEach(note => {
            this.playNote(note, instrument, duration, velocity, startTime);
        });
        
        console.log(`🎼 Playing ${instrument} chord:`, notes);
    }

    // Demo patterns for different instruments
    playDemoPattern(instrument) {
        switch (instrument) {
            case 'piano':
                this.playSequence(
                    ['C4', 'E4', 'G4', 'C5', 'G4', 'E4', 'C4', 'rest'],
                    'piano',
                    [0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1],
                    [0.25, 0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0]
                );
                break;
                
            case 'violin':
                this.playSequence(
                    ['G3', 'A3', 'B3', 'C4', 'D4', 'E4', 'F4', 'G4'],
                    'violin',
                    [0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8],
                    [0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.7]
                );
                break;
                
            case 'drums':
                this.playSequence(
                    ['kick', 'kick', 'kick', 'kick', 'kick', 'kick', 'kick', 'kick'],
                    'drums',
                    [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75],
                    [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                    [0.8, 0.6, 0.8, 0.6, 0.8, 0.6, 0.8, 0.6]
                );
                break;
                
            case 'bass':
                this.playSequence(
                    ['C2', 'C2', 'F2', 'F2', 'G2', 'G2', 'C2', 'C2'],
                    'bass',
                    [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
                    [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
                );
                break;
        }
    }

    // Play all demo patterns simultaneously
    playFullDemo() {
        console.log('🎵 Playing full demo composition...');
        
        // Schedule all parts
        setTimeout(() => this.playDemoPattern('bass'), 0);
        setTimeout(() => this.playDemoPattern('drums'), 100);
        setTimeout(() => this.playDemoPattern('piano'), 200);
        setTimeout(() => this.playDemoPattern('violin'), 400);
    }

    // Master volume control
    setMasterVolume(volume) {
        if (this.masterGain) {
            this.masterGain.gain.setValueAtTime(volume, this.audioContext.currentTime);
        }
    }

    // Generate romantic style music
    playRomanticStyle() {
        // Soft piano chord progression
        setTimeout(() => this.playChord(['C4', 'E4', 'G4'], 'piano', 2.0, 0.4), 0);
        setTimeout(() => this.playChord(['F3', 'A3', 'C4'], 'piano', 2.0, 0.4), 2000);
        setTimeout(() => this.playChord(['G3', 'B3', 'D4'], 'piano', 2.0, 0.4), 4000);
        setTimeout(() => this.playChord(['C4', 'E4', 'G4'], 'piano', 2.0, 0.4), 6000);
        
        // Gentle violin melody
        setTimeout(() => {
            this.playSequence(
                ['E4', 'F4', 'G4', 'A4', 'G4', 'F4', 'E4', 'C4'],
                'violin',
                [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
                [0.7, 0.7, 0.7, 1.0, 0.7, 0.7, 0.7, 1.5],
                [0.3, 0.3, 0.4, 0.5, 0.4, 0.3, 0.3, 0.4]
            );
        }, 1000);
    }

    // Generate dramatic style music
    playDramaticStyle() {
        // Powerful bass line
        this.playSequence(
            ['C1', 'C1', 'F1', 'G1', 'C1'],
            'bass',
            [0, 0.5, 1.0, 1.5, 2.0],
            [0.4, 0.4, 0.4, 0.4, 0.8],
            [0.9, 0.7, 0.9, 0.9, 1.0]
        );
        
        // Dramatic drums
        setTimeout(() => {
            this.playSequence(
                ['kick', 'kick', 'kick', 'kick', 'kick'],
                'drums',
                [0, 0.5, 1.0, 1.5, 2.0],
                [0.2, 0.2, 0.2, 0.2, 0.3],
                [1.0, 0.8, 1.0, 1.0, 1.0]
            );
        }, 100);
        
        // Intense violin
        setTimeout(() => {
            this.playSequence(
                ['C5', 'D5', 'E5', 'F5', 'G5'],
                'violin',
                [0.2, 0.7, 1.2, 1.7, 2.2],
                [0.4, 0.4, 0.4, 0.4, 0.8],
                [0.7, 0.8, 0.9, 1.0, 1.0]
            );
        }, 300);
    }
}

// Global audio engine instance
let audioEngine = null;

// Initialize audio engine
function initAudioEngine() {
    if (!audioEngine) {
        audioEngine = new AudioEngine();
    }
    return audioEngine;
}
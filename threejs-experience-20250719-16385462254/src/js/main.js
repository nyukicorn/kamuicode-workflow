class VRExperience {
    constructor() {
        this.vrScene = null;
        this.controls = null;
        this.particleSystem = null;
        this.audioContext = null;
        this.audioBuffer = null;
        this.audioSource = null;
        this.gainNode = null;
        this.isPlaying = false;
        this.clock = new THREE.Clock();
        
        this.init();
    }

    async init() {
        if (!this.checkWebGLSupport()) {
            this.showWebGLError();
            return;
        }

        this.showLoadingScreen();
        
        try {
            await this.initializeVR();
            this.setupEventListeners();
            this.hideLoadingScreen();
            this.startRenderLoop();
            
            console.log('VR体験が正常に初期化されました');
        } catch (error) {
            console.error('VR体験の初期化に失敗しました:', error);
            this.showError('初期化に失敗しました。ページを再読み込みしてください。');
        }
    }

    checkWebGLSupport() {
        try {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            return !!context;
        } catch (e) {
            return false;
        }
    }

    showWebGLError() {
        document.getElementById('app').style.display = 'none';
        document.getElementById('webgl-error').style.display = 'block';
        this.hideLoadingScreen();
    }

    showLoadingScreen() {
        document.getElementById('loading-screen').style.display = 'flex';
    }

    hideLoadingScreen() {
        document.getElementById('loading-screen').style.display = 'none';
    }

    showError(message) {
        document.querySelector('#loading-screen p').textContent = message;
    }

    async initializeVR() {
        this.vrScene = new VRScene();
        
        await new Promise((resolve) => {
            document.addEventListener('panoramaLoaded', resolve, { once: true });
            setTimeout(resolve, 5000);
        });

        this.controls = new VRControls(this.vrScene.camera, this.vrScene.renderer.domElement);
        this.particleSystem = new UmbrellaParticleSystem(this.vrScene.scene);
        
        await this.initializeAudio();
    }

    async initializeAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            const response = await fetch('../music/generated-music.wav');
            const arrayBuffer = await response.arrayBuffer();
            this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            this.gainNode = this.audioContext.createGain();
            this.gainNode.connect(this.audioContext.destination);
            this.gainNode.gain.value = 0.5;
            
            console.log('音楽ファイルが正常に読み込まれました');
        } catch (error) {
            console.warn('音楽ファイルの読み込みに失敗しました:', error);
        }
    }

    setupEventListeners() {
        window.addEventListener('resize', () => {
            this.vrScene.onWindowResize();
        });

        document.getElementById('music-toggle').addEventListener('click', () => {
            this.toggleMusic();
        });

        document.getElementById('volume-slider').addEventListener('input', (event) => {
            this.setVolume(parseFloat(event.target.value));
        });

        document.addEventListener('keydown', (event) => {
            if (event.code === 'KeyM') {
                this.toggleMusic();
            }
        });

        window.addEventListener('beforeunload', () => {
            this.dispose();
        });
    }

    toggleMusic() {
        if (!this.audioContext || !this.audioBuffer) {
            console.warn('音楽機能が利用できません');
            return;
        }

        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }

        if (this.isPlaying) {
            this.stopMusic();
        } else {
            this.playMusic();
        }
    }

    playMusic() {
        if (!this.audioBuffer) return;

        if (this.audioSource) {
            this.audioSource.stop();
        }

        this.audioSource = this.audioContext.createBufferSource();
        this.audioSource.buffer = this.audioBuffer;
        this.audioSource.loop = true;
        this.audioSource.connect(this.gainNode);
        this.audioSource.start();

        this.isPlaying = true;
        this.updateMusicButton();
    }

    stopMusic() {
        if (this.audioSource) {
            this.audioSource.stop();
            this.audioSource = null;
        }

        this.isPlaying = false;
        this.updateMusicButton();
    }

    setVolume(value) {
        if (this.gainNode) {
            this.gainNode.gain.value = value;
        }
    }

    updateMusicButton() {
        const button = document.getElementById('music-toggle');
        const icon = document.getElementById('music-icon');
        const text = document.getElementById('music-text');

        if (this.isPlaying) {
            icon.textContent = '🔇';
            text.textContent = '音楽OFF';
            button.classList.add('active');
        } else {
            icon.textContent = '🎵';
            text.textContent = '音楽ON';
            button.classList.remove('active');
        }
    }

    startRenderLoop() {
        const animate = () => {
            requestAnimationFrame(animate);
            
            const deltaTime = this.clock.getDelta();
            
            if (this.controls) {
                this.controls.update();
            }
            
            if (this.particleSystem) {
                this.particleSystem.update(deltaTime);
            }
            
            if (this.vrScene) {
                this.vrScene.render();
            }
        };
        
        animate();
    }

    dispose() {
        if (this.audioSource) {
            this.audioSource.stop();
        }
        
        if (this.audioContext) {
            this.audioContext.close();
        }
        
        if (this.particleSystem) {
            this.particleSystem.dispose();
        }
        
        if (this.controls) {
            this.controls.dispose();
        }
        
        if (this.vrScene) {
            this.vrScene.dispose();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.vrExperience = new VRExperience();
});
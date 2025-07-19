class VRScene {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = null;
        this.panoramaSphere = null;
        this.textureLoader = new THREE.TextureLoader();
        
        this.init();
    }

    init() {
        this.setupRenderer();
        this.setupCamera();
        this.setupPanorama();
        this.setupLighting();
    }

    setupRenderer() {
        const canvas = document.getElementById('canvas');
        this.renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            antialias: true,
            powerPreference: "high-performance"
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
    }

    setupCamera() {
        this.camera.position.set(0, 0, 0);
        this.camera.lookAt(0, 0, -1);
    }

    setupPanorama() {
        const geometry = new THREE.SphereGeometry(100, 64, 32);
        
        this.textureLoader.load(
            '../assets/panorama.jpg',
            (texture) => {
                texture.mapping = THREE.EquirectangularReflectionMapping;
                texture.wrapS = THREE.RepeatWrapping;
                texture.wrapT = THREE.ClampToEdgeWrapping;
                texture.minFilter = THREE.LinearFilter;
                texture.magFilter = THREE.LinearFilter;
                
                const material = new THREE.MeshBasicMaterial({ 
                    map: texture,
                    side: THREE.BackSide
                });
                
                this.panoramaSphere = new THREE.Mesh(geometry, material);
                this.scene.add(this.panoramaSphere);
                
                document.dispatchEvent(new CustomEvent('panoramaLoaded'));
            },
            (progress) => {
                console.log('パノラマ読み込み進行状況:', (progress.loaded / progress.total * 100) + '%');
            },
            (error) => {
                console.error('パノラマ画像の読み込みに失敗しました:', error);
            }
        );
    }

    setupLighting() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    render() {
        this.renderer.render(this.scene, this.camera);
    }

    dispose() {
        if (this.panoramaSphere) {
            this.panoramaSphere.geometry.dispose();
            this.panoramaSphere.material.dispose();
        }
        this.renderer.dispose();
    }
}
class VRControls {
    constructor(camera, domElement) {
        this.camera = camera;
        this.domElement = domElement;
        this.controls = null;
        this.touchSupport = 'ontouchstart' in window;
        
        this.init();
    }

    init() {
        this.setupOrbitControls();
        this.setupTouchControls();
        this.setupKeyboardControls();
    }

    setupOrbitControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.domElement);
        
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        
        this.controls.enableZoom = true;
        this.controls.minDistance = 1;
        this.controls.maxDistance = 50;
        this.controls.zoomSpeed = 0.8;
        
        this.controls.enableRotate = true;
        this.controls.rotateSpeed = 0.5;
        this.controls.autoRotate = false;
        this.controls.autoRotateSpeed = 0.5;
        
        this.controls.enablePan = false;
        
        this.controls.minPolarAngle = 0;
        this.controls.maxPolarAngle = Math.PI;
        
        this.controls.target.set(0, 0, 0);
    }

    setupTouchControls() {
        if (!this.touchSupport) return;

        let touchStartX = 0;
        let touchStartY = 0;
        let isTouchMoving = false;

        this.domElement.addEventListener('touchstart', (event) => {
            if (event.touches.length === 1) {
                touchStartX = event.touches[0].clientX;
                touchStartY = event.touches[0].clientY;
                isTouchMoving = false;
            }
        }, { passive: false });

        this.domElement.addEventListener('touchmove', (event) => {
            event.preventDefault();
            
            if (event.touches.length === 1) {
                isTouchMoving = true;
                const deltaX = event.touches[0].clientX - touchStartX;
                const deltaY = event.touches[0].clientY - touchStartY;
                
                const rotationSpeed = 0.005;
                this.controls.object.rotation.y -= deltaX * rotationSpeed;
                this.controls.object.rotation.x -= deltaY * rotationSpeed;
                
                this.controls.object.rotation.x = Math.max(
                    -Math.PI / 2, 
                    Math.min(Math.PI / 2, this.controls.object.rotation.x)
                );
                
                touchStartX = event.touches[0].clientX;
                touchStartY = event.touches[0].clientY;
            }
        }, { passive: false });

        this.domElement.addEventListener('touchend', (event) => {
            if (!isTouchMoving && event.changedTouches.length === 1) {
                this.handleTap(event.changedTouches[0]);
            }
        });
    }

    setupKeyboardControls() {
        document.addEventListener('keydown', (event) => {
            const rotationSpeed = 0.1;
            const zoomSpeed = 2;

            switch (event.code) {
                case 'ArrowLeft':
                    this.camera.rotation.y += rotationSpeed;
                    break;
                case 'ArrowRight':
                    this.camera.rotation.y -= rotationSpeed;
                    break;
                case 'ArrowUp':
                    this.camera.rotation.x += rotationSpeed;
                    break;
                case 'ArrowDown':
                    this.camera.rotation.x -= rotationSpeed;
                    break;
                case 'KeyW':
                case 'Equal':
                    this.controls.dollyIn(zoomSpeed);
                    break;
                case 'KeyS':
                case 'Minus':
                    this.controls.dollyOut(zoomSpeed);
                    break;
                case 'Space':
                    event.preventDefault();
                    this.resetView();
                    break;
                case 'KeyR':
                    this.toggleAutoRotate();
                    break;
            }
        });
    }

    handleTap(touch) {
        const rect = this.domElement.getBoundingClientRect();
        const x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
        const y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;
        
        console.log('VR空間をタップしました:', { x, y });
    }

    resetView() {
        this.camera.position.set(0, 0, 0);
        this.camera.rotation.set(0, 0, 0);
        this.controls.target.set(0, 0, 0);
        this.controls.update();
    }

    toggleAutoRotate() {
        this.controls.autoRotate = !this.controls.autoRotate;
        console.log('自動回転:', this.controls.autoRotate ? 'ON' : 'OFF');
    }

    update() {
        if (this.controls) {
            this.controls.update();
        }
    }

    dispose() {
        if (this.controls) {
            this.controls.dispose();
        }
    }

    getControls() {
        return this.controls;
    }
}
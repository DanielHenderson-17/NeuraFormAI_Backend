import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class VRMContainer extends StatefulWidget {
  final String? vrmModel;
  final Function(String)? onVrmModelChanged;
  
  const VRMContainer({
    Key? key,
    this.vrmModel,
    this.onVrmModelChanged,
  }) : super(key: key);

  @override
  State<VRMContainer> createState() => _VRMContainerState();
}

class _VRMContainerState extends State<VRMContainer> {
  late WebViewController _webViewController;
  bool _isWebViewReady = false;
  String? _currentVrmModel;
  
  @override
  void initState() {
    super.initState();
    _currentVrmModel = widget.vrmModel;
    _initializeWebView();
  }
  
  void _initializeWebView() {
    _webViewController = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (String url) {
            setState(() {
              _isWebViewReady = true;
            });
            _loadVRMModel();
          },
        ),
      )
      ..loadHtmlString(_getVRMViewerHTML());
  }
  
  String _getVRMViewerHTML() {
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VRM Viewer</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: Arial, sans-serif;
            overflow: hidden;
        }
        #vrm-container {
            width: 100vw;
            height: 100vh;
            position: relative;
        }
        #loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 18px;
            z-index: 1000;
        }
        #controls {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1001;
            background: rgba(0,0,0,0.7);
            padding: 10px;
            border-radius: 8px;
            color: white;
        }
        .control-btn {
            background: #4CAF50;
            border: none;
            color: white;
            padding: 8px 12px;
            margin: 2px;
            border-radius: 4px;
            cursor: pointer;
        }
        .control-btn:hover {
            background: #45a049;
        }
        .control-btn:disabled {
            background: #cccccc;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div id="vrm-container">
        <div id="loading">Loading VRM Viewer...</div>
        <div id="controls">
            <button class="control-btn" onclick="resetCamera()">Reset Camera</button>
            <button class="control-btn" onclick="toggleAnimation()">Toggle Animation</button>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three-vrm@0.0.30/lib/three-vrm.min.js"></script>
    
    <script>
        let scene, camera, renderer, mixer, clock;
        let currentModel = null;
        let isAnimating = true;
        
        function init() {
            // Scene setup
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            
            // Camera setup
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.5, 3);
            
            // Renderer setup
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            
            document.getElementById('vrm-container').appendChild(renderer.domElement);
            
            // Lighting
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(1, 1, 1);
            directionalLight.castShadow = true;
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
            scene.add(directionalLight);
            
            // Clock for animations
            clock = new THREE.Clock();
            
            // Handle window resize
            window.addEventListener('resize', onWindowResize, false);
            
            // Start render loop
            animate();
            
            // Hide loading
            document.getElementById('loading').style.display = 'none';
        }
        
        function loadVRMModel(modelPath) {
            if (currentModel) {
                scene.remove(currentModel);
            }
            
            const loader = new THREE.GLTFLoader();
            loader.load(
                modelPath,
                function (gltf) {
                    THREE.VRM.from(gltf).then(function (vrm) {
                        currentModel = vrm.scene;
                        
                        // Position the model
                        currentModel.position.set(0, 0, 0);
                        
                        // Add to scene
                        scene.add(currentModel);
                        
                        // Setup mixer for animations
                        if (gltf.animations && gltf.animations.length > 0) {
                            mixer = new THREE.AnimationMixer(currentModel);
                            const action = mixer.clipAction(gltf.animations[0]);
                            action.play();
                        }
                        
                        console.log('VRM model loaded successfully');
                    });
                },
                function (progress) {
                    console.log('Loading progress:', (progress.loaded / progress.total * 100) + '%');
                },
                function (error) {
                    console.error('Error loading VRM model:', error);
                }
            );
        }
        
        function animate() {
            requestAnimationFrame(animate);
            
            if (mixer && isAnimating) {
                mixer.update(clock.getDelta());
            }
            
            renderer.render(scene, camera);
        }
        
        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }
        
        function resetCamera() {
            camera.position.set(0, 1.5, 3);
            camera.lookAt(0, 1, 0);
        }
        
        function toggleAnimation() {
            isAnimating = !isAnimating;
            const btn = event.target;
            btn.textContent = isAnimating ? 'Pause Animation' : 'Play Animation';
        }
        
        // Mouse controls
        let isMouseDown = false;
        let mouseX = 0;
        let mouseY = 0;
        
        renderer.domElement.addEventListener('mousedown', function(event) {
            isMouseDown = true;
            mouseX = event.clientX;
            mouseY = event.clientY;
        });
        
        renderer.domElement.addEventListener('mouseup', function() {
            isMouseDown = false;
        });
        
        renderer.domElement.addEventListener('mousemove', function(event) {
            if (isMouseDown) {
                const deltaX = event.clientX - mouseX;
                const deltaY = event.clientY - mouseY;
                
                camera.position.x += deltaX * 0.01;
                camera.position.y -= deltaY * 0.01;
                
                mouseX = event.clientX;
                mouseY = event.clientY;
            }
        });
        
        // Initialize when page loads
        window.addEventListener('load', init);
        
        // Function to be called from Flutter
        window.loadVRMModel = loadVRMModel;
    </script>
</body>
</html>
    ''';
  }
  
  void _loadVRMModel() {
    if (!_isWebViewReady || _currentVrmModel == null) return;
    
    final modelPath = 'assets/legacy/vrms/$_currentVrmModel';
    _webViewController.runJavaScript('''
      if (window.loadVRMModel) {
        window.loadVRMModel('$modelPath');
      }
    ''');
  }
  
  @override
  void didUpdateWidget(VRMContainer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.vrmModel != _currentVrmModel) {
      _currentVrmModel = widget.vrmModel;
      _loadVRMModel();
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: WebViewWidget(controller: _webViewController),
      ),
    );
  }
  
  @override
  void dispose() {
    super.dispose();
  }
}

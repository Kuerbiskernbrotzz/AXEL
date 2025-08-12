// Core Three.js objects
let scene, camera, renderer;

// Group and meshes
let sphereGroup, sphereMesh, particleSystem;

// Visualization state
let mode = 'idle';
let targetStrength = 0;
let currentStrength = 0;
let originalPositions;
let externalLevel = null;

/**
 * Initializes the Three.js scene, camera, renderer, and meshes.
 * Called once when the DOM is ready.
 */
function init() {
  console.log("Visualizer init");

  // Create the scene and set background color
  scene = new THREE.Scene();
  scene.background = new THREE.Color("rgb(35, 39, 46)");

  // Set up a perspective camera
  camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(0, 0, 20);

  // Create the WebGL renderer
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);


  // Create a group to hold our meshes
  sphereGroup = new THREE.Group();
  scene.add(sphereGroup);

  // Create a wireframe sphere mesh (32,32 segments)
  const geom = new THREE.SphereGeometry(5, 32, 32);
  const mat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    wireframe: true,
    opacity: 0.7,
    transparent: true
  });
  sphereMesh = new THREE.Mesh(geom, mat);
  sphereGroup.add(sphereMesh);

  // Cache original vertex positions for deformation
  const posAttr = sphereMesh.geometry.attributes.position;
  originalPositions = new Float32Array(posAttr.count * 3);
  for (let i = 0; i < posAttr.count * 3; i++) {
    originalPositions[i] = posAttr.array[i];
  }

  // Create a surrounding particle cloud (white particles)
  const count = 500;
  const posArr = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const phi = Math.acos(2 * Math.random() - 1);
    const theta = 2 * Math.PI * Math.random();
    const r = 7 + Math.random() * 3;
    posArr[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
    posArr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    posArr[i * 3 + 2] = r * Math.cos(phi);
  }
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
  const pMat = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.05,
    transparent: true,
    opacity: 0.8
  });
  particleSystem = new THREE.Points(pGeo, pMat);
  sphereGroup.add(particleSystem);

  // Handle window resize to adjust camera and renderer
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

/**
 * Main animation loop.
 * Updates rotation, interpolates strength, deforms sphere, and renders.
 */
function animate() {
  requestAnimationFrame(animate);

  sphereGroup.rotation.y += 0.0005;
  currentStrength += (targetStrength - currentStrength) * 0.04;

  if (mode === 'listening') {
    targetStrength = 0.2 + (Math.random() - 0.5) * 0.1;
  } else if (mode === 'visualize') {
    if (externalLevel !== null) {
      targetStrength = 0.1 + externalLevel * 4;
    } else {
      targetStrength = 0.3 + (Math.random() - 0.5) * 0.2;
    }
  }

  deformSphere(currentStrength);
  renderer.render(scene, camera);
}

/**
 * Deforms the sphere mesh vertices based on a strength factor.
 */
function deformSphere(strength) {
  const pos = sphereMesh.geometry.attributes.position;
  const time = Date.now() * 0.002;

  for (let i = 0; i < pos.count; i++) {
    const ox = originalPositions[i * 3],
          oy = originalPositions[i * 3 + 1],
          oz = originalPositions[i * 3 + 2];
    const wave = 1 + Math.sin(time + ox * 2 + oy * 2) * strength * 0.2;
    pos.setXYZ(i, ox * wave, oy * wave, oz * wave);
  }
  pos.needsUpdate = true;
}

// -------------------
// Public API methods
// -------------------

/**
 * Sets the visualizer mode: 'idle', 'listening', 'visualize'
 */
function setMode(m) {
  mode = m;
  externalLevel = null;
  console.log("JS setMode:", m);
  if (mode === 'idle') {
    targetStrength = 0;
  } else if (mode === 'listening') {
    targetStrength = 0.2;
  } else if (mode === 'visualize') {
    targetStrength = 0.3;
  }
}

/**
 * Feeds an external audio level into the visualizer.
 * @param {number} val - normalized audio level 0.0–1.0
 */
function feedAudioLevel(val) {
  externalLevel = Math.max(0, Math.min(1, val));
  console.log("JS feedAudioLevel:", externalLevel);
}

function setVolume(val) {
  // Placeholder: Du kannst hier später die Lautstärke für Audio einbauen
  console.log("JS setVolume:", val);
}
function setMuted(muted) {
  // Placeholder: Du kannst hier später das Mute-Handling für Audio einbauen
  console.log("JS setMuted:", muted);
}

// Entferne oder ersetze diese Funktion:
window.playAudioFile = function(path) {
    // Diese Funktion wird nicht mehr benötigt
    console.log("Audio playback handled by PyAudio");
};

// Initialize when DOM is ready and set up WebChannel
window.addEventListener('DOMContentLoaded', () => {
  init();
  animate();
  console.log("Visualizer ready");
});

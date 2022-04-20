preample = """
<html>

<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- webpage template-->
  <link rel="stylesheet" href="./website.css">
  <!-- model-viewer css -->
  <link rel="stylesheet" href="./demo-styles.css">
</head>

<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>

<body>

  <center>
      <h1>{0}</h1>
  </center>

  <br>

  <center>
    <div class="container">

      <div class="row">
        <div class="column">
          <div class="header header-result">RGB Frame</div>
        </div>
        <div class="column">
          <div class="header header-result">Mask</div>
        </div>
        <div class="column">
          <div class="header header-result">3D Model</div>
        </div>
        <div class="column">
          <div class="header header-result">Textured Model</div>
        </div>
      </div>

      {1}

    </div>
  </center>
</body>

<script>
(() => {{
  const tapDistance = 2;
  let panning = false;
  let panX, panY;
  let startX, startY;
  let lastX, lastY;
  let metersPerPixel;

  const startPan = (modelViewer) => {{
    const orbit = modelViewer.getCameraOrbit();
    const {{theta, phi, radius}} = orbit;
    const psi = theta - modelViewer.turntableRotation;
    metersPerPixel = 0.75 * radius / modelViewer.getBoundingClientRect().height;
    panX = [-Math.cos(psi), 0, Math.sin(psi)];
    panY = [
      -Math.cos(phi) * Math.sin(psi),
      Math.sin(phi),
      -Math.cos(phi) * Math.cos(psi)
    ];
    modelViewer.interactionPrompt = 'none';
  }};

  const movePan = (modelViewer, thisX, thisY) => {{
    const dx = (thisX - lastX) * metersPerPixel;
    const dy = (thisY - lastY) * metersPerPixel;
    lastX = thisX;
    lastY = thisY;

    const target = modelViewer.getCameraTarget();
    target.x += dx * panX[0] + dy * panY[0];
    target.y += dx * panX[1] + dy * panY[1];
    target.z += dx * panX[2] + dy * panY[2];
    modelViewer.cameraTarget = `${{target.x}}m ${{target.y}}m ${{target.z}}m`;

    // This pauses turntable rotation
    modelViewer.dispatchEvent(new CustomEvent(
          'camera-change', {{detail: {{source: 'user-interaction'}}}}));
  }};

  const recenter = (modelViewer, pointer) => {{
    panning = false;
    if (Math.abs(pointer.clientX - startX) > tapDistance ||
        Math.abs(pointer.clientY - startY) > tapDistance)
      return;
    const rect = modelViewer.getBoundingClientRect();
    const x = pointer.clientX - rect.left;
    const y = pointer.clientY - rect.top;
    const hit = modelViewer.positionAndNormalFromPoint(x, y);
    modelViewer.cameraTarget =
        hit == null ? 'auto auto auto' : hit.position.toString();
  }};

  const modelViewers = document.querySelectorAll('model-viewer');
  modelViewers.forEach(function(modelViewer) {{
    modelViewer.addEventListener('mousedown', (event) => {{
      startX = event.clientX;
      startY = event.clientY;
      panning = event.button === 2 || event.ctrlKey || event.metaKey ||
          event.shiftKey;
      if (!panning)
        return;

      lastX = startX;
      lastY = startY;
      startPan(modelViewer);
      event.stopPropagation();
    }}, true);

    modelViewer.addEventListener('touchstart', (event) => {{
      const {{targetTouches, touches}} = event;
      startX = targetTouches[0].clientX;
      startY = targetTouches[0].clientY;
      panning = targetTouches.length === 2 && targetTouches.length === touches.length;
      if (!panning)
        return;

      lastX = 0.5 * (targetTouches[0].clientX + targetTouches[1].clientX);
      lastY = 0.5 * (targetTouches[0].clientY + targetTouches[1].clientY);
      startPan(modelViewer);
    }}, true);

    modelViewer.addEventListener('mousemove', (event) => {{
      if (!panning)
        return;

      movePan(modelViewer, event.clientX, event.clientY);
      event.stopPropagation();
    }}, true);

    modelViewer.addEventListener('touchmove', (event) => {{
      if (!panning || event.targetTouches.length !== 2)
        return;

      const {{targetTouches}} = event;
      const thisX = 0.5 * (targetTouches[0].clientX + targetTouches[1].clientX);
      const thisY = 0.5 * (targetTouches[0].clientY + targetTouches[1].clientY);
      movePan(modelViewer, thisX, thisY);
    }}, true);

    modelViewer.addEventListener('mouseup', (event) => {{
      recenter(modelViewer, event);
    }}, true);

    modelViewer.addEventListener('touchend', (event) => {{
      if (event.targetTouches.length === 0) {{
        recenter(modelViewer, event.changedTouches[0]);

        if (event.cancelable) {{
          event.preventDefault();
        }}
      }}
    }}, true);
  }});
}})();
</script>

</html>
"""

row = """
      <div class="row">
        <div class="semantic"></div>

        <div class ="column">
            <a href="{0}"><img class="input-img view1" src="{0}"></img></a>
        </div>

        <div class ="column">
            <a href="{1}"><img class="input-img view2" src="{1}"></img></a>
        </div>

        <div class="column">
          <div id="card">
            <model-viewer id="mesh" src="{2}" shadow-intensity="1" camera-controls interaction-prompt="none" exposure="0.2" ar-status="not-presenting"></model-viewer>
          </div>
        </div>

        <div class="column">
          <div id="card">
            <model-viewer src="{3}" shadow-intensity="1" camera-controls interaction-prompt="none" exposure="0.2" ar-status="not-presenting"></model-viewer>
          </div>
        </div>
      </div>

      </div>
"""

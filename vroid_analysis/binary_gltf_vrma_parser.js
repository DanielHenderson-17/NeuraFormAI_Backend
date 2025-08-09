// Binary glTF VRMA Parser
// Properly parses binary glTF VRMA files to extract bone mappings

console.log("🎯 Binary glTF VRMA Parser Loaded");

// Store parsed data
let parseData = {
  timestamp: new Date().toISOString(),
  vrmaFiles: [],
  parsedData: [],
  boneMappings: [],
  errors: [],
};

// Parse binary glTF VRMA content
function parseBinaryGLTF(arrayBuffer, filename) {
  console.log("🔍 Parsing binary glTF VRMA:", filename);

  try {
    const uint8Array = new Uint8Array(arrayBuffer);
    const dataView = new DataView(arrayBuffer);
    const textDecoder = new TextDecoder();

    // Check for binary glTF header
    const magic = textDecoder.decode(uint8Array.slice(0, 4));
    const version = dataView.getUint32(4, true);
    const totalLength = dataView.getUint32(8, true);

    console.log(
      "🔍 Binary glTF header:",
      magic,
      "version:",
      version,
      "length:",
      totalLength
    );

    if (magic !== "glTF" || version !== 2) {
      throw new Error(
        `Invalid binary glTF: magic=${magic}, version=${version}`
      );
    }

    let offset = 12;
    const chunks = [];

    // Parse chunks
    while (offset < totalLength) {
      const chunkLength = dataView.getUint32(offset, true);
      const chunkType = textDecoder.decode(
        uint8Array.slice(offset + 4, offset + 8)
      );
      const chunkData = uint8Array.slice(offset + 8, offset + 8 + chunkLength);

      console.log("🔍 Chunk:", chunkType, "length:", chunkLength);
      chunks.push({ type: chunkType, data: chunkData });

      offset += 8 + chunkLength;
    }

    // Find JSON chunk
    const jsonChunk = chunks.find((chunk) => chunk.type === "JSON");
    if (!jsonChunk) {
      throw new Error("No JSON chunk found in binary glTF");
    }

    // Parse JSON
    const jsonText = textDecoder.decode(jsonChunk.data);
    const gltfData = JSON.parse(jsonText);
    console.log("🎯 Successfully parsed binary glTF JSON");

    // Store parsed data
    parseData.parsedData.push({
      filename: filename,
      timestamp: new Date().toISOString(),
      gltfData: gltfData,
      chunks: chunks.map((chunk) => ({
        type: chunk.type,
        length: chunk.data.length,
      })),
    });

    // Look for VRMC_vrm_animation extension
    if (gltfData.extensions && gltfData.extensions.VRMC_vrm_animation) {
      console.log("🎯 Found VRMC_vrm_animation extension!");
      const vrmAnimation = gltfData.extensions.VRMC_vrm_animation;

      // Extract humanoid bone mappings
      if (vrmAnimation.humanoid && vrmAnimation.humanoid.humanBones) {
        console.log("🎯 Found humanoid bone mappings!");
        console.log("🎯 Bone mappings:", vrmAnimation.humanoid.humanBones);

        parseData.boneMappings.push({
          filename: filename,
          timestamp: new Date().toISOString(),
          type: "vrmc_humanoid_bones",
          bones: vrmAnimation.humanoid.humanBones,
        });
      }

      // Extract animation data
      if (vrmAnimation.specVersion) {
        console.log(
          "🎯 VRMC_vrm_animation spec version:",
          vrmAnimation.specVersion
        );
      }

      // Look for animation tracks
      if (vrmAnimation.humanoid && vrmAnimation.humanoid.humanBones) {
        console.log(
          "🎯 Humanoid bones found:",
          Object.keys(vrmAnimation.humanoid.humanBones)
        );
      }
    }

    // Look for bone nodes in the glTF
    if (gltfData.nodes) {
      console.log("🎯 Found", gltfData.nodes.length, "nodes");

      const boneNodes = [];
      gltfData.nodes.forEach((node, index) => {
        if (
          node.name &&
          (node.name.toLowerCase().includes("bone") ||
            node.name.toLowerCase().includes("joint") ||
            node.name.toLowerCase().includes("j_bip") ||
            node.name.toLowerCase().includes("humanoid"))
        ) {
          console.log("🎯 Found bone node:", index, node.name);
          boneNodes.push({
            index: index,
            name: node.name,
            node: node,
          });
        }
      });

      if (boneNodes.length > 0) {
        parseData.boneMappings.push({
          filename: filename,
          timestamp: new Date().toISOString(),
          type: "bone_nodes",
          nodes: boneNodes,
        });
      }
    }

    // Look for animations
    if (gltfData.animations) {
      console.log("🎯 Found", gltfData.animations.length, "animations");

      gltfData.animations.forEach((animation, index) => {
        console.log("🎯 Animation", index, ":", animation.name);
        if (animation.channels) {
          console.log("🎯 Animation channels:", animation.channels.length);
          animation.channels.forEach((channel, chIndex) => {
            if (channel.target && channel.target.node !== undefined) {
              console.log(
                "🎯 Channel",
                chIndex,
                "targets node:",
                channel.target.node
              );
            }
          });
        }
      });
    }

    // Look for binary data chunks (animation data)
    const binChunk = chunks.find((chunk) => chunk.type === "BIN\x00");
    if (binChunk) {
      console.log("🎯 Found binary data chunk:", binChunk.data.length, "bytes");

      // Look for animation data in binary chunk
      if (gltfData.animations) {
        gltfData.animations.forEach((animation, animIndex) => {
          if (animation.samplers) {
            animation.samplers.forEach((sampler, samplerIndex) => {
              if (
                sampler.input !== undefined &&
                gltfData.accessors[sampler.input]
              ) {
                const accessor = gltfData.accessors[sampler.input];
                console.log(
                  "🎯 Animation",
                  animIndex,
                  "sampler",
                  samplerIndex,
                  "accessor:",
                  accessor
                );
              }
            });
          }
        });
      }
    }
  } catch (e) {
    console.log("⚠️ Error parsing binary glTF:", e);
    parseData.errors.push({
      filename: filename,
      timestamp: new Date().toISOString(),
      error: "Binary glTF parse error",
      details: e.message,
    });
  }
}

// Monitor VRMA file loading
function monitorVRMAFiles() {
  console.log("🎯 Setting up VRMA file monitoring...");

  // Monitor FileReader
  const originalReadAsArrayBuffer = FileReader.prototype.readAsArrayBuffer;
  FileReader.prototype.readAsArrayBuffer = function (blob) {
    if (blob.name && blob.name.endsWith(".vrma")) {
      console.log("🎯 VRMA file detected:", blob.name, blob.size);

      this.addEventListener("load", function () {
        console.log("🎯 VRMA file loaded:", this.result.byteLength, "bytes");

        parseData.vrmaFiles.push({
          name: blob.name,
          size: blob.size,
          dataSize: this.result.byteLength,
          timestamp: new Date().toISOString(),
        });

        parseBinaryGLTF(this.result, blob.name);
      });
    }

    return originalReadAsArrayBuffer.call(this, blob);
  };

  // Monitor file input changes
  document.addEventListener(
    "change",
    function (event) {
      if (event.target && event.target.files) {
        for (let file of event.target.files) {
          if (file.name.endsWith(".vrma")) {
            console.log("🎯 VRMA file input:", file.name, file.size);

            const reader = new FileReader();
            reader.onload = function () {
              console.log(
                "🎯 Direct VRMA read:",
                this.result.byteLength,
                "bytes"
              );

              parseData.vrmaFiles.push({
                name: file.name,
                size: file.size,
                dataSize: this.result.byteLength,
                timestamp: new Date().toISOString(),
                source: "direct_read",
              });

              parseBinaryGLTF(this.result, file.name);
            };
            reader.readAsArrayBuffer(file);
          }
        }
      }
    },
    true
  );
}

// Export function
window.exportBinaryGLTFData = function () {
  try {
    console.log("📁 Preparing to export binary glTF data...");
    console.log("📊 VRMA files:", parseData.vrmaFiles.length);
    console.log("📊 Parsed data:", parseData.parsedData.length);
    console.log("📊 Bone mappings:", parseData.boneMappings.length);
    console.log("📊 Errors:", parseData.errors.length);

    const dataStr = JSON.stringify(parseData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `binary_gltf_vrma_parser_${Date.now()}.json`;
    a.click();

    URL.revokeObjectURL(url);
    console.log("📁 Binary glTF data exported successfully");
    return parseData;
  } catch (error) {
    console.error("❌ Export failed:", error);
    return null;
  }
};

// Start monitoring
monitorVRMAFiles();

console.log(`
🎯 BINARY GLTF VRMA PARSER ACTIVE
==================================
📋 Instructions:
1. Load a VRM model in VRoid Studio
2. Upload peace.vrma (or any VRMA file)
3. Run: exportBinaryGLTFData() in console
4. Check the downloaded JSON file

🎯 What we're parsing:
- Binary glTF VRMA files
- glTF chunks (JSON, BIN)
- VRMC_vrm_animation extension
- Humanoid bone mappings
- Bone node definitions
- Animation data and samplers

📊 Target: Extract complete VRMA structure and bone mappings from binary glTF
`);

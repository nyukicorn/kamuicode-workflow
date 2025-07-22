# Polycam TRELLIS MCP Server

A Model Context Protocol (MCP) server that provides Text-to-3D and Image-to-3D generation using the TRELLIS model.

## Features

- **Text-to-3D Generation**: Generate 3D models from text descriptions
- **Image-to-3D Generation**: Convert 2D images to 3D models  
- **Multiple Output Formats**: Support for GLB, PLY, and mesh formats
- **Async Job Management**: Non-blocking generation with status tracking
- **Progress Monitoring**: Real-time progress updates

## Installation

```bash
cd polycam-mcp-server
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
python trellis_server.py
```

### MCP Tools

#### 1. trellis_text_submit
Submit a text prompt for 3D model generation.

**Parameters:**
- `prompt` (required): Text description for 3D model
- `output_format` (optional): Output format ("glb", "ply", "mesh") - default: "glb"  
- `steps` (optional): Number of diffusion steps (10-100) - default: 50

**Returns:** Job ID for tracking

#### 2. trellis_image_submit
Submit an image for 3D model generation.

**Parameters:**
- `image_url` (required): URL or path to input image
- `output_format` (optional): Output format ("glb", "ply", "mesh") - default: "glb"
- `steps` (optional): Number of diffusion steps (10-100) - default: 50

**Returns:** Job ID for tracking

#### 3. trellis_status
Check the status of a generation job.

**Parameters:**
- `job_id` (required): Job ID to check

**Returns:** Status information (submitted, running, completed, failed)

#### 4. trellis_result
Get the result of a completed generation job.

**Parameters:** 
- `job_id` (required): Job ID to get result

**Returns:** Path to generated 3D model file

## Integration with KamuiCode

### MCP Configuration

The server integrates with KamuiCode through `mcp-polycam.json`:

```json
{
  "mcpServers": {
    "t2i3d-polycam-trellis": {
      "type": "http",
      "url": "http://localhost:8000",
      "description": "Polycam TRELLIS Text-to-3D Generation (2B parameters) ⭐"
    },
    "i2i3d-polycam-trellis": {
      "type": "http", 
      "url": "http://localhost:8000",
      "description": "Polycam TRELLIS Image-to-3D Generation (High Quality) ⭐"
    }
  }
}
```

### Claude Code Usage

```bash
# Start Claude with Polycam MCP
claude --mcp-config=/path/to/mcp-polycam.json
```

Then use tools like:
- `mcp__t2i3d-polycam-trellis__trellis_text_submit`
- `mcp__i2i3d-polycam-trellis__trellis_image_submit`

## Development Status

- ✅ Core MCP server framework
- ✅ Job management system
- ✅ Tool definitions and handlers
- 🚧 TRELLIS model integration (in progress)
- ⏳ CUDA environment setup
- ⏳ GitHub Actions integration

## Next Steps

1. Integrate actual TRELLIS model
2. Add CUDA environment setup
3. Create GitHub Actions workflow
4. Add comprehensive error handling
5. Implement result file management

## Architecture

```
polycam-mcp-server/
├── trellis_server.py     # Main MCP server
├── requirements.txt      # Python dependencies  
├── outputs/             # Generated 3D models
└── README.md           # This file
```
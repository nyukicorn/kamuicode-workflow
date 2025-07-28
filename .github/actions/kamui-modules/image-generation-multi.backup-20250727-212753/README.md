# Multi Image Generation Module

A GitHub Action module for generating multiple images with various AI models using KamuiCode MCP.

## 🎯 Features

- **Multiple Image Generation**: Generate 1-10 images in a single run
- **Model Comparison**: Compare outputs from different AI models
- **Parallel Processing**: Efficient generation with concurrent execution
- **Automatic Reports**: Generate comparison reports for model analysis
- **Backward Compatibility**: Works with existing single-image workflows

## 📋 Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `image-prompt` | The image generation prompt | ✅ | - |
| `image-count` | Number of images to generate (1-10) | ❌ | `1` |
| `models` | Comma-separated list of models | ❌ | `auto` |
| `enable-comparison` | Enable model comparison mode | ❌ | `false` |
| `folder-name` | Folder name for storing images | ✅ | - |
| `branch-name` | Branch to work on | ✅ | - |
| `oauth-token` | Claude Code OAuth token | ✅ | - |
| `mcp-config` | MCP configuration JSON | ✅ | - |

### Supported Models

- `auto` - AI-powered automatic selection
- `imagen4-ultra` - High-quality realistic images
- `imagen4-fast` - Fast generation
- `imagen3` - Google's Imagen3 model
- `flux-schnell` - Artistic and illustration content
- `photo-flux` - Photo-realistic images

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `images-completed` | Number of successfully generated images |
| `image-urls` | JSON array of generated image URLs |
| `models-used` | JSON array of models actually used |
| `comparison-report` | Path to comparison report (if enabled) |
| `google-image-url` | First image URL (backward compatibility) |

## 🔧 Usage Examples

### Basic Multi-Image Generation

```yaml
- name: Generate 3 images
  uses: ./.github/actions/kamui-modules/image-generation-multi
  with:
    image-prompt: "A beautiful sunset over mountains"
    image-count: "3"
    folder-name: "sunset-images"
    branch-name: ${{ github.ref_name }}
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Model Comparison

```yaml
- name: Compare image models
  uses: ./.github/actions/kamui-modules/image-generation-multi
  with:
    image-prompt: "A futuristic city skyline"
    image-count: "1"
    models: "imagen4-fast,flux-schnell,imagen3"
    enable-comparison: "true"
    folder-name: "model-comparison"
    branch-name: ${{ github.ref_name }}
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Multiple Models × Multiple Images

```yaml
- name: Generate with multiple models
  uses: ./.github/actions/kamui-modules/image-generation-multi
  with:
    image-prompt: "Abstract digital art"
    image-count: "2"
    models: "imagen4-fast,flux-schnell"
    folder-name: "abstract-art"
    branch-name: ${{ github.ref_name }}
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

## 📁 Output Structure

```
folder-name/
├── images/
│   ├── generated-image.png              # First image (backward compatibility)
│   ├── generated-image-1-imagen4-fast.png
│   ├── generated-image-2-flux-schnell.png
│   └── generated-image-3-imagen3.png
├── image-urls.json                      # Array of Google URLs
├── models-used.json                     # Array of used models
├── comparison-report.md                 # Comparison report (if enabled)
└── google-image-url.txt                # First image URL (backward compatibility)
```

## ⚡ Execution Modes

### 1. Single Model Multi-Image
```yaml
image-count: "5"
models: "imagen4-fast"
```
Generates 5 images using the same model.

### 2. Model Comparison
```yaml
image-count: "1"
models: "imagen4-fast,flux-schnell,imagen3"
enable-comparison: "true"
```
Generates one image per model and creates a comparison report.

### 3. Multi-Model Multi-Image
```yaml
image-count: "2"
models: "imagen4-fast,flux-schnell"
```
Generates 2 images with each model (4 total images).

## 📊 Comparison Report

When `enable-comparison` is enabled, a detailed report is generated with:

- Generation conditions and timestamp
- Results table with model, filename, and generation time
- Statistical analysis (average, fastest, slowest times)
- Success rates and execution details

## 🚫 Limitations

- **Maximum Images**: 10 per execution (GitHub Actions time limit)
- **Parallel Limit**: Up to 5 concurrent generations (MCP rate limits)
- **File Size**: Max 50MB per image
- **Execution Time**: 15 minutes total limit

## 🔄 Backward Compatibility

This module maintains full backward compatibility with the existing `image-generation` module:

- First generated image is saved as `generated-image.png`
- `google-image-url` output contains the first image URL
- Existing workflows work without modification

## 🧪 Error Handling

- Invalid image counts (< 1 or > 10) result in immediate failure
- Unknown models fallback to `imagen4-fast`
- Individual image failures don't stop the entire process
- Detailed logging for troubleshooting

## 🎨 AI Model Selection

When using `models: "auto"`, the system analyzes the prompt:

- **Realistic content** (photo, portrait, landscape) → `imagen4-ultra`
- **Artistic content** (anime, cartoon, illustration) → `flux-schnell`  
- **Speed preference** (fast, quick, speed) → `imagen4-fast`
- **Default** → `imagen4-fast`

## 📈 Performance Optimization

- Parallel processing for multiple images
- Efficient model switching
- Optimized MCP configuration
- Resource-aware execution limits
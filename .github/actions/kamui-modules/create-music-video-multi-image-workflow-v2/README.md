# Multi-Image Music Video Workflow V2

Enhanced multi-image generation module with backward compatibility for KamuiCode workflows.

## 🌟 Features

- **🔄 100% Backward Compatible**: All existing workflows work without modification
- **🎨 Multi-Image Generation**: Generate 1-10 images with intelligent model selection
- **🧠 Smart Strategy Selection**: Automatic parallel/sequential optimization
- **📊 Quality Assessment**: Automated quality scoring and primary image selection
- **📈 Model Comparison**: Compare multiple models and generate reports
- **⚡ Performance Optimized**: Resource-aware parallel generation with rate limiting

## 📋 Usage

### Basic Usage (Backward Compatible)

```yaml
- name: Generate Images
  uses: ./.github/actions/kamui-modules/create-music-video-multi-image-workflow-v2
  with:
    image-prompt: "A beautiful sunset over mountains"
    folder-name: "my-project"
    branch-name: "main"
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Enhanced Multi-Image Usage

```yaml
- name: Generate Multiple Images
  uses: ./.github/actions/kamui-modules/create-music-video-multi-image-workflow-v2
  with:
    image-prompt: "A futuristic cityscape at night"
    image-count: '5'
    models: 'imagen4-ultra,flux-schnell,imagen4-fast'
    generation-strategy: 'smart'
    enable-comparison: 'true'
    quality-threshold: '0.8'
    max-parallel: '3'
    folder-name: "enhanced-project"
    branch-name: "main"
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

## 📥 Inputs

### Required Parameters

| Parameter | Description | Type |
|-----------|-------------|------|
| `image-prompt` | The image generation prompt | `string` |
| `folder-name` | Folder name for storing image files | `string` |
| `branch-name` | Git branch to work on | `string` |
| `oauth-token` | Claude Code OAuth token | `string` |
| `mcp-config` | MCP configuration JSON | `string` |

### Optional Parameters (Enhanced Features)

| Parameter | Description | Type | Default | Range |
|-----------|-------------|------|---------|-------|
| `image-count` | Number of images to generate | `integer` | `1` | `1-10` |
| `models` | Comma-separated list of models | `string` | `auto` | See models below |
| `generation-strategy` | Generation strategy | `string` | `smart` | `sequential`, `parallel`, `smart` |
| `enable-comparison` | Enable model comparison reports | `boolean` | `false` | `true`, `false` |
| `quality-threshold` | Minimum quality score | `float` | `0.7` | `0.0-1.0` |
| `max-parallel` | Maximum parallel generations | `integer` | `3` | `1-5` |

### Available Models

- `auto` - Intelligent model selection based on prompt analysis
- `imagen4-ultra` - High-quality photorealistic images
- `imagen4-fast` - Fast general-purpose generation
- `imagen3` - Google's Imagen3 model
- `flux-schnell` - Artistic and stylized images
- `photo-flux` - Professional photography style

## 📤 Outputs

### Backward Compatible Outputs

| Output | Description | Type |
|--------|-------------|------|
| `image-completed` | Whether generation was successful | `boolean` |
| `google-image-url` | Google URL of primary image | `string` |
| `used-model` | Model used for primary image | `string` |

### Enhanced Outputs

| Output | Description | Type |
|--------|-------------|------|
| `images-completed` | Number of images successfully generated | `integer` |
| `image-urls` | JSON array of all image URLs | `array` |
| `models-used` | JSON array of models used | `array` |
| `quality-scores` | JSON array of quality scores | `array` |
| `primary-image-index` | Index of highest quality image | `integer` |
| `generation-report` | Path to detailed generation report | `string` |

## 📁 File Structure

The module creates the following file structure:

```
{folder-name}/
├── images/
│   ├── generated-image.png          # Primary image (backward compatibility)
│   ├── generated-image-1.png        # First generated image
│   ├── generated-image-2.png        # Second generated image
│   └── ...
├── metadata/
│   ├── generation-report.json       # Detailed generation data
│   └── model-comparison.md          # Comparison report (if enabled)
├── google-image-url.txt             # Primary image URL (backward compatibility)
├── image-urls.json                  # All image URLs array
├── models-used.json                 # Models used array
└── quality-scores.json              # Quality scores array
```

## 🧠 Intelligent Features

### Smart Model Selection

When `models: 'auto'` is used, the module analyzes the prompt to select optimal models:

- **Realistic content** → `imagen4-ultra`
- **Artistic content** → `flux-schnell`
- **Speed preference** → `imagen4-fast`
- **Default** → `imagen4-fast`

### Generation Strategies

#### Sequential Strategy
- Generates images one at a time
- Best for quality optimization
- Uses results to improve subsequent generations

#### Parallel Strategy
- Generates all images simultaneously
- Maximum speed with resource management
- Best for bulk generation

#### Smart Strategy (Default)
- Automatically selects optimal approach
- Parallel for multiple images without quality focus
- Sequential for quality-focused or comparison mode

### Quality Assessment

The module automatically assesses image quality based on:
- File size and validity
- Resolution appropriateness
- Content alignment with prompt
- Technical quality metrics

## 📊 Comparison Reports

When `enable-comparison: 'true'` is set, the module generates detailed comparison reports including:

- Generation statistics
- Model performance comparison
- Quality score analysis
- Time efficiency metrics
- Recommendations for future use

## 🔧 Integration Examples

### Accessing Multiple Images

```yaml
- name: Process All Generated Images
  run: |
    IMAGE_URLS='${{ steps.generate.outputs.image-urls }}'
    echo "$IMAGE_URLS" | jq -r '.[]' | while read url; do
      echo "Processing image: $url"
      # Process each image
    done
```

### Using Quality Scores

```yaml
- name: Select Best Images
  run: |
    QUALITY_SCORES='${{ steps.generate.outputs.quality-scores }}'
    PRIMARY_INDEX='${{ steps.generate.outputs.primary-image-index }}'
    echo "Best image is at index: $PRIMARY_INDEX"
    echo "Quality scores: $QUALITY_SCORES"
```

### Conditional Processing

```yaml
- name: Enhanced Processing
  if: steps.generate.outputs.images-completed > '1'
  run: |
    echo "Multi-image mode: processing ${{ steps.generate.outputs.images-completed }} images"
    # Enhanced multi-image processing
```

## ⚠️ Important Notes

### Backward Compatibility

- All existing workflows continue to work without modification
- The `google-image-url` output always contains the primary (highest quality) image URL
- The file `generated-image.png` is always created for compatibility
- All original output formats are preserved

### Performance Considerations

- Maximum of 10 images per generation to prevent resource exhaustion
- Parallel generation limited to 5 concurrent processes
- Automatic resource monitoring and adjustment
- Smart timeout handling for long-running generations

### Quality Threshold

- Images below the quality threshold are not counted as successful
- Minimum threshold of 0.0, maximum of 1.0
- Default threshold of 0.7 provides good balance
- Failed quality checks trigger retry with different models

## 🚀 Advanced Usage

### Model Comparison Workflow

```yaml
- name: Compare Multiple Models
  uses: ./.github/actions/kamui-modules/create-music-video-multi-image-workflow-v2
  with:
    image-prompt: "A professional headshot photo"
    image-count: '1'
    models: 'imagen4-ultra,photo-flux,imagen4-fast'
    enable-comparison: 'true'
    quality-threshold: '0.8'
    # This generates 3 images (1 per model) with detailed comparison
```

### High-Volume Generation

```yaml
- name: Generate Image Variations
  uses: ./.github/actions/kamui-modules/create-music-video-multi-image-workflow-v2
  with:
    image-prompt: "Various angles of a modern building"
    image-count: '8'
    models: 'auto'
    generation-strategy: 'parallel'
    max-parallel: '4'
    quality-threshold: '0.6'
    # Generates 8 variations quickly with parallel processing
```

## 📈 Monitoring and Debugging

### Generation Reports

The module creates detailed JSON reports with:
- Generation timings
- Success/failure status
- Quality assessments
- Model performance data
- Resource usage statistics

### Error Handling

- Graceful degradation on partial failures
- Automatic retry with fallback models
- Detailed error logging and reporting
- Resource cleanup on failures

## 🔗 Integration with Downstream Modules

### Video Generation

The primary image URL (`google-image-url`) is automatically passed to video generation modules:

```yaml
- name: Generate Video
  uses: ./.github/actions/kamui-modules/video-generation
  with:
    google-image-url: ${{ steps.images.outputs.google-image-url }}
    # Works exactly as before - no changes needed
```

### Pointcloud Generation

The primary image file (`generated-image.png`) is available for pointcloud generation:

```yaml
- name: Generate Pointcloud
  uses: ./.github/actions/kamui-modules/pointcloud-generation
  with:
    input-image-path: "${{ steps.setup.outputs.folder-name }}/images/generated-image.png"
    # Works exactly as before - no changes needed
```

### Web Player Enhancement

Web players can automatically detect and display multiple images:

```yaml
- name: Enhanced Web Player
  uses: ./.github/actions/kamui-modules/web-player-generation
  with:
    folder-name: ${{ steps.setup.outputs.folder-name }}
    # Automatically detects multiple images and creates gallery
```

## 📚 Migration Guide

### From Single Image Generation

**No changes required** - all existing workflows continue to work identically.

### To Enable Multi-Image Features

Simply add the new parameters:

```yaml
# Before (continues to work)
- uses: ./.github/actions/kamui-modules/create-music-video-multi-image-workflow-v2
  with:
    image-prompt: "A sunset"
    folder-name: "project"
    # ... other required params

# After (enhanced)
- uses: ./.github/actions/kamui-modules/create-music-video-multi-image-workflow-v2
  with:
    image-prompt: "A sunset"
    image-count: '3'              # NEW
    models: 'auto'                # NEW
    enable-comparison: 'true'     # NEW
    folder-name: "project"
    # ... other required params
```

## 🤝 Contributing

This module follows KamuiCode development standards:
- Maintain backward compatibility
- Comprehensive error handling
- Performance optimization
- Detailed documentation
- Thorough testing

---

*🤖 Generated with [Claude Code](https://claude.ai/code)*

*Co-Authored-By: Claude <noreply@anthropic.com>*
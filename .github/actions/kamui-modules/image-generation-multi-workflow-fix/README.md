# Multi Image Generation - Enhanced (Workflow Fix)

🎨 **Advanced multi-image generation with enhanced workflow validation and compatibility**

## 🎯 Overview

This enhanced module provides robust multi-image generation capabilities with comprehensive workflow validation, backward compatibility, and advanced error handling. It's designed to seamlessly integrate with downstream modules while providing enhanced features for complex image generation workflows.

## ✨ Key Features

### 🔧 Enhanced Compatibility
- **100% Backward Compatibility**: Works with existing workflows unchanged
- **Validated Interfaces**: All parameter flows validated against downstream modules
- **Safe Migration**: Drop-in replacement for `image-generation-multi`

### 🚀 Advanced Generation
- **Multi-Model Support**: Generate with multiple AI models simultaneously
- **Smart Parallelization**: Optimized concurrent processing based on quality presets
- **Quality Presets**: `fast`, `balanced`, `high` - automatic optimization
- **Format Support**: PNG, JPG, WEBP output formats

### 📊 Comprehensive Monitoring
- **Real-time Metrics**: Generation times, success rates, error tracking
- **Enhanced Reports**: Detailed comparison and performance analysis
- **Error Recovery**: Automatic retry with detailed error logging
- **Resource Optimization**: Smart memory and CPU usage management

### 🛡️ Robust Error Handling
- **Timeout Protection**: 5-minute timeout per image with graceful handling
- **Validation**: Input/output validation with clear error messages
- **Partial Success**: Continue generation even if some images fail
- **Detailed Logging**: Comprehensive error tracking and reporting

## 📋 Usage

### Basic Usage (Backward Compatible)
```yaml
- uses: ./.github/actions/kamui-modules/image-generation-multi-workflow-fix
  with:
    image-prompt: "A beautiful sunset landscape"
    folder-name: "my-images"
    branch-name: "main"
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Advanced Multi-Image Generation
```yaml
- uses: ./.github/actions/kamui-modules/image-generation-multi-workflow-fix
  with:
    image-prompt: "Abstract digital art"
    image-count: "5"
    models: "imagen4-fast,flux-schnell,imagen4-ultra"
    enable-comparison: "true"
    quality-preset: "high"
    output-format: "png"
    folder-name: "art-comparison"
    branch-name: "main"
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Integration with Downstream Modules
```yaml
jobs:
  generate_images:
    runs-on: ubuntu-latest
    outputs:
      folder-name: ${{ steps.gen.outputs.folder-name }}
      image-urls: ${{ steps.gen.outputs.image-urls }}
      success-rate: ${{ steps.gen.outputs.success-rate }}
    steps:
      - uses: ./.github/actions/kamui-modules/image-generation-multi-workflow-fix
        id: gen
        with:
          image-prompt: "Landscape photography"
          image-count: "3"
          models: "imagen4-fast"
          folder-name: "landscapes-${{ github.run_id }}"
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}

  analyze_images:
    needs: [generate_images]
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/kamui-modules/image-world-analysis
        with:
          image-file: "${{ needs.generate_images.outputs.folder-name }}/images/generated-image.png"
          folder-name: ${{ needs.generate_images.outputs.folder-name }}
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

## 📝 Inputs

### Core Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `image-prompt` | ✅ | - | The image generation prompt (1-500 characters) |
| `image-count` | ❌ | `1` | Number of images to generate (1-10) |
| `models` | ❌ | `auto` | Comma-separated list of models |
| `enable-comparison` | ❌ | `false` | Enable model comparison mode |

### Infrastructure Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `folder-name` | ✅ | - | Folder name for storing files |
| `branch-name` | ✅ | - | Git branch to work on |
| `oauth-token` | ✅ | - | Claude Code OAuth token |
| `mcp-config` | ✅ | - | MCP configuration JSON |

### Enhancement Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `output-format` | ❌ | `png` | Output format (png/jpg/webp) |
| `quality-preset` | ❌ | `balanced` | Quality preset (fast/balanced/high) |

### Supported Models
- `auto` - Intelligent model selection based on prompt
- `imagen4-ultra` - Highest quality, slower generation
- `imagen4-fast` - Good quality, faster generation
- `imagen3` - Google's Imagen 3 model
- `flux-schnell` - Fast artistic generation
- `photo-flux` - Photorealistic images

## 📤 Outputs

### Primary Outputs
| Output | Type | Description |
|--------|------|-------------|
| `images-completed` | number | Number of successfully generated images |
| `image-urls` | JSON array | Array of all generated image URLs |
| `models-used` | JSON array | Array of models actually used |
| `comparison-report` | string | Path to comparison report (if enabled) |

### Backward Compatibility Outputs
| Output | Type | Description |
|--------|------|-------------|
| `google-image-url` | string | First image URL (backward compatibility) |
| `image-completed` | boolean | Whether any image was generated |
| `used-model` | string | First model used (backward compatibility) |
| `folder-name` | string | Folder name for downstream modules |

### Performance Metrics
| Output | Type | Description |
|--------|------|-------------|
| `total-generation-time` | number | Total time in seconds |
| `average-generation-time` | number | Average time per image |
| `failed-generations` | number | Number of failed generations |
| `success-rate` | number | Success rate as percentage |

## 📁 File Structure

The module creates a comprehensive file structure for organized output:

```
{folder-name}/
├── images/
│   ├── generated-image.png              # First image (backward compatibility)
│   ├── generated-image-1-imagen4-fast.png
│   ├── generated-image-2-flux-schnell.png
│   └── ...
├── metadata/
│   ├── image-urls.json                  # Array of all URLs
│   ├── models-used.json                 # Array of models used
│   ├── generation-times.json            # Generation time data
│   └── generation-metrics.json          # Comprehensive metrics
├── reports/
│   ├── comparison-report.md             # Detailed comparison (if enabled)
│   └── generation-summary.md            # Always generated summary
├── errors/
│   └── generation-errors.jsonl          # Error details (if any failures)
└── google-image-url.txt                 # First URL (backward compatibility)
```

## 🔄 Workflow Integration Examples

### Model Comparison Workflow
```yaml
name: Multi-Model Image Comparison
on:
  workflow_dispatch:
    inputs:
      prompt:
        description: 'Image description'
        required: true

jobs:
  compare_models:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/kamui-modules/image-generation-multi-workflow-fix
        with:
          image-prompt: ${{ inputs.prompt }}
          image-count: "1"
          models: "imagen4-ultra,imagen4-fast,flux-schnell"
          enable-comparison: "true"
          quality-preset: "high"
          folder-name: "comparison-${{ github.run_id }}"
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Batch Generation Workflow
```yaml
name: Batch Image Generation
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  batch_generate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        prompt: 
          - "Morning landscape"
          - "Evening cityscape" 
          - "Abstract patterns"
    steps:
      - uses: ./.github/actions/kamui-modules/image-generation-multi-workflow-fix
        with:
          image-prompt: ${{ matrix.prompt }}
          image-count: "5"
          models: "imagen4-fast"
          quality-preset: "fast"
          folder-name: "batch-${{ matrix.prompt }}-${{ github.run_id }}"
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Full Pipeline Integration
```yaml
name: Complete Image Processing Pipeline
on:
  workflow_dispatch:
    inputs:
      description:
        description: 'Image description'
        required: true

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      folder: ${{ steps.gen.outputs.folder-name }}
      urls: ${{ steps.gen.outputs.image-urls }}
    steps:
      - uses: ./.github/actions/kamui-modules/image-generation-multi-workflow-fix
        id: gen
        with:
          image-prompt: ${{ inputs.description }}
          image-count: "3"
          models: "imagen4-fast,flux-schnell"
          enable-comparison: "true"
          folder-name: "pipeline-${{ github.run_id }}"
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}

  analyze:
    needs: [generate]
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/kamui-modules/image-world-analysis
        with:
          image-file: "${{ needs.generate.outputs.folder }}/images/generated-image.png"
          folder-name: ${{ needs.generate.outputs.folder }}
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}

  synthesize:
    needs: [generate, analyze]
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/kamui-modules/world-synthesis-v2
        with:
          image-analysis-json: "${{ needs.generate.outputs.folder }}/world-analysis/image-analysis.json"
          folder-name: ${{ needs.generate.outputs.folder }}
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

## 🛠️ Performance Optimization

### Quality Presets

| Preset | Speed | Quality | Parallelism | Best For |
|--------|-------|---------|-------------|----------|
| `fast` | ⚡⚡⚡ | ⭐⭐ | High (up to 4) | Prototyping, batch jobs |
| `balanced` | ⚡⚡ | ⭐⭐⭐ | Medium (up to 3) | General use (default) |
| `high` | ⚡ | ⭐⭐⭐⭐ | Low (up to 2) | Final production images |

### Resource Management

- **Memory Usage**: Optimized for GitHub Actions (< 2GB peak)
- **Execution Time**: Target < 15 minutes for 10 images
- **Network**: Efficient batching to minimize API calls
- **Storage**: Automatic cleanup of temporary files

## 🚨 Error Handling

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|--------|----------|
| `Invalid image count` | Count outside 1-10 range | Use valid range 1-10 |
| `Invalid model` | Unknown model name | Use supported model names |
| `MCP config invalid` | Malformed JSON | Validate MCP configuration |
| `Generation timeout` | Model overloaded | Retry or use faster model |
| `No images generated` | All generations failed | Check error logs in `errors/` |

### Error Recovery

The module includes automatic error recovery:
- **Retry Logic**: Failed generations are logged but don't stop the process
- **Partial Success**: Continue with remaining images if some fail
- **Detailed Logging**: All errors saved to `errors/generation-errors.jsonl`
- **Graceful Degradation**: Always produce valid outputs even with failures

## 🔄 Migration from Original Module

### Drop-in Replacement
Replace `image-generation-multi` with `image-generation-multi-workflow-fix`:

```yaml
# Before
- uses: ./.github/actions/kamui-modules/image-generation-multi

# After (no other changes needed)
- uses: ./.github/actions/kamui-modules/image-generation-multi-workflow-fix
```

### Enhanced Features (Optional)
Add new parameters to leverage enhanced capabilities:

```yaml
- uses: ./.github/actions/kamui-modules/image-generation-multi-workflow-fix
  with:
    # Existing parameters work unchanged
    image-prompt: "Your prompt"
    # Add new optional enhancements
    quality-preset: "high"
    output-format: "webp"
    enable-comparison: "true"
```

## 📊 Monitoring and Analytics

### Real-time Monitoring
- Generation progress with live updates
- Success rate tracking
- Performance metrics display
- Resource usage monitoring

### Post-generation Analytics
- Comprehensive comparison reports
- Performance statistics
- Error analysis and recommendations
- Model efficiency comparisons

## 🤝 Compatibility Matrix

| Downstream Module | Compatibility | Notes |
|-------------------|---------------|-------|
| `image-world-analysis` | ✅ Full | Uses generated image files |
| `world-synthesis-v2` | ✅ Chain | Via image-world-analysis |
| `threejs-*` modules | ✅ Enhanced | Supports multiple images |
| Legacy workflows | ✅ 100% | Drop-in replacement |

## 📝 Contributing

This module is part of the KamuiCode Workflow ecosystem. For improvements or bug reports, please follow the project's contribution guidelines.

## 📄 License

This module is part of the KamuiCode Workflow project and follows the same licensing terms.

---

*🤖 Enhanced Multi Image Generation Module v2.0 - Built with workflow validation and compatibility in mind*
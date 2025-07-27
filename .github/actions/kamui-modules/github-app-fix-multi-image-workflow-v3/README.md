# Multi Image Generation Workflow v3

🎨 Enhanced multi-image generation action with robust error handling, comprehensive validation, and advanced workflow integration capabilities.

## 🚀 Quick Start

```yaml
- name: Generate Multiple Images with v3
  uses: ./.github/actions/kamui-modules/github-app-fix-multi-image-workflow-v3
  with:
    image-prompt: "Beautiful cherry blossoms in spring"
    image-count: "3"
    models: "imagen4-fast,flux-schnell"
    enable-comparison: "true"
    folder-name: "my-images"
    branch-name: ${{ github.ref_name }}
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

## ✨ New Features in v3

### 🔧 Enhanced Error Handling
- **Retry Mechanism**: Automatic retry with exponential backoff (3 attempts max)
- **Graceful Degradation**: Continue processing on individual failures
- **Resource Monitoring**: Real-time memory and disk usage tracking
- **Error Classification**: Detailed error reporting and debugging information

### 🔍 Advanced Validation
- **Input Validation**: Comprehensive parameter validation with clear error messages
- **Model Validation**: Verify all specified models are supported
- **Resource Limits**: Prevent resource exhaustion with intelligent limits
- **Interface Compatibility**: 100% backward compatibility guaranteed

### 📊 Enhanced Reporting
- **Progress Tracking**: Real-time progress updates during generation
- **Performance Metrics**: Detailed timing and efficiency analysis
- **Success Rate Monitoring**: Automatic quality assessment
- **Advanced Comparison Reports**: Rich markdown reports with recommendations

### 🎯 Workflow Integration
- **Parameter Validation**: Pre-execution validation of all workflow parameters
- **Interface Contracts**: Guaranteed output format for downstream modules
- **Backward Compatibility**: Seamless integration with existing workflows

## 📋 Features

- ✅ **Multiple Images**: Generate 1-10 images in a single run
- ⚡ **Retry Mechanism**: Robust error recovery with exponential backoff
- 🔄 **Multiple Models**: Support for 6 different AI models
- 📊 **Enhanced Reports**: Advanced comparison analysis and performance metrics
- 🔒 **Error Recovery**: Intelligent failure handling and continuation
- 📈 **Progress Tracking**: Real-time status updates with resource monitoring
- 🔄 **100% Backward Compatible**: Drop-in replacement for existing workflows
- 🎯 **Validation Framework**: Comprehensive input and output validation
- 📋 **Interface Contracts**: Guaranteed parameter flow to downstream modules

## 🛠️ Configuration

### Required Inputs

| Parameter | Type | Description | Required | Default |
|-----------|------|-------------|----------|---------|
| `image-prompt` | string | The image generation prompt | ✅ Yes | N/A |
| `folder-name` | string | Folder name for storing image files | ✅ Yes | N/A |
| `branch-name` | string | Git branch to work on | ✅ Yes | N/A |
| `oauth-token` | string | Claude Code OAuth token | ✅ Yes | N/A |
| `mcp-config` | string | MCP configuration JSON | ✅ Yes | N/A |

### Optional Inputs

| Parameter | Type | Description | Required | Default |
|-----------|------|-------------|----------|---------|
| `image-count` | string | Number of images (1-10) | ❌ No | `'1'` |
| `models` | string | Comma-separated model list | ❌ No | `'auto'` |
| `enable-comparison` | string | Enable model comparison | ❌ No | `'false'` |

### Supported Models

- `auto` - Intelligent model selection based on prompt
- `imagen4-ultra` - High-quality realistic images
- `imagen4-fast` - Fast generation with good quality
- `imagen3` - Google's Imagen3 model
- `flux-schnell` - Artistic and stylized images
- `photo-flux` - Photography-focused generation

### Outputs

| Parameter | Type | Description | Compatibility |
|-----------|------|-------------|---------------|
| `images-completed` | number | Successfully generated images | ✅ Enhanced |
| `image-urls` | string | JSON array of image URLs | ✅ Enhanced |
| `models-used` | string | JSON array of models used | ✅ Enhanced |
| `comparison-report` | string | Path to comparison report | ✅ Enhanced |
| `google-image-url` | string | First image URL | ✅ **100% Compatible** |

## 🎯 Use Cases

### Basic Multi-Image Generation

```yaml
- name: Generate Multiple Images
  uses: ./.github/actions/kamui-modules/github-app-fix-multi-image-workflow-v3
  with:
    image-prompt: "Serene mountain landscape at sunset"
    image-count: "5"
    folder-name: "landscapes"
    branch-name: ${{ github.ref_name }}
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Model Comparison Analysis

```yaml
- name: Compare Image Generation Models
  uses: ./.github/actions/kamui-modules/github-app-fix-multi-image-workflow-v3
  with:
    image-prompt: "Futuristic cityscape with flying cars"
    image-count: "2"
    models: "imagen4-ultra,imagen4-fast,flux-schnell"
    enable-comparison: "true"
    folder-name: "model-comparison"
    branch-name: ${{ github.ref_name }}
    oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Integration with Downstream Modules

```yaml
jobs:
  generate-images:
    runs-on: ubuntu-latest
    outputs:
      google-image-url: ${{ steps.images.outputs.google-image-url }}
      images-completed: ${{ steps.images.outputs.images-completed }}
      comparison-report: ${{ steps.images.outputs.comparison-report }}
    steps:
      - name: Generate Images
        id: images
        uses: ./.github/actions/kamui-modules/github-app-fix-multi-image-workflow-v3
        with:
          image-prompt: "Beautiful garden with flowers"
          image-count: "3"
          models: "imagen4-fast,flux-schnell"
          enable-comparison: "true"
          folder-name: "garden-images"
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}

  analyze-images:
    needs: generate-images
    runs-on: ubuntu-latest
    steps:
      - name: Analyze Generated Image
        uses: ./.github/actions/kamui-modules/image-world-analysis
        with:
          image-url: ${{ needs.generate-images.outputs.google-image-url }}
          # ✅ 100% compatible with existing modules

  create-video:
    needs: generate-images
    runs-on: ubuntu-latest
    steps:
      - name: Generate Video from Images
        uses: ./.github/actions/kamui-modules/video-generation
        with:
          image-url: ${{ needs.generate-images.outputs.google-image-url }}
          # ✅ 100% compatible with existing modules
```

## 🔧 Advanced Configuration

### Resource Optimization

For large batch generation, the module automatically:
- Monitors memory usage and adjusts execution strategy
- Implements intelligent retry mechanisms
- Provides detailed progress tracking
- Optimizes resource allocation

### Error Handling

The v3 module provides enhanced error handling:

```yaml
- name: Robust Image Generation
  uses: ./.github/actions/kamui-modules/github-app-fix-multi-image-workflow-v3
  with:
    image-prompt: "Complex scene with multiple elements"
    image-count: "10"  # Large batch
    models: "imagen4-fast,flux-schnell,imagen4-ultra"
    enable-comparison: "true"
    # Module will automatically:
    # - Retry failed generations (3 attempts with backoff)
    # - Continue processing on individual failures
    # - Report detailed success rates
    # - Provide actionable recommendations
```

## 🐛 Troubleshooting

### Common Issues

#### Issue: "Invalid model" error
**Solution**: Check that all models in the comma-separated list are supported:
```yaml
models: "imagen4-fast,flux-schnell"  # ✅ Correct
models: "invalid-model,imagen4-fast" # ❌ Will fail validation
```

#### Issue: "Resource limit exceeded"
**Solution**: Reduce total image count or number of models:
```yaml
image-count: "5"
models: "imagen4-fast,flux-schnell"  # Total: 10 images (5×2 models)
# Must be ≤ 20 total images
```

#### Issue: Low success rate
**Solution**: The module provides automatic recommendations in the comparison report.

### Performance Optimization

#### For Large Batches
- Use `enable-comparison: "true"` to get detailed performance analysis
- Monitor the generated comparison report for optimization recommendations
- Consider using faster models (`imagen4-fast`) for large batches

#### For Quality Focus
- Use `imagen4-ultra` for highest quality
- Set `image-count: "1"` with multiple models for comparison
- Enable comparison mode for quality analysis

## 📊 Success Metrics

The v3 module tracks and reports:

- **Success Rate**: Percentage of successful generations
- **Performance Metrics**: Average, fastest, and slowest generation times
- **Resource Usage**: Memory and disk utilization
- **Quality Assessment**: Automatic recommendations based on results

## 🔄 Migration from Previous Versions

### From image-generation-multi

The v3 module is a **drop-in replacement**:

```yaml
# Before (image-generation-multi)
- uses: ./.github/actions/kamui-modules/image-generation-multi

# After (v3 with enhanced features)
- uses: ./.github/actions/kamui-modules/github-app-fix-multi-image-workflow-v3
```

**All existing workflows will continue to work without any changes.**

### Enhanced Features Available

When migrating to v3, you automatically get:
- ✅ Retry mechanisms for better reliability
- ✅ Enhanced error handling and recovery
- ✅ Detailed progress tracking
- ✅ Advanced comparison reports
- ✅ Resource monitoring
- ✅ Input validation

## 🎯 Interface Compatibility

### 100% Backward Compatibility

The v3 module maintains **perfect compatibility** with all existing downstream modules:

| Downstream Module | Compatibility | Required Output | Status |
|------------------|---------------|-----------------|---------|
| `image-world-analysis` | ✅ 100% | `google-image-url` | ✅ Maintained |
| `video-generation` | ✅ 100% | `google-image-url` | ✅ Maintained |
| `threejs-integration` | ✅ 100% | File structure | ✅ Maintained |
| `web-player-generation` | ✅ 100%+ | Enhanced with new outputs | ✅ Enhanced |

### Parameter Flow Validation

The v3 module includes built-in validation to ensure:
- All required parameters are provided
- Parameter types and formats are correct
- Resource limits are not exceeded
- Model specifications are valid

## 🔍 Validation Framework

### Pre-execution Validation
- Input parameter validation
- Model compatibility checks  
- Resource availability verification
- Interface contract validation

### Runtime Monitoring
- Progress tracking and reporting
- Resource usage monitoring
- Error detection and recovery
- Success rate analysis

### Post-execution Validation
- Output format verification
- File structure validation
- Compatibility guarantee enforcement

## 🚀 Best Practices

### For Reliable Generation
1. Use retry-friendly prompts (avoid time-sensitive content)
2. Enable comparison mode for quality analysis
3. Monitor success rates in generated reports
4. Use appropriate models for your content type

### For Performance
1. Use `imagen4-fast` for large batches
2. Enable comparison only when needed
3. Monitor resource usage in reports
4. Consider prompt complexity vs. generation time

### For Integration
1. Always use the `google-image-url` output for compatibility
2. Check the `images-completed` output for success validation
3. Use the comparison report for optimization insights
4. Monitor the generated outputs for downstream processing

## 📝 Example Workflows

### Complete Image Generation Pipeline

```yaml
name: Complete Image Generation Pipeline v3
on: [workflow_dispatch]

jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      folder-name: ${{ steps.setup.outputs.folder-name }}
    steps:
      - name: Setup Branch
        id: setup
        uses: ./.github/actions/kamui-modules/setup-branch
        with:
          branch-name: ${{ github.ref_name }}

  generate-images:
    needs: setup
    runs-on: ubuntu-latest
    outputs:
      google-image-url: ${{ steps.images.outputs.google-image-url }}
      images-completed: ${{ steps.images.outputs.images-completed }}
      comparison-report: ${{ steps.images.outputs.comparison-report }}
    steps:
      - name: Generate Multiple Images v3
        id: images
        uses: ./.github/actions/kamui-modules/github-app-fix-multi-image-workflow-v3
        with:
          image-prompt: "Ethereal fantasy landscape with magical elements"
          image-count: "5"
          models: "imagen4-ultra,flux-schnell"
          enable-comparison: "true"
          folder-name: ${{ needs.setup.outputs.folder-name }}
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}

  analyze:
    needs: [setup, generate-images]
    runs-on: ubuntu-latest
    steps:
      - name: Analyze Primary Image
        uses: ./.github/actions/kamui-modules/image-world-analysis
        with:
          image-url: ${{ needs.generate-images.outputs.google-image-url }}
          folder-name: ${{ needs.setup.outputs.folder-name }}
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}

  create-experience:
    needs: [setup, generate-images]
    runs-on: ubuntu-latest
    steps:
      - name: Generate Web Player
        uses: ./.github/actions/kamui-modules/web-player-generation
        with:
          folder-name: ${{ needs.setup.outputs.folder-name }}
          image-count: ${{ needs.generate-images.outputs.images-completed }}
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}
```

---

## 🤖 Technical Details

- **Module Version**: v3.0.0
- **Compatibility**: 100% backward compatible
- **Enhancement Level**: Advanced error handling and validation
- **Performance**: Optimized for reliability and comprehensive reporting
- **Integration**: Seamless with all existing KamuiCode modules

---

**🎨 Enhanced Multi Image Generation Workflow v3 - Building the future of AI-powered content creation with reliability and precision.**
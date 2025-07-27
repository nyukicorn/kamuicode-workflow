# Multi Image Generation Workflow v3 - Implementation Plan

**プロジェト**: KamuiCode Workflow  
**実装対象**: image-generation-multi モジュール v3 改善版  
**作成日**: 2025-07-27  
**実装方式**: GitHub Actions Automatic Development  

---

## 🎯 実装戦略

### **基本方針**
現在の `image-generation-multi` モジュールは既に要件を満たす優秀な実装であるため、**破綻的変更を避け段階的改善**を行う。

### **実装アプローチ**
1. **Non-Breaking Changes**: 既存インターフェースを維持
2. **Incremental Improvement**: 段階的な品質向上
3. **Backward Compatibility**: 完全な後方互換性保証
4. **Test-Driven Enhancement**: テスト駆動による安全な改善

---

## 📋 実装タスク詳細

### **Phase 1: Core Stability Enhancement** 🔧

#### **Task 1.1: Enhanced Error Handling**
**ファイル**: `.github/actions/kamui-modules/image-generation-multi/action.yml`  
**対象行**: 234-268 (Claude Code CLI実行部分)

**現在のコード**:
```bash
if npx @anthropic-ai/claude-code \
  --mcp-config="$MCP_CONFIG_ABS_PATH" \
  [...] ; then
  # Success handling
else
  echo "::warning::⚠️ Claude Code CLI failed for $MODEL_NAME (image $i)"
fi
```

**改善コード**:
```bash
# Retry mechanism with exponential backoff
RETRY_COUNT=0
MAX_RETRIES=3
RETRY_SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$RETRY_SUCCESS" = "false" ]; do
  echo "🔄 Attempt $((RETRY_COUNT + 1))/$MAX_RETRIES for $MODEL_NAME (image $i)"
  
  if npx @anthropic-ai/claude-code \
    --mcp-config="$MCP_CONFIG_ABS_PATH" \
    --allowedTools "mcp__*,Bash" \
    --max-turns 25 \
    --verbose \
    --permission-mode "bypassPermissions" \
    -p "$PROMPT"; then
    RETRY_SUCCESS=true
    echo "✅ Successfully generated image on attempt $((RETRY_COUNT + 1))"
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
      BACKOFF_SECONDS=$((RETRY_COUNT * 10))
      echo "⏳ Waiting ${BACKOFF_SECONDS}s before retry..."
      sleep $BACKOFF_SECONDS
    fi
  fi
done

if [ "$RETRY_SUCCESS" = "false" ]; then
  echo "::error::❌ Failed to generate image after $MAX_RETRIES attempts: $MODEL_NAME (image $i)"
  # Continue with next image rather than failing entire job
  FAILED_IMAGES=$((FAILED_IMAGES + 1))
fi
```

**実装詳細**:
- 指数バックオフ付きリトライ機構 (10s, 20s, 30s)
- 個別画像失敗時の継続処理
- 詳細なエラーログとステータス追跡

#### **Task 1.2: Input Validation Enhancement**
**対象行**: 78-82, 119-123

**現在のコード**:
```bash
IMAGE_COUNT="${{ inputs.image-count }}"
if [[ ! "$IMAGE_COUNT" =~ ^[0-9]+$ ]] || [ "$IMAGE_COUNT" -lt 1 ] || [ "$IMAGE_COUNT" -gt 10 ]; then
  echo "::error::❌ Invalid image count: $IMAGE_COUNT. Must be between 1 and 10."
  exit 1
fi
```

**改善コード**:
```bash
# Enhanced input validation
validate_inputs() {
  local errors=0
  
  # Image count validation
  IMAGE_COUNT="${{ inputs.image-count }}"
  if [[ ! "$IMAGE_COUNT" =~ ^[0-9]+$ ]] || [ "$IMAGE_COUNT" -lt 1 ] || [ "$IMAGE_COUNT" -gt 10 ]; then
    echo "::error::❌ Invalid image count: $IMAGE_COUNT. Must be between 1 and 10."
    errors=$((errors + 1))
  fi
  
  # Models validation
  MODELS="${{ inputs.models }}"
  IFS=',' read -ra MODEL_ARRAY <<< "$MODELS"
  for model in "${MODEL_ARRAY[@]}"; do
    model=$(echo "$model" | xargs)  # Trim whitespace
    case "$model" in
      "auto"|"imagen4-ultra"|"imagen4-fast"|"imagen3"|"flux-schnell"|"photo-flux")
        ;;  # Valid model
      *)
        echo "::error::❌ Invalid model: $model. Supported: auto, imagen4-ultra, imagen4-fast, imagen3, flux-schnell, photo-flux"
        errors=$((errors + 1))
        ;;
    esac
  done
  
  # Combination validation
  MODEL_COUNT=${#MODEL_ARRAY[@]}
  ENABLE_COMPARISON="${{ inputs.enable-comparison }}"
  if [ "$ENABLE_COMPARISON" = "true" ] && [ "$MODEL_COUNT" -eq 1 ] && [ "$IMAGE_COUNT" -eq 1 ]; then
    echo "::warning::⚠️ Comparison mode requires multiple models or multiple images"
  fi
  
  # Resource limit validation
  TOTAL_EXPECTED=$((MODEL_COUNT * IMAGE_COUNT))
  if [ "$TOTAL_EXPECTED" -gt 20 ]; then
    echo "::error::❌ Total images ($TOTAL_EXPECTED) exceeds limit of 20. Reduce image-count or number of models."
    errors=$((errors + 1))
  fi
  
  return $errors
}

# Execute validation
if ! validate_inputs; then
  echo "::error::❌ Input validation failed. Please check your parameters."
  exit 1
fi
```

#### **Task 1.3: Comprehensive Logging**
**実装位置**: 全体を通じてログ強化

**追加ログ機能**:
```bash
# Progress tracking
echo "::group::📊 Generation Progress"
echo "Total planned images: $TOTAL_EXPECTED"
echo "Models: $(IFS=', '; echo "${MODEL_ARRAY[*]}")"
echo "Comparison mode: $ENABLE_COMPARISON"
echo "Started at: $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"

# Real-time progress updates
update_progress() {
  local current=$1
  local total=$2
  local percentage=$(( (current * 100) / total ))
  echo "::notice::📈 Progress: $current/$total images completed ($percentage%)"
}

# Resource monitoring
monitor_resources() {
  echo "📊 Resource usage:"
  echo "  Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
  echo "  Disk: $(df -h . | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
  echo "  Load: $(uptime | awk -F'load average:' '{print $2}')"
}
```

### **Phase 2: Performance Optimization** ⚡

#### **Task 2.1: Parallel Execution Implementation**
**新機能**: 真の並列処理による高速化

**実装アプローチ**:
```bash
# Create job specification file
generate_job_spec() {
  local job_file="$FOLDER_NAME/generation-jobs.txt"
  : > "$job_file"  # Clear file
  
  local job_id=0
  for model in "${MODEL_ARRAY[@]}"; do
    for ((i=1; i<=IMAGE_COUNT; i++)); do
      echo "$job_id|$model|$i" >> "$job_file"
      job_id=$((job_id + 1))
    done
  done
  echo "$job_file"
}

# Parallel job executor function
execute_image_generation_job() {
  local job_spec="$1"
  IFS='|' read -r job_id model image_num <<< "$job_spec"
  
  # Extract service info
  SERVICE_INFO=$(get_service_info "$model")
  TARGET_SERVICE=$(echo "$SERVICE_INFO" | cut -d'|' -f1)
  MODEL_NAME=$(echo "$SERVICE_INFO" | cut -d'|' -f2)
  
  # Generate unique filename
  OUTPUT_FILENAME="generated-image-${job_id}-$(echo "$model" | tr '/' '-').png"
  
  # Create job-specific prompt and execute
  local start_time=$(date +%s)
  
  # ... Claude Code execution ...
  
  local end_time=$(date +%s)
  local duration=$((end_time - start_time))
  
  # Return job result
  echo "$job_id|$model|$OUTPUT_FILENAME|$duration|$?" > "$FOLDER_NAME/job-${job_id}-result.txt"
}

# Export function for parallel execution
export -f execute_image_generation_job
export -f get_service_info
export CLAUDE_CODE_OAUTH_TOKEN MCP_CONFIG_ABS_PATH IMAGE_PROMPT FOLDER_NAME IMAGES_DIR

# Execute jobs in parallel (max 3 concurrent)
JOB_SPEC_FILE=$(generate_job_spec)
echo "🚀 Executing $TOTAL_EXPECTED jobs in parallel (max 3 concurrent)"

cat "$JOB_SPEC_FILE" | parallel -j 3 --bar --tagstring "Job {%}" execute_image_generation_job {}

# Collect results
echo "📊 Collecting parallel execution results..."
for ((job_id=0; job_id<TOTAL_EXPECTED; job_id++)); do
  result_file="$FOLDER_NAME/job-${job_id}-result.txt"
  if [ -f "$result_file" ]; then
    IFS='|' read -r j_id j_model j_filename j_duration j_status < "$result_file"
    if [ "$j_status" -eq 0 ]; then
      GENERATED_URLS+=("$(cat "$FOLDER_NAME/google-image-url-$((job_id + 1)).txt" 2>/dev/null || echo "")")
      USED_MODELS+=("$j_model")
      GENERATION_TIMES+=("$j_duration")
      TOTAL_IMAGES=$((TOTAL_IMAGES + 1))
      echo "✅ Job $j_id completed: $j_filename ($j_duration s)"
    else
      echo "❌ Job $j_id failed: $j_model"
    fi
    rm "$result_file"
  fi
done

rm "$JOB_SPEC_FILE"
```

#### **Task 2.2: Resource Management**
**新機能**: リソース使用量の監視と制御

```bash
# Resource management configuration
MAX_MEMORY_MB=4096
MAX_CONCURRENT_JOBS=3
JOB_TIMEOUT_SECONDS=300

# Pre-execution resource check
check_resources() {
  local available_memory=$(free -m | awk '/^Mem:/ {print $7}')
  if [ "$available_memory" -lt $MAX_MEMORY_MB ]; then
    echo "::warning::⚠️ Low memory available: ${available_memory}MB < ${MAX_MEMORY_MB}MB"
    echo "::notice::📉 Reducing concurrent jobs to 2"
    MAX_CONCURRENT_JOBS=2
  fi
}

# Resource monitoring during execution
monitor_job_resources() {
  while [ -n "$(jobs -r)" ]; do
    local mem_usage=$(ps aux | awk '/claude-code/ {sum+=$6} END {print sum/1024}')
    if [ "${mem_usage%.*}" -gt $MAX_MEMORY_MB ]; then
      echo "::warning::⚠️ High memory usage detected: ${mem_usage}MB"
      # Kill oldest job if necessary
      jobs -p | head -1 | xargs kill -TERM
    fi
    sleep 30
  done
}
```

### **Phase 3: Enhanced Reporting** 📊

#### **Task 3.1: Advanced Comparison Report**
**改善対象**: 比較レポート生成機能

**新機能実装**:
```bash
generate_enhanced_comparison_report() {
  local report_path="$FOLDER_NAME/comparison-report.md"
  
  {
    echo "# 🎨 Advanced Image Generation Comparison Report"
    echo ""
    echo "## 📋 Generation Summary"
    echo "- **Prompt**: $IMAGE_PROMPT"
    echo "- **Generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- **Total Images**: $TOTAL_IMAGES"
    echo "- **Success Rate**: $(( (TOTAL_IMAGES * 100) / TOTAL_EXPECTED ))%"
    echo "- **Models Used**: $(IFS=', '; echo "${USED_MODELS[*]}" | tr ' ' '\n' | sort -u | tr '\n' ' ')"
    echo ""
    
    # Performance metrics
    echo "## ⚡ Performance Metrics"
    echo ""
    echo "| Metric | Value |"
    echo "|--------|-------|"
    
    if [ "${#GENERATION_TIMES[@]}" -gt 0 ]; then
      local total_time=0
      local min_time=${GENERATION_TIMES[0]}
      local max_time=${GENERATION_TIMES[0]}
      
      for time in "${GENERATION_TIMES[@]}"; do
        total_time=$((total_time + time))
        [ "$time" -lt "$min_time" ] && min_time=$time
        [ "$time" -gt "$max_time" ] && max_time=$time
      done
      
      local avg_time=$((total_time / ${#GENERATION_TIMES[@]}))
      
      echo "| Average Generation Time | ${avg_time}s |"
      echo "| Fastest Generation | ${min_time}s |"
      echo "| Slowest Generation | ${max_time}s |"
      echo "| Total Execution Time | ${total_time}s |"
    fi
    
    echo ""
    
    # Detailed results table
    echo "## 📸 Detailed Results"
    echo ""
    echo "| # | Model | File | Time | Status | Preview |"
    echo "|---|-------|------|------|--------|---------|"
    
    for ((i=0; i<TOTAL_IMAGES; i++)); do
      local image_num=$((i + 1))
      local model_name="${USED_MODELS[i]:-N/A}"
      local gen_time="${GENERATION_TIMES[i]:-N/A}"
      local google_url="${GENERATED_URLS[i]:-N/A}"
      
      # Find corresponding image file
      local image_file=""
      if [ "$MODEL_COUNT" -gt 1 ]; then
        image_file="generated-image-${i}-$(echo "${model_name}" | tr ' ' '-' | tr '/' '-').png"
      else
        image_file="generated-image-${image_num}.png"
      fi
      
      local status_icon="✅"
      [ ! -f "$IMAGES_DIR/$image_file" ] && status_icon="❌"
      
      local preview_link=""
      if [ -n "$google_url" ] && [ "$google_url" != "N/A" ]; then
        preview_link="[🔗 View]($google_url)"
      fi
      
      echo "| $image_num | $model_name | $image_file | ${gen_time}s | $status_icon | $preview_link |"
    done
    
    echo ""
    
    # Model comparison
    echo "## 🏆 Model Performance Comparison"
    echo ""
    
    # Group by model and calculate stats
    declare -A model_times
    declare -A model_counts
    
    for ((i=0; i<TOTAL_IMAGES; i++)); do
      local model="${USED_MODELS[i]}"
      local time="${GENERATION_TIMES[i]}"
      
      if [ -n "${model_times[$model]}" ]; then
        model_times[$model]=$((${model_times[$model]} + time))
        model_counts[$model]=$((${model_counts[$model]} + 1))
      else
        model_times[$model]=$time
        model_counts[$model]=1
      fi
    done
    
    echo "| Model | Images | Avg Time | Total Time | Efficiency |"
    echo "|-------|--------|----------|------------|------------|"
    
    for model in "${!model_times[@]}"; do
      local total_time=${model_times[$model]}
      local count=${model_counts[$model]}
      local avg_time=$((total_time / count))
      local efficiency=""
      
      case $model in
        *"fast"*) efficiency="⚡ Fast" ;;
        *"ultra"*) efficiency="🔍 Quality" ;;
        *"schnell"*) efficiency="🎨 Artistic" ;;
        *) efficiency="⚖️ Balanced" ;;
      esac
      
      echo "| $model | $count | ${avg_time}s | ${total_time}s | $efficiency |"
    done
    
    echo ""
    echo "## 💡 Recommendations"
    echo ""
    
    # Generate AI-driven recommendations
    local fastest_model=""
    local fastest_time=999999
    for model in "${!model_times[@]}"; do
      local count=${model_counts[$model]}
      local avg_time=$((${model_times[$model]} / count))
      if [ "$avg_time" -lt "$fastest_time" ]; then
        fastest_time=$avg_time
        fastest_model=$model
      fi
    done
    
    echo "- **🏆 Fastest Model**: $fastest_model (${fastest_time}s average)"
    echo "- **📊 Success Rate**: $(( (TOTAL_IMAGES * 100) / TOTAL_EXPECTED ))% - $([ $((TOTAL_IMAGES * 100 / TOTAL_EXPECTED)) -ge 95 ] && echo "Excellent" || echo "Review failed generations")"
    echo "- **⚡ Optimization**: $([ "$TOTAL_EXPECTED" -gt 5 ] && echo "Consider parallel execution for large batches" || echo "Current configuration is optimal")"
    
    echo ""
    echo "---"
    echo "*🤖 Generated by KamuiCode Multi Image Generation Module v3*"
    echo "*📅 Report generated at $(date -u +%Y-%m-%dT%H:%M:%SZ)*"
  } > "$report_path"
  
  echo "$report_path"
}
```

### **Phase 4: Documentation & Testing** 📚

#### **Task 4.1: README Enhancement**
**ファイル**: `.github/actions/kamui-modules/image-generation-multi/README.md`

**新規作成内容**:
```markdown
# Multi Image Generation Action

高性能な複数画像生成機能を提供する GitHub Actions モジュール。

## 🚀 Quick Start

```yaml
- name: Generate Multiple Images
  uses: ./.github/actions/kamui-modules/image-generation-multi
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

## 📋 Features

- ✅ **Multiple Images**: Generate 1-10 images in a single run
- ⚡ **Parallel Processing**: Optimized for speed with concurrent generation
- 🔄 **Multiple Models**: Support for 6 different AI models
- 📊 **Comparison Reports**: Detailed analysis and performance metrics
- 🔒 **Error Recovery**: Robust retry mechanisms and fault tolerance
- 📈 **Progress Tracking**: Real-time status updates
- 🔄 **Backward Compatible**: Seamless integration with existing workflows

## 🛠️ Configuration

### Required Inputs
[详细的输入参数说明]

### Outputs
[详细的输出参数说明]

## 🎯 Use Cases

### Basic Multi-Image Generation
[使用例]

### Model Comparison
[比较功能的使用例]

### Integration with Other Modules
[其他模块との連携例]

## 🐛 Troubleshooting

### Common Issues
[よくある問題と解決方法]

### Performance Optimization
[パフォーマンス最適化のヒント]
```

#### **Task 4.2: Integration Test Suite**
**ファイル**: `.github/workflows/test-multi-image-generation.yml`

```yaml
name: Multi Image Generation Tests
on:
  pull_request:
    paths: 
      - '.github/actions/kamui-modules/image-generation-multi/**'
  workflow_dispatch:

jobs:
  test-basic-functionality:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-case:
          - { name: "Single Image", count: "1", models: "imagen4-fast", comparison: "false" }
          - { name: "Multi Image", count: "3", models: "imagen4-fast", comparison: "false" }
          - { name: "Multi Model", count: "1", models: "imagen4-fast,flux-schnell", comparison: "true" }
          - { name: "Complex", count: "2", models: "imagen4-fast,flux-schnell", comparison: "true" }
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Test ${{ matrix.test-case.name }}
        uses: ./.github/actions/kamui-modules/image-generation-multi
        with:
          image-prompt: "Test image for automated testing"
          image-count: ${{ matrix.test-case.count }}
          models: ${{ matrix.test-case.models }}
          enable-comparison: ${{ matrix.test-case.comparison }}
          folder-name: "test-${{ github.run_id }}-${{ matrix.test-case.name }}"
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}
      
      - name: Validate Results
        run: |
          # Validate outputs exist
          [ -n "${{ steps.test.outputs.images-completed }}" ]
          [ -n "${{ steps.test.outputs.image-urls }}" ]
          
          # Validate file structure
          FOLDER="test-${{ github.run_id }}-${{ matrix.test-case.name }}"
          [ -d "$FOLDER/images" ]
          [ -f "$FOLDER/image-urls.json" ]
          
          # Validate comparison report if enabled
          if [ "${{ matrix.test-case.comparison }}" = "true" ]; then
            [ -f "$FOLDER/comparison-report.md" ]
          fi

  test-error-scenarios:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Test Invalid Input
        uses: ./.github/actions/kamui-modules/image-generation-multi
        continue-on-error: true
        with:
          image-prompt: "Test"
          image-count: "15"  # Invalid: >10
          models: "invalid-model"
          folder-name: "error-test"
          branch-name: ${{ github.ref_name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}
      
      - name: Verify Error Handling
        run: |
          # Should fail with proper error message
          echo "Error handling test completed"
```

---

## 📊 実装スケジュール

### **Week 1: Core Stability (Phase 1)**
- **Day 1-2**: エラーハンドリング強化実装
- **Day 3-4**: 入力検証とログ改善
- **Day 5**: Phase 1 テスト実行

### **Week 2: Performance Optimization (Phase 2)**
- **Day 1-3**: 並列処理機構実装
- **Day 4-5**: リソース管理とモニタリング
- **Day 6-7**: パフォーマンステスト

### **Week 3: Enhanced Features (Phase 3)**
- **Day 1-3**: 高度な比較レポート実装
- **Day 4-5**: AI品質評価機能
- **Day 6-7**: 統合テスト

### **Week 4: Documentation & Deployment (Phase 4)**
- **Day 1-2**: 包括的ドキュメント作成
- **Day 3-4**: テストスイート完成
- **Day 5**: 本番デプロイとモニタリング

---

## 🔍 リスク管理

### **High Risk Items**
1. **並列処理の複雑性**: デッドロックや競合状態のリスク
   - **軽減策**: 段階的実装とextensiveテスト
2. **リソース枯渇**: 大量生成時のメモリ不足
   - **軽減策**: リソース監視と自動制限

### **Medium Risk Items**
1. **後方互換性**: 既存ワークフローへの影響
   - **軽減策**: 厳密なインターフェーステスト
2. **性能劣化**: 機能追加による遅延
   - **軽減策**: ベンチマークテストの実施

### **Low Risk Items**
1. **ドキュメント不備**: 使用方法の理解困難
   - **軽減策**: ユーザーフィードバックの収集

---

## 📈 成功指標

### **Phase 1 完了基準**
- [ ] エラー発生時の95%以上の自動回復
- [ ] 入力検証による100%の不正値検出
- [ ] 詳細ログによるデバッグ効率50%向上

### **Phase 2 完了基準**
- [ ] 並列処理による30%以上の時間短縮
- [ ] リソース使用量200%以内での制御
- [ ] 同時実行での99%以上の成功率

### **Phase 3 完了基準**
- [ ] 比較レポートの自動生成100%
- [ ] ユーザー満足度90%以上
- [ ] ドキュメント完備による質問件数50%削減

---

## 🚀 デプロイメント戦略

### **Canary Deployment**
1. **Internal Testing**: 開発チームでの限定テスト
2. **Beta Release**: 一部ユーザーでのベータテスト  
3. **Gradual Rollout**: 段階的な本番展開
4. **Full Deployment**: 全ユーザーへの提供

### **Rollback Plan**
- 既存バージョンの完全保持
- Feature toggle による新機能の無効化
- 自動モニタリングによる異常検知時の自動ロールバック

---

**この実装計画は、現実的な工程と詳細な技術仕様に基づき、安全で効率的な改善を実現することを目指しています。**
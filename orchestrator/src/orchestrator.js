#!/usr/bin/env node

/**
 * KamuiCode Workflow Orchestrator
 * 自然言語指示から動的にGitHub Actionsワークフローを生成・実行
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class KamuiOrchestrator {
  constructor() {
    this.configPath = path.join(__dirname, '../config');
    this.modules = this.loadModules();
    this.templates = this.loadTemplates();
    this.workflowCounter = 0;
  }

  /**
   * モジュール定義を読み込み
   */
  loadModules() {
    const modulesPath = path.join(this.configPath, 'modules.json');
    try {
      const data = fs.readFileSync(modulesPath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.error('❌ Failed to load modules.json:', error.message);
      process.exit(1);
    }
  }

  /**
   * テンプレート定義を読み込み
   */
  loadTemplates() {
    const templatesPath = path.join(this.configPath, 'templates.json');
    try {
      const data = fs.readFileSync(templatesPath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.error('❌ Failed to load templates.json:', error.message);
      process.exit(1);
    }
  }

  /**
   * 自然言語コマンドを解析して実行プランを生成
   * Phase 1: 基本的なパターンマッチング
   */
  parseCommand(command) {
    console.log('🔍 Parsing command:', command);
    
    const plan = {
      modules: [],
      parameters: {},
      workflow: 'custom'
    };

    // 画像生成の解析
    const imagePatterns = [
      /imagen4.*?(\d+).*?画像/i,
      /imagen4.*?画像.*?(\d+)/i,
      /imagen4.*?で.*?画像/i
    ];

    for (const pattern of imagePatterns) {
      const match = command.match(pattern);
      if (match) {
        plan.modules.push({
          name: 'setup-branch',
          params: {}
        });
        plan.modules.push({
          name: 'image-generation',
          params: {
            provider: 'imagen4',
            count: match[1] ? parseInt(match[1]) : 1
          }
        });
        break;
      }
    }

    // 音楽生成の解析
    if (command.includes('音楽') || command.includes('ミュージック')) {
      plan.modules.push({
        name: 'music-planning',
        params: {}
      });
      plan.modules.push({
        name: 'music-generation',
        params: {
          provider: 'google-lyria'
        }
      });
    }

    // 動画生成の解析
    const videoPatterns = [
      /hailuo.*?動画/i,
      /baidu.*?動画/i,
      /動画.*?(\d+).*?本/i
    ];

    for (const pattern of videoPatterns) {
      const match = command.match(pattern);
      if (match) {
        plan.modules.push({
          name: 'video-generation',
          params: {
            provider: pattern.source.includes('hailuo') ? 'hailuo-02' : 'baidu',
            count: match[1] ? parseInt(match[1]) : 1
          }
        });
        break;
      }
    }

    // 動画統合の解析
    if (command.includes('つなぎ合わせ') || command.includes('ミュージックビデオ')) {
      plan.modules.push({
        name: 'video-concatenation',
        params: {}
      });
    }

    console.log('📋 Generated plan:', JSON.stringify(plan, null, 2));
    return plan;
  }

  /**
   * 実行プランを検証
   */
  validatePlan(plan) {
    const errors = [];
    
    // 依存関係チェック
    const moduleNames = plan.modules.map(m => m.name);
    
    for (const module of plan.modules) {
      if (!this.modules.modules[module.name]) {
        errors.push(`Unknown module: ${module.name}`);
        continue;
      }
      
      const moduleDef = this.modules.modules[module.name];
      for (const dep of moduleDef.dependencies) {
        if (!moduleNames.includes(dep)) {
          // 自動で依存関係を追加
          console.log(`🔧 Auto-adding dependency: ${dep}`);
          plan.modules.unshift({
            name: dep,
            params: {}
          });
        }
      }
    }

    // 重複除去
    const seen = new Set();
    plan.modules = plan.modules.filter(module => {
      if (seen.has(module.name)) {
        return false;
      }
      seen.add(module.name);
      return true;
    });

    return { valid: errors.length === 0, errors, plan };
  }

  /**
   * GitHub Actions YAMLを生成
   */
  generateWorkflow(plan, concept) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const workflowId = `orchestrated-${timestamp}`;
    
    // ベーステンプレートを選択
    let template;
    if (plan.modules.some(m => m.name === 'music-generation')) {
      template = JSON.parse(JSON.stringify(this.templates.workflows['music-video'].template));
    } else {
      template = JSON.parse(JSON.stringify(this.templates.workflows['image-only'].template));
    }

    // ワークフロー名を更新
    template.name = `${template.name} - ${workflowId}`;
    
    // ジョブステップを生成
    const steps = template.jobs[Object.keys(template.jobs)[0]].steps;
    
    // 既存のsetupステップは保持
    const additionalSteps = [];

    for (const module of plan.modules) {
      if (module.name === 'setup-branch') continue; // 既に含まれている
      
      const moduleDef = this.modules.modules[module.name];
      if (!moduleDef) continue;

      const step = {
        name: moduleDef.description,
        id: module.name.replace(/-/g, '_'),
        uses: moduleDef.path,
        with: {}
      };

      // 共通パラメータを設定
      if (moduleDef.inputs.includes('folder-name')) {
        step.with['folder-name'] = '${{ steps.setup.outputs.folder-name }}';
      }
      if (moduleDef.inputs.includes('branch-name')) {
        step.with['branch-name'] = '${{ steps.setup.outputs.branch-name }}';
      }
      if (moduleDef.inputs.includes('oauth-token')) {
        step.with['oauth-token'] = '${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}';
      }
      if (moduleDef.inputs.includes('mcp-config')) {
        step.with['mcp-config'] = '${{ secrets.MCP_CONFIG }}';
      }

      // モジュール固有のパラメータ
      if (module.name === 'image-generation') {
        step.with['image-prompt'] = concept || '美しい風景';
      }
      if (module.name === 'music-generation') {
        step.with['music-concept'] = concept || 'リラックスできる音楽';
        step.with['music-prompt'] = '${{ steps.music_planning.outputs.music-prompt }}';
      }
      if (module.name === 'music-planning') {
        step.with['music-concept'] = concept || 'リラックスできる音楽';
      }

      additionalSteps.push(step);
    }

    // ステップを追加
    steps.push(...additionalSteps);

    return template;
  }

  /**
   * Phase 1 テスト: 単一モジュール実行
   */
  async testSingleModule(command) {
    console.log('🧪 Phase 1 Test: Single Module Execution');
    console.log('Command:', command);
    
    try {
      // 1. 自然言語解析
      const plan = this.parseCommand(command);
      
      // 2. プラン検証
      const validation = this.validatePlan(plan);
      if (!validation.valid) {
        console.error('❌ Plan validation failed:', validation.errors);
        return false;
      }

      // 3. ワークフロー生成
      const workflow = this.generateWorkflow(validation.plan, command);
      
      // 4. ワークフロー保存
      const workflowDir = path.join(process.cwd(), '..', '.github/workflows');
      if (!fs.existsSync(workflowDir)) {
        fs.mkdirSync(workflowDir, { recursive: true });
      }
      const workflowPath = path.join(workflowDir, `test-orchestrator-${Date.now()}.yml`);
      const yamlContent = this.generateYAMLString(workflow);
      
      fs.writeFileSync(workflowPath, yamlContent);
      console.log('✅ Workflow generated:', workflowPath);
      console.log('📄 Workflow content preview:');
      console.log(yamlContent.split('\n').slice(0, 20).join('\n'));
      
      return true;
    } catch (error) {
      console.error('❌ Test failed:', error.message);
      return false;
    }
  }

  /**
   * JSONをYAMLに変換（改良版）
   */
  convertToYAML(obj, indent = 0) {
    const spaces = '  '.repeat(indent);
    let yaml = '';

    for (const [key, value] of Object.entries(obj)) {
      if (value === null || value === undefined) {
        yaml += `${spaces}${key}: null\n`;
      } else if (typeof value === 'string') {
        // 特殊文字を含む場合はクォート
        if (value.includes('${{') || value.includes('\n') || value.includes(':')) {
          yaml += `${spaces}${key}: "${value.replace(/"/g, '\\"')}"\n`;
        } else {
          yaml += `${spaces}${key}: ${value}\n`;
        }
      } else if (typeof value === 'number' || typeof value === 'boolean') {
        yaml += `${spaces}${key}: ${value}\n`;
      } else if (Array.isArray(value)) {
        if (value.length === 0) {
          yaml += `${spaces}${key}: []\n`;
        } else {
          yaml += `${spaces}${key}:\n`;
          for (const item of value) {
            if (typeof item === 'object' && item !== null) {
              yaml += `${spaces}- `;
              const itemYaml = this.convertToYAML(item, indent + 1);
              const lines = itemYaml.split('\n');
              // 最初の行は`- `の後に続ける
              yaml += lines[0].trim() + '\n';
              // 残りの行は適切にインデント
              for (let i = 1; i < lines.length - 1; i++) {
                if (lines[i].trim()) {
                  yaml += `${spaces}  ${lines[i].trim()}\n`;
                }
              }
            } else {
              yaml += `${spaces}- ${item}\n`;
            }
          }
        }
      } else if (typeof value === 'object') {
        yaml += `${spaces}${key}:\n`;
        yaml += this.convertToYAML(value, indent + 1);
      }
    }

    return yaml;
  }

  /**
   * ワークフロー用のYAML文字列を直接生成（より実用的）
   */
  generateYAMLString(workflow) {
    const job = workflow.jobs[Object.keys(workflow.jobs)[0]];
    
    let yaml = `name: "${workflow.name}"\n\n`;
    
    yaml += 'on:\n';
    yaml += '  workflow_dispatch:\n';
    yaml += '    inputs:\n';
    for (const [inputName, inputDef] of Object.entries(workflow.on.workflow_dispatch.inputs)) {
      yaml += `      ${inputName}:\n`;
      yaml += `        description: "${inputDef.description}"\n`;
      yaml += `        required: ${inputDef.required}\n`;
      yaml += `        type: ${inputDef.type}\n`;
    }
    
    yaml += '\n';
    yaml += 'permissions:\n';
    for (const [perm, value] of Object.entries(workflow.permissions)) {
      yaml += `  ${perm}: ${value}\n`;
    }
    
    yaml += '\n';
    yaml += 'jobs:\n';
    for (const [jobName, jobDef] of Object.entries(workflow.jobs)) {
      yaml += `  ${jobName}:\n`;
      yaml += `    runs-on: ${jobDef['runs-on']}\n`;
      yaml += `    timeout-minutes: ${jobDef['timeout-minutes']}\n`;
      yaml += '    steps:\n';
      
      for (const step of jobDef.steps) {
        yaml += `    - name: "${step.name}"\n`;
        if (step.id) yaml += `      id: ${step.id}\n`;
        yaml += `      uses: ${step.uses}\n`;
        if (step.with && Object.keys(step.with).length > 0) {
          yaml += '      with:\n';
          for (const [key, value] of Object.entries(step.with)) {
            yaml += `        ${key}: "${value}"\n`;
          }
        }
        yaml += '\n';
      }
    }
    
    return yaml;
  }

  /**
   * デバッグ情報を表示
   */
  debug() {
    console.log('🔧 Debug Information:');
    console.log('Modules loaded:', Object.keys(this.modules.modules).length);
    console.log('Templates loaded:', Object.keys(this.templates.workflows).length);
    console.log('Available modules:', Object.keys(this.modules.modules));
  }
}

// CLI実行部分
if (require.main === module) {
  const orchestrator = new KamuiOrchestrator();
  
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('🎭 KamuiCode Workflow Orchestrator');
    console.log('');
    console.log('Usage:');
    console.log('  node orchestrator.js "command"');
    console.log('  node orchestrator.js --debug');
    console.log('  node orchestrator.js --test');
    console.log('');
    console.log('Examples:');
    console.log('  node orchestrator.js "Imagen4で美しい桜の画像を1つ作って"');
    console.log('  node orchestrator.js "音楽付きのミュージックビデオを作成"');
    process.exit(0);
  }

  if (args[0] === '--debug') {
    orchestrator.debug();
  } else if (args[0] === '--test') {
    console.log('🧪 Running Phase 1 Tests...');
    orchestrator.testSingleModule("Imagen4で美しい桜の画像を1つ作って");
  } else {
    const command = args.join(' ');
    orchestrator.testSingleModule(command);
  }
}

module.exports = KamuiOrchestrator;
# Simple Test Module

Simple test module for KamuiCode Workflow push functionality testing.

## Inputs

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `test-message` | Test message to output | Yes | - |
| `test-count` | Number of times to repeat the message | No | `3` |

## Outputs

| Output | Description |
|--------|-------------|
| `result` | Test execution result |
| `message-count` | Actual number of messages output |

## Usage

```yaml
- name: Run Simple Test
  uses: ./.github/actions/kamui-modules/simple-test-module
  with:
    test-message: "Hello, World!"
    test-count: 5
```

## Functionality

1. Outputs the test message the specified number of times
2. Displays the current timestamp
3. Outputs the execution result in JSON format

This module is designed for testing the push functionality of the auto-development system.
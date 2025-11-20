# CLAUDE.md - AI Assistant Development Guide

**Repository:** ec2_manager
**Purpose:** Desktop GUI application for managing AWS EC2 instances
**Primary Language:** Python 3.6+
**UI Framework:** CustomTkinter
**AWS SDK:** boto3

---

## 📋 Table of Contents

1. [Repository Overview](#repository-overview)
2. [Codebase Structure](#codebase-structure)
3. [Development Workflows](#development-workflows)
4. [Key Conventions](#key-conventions)
5. [AI Assistant Guidelines](#ai-assistant-guidelines)
6. [Common Tasks](#common-tasks)
7. [Testing Strategy](#testing-strategy)
8. [Contributing](#contributing)

---

## 🎯 Repository Overview

### What This Application Does

EC2 Manager is a lightweight desktop application that provides a graphical interface for managing AWS EC2 instances without requiring the AWS Console. Users can:

- Connect using AWS credentials (Access Key, Secret Key, Region)
- List all EC2 instances in their account with caching for performance
- Start, stop, and reboot instances with confirmation dialogs
- View detailed network information (IPs, DNS names, elastic IPs)
- Use keyboard shortcuts for quick access (Ctrl+R, Ctrl+S, Ctrl+T, etc.)
- Disconnect and reconnect to AWS without restarting the application

### Current State

- **Total LOC:** ~469 lines of application code + ~350 lines of test code
- **Test Coverage:** ~90% for core modules (30+ unit tests implemented)
- **Documentation:** Comprehensive CLAUDE.md, README, code review report, and test documentation
- **CI/CD:** None configured (tests ready for CI/CD integration)
- **Code Quality:** P0, P1, and P2 issues resolved; threaded, cached, tested
- **Maturity Level:** Production-ready with comprehensive test coverage

### Key Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.6+ |
| GUI Framework | CustomTkinter | Latest |
| AWS SDK | boto3 | Latest |
| GUI Toolkit | tkinter | Built-in |

---

## 📁 Codebase Structure

```
ec2_manager/
├── main.py                           # Entry point - launches the GUI application
├── setup.py                          # Package configuration for pip install
├── requirements.txt                  # Dependencies: boto3, customtkinter
├── README.md                         # User-facing documentation
├── .gitignore                        # Ignores demo video file
│
├── gui/                              # GUI layer
│   ├── __init__.py                   # Exports EC2ManagerApp
│   └── main_window.py                # Main CustomTkinter GUI (140 lines)
│
├── aws_connection/                   # AWS integration layer
│   ├── __init__.py                   # Exports AWS functions
│   ├── credentials.py                # AWS session setup (40 lines)
│   └── ec2_control.py                # EC2 operations (105 lines)
│
└── utils/                            # Helper utilities
    ├── __init__.py                   # Exports helper functions
    └── helpers.py                    # Logging, validation, formatting (65 lines)
```

### Module Responsibilities

#### `main.py`
- Application entry point
- Initializes and runs the EC2ManagerApp GUI
- Keep this minimal - all logic should be in modules

#### `gui/main_window.py`
- CustomTkinter GUI implementation
- EC2ManagerApp class extends `customtkinter.CTk`
- Contains credential input fields, instance listbox, control buttons, info panel
- Calls aws_connection functions for all EC2 operations
- **Guidelines:** Keep UI logic separate from business logic

#### `aws_connection/credentials.py`
- Function: `setup_aws_session(access_key, secret_key, region)`
- Creates and validates boto3 session
- Returns EC2 client object or raises exceptions
- **Guidelines:** Never store credentials in code or config files

#### `aws_connection/ec2_control.py`
- Core EC2 operations using boto3 EC2 client
- Functions:
  - `list_instances(ec2_client)` - Returns all instances with details
  - `start_instance(ec2_client, instance_id)` - Starts stopped instance
  - `stop_instance(ec2_client, instance_id)` - Stops running instance
  - `reboot_instance(ec2_client, instance_id)` - Reboots instance
  - `get_instance_network_info(ec2_client, instance_id)` - Network details
- **Guidelines:** Add new EC2 operations here

#### `utils/helpers.py`
- Helper functions for logging, validation, formatting
- Keep pure utility functions here
- No AWS or GUI dependencies

---

## 🔄 Development Workflows

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd ec2_manager

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running the Application

```bash
# Run from source
python main.py

# Or if installed
ec2-manager
```

### Git Workflow

```bash
# Feature branch naming convention
git checkout -b claude/<descriptive-feature-name>-<session-id>

# Make changes
git add .
git commit -m "Descriptive commit message"

# Push to feature branch
git push -u origin claude/<branch-name>
```

**Important Git Notes:**
- Branch names must start with `claude/` for AI assistant work
- Use descriptive commit messages (not "update" or "fix")
- Always push to feature branches, never directly to main
- Network failures: Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Code Review Process

Before committing:
1. Test changes manually with AWS credentials
2. Check for hardcoded credentials or secrets
3. Verify no breaking changes to existing functionality
4. Update docstrings if function signatures changed
5. Run application end-to-end

---

## 📐 Key Conventions

### Python Code Style

- **Indentation:** 4 spaces (no tabs)
- **Line Length:** Aim for 80-100 characters, max 120
- **Imports:** Group by standard library, third-party, local modules
- **Naming:**
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

### Documentation

- **Docstrings:** Use triple quotes with parameter descriptions
- **Format:**
  ```python
  def function_name(param1, param2):
      """
      Brief description of function.

      Args:
          param1 (type): Description
          param2 (type): Description

      Returns:
          type: Description

      Raises:
          ExceptionType: When this happens
      """
  ```

### Error Handling

- Use try-except blocks for AWS API calls
- Catch specific exceptions (`botocore.exceptions.ClientError`)
- Provide user-friendly error messages
- Log errors for debugging

**Example:**
```python
try:
    response = ec2_client.start_instances(InstanceIds=[instance_id])
    return f"Instance {instance_id} started successfully"
except ClientError as e:
    error_code = e.response['Error']['Code']
    error_message = e.response['Error']['Message']
    return f"Failed to start instance: {error_message}"
```

### Security Best Practices

- **Never** commit AWS credentials
- **Never** hardcode access keys or secrets
- Always validate user input
- Use AWS IAM best practices (least privilege)
- Be cautious with instance operations (stop/terminate)

### Module Organization

- Keep modules focused on single responsibility
- GUI logic stays in `gui/`
- AWS operations stay in `aws_connection/`
- Pure utilities stay in `utils/`
- No circular dependencies

### Threading and Async Operations

**Pattern for non-blocking AWS calls:**
```python
def perform_aws_operation(self):
    def run_in_background():
        # Disable UI
        self.after(0, lambda: self._set_buttons_state("disabled"))

        # Perform AWS operation
        result = some_aws_function(self.aws_session)

        # Update UI (thread-safe with self.after)
        self.after(0, lambda: self.handle_result(result))
        self.after(0, lambda: self._set_buttons_state("normal"))

    thread = threading.Thread(target=run_in_background, daemon=True)
    thread.start()
```

**Key principles:**
- All AWS API calls run in background threads
- Use `self.after(0, lambda: ...)` for thread-safe UI updates
- Set `daemon=True` so threads don't block application exit
- Disable buttons during operations to prevent race conditions

### Caching Strategy

- Instance list cached in `self.instance_cache`
- Cache used on navigation, invalidated on state changes
- `update_instance_list(use_cache=True)` for cached reads
- Explicit refresh (`use_cache=False`) forces AWS API call
- Benefits: Reduced API calls, faster UX, lower AWS costs

---

## 🤖 AI Assistant Guidelines

### When Making Changes

1. **Always read files first** before editing
   - Use Read tool to understand current implementation
   - Check related files for dependencies

2. **Understand the context**
   - Review recent commits with `git log`
   - Check current branch with `git status`
   - Read related function docstrings

3. **Make targeted changes**
   - Edit existing files rather than rewriting
   - Preserve existing patterns and style
   - Maintain backward compatibility

4. **Test conceptually**
   - Think through the user workflow
   - Consider edge cases (no instances, network errors, invalid credentials)
   - Verify AWS API responses

### When Adding Features

1. **Determine the right location**
   - GUI changes → `gui/main_window.py`
   - New EC2 operation → `aws_connection/ec2_control.py`
   - Helper function → `utils/helpers.py`

2. **Follow existing patterns**
   - Match function signature style
   - Use similar error handling
   - Maintain consistent docstring format

3. **Consider dependencies**
   - Check if new dependencies needed in `requirements.txt`
   - Verify boto3 API availability
   - Test with AWS free tier resources

### When Fixing Bugs

1. **Locate the issue**
   - Use Grep to find relevant code
   - Check function call chain
   - Review error messages

2. **Understand the root cause**
   - Don't just fix symptoms
   - Check AWS API documentation if needed
   - Consider user input validation

3. **Verify the fix**
   - Think through test cases
   - Check for similar issues elsewhere
   - Update comments/docstrings if needed

### File Reading Strategy

- **Start broad:** Read module `__init__.py` files to understand exports
- **Then specific:** Read the specific function/class you need to modify
- **Check dependencies:** Read imported modules if behavior is unclear
- **Parallel reads:** Use multiple Read tool calls for independent files

### Common Pitfalls to Avoid

❌ **Don't:**
- Rewrite entire files when only small changes needed
- Add features without understanding existing code
- Commit without testing the workflow
- Hardcode values that should be configurable
- Ignore error handling
- Create new files when existing ones suffice
- Use generic commit messages

✅ **Do:**
- Read before editing
- Use Edit tool for targeted changes
- Follow existing code patterns
- Add proper error handling
- Update docstrings
- Test changes mentally
- Write descriptive commit messages

---

## 🛠️ Common Tasks

### Adding a New EC2 Operation

1. **Add function to `aws_connection/ec2_control.py`:**
   ```python
   def new_operation(ec2_client, instance_id):
       """
       Description of operation.

       Args:
           ec2_client: boto3 EC2 client
           instance_id (str): EC2 instance ID

       Returns:
           str: Success/error message
       """
       try:
           response = ec2_client.some_operation(InstanceIds=[instance_id])
           return "Operation successful"
       except ClientError as e:
           return f"Operation failed: {e.response['Error']['Message']}"
   ```

2. **Export in `aws_connection/__init__.py`:**
   ```python
   from .ec2_control import new_operation
   ```

3. **Add GUI button in `gui/main_window.py`:**
   - Create button in `__init__`
   - Connect to handler method
   - Call `aws_connection.new_operation()`

### Adding a New Dependency

1. **Add to `requirements.txt`:**
   ```
   new-package>=1.0.0
   ```

2. **Add to `setup.py` install_requires:**
   ```python
   install_requires=[
       'boto3',
       'customtkinter',
       'new-package>=1.0.0',
   ],
   ```

3. **Import in relevant module:**
   ```python
   import new_package
   ```

### Adding a Configuration Option

Currently, there's no persistent configuration. If adding config:

1. **Create `config.py` in root:**
   ```python
   import json
   from pathlib import Path

   CONFIG_FILE = Path.home() / '.ec2_manager_config.json'

   def load_config():
       if CONFIG_FILE.exists():
           return json.loads(CONFIG_FILE.read_text())
       return {}

   def save_config(config):
       CONFIG_FILE.write_text(json.dumps(config, indent=2))
   ```

2. **Use in application** (but never store credentials!)

### Improving Error Messages

1. **Locate error handling** (try-except blocks)
2. **Make messages user-friendly:**
   - Bad: `"Error: ClientError"`
   - Good: `"Failed to connect to AWS. Please check your credentials and region."`
3. **Include actionable guidance:**
   - What went wrong
   - What the user should check
   - How to fix it

---

## 🧪 Testing Strategy

### Current State
- **✅ Unit tests implemented** - Comprehensive test suite with 30+ test cases
- **Test Coverage:** ~90% for core modules (credentials, ec2_control, helpers)
- **Framework:** unittest (built-in) with unittest.mock for AWS mocking
- Manual testing still recommended for GUI changes

### Test Structure

```
tests/
├── __init__.py
├── README.md                # Detailed testing documentation
├── test_credentials.py      # AWS session setup tests (7 test cases)
├── test_ec2_control.py      # EC2 operations tests (14 test cases)
└── test_helpers.py          # Utility functions tests (9 test cases)
```

### Running Tests

**Prerequisites:**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or minimal test dependencies
pip install pytest pytest-cov
```

**Run all tests:**
```bash
# Using pytest (recommended)
python -m pytest tests/ -v

# Using unittest
python -m unittest discover tests/ -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html
```

**Run specific tests:**
```bash
# Test one file
python -m pytest tests/test_helpers.py -v

# Test one class
python -m pytest tests/test_ec2_control.py::TestEC2Control -v

# Test one method
python tests/test_helpers.py
```

### Test Coverage

| Module | Test File | Coverage | Test Cases |
|--------|-----------|----------|------------|
| `utils/helpers.py` | test_helpers.py | 100% | 9 |
| `aws_connection/credentials.py` | test_credentials.py | 95% | 7 |
| `aws_connection/ec2_control.py` | test_ec2_control.py | 95% | 14 |
| **Total** | **All tests** | **~90%** | **30+** |

**What's tested:**
- ✅ Credential validation (valid, empty, partial, whitespace)
- ✅ AWS session setup (success, errors, invalid credentials)
- ✅ EC2 operations (list, start, stop, reboot, network info)
- ✅ Error handling (ClientError, generic exceptions)
- ✅ Data formatting (complete, partial, minimal data)
- ✅ Edge cases (no public IP, invalid instance ID, etc.)

**What's not tested:**
- GUI components (requires GUI testing framework)
- Integration tests with real AWS (requires test AWS account)
- Threading behavior (complex to test in unit tests)

### Integration Tests

For integration testing with real AWS credentials:
1. Create a test AWS account or use isolated test region
2. Create test EC2 instances with known IDs
3. Run application manually with test credentials
4. Verify operations work end-to-end

**Security note:** Never commit real AWS credentials to tests!

#### Manual Testing Checklist

Before committing GUI changes:
- [ ] Application launches without errors
- [ ] Credential validation works (valid and invalid)
- [ ] Instance list displays correctly
- [ ] Start/Stop/Reboot buttons work
- [ ] Instance details display correctly
- [ ] Error messages are user-friendly
- [ ] No hardcoded credentials in code

---

## 👥 Contributing

### Project Maintainers

- **Abdur-Rahman Bilal** <aramb@aramservices.com> - Co-author

### For AI Assistants

When making commits on behalf of the user:

1. **Use proper co-author attribution:**
   ```bash
   git commit -m "Add new EC2 operation feature

   Co-authored-by: Abdur-Rahman Bilal <aramb@aramservices.com>"
   ```

2. **Branch naming:**
   - Use `claude/<feature-description>-<session-id>`
   - Example: `claude/add-terminate-instance-019Zn...`

3. **Commit message format:**
   ```
   Brief summary (50 chars or less)

   More detailed explanation if needed. Wrap at 72 characters.
   - List specific changes
   - Explain why, not just what

   Co-authored-by: Abdur-Rahman Bilal <aramb@aramservices.com>
   ```

### Code Review Guidelines

Before pushing:
- [ ] Code follows existing style conventions
- [ ] Docstrings updated for new/modified functions
- [ ] No credentials or secrets in code
- [ ] Error handling implemented
- [ ] Changes tested manually
- [ ] Commit message is descriptive
- [ ] Co-author attribution included

### Feature Requests and Bug Reports

When implementing requested features:
1. Understand the full requirement
2. Check for existing similar functionality
3. Plan the implementation (which files to modify)
4. Make minimal changes needed
5. Test thoroughly
6. Document in commit message

---

## 📚 Additional Resources

### AWS Documentation
- [boto3 EC2 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html)
- [EC2 Instance Lifecycle](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html)

### CustomTkinter Documentation
- [CustomTkinter GitHub](https://github.com/TomSchimansky/CustomTkinter)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)

### Python Best Practices
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Exception Handling](https://docs.python.org/3/tutorial/errors.html)

---

## 🔍 Quick Reference

### File Locations
- Entry point: `/home/user/ec2_manager/main.py:1`
- Main GUI: `/home/user/ec2_manager/gui/main_window.py:1`
- EC2 operations: `/home/user/ec2_manager/aws_connection/ec2_control.py:1`
- AWS auth: `/home/user/ec2_manager/aws_connection/credentials.py:1`
- Helpers: `/home/user/ec2_manager/utils/helpers.py:1`

### Key Functions
- `setup_aws_session()` - `/home/user/ec2_manager/aws_connection/credentials.py`
- `list_instances()` - `/home/user/ec2_manager/aws_connection/ec2_control.py`
- `start_instance()` - `/home/user/ec2_manager/aws_connection/ec2_control.py`
- `stop_instance()` - `/home/user/ec2_manager/aws_connection/ec2_control.py`
- `reboot_instance()` - `/home/user/ec2_manager/aws_connection/ec2_control.py`
- `_perform_instance_action()` - Generic method for instance operations in `gui/main_window.py`
- `update_instance_list(use_cache)` - Load instances with optional caching

### Keyboard Shortcuts (Added in P2)
- **Ctrl+R** - Refresh instance list (force reload from AWS)
- **Ctrl+S** - Start selected instance
- **Ctrl+T** - Stop selected instance (with confirmation)
- **Ctrl+B** - Reboot selected instance (with confirmation)
- **Ctrl+D** - Disconnect from AWS
- **F5** - Refresh instance list (force reload from AWS)

### Development Commands
```bash
# Run application
python main.py

# Install dependencies
pip install -r requirements.txt

# Install in dev mode
pip install -e .

# Check git status
git status

# View recent commits
git log --oneline -10

# Create feature branch
git checkout -b claude/feature-name-<session-id>

# Commit with co-author
git commit -m "Message

Co-authored-by: Abdur-Rahman Bilal <aramb@aramservices.com>"

# Push to feature branch
git push -u origin <branch-name>
```

---

**Last Updated:** 2025-11-20
**Repository Version:** Based on commit a496db7
**Documentation Maintainer:** AI Assistant (Claude)
**For Questions:** Contact Abdur-Rahman Bilal <aramb@aramservices.com>

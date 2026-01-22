# Review Python Code

Perform a comprehensive review of the selected Python code using available tools and best practices.

## Analysis Steps

### 1. Static Analysis
Use #tool:pylance to check for:
- Type errors and missing type hints
- Undefined variables or imports
- Unused imports and variables
- Import organization issues

### 2. Code Quality
Review for:
- **Naming**: Use snake_case for functions/variables, PascalCase for classes
- **Complexity**: Functions should be < 20 lines, cyclomatic complexity < 10
- **DRY**: Identify code duplication
- **Magic numbers**: Replace with named constants
- **Documentation**: Missing or inadequate docstrings

### 3. Error Handling
Check for:
- Missing try/except blocks for risky operations (I/O, network, parsing)
- Bare `except:` clauses (should catch specific exceptions)
- Proper error logging with context
- Input validation for function parameters

### 4. Performance
Identify potential issues:
- Unnecessary loops or list comprehensions
- N+1 database queries
- Missing async/await for I/O operations
- Inefficient data structures (list vs set/dict lookups)

### 5. Security
Check for vulnerabilities:
- SQL injection risks (use parameterized queries)
- Command injection (avoid shell=True)
- Path traversal vulnerabilities
- Hardcoded secrets or credentials
- Unsafe deserialization (pickle, eval)

### 6. Testing
Use @workspace to verify:
- Corresponding test file exists
- Test coverage for edge cases and error conditions
- Tests follow pytest conventions

### 7. Project Standards
Reference #file:.github/copilot-instructions.md to ensure:
- Code follows project naming conventions
- Error handling matches project patterns
- Dependencies are properly managed

## Output Format

For each issue found, provide:
1. **Issue**: Brief description with severity (Critical/High/Medium/Low)
2. **Location**: Specific line or function name
3. **Problem**: Detailed explanation
4. **Fix**: Concrete code example showing the improvement
5. **Rationale**: Why this change matters

Prioritize critical security and correctness issues first, then code quality improvements.

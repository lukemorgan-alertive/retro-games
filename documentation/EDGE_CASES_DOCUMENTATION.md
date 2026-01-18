# Edge Cases in Programming Logic - Retro Games Application

## Overview
This document catalogs edge cases identified and remediated in the Retro Games CLI and API applications. Edge cases are unusual or extreme inputs/conditions that may cause unexpected behavior if not properly handled.

---

## 1. Input Validation Edge Cases

### 1.1 String Length Limits
**Issue:** Unbounded string inputs could cause database bloat or application crashes.

**Locations:**
- `retro-games-cli/main.py` - `add_game()` function
- `retro-games-api/app.py` - `GameCreate` and `GameUpdate` models

**Remediation:**
- Title field: Max 500 characters
- Platform field: Max 100 characters
- Enforced at both CLI validation and API Pydantic model levels

**Edge cases handled:**
- Empty strings (rejected via `min_length=1`)
- Extremely long strings (truncated/rejected)
- Whitespace-only strings (trimmed and validated)

### 1.2 Year Boundary Validation
**Issue:** Invalid years could corrupt data integrity.

**Locations:**
- `retro-games-cli/main.py` - `add_game()` function
- `retro-games-api/app.py` - `GameCreate` and `GameUpdate` models

**Remediation:**
- Year range: 1970-2030 (reasonable bounds for retro games)
- API enforces via Pydantic `Field(ge=1970, le=2030)`
- CLI now validates in `add_game()` function

**Edge cases handled:**
- Negative years
- Years in the distant past (< 1970)
- Years in the distant future (> 2030)
- Non-numeric year inputs (handled by type conversion)

### 1.3 Date Format Validation
**Issue:** Invalid date formats could cause parsing errors.

**Locations:**
- `retro-games-cli/main.py` - `validate_date()` function
- `retro-games-api/app.py` - Pydantic automatic date parsing

**Remediation:**
- Strict ISO 8601 format required (YYYY-MM-DD)
- Invalid dates rejected with clear error messages
- CSV import skips rows with invalid dates

**Edge cases handled:**
- Invalid date formats (e.g., MM/DD/YYYY, DD-MM-YYYY)
- Non-existent dates (e.g., 2024-02-30)
- Partial dates (e.g., 2024-02)
- Null/empty date values

### 1.4 Condition Enum Validation
**Issue:** Invalid condition values could bypass database constraints.

**Locations:**
- `retro-games-cli/main.py` - `validate_condition()` function
- `retro-games-api/app.py` - Literal type enum
- Database schema - CHECK constraint

**Remediation:**
- Allowed values: 'mint', 'vgc', 'gc', 'used'
- Case-insensitive validation (normalized to lowercase)
- Optional field (None is valid)
- Three layers of defense: app validation, API validation, DB constraint

**Edge cases handled:**
- None/null values (treated as valid optional)
- Empty strings (converted to None)
- Whitespace-only strings (converted to None)
- Invalid values (rejected with error)
- Mixed case inputs (normalized)

---

## 2. File I/O Edge Cases

### 2.1 CSV Import
**Issue:** Malformed or malicious CSV files could crash the application.

**Locations:**
- `retro-games-cli/main.py` - `import_csv()` function

**Remediation:**
- Missing required columns detected and rejected immediately
- Invalid rows skipped with silent failure (not crashing entire import)
- File encoding errors handled via `errors="replace"`
- Memory-efficient row-by-row processing for large files
- File existence validation added

**Edge cases handled:**
- Missing CSV file (FileNotFoundError)
- Missing required columns (ValueError)
- Empty CSV files (returns count=0)
- Encoding issues (UTF-8 with replacement characters)
- Malformed rows (skipped, not crashed)
- Very large files (streaming, not loading all into memory)
- Empty cells (treated as missing/invalid)
- Special characters in data (handled by csv module)

### 2.2 CSV Export
**Issue:** File write failures could lose data.

**Locations:**
- `retro-games-cli/main.py` - `export_csv()` function

**Edge cases handled:**
- None values in condition field (exported as empty string)
- File permission errors (propagated to caller)
- Disk full scenarios (exception raised)
- Special characters escaped by csv module

---

## 3. Database Edge Cases

### 3.1 Connection Management
**Issue:** Unclosed connections or lock timeouts could cause resource leaks.

**Locations:**
- `retro-games-cli/main.py` - `get_connection()` function
- `retro-games-api/models.py` - `get_db_connection()` context manager

**Remediation:**
- Context managers ensure connection cleanup (finally block)
- Timeout set to 30 seconds to prevent indefinite blocking
- Foreign key enforcement enabled
- Proper error propagation

**Edge cases handled:**
- Database locked scenarios (timeout after 30s)
- File permission errors
- Disk full errors
- Connection cleanup even on exceptions
- Concurrent access (SQLite default locking)

### 3.2 Query Failures
**Issue:** Database operations could fail silently or crash.

**Locations:**
- All database query functions in both CLI and API

**Remediation:**
- All queries use parameterized statements (SQL injection prevention)
- Try/except blocks with proper error messages
- Transaction commits explicit
- Rowcount checked for update/delete operations

**Edge cases handled:**
- Non-existent records (404 in API, False return in models)
- Constraint violations (IntegrityError caught and reported)
- Concurrent write conflicts (OperationalError)
- Empty result sets (handled gracefully)

---

## 4. API-Specific Edge Cases

### 4.1 HTTP Request Validation
**Issue:** Invalid request payloads could crash the API.

**Locations:**
- `retro-games-api/app.py` - All endpoint handlers

**Remediation:**
- Pydantic models validate all inputs automatically
- FastAPI returns 422 Unprocessable Entity for validation errors
- Clear error messages returned to client

**Edge cases handled:**
- Missing required fields (422 error)
- Wrong data types (422 error)
- Out-of-range values (422 error)
- Malformed JSON (400 error from FastAPI)
- Extra unexpected fields (ignored by Pydantic)

### 4.2 Resource Not Found
**Issue:** Requests for non-existent resources could cause crashes.

**Locations:**
- `retro-games-api/app.py` - `get_game()`, `update_game()`, `delete_game()`

**Remediation:**
- Explicit None checks after database queries
- 404 status code with descriptive messages
- Consistent error response format

**Edge cases handled:**
- Non-existent game IDs
- Invalid ID formats (type validation by FastAPI)
- Deleted resources (returns 404)

---

## 5. Concurrency Edge Cases

### 5.1 SQLite Locking
**Issue:** SQLite is not designed for high-concurrency writes.

**Current Status:** 
- ⚠️ **Partial handling** - Timeout set but no retry logic
- Single-threaded application mitigates most issues
- FastAPI may handle concurrent requests

**Recommendations for production:**
- Add retry logic with exponential backoff
- Consider PostgreSQL/MySQL for high-concurrency scenarios
- Implement optimistic locking for updates
- Add connection pooling

**Edge cases to consider:**
- Multiple CLI processes writing simultaneously
- API handling concurrent write requests
- Long-running transactions blocking others

---

## 6. Type Conversion Edge Cases

### 6.1 Numeric Conversions
**Issue:** Invalid numeric strings could cause ValueError.

**Locations:**
- `retro-games-cli/main.py` - `import_csv()` function (release_year parsing)

**Remediation:**
- Try/except blocks around `int()` conversions
- Invalid rows skipped during CSV import
- CLI argparse handles type validation automatically

**Edge cases handled:**
- Non-numeric strings (caught and skipped)
- Floating point numbers (truncated by int())
- Scientific notation (accepted by int() in some cases)
- Empty strings (caught and skipped)

### 6.2 Date Conversions
**Issue:** Date serialization/deserialization could fail.

**Locations:**
- `retro-games-api/models.py` - All model methods
- `retro-games-cli/main.py` - `validate_date()` function

**Remediation:**
- `.isoformat()` method used for date→string conversion
- `date.fromisoformat()` used for string→date validation
- Pydantic handles date parsing in API automatically

**Edge cases handled:**
- Invalid ISO formats (rejected)
- Timezone information (not supported, UTC assumed)
- Date vs datetime distinction (date objects only)

---

## 7. Empty/Null Value Edge Cases

### 7.1 Optional Fields
**Issue:** None/null values could cause AttributeError or database errors.

**Locations:**
- `condition` field throughout application

**Remediation:**
- Explicit Optional[str] type hints
- None checks before string operations
- Database allows NULL for condition column
- CSV export handles None → empty string conversion

**Edge cases handled:**
- None values (valid for condition field)
- Empty strings (converted to None in CLI)
- Whitespace-only strings (converted to None)
- Missing CSV columns (defaulted to None)

### 7.2 Empty Collections
**Issue:** Operations on empty result sets could fail.

**Locations:**
- `retro-games-cli/main.py` - `list_games()` display logic
- `retro-games-api/app.py` - `list_games()` endpoint

**Remediation:**
- Explicit check for empty results before display
- Empty arrays returned (not null) in API
- "No games found" message in CLI

**Edge cases handled:**
- Empty database (displays message)
- Empty list returned from API (valid JSON array)
- No search results (handled gracefully)

---

## 8. Display and Formatting Edge Cases

### 8.1 Table Formatting
**Issue:** Long strings or special characters could break CLI table layout.

**Locations:**
- `retro-games-cli/main.py` - `list_games()` display logic

**Current Status:**
- ✅ Dynamic column widths calculated
- ✅ Proper string justification
- ⚠️ Very long strings may cause terminal wrapping

**Edge cases handled:**
- Variable-length game titles (dynamic sizing)
- Empty condition fields (displayed as empty)
- Special characters (passed through as-is)

**Potential improvements:**
- Truncate extremely long strings with ellipsis
- Handle special characters that break terminal display
- Support different terminal widths

---

## 9. Security Edge Cases

### 9.1 SQL Injection Prevention
**Status:** ✅ **FULLY REMEDIATED**

**Locations:**
- All database queries in both CLI and API

**Remediation:**
- 100% parameterized queries (no string concatenation)
- User input never interpolated into SQL statements
- Database-level CHECK constraints as defense-in-depth

**Attack vectors prevented:**
- Malicious title/platform/condition inputs
- Special characters in user input (', ", --, ;)
- UNION-based injection attempts
- Boolean-based blind injection
- Time-based blind injection

### 9.2 Path Traversal
**Issue:** User-specified file paths could access sensitive files.

**Locations:**
- `retro-games-cli/main.py` - `import_csv()` and `export_csv()` commands

**Current Status:**
- ⚠️ **Minimal protection** - relies on filesystem permissions
- No explicit path validation/sanitization

**Recommendations:**
- Validate paths are within expected directories
- Reject paths with `..` components
- Use absolute paths with proper validation
- Consider restricting to specific directories

---

## 10. Error Handling Consistency

### 10.1 Exception Propagation
**Philosophy:** Fail fast, fail clear.

**Strategy:**
- Validation errors raised immediately with clear messages
- Database errors caught and re-raised with context
- HTTP errors use appropriate status codes
- CLI errors printed to stderr with exit codes

**Consistency rules:**
- ValueError for application-level validation failures
- sqlite3.Error for database-specific errors
- HTTPException for API errors with proper status codes
- argparse.ArgumentTypeError for CLI argument validation

---

## Testing Recommendations

### Unit Tests Needed:
1. Test all validation functions with boundary values
2. Test CSV import with malformed files
3. Test database operations with concurrent access
4. Test API endpoints with invalid payloads
5. Test string length limits at boundaries (499, 500, 501 chars)

### Integration Tests Needed:
1. Test full CSV import→list→export cycle
2. Test API CRUD operations end-to-end
3. Test CLI and API interoperability with shared database
4. Test error recovery scenarios

### Load Tests Needed:
1. Test concurrent API requests
2. Test large CSV file imports
3. Test database with thousands of records

---

## Summary of Remediations Applied

| Edge Case | Location | Status | Mitigation |
|-----------|----------|--------|------------|
| String length limits | CLI + API | ✅ Fixed | Max length validation added |
| Year boundaries | CLI | ✅ Fixed | Range validation (1970-2030) |
| Whitespace-only condition | CLI | ✅ Fixed | Empty string detection |
| Database timeout | API models | ✅ Fixed | 30s timeout configured |
| CSV file not found | CLI | ✅ Fixed | Explicit existence check |
| CSV encoding errors | CLI | ✅ Fixed | UTF-8 with error replacement |
| Better error messages | CLI | ✅ Fixed | sqlite3.Error with context |
| Missing documentation | All | ✅ Fixed | This document created |

---

## Version History

- **v1.0 (2026-01-17)**: Initial documentation after edge case remediation
  - Added length limits to title/platform fields
  - Added year range validation to CLI
  - Added whitespace-only string handling
  - Added database connection timeout
  - Added CSV file existence validation
  - Enhanced error messages throughout
  - Created comprehensive documentation

---

## Future Improvements

1. **Add retry logic** for database lock timeouts
2. **Implement logging** for skipped CSV rows
3. **Add path traversal protection** for file operations
4. **Implement rate limiting** in API
5. **Add database migrations** support
6. **Consider connection pooling** for API
7. **Add comprehensive test suite**
8. **Implement request validation logging** in API
9. **Add metrics/monitoring** for production use
10. **Consider async database operations** in API

---

*Document maintained by: Development Team*  
*Last updated: 2026-01-17*

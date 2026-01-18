---
name: SQL Injection Prevention
description: This prompt is used to help prevent SQL injection vulnerabilities in code.
agent: agent
---

This project currently uses and SQLite database. Please review the provided code for any potential SQL injection vulnerabilities. If any are found, suggest and implement appropriate mitigation strategies, such as using parameterized queries or prepared statements.

Ensure that all database interactions follow best practices for security and data integrity. If necessary, refactor the code to enhance its resilience against SQL injection attacks while maintaining its original functionality.

Please follow python best practices and ensure that any areas of concern are clearly documented with comments explaining the changes made and the reasons behind them.
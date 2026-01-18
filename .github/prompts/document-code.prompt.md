---
name: Document Code
description: This prompt is used to add comprehensive documentation to the provided code
agent: agent
---

Please ensure that all functions, classes, and methods in the provided code are thoroughly documented ALONGSIDE THE CODE THEY ARE EXPLAINING. THIS MEANS THE CODE FILES NEED TO CONTAIN THE DOCUMENTATION; use appropriate docstrings or comments. The documentation should include descriptions of parameters, return values, exceptions raised, and any relevant examples to help users understand how to use the code effectively.

Please use python best practices for documentation, such as adhering to the NumPy or Google style guides for docstrings. If there are any complex sections of code, please add inline comments to clarify their purpose and functionality.

Additionally, create a separate markdown file named `DOCUMENTATION.md` IF IT DOES NOT ALREADY EXIST. The DOCUMENTATION.md file needs to provides an overview of the entire codebase. This file should include:

1. A high-level summary of the codebase's purpose and functionality.
2. Instructions on how to set up and run the code.
3. Examples of common use cases.
4. Any dependencies or prerequisites needed to work with the code.
5. Contribution guidelines for future developers.
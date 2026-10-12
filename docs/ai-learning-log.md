# CampusFlow AI Learning Log

## 1. Purpose

This document records how the CampusFlow team used AI assistance during planning, implementation, testing, documentation, and debugging.

The purpose was not simply to obtain working code. It was to understand the implementation, evaluate suggestions, verify behavior through tests and manual checks, and make informed decisions about the final product.

AI-generated suggestions were treated as proposals that required review and verification, not as automatically correct answers.

## 2. Engineer A — Regina Adikwu

### Interaction 1: Implementing and validating ticket creation

**Task or question**

How can CampusFlow create helpdesk tickets while validating the required fields and calculating priority according to the agreed rules?

**AI assistance**

AI helped develop the ticket creation and priority calculation functions. The suggested implementation included validation for ticket titles, categories, urgency, affected-user counts, ticket identifiers, and priority calculation.

**What I learned**

I learned that validation should happen before a ticket is added to the collection. This helps prevent invalid input from changing application state.

I also learned that priority rules must be evaluated in the correct order. For example, high urgency combined with at least 10 affected users must result in critical priority, rather than merely high priority.

Another lesson was that tests should check not only successful operations but also invalid inputs and whether failed operations leave the original data unchanged.

**Independent verification and evidence**

I ran the ticket tests using:

`python3 -m unittest tests.test_tickets -v`

The observed result was 12 tests passing.

Later, the complete suite also passed all 30 tests using:

`python3 -m unittest discover -s tests -v`

These results support the tested behavior, although they do not prove that every possible edge case has been covered.

### Interaction 2: Implementing JSON persistence and storage validation

**Task or question**

How can CampusFlow load and save ticket records reliably, reject malformed data, and preserve existing data when a save operation fails?

**AI assistance**

AI suggested JSON loading and saving functions, ticket-record validation, error handling, and atomic saving using a temporary file followed by file replacement.

AI also helped create tests for missing files, valid save-and-load round trips, malformed JSON, invalid records, duplicate ticket IDs, and invalid saves.

**What I learned**

I learned that storing data is not just a matter of writing a list to a file. The application must also validate data when loading it, handle file errors clearly, and avoid replacing valid saved data with invalid data.

I also learned the importance of testing persistence separately from the functions that create and modify tickets.

**Independent verification and evidence**

I ran:

`python3 -m unittest tests.test_storage -v`

The observed result was 7 tests passing.

I then created a ticket through the command-line application, exited, restarted the application, and listed the tickets again.

Ticket `T001`, titled `wi-fi unavailable`, was still present. It had urgency `high`, 12 affected users, priority `critical`, status `open`, and no assigned staff member.

This provided manual evidence that the tested application could save a ticket and load it again after restarting.

### Interaction 3: Reviewing the CLI, reports, and documentation

**Task or question**

How can the individual ticket, workflow, storage, and reporting functions be brought together into an interactive command-line application, and how can the project be documented for another developer?

**AI assistance**

AI helped develop the command-line menu, connect the application to the ticket and workflow functions, display reports, and prepare a README explaining setup, usage, priority rules, persistence, tests, and limitations.

**What I learned**

I learned that implementing individual functions is only part of building a product. The application also needs a usable entry point, understandable prompts, error handling, persistent storage, automated tests, and documentation.

I also learned that documentation must describe the actual project. Giving a file a suitable commit message does not mean that its contents have been reviewed or corrected.

**Independent verification and evidence**

I ran the complete test suite with:

`python3 -m unittest discover -s tests -v`

The observed result was 30 tests passing.

I manually created a ticket and checked the unresolved work queue and report. The application displayed one total ticket, one open ticket, and one critical ticket.

I also checked Git status and the commit history to confirm the state of the repository.

**Independent correction and improvement**

During the collaboration, I noticed that the README had not actually been reviewed and corrected as I had intended. I raised this issue rather than assuming that a proposed commit message meant the documentation was complete.

I also asked about `campusflow/__init__.py` when I noticed it had not been addressed explicitly.

These decisions reminded me to compare AI assistance against the original task requirements instead of accepting an answer merely because it sounds complete.

## 3. Engineer B — Regina

### Introduction

During the development of CampusFlow, AI was used as a programming assistant to help generate implementation ideas, develop code, explain technical decisions, and prepare tests and documentation.

The goal was to use AI to accelerate development while learning how the application works and checking whether the suggested implementation satisfies the project requirements.

### Interaction 1: Ticket workflow and status management

**Task or question**

How can CampusFlow manage ticket assignment, status transitions, reopening resolved tickets, and the order of the unresolved work queue?

**AI assistance**

AI helped develop the workflow functions for assigning tickets, changing ticket status, reopening resolved tickets, and sorting unresolved tickets by priority and numeric ticket ID.

It also helped develop automated tests for valid and invalid workflow operations.

**What I learned**

I learned that a ticket management system needs clear rules governing how tickets change state.

For example, a ticket should not move to `in_progress` until it has been assigned. A resolved ticket should not be modified until it has been explicitly reopened. Assigning a ticket should not automatically change its status.

I also learned that sorting a work queue requires a defined priority order and a consistent secondary ordering rule.

**Verification and evidence**

The workflow test suite was run with:

`python3 -m unittest tests.test_workflow -v`

The observed result was 8 tests passing.

The complete test suite later reported 30 tests passing.

### Interaction 2: Ticket storage and data validation

**Task or question**

How can CampusFlow save ticket records in JSON, load them after restarting the application, and handle invalid or malformed saved data?

**AI assistance**

AI helped develop the storage implementation, including validation of ticket records, handling missing files, reporting malformed JSON, checking duplicate ticket identifiers, and saving records through a temporary file followed by replacement.

AI also helped prepare automated tests for storage behavior and error handling.

**What I learned**

I learned that persistence involves more than writing data to a file. An application must also check the data it loads, handle failures clearly, and avoid replacing valid saved data with invalid records.

I also learned why testing both successful and unsuccessful storage operations matters.

**Verification and evidence**

The storage test suite was run with:

`python3 -m unittest tests.test_storage -v`

The observed result was 7 tests passing.

The full test suite later reported 30 tests passing.

During manual testing, a ticket was created, the application was exited and restarted, and the ticket was displayed again. This provided evidence that ticket data persisted across application restarts.

### Interaction 3: Reports, command-line interface, and integration

**Task or question**

How can the ticket, workflow, storage, and reporting functions be integrated into a command-line application that users can operate?

**AI assistance**

AI helped develop the report-generation functions, the interactive menu in `main.py`, and the documentation describing how to set up, run, and test CampusFlow.

The report functions summarize the total number of tickets and their distribution by status and priority.

**What I learned**

I learned that individual functions must work together to form a usable application. The application needs a clear entry point, useful prompts, error handling, persistent storage, and reports that accurately summarize ticket data.

I also learned that automated tests and manual checks serve complementary purposes: tests verify specific behaviors, while manual testing helps confirm that users can operate the integrated application.

**Verification and evidence**

The complete test suite was run using:

`python3 -m unittest discover -s tests -v`

The observed result was 30 tests passing.

During manual testing, the application displayed the unresolved work queue and a report showing one total ticket, one open ticket, and one critical ticket.

### Independent review and learning

**This section must reflect Wisdom's actual experience before submission.**

To complete this section, I reviewed an AI-generated suggestion and independently identified the following issue or improvement:

- **Suggestion reviewed:** [Describe the actual AI-generated suggestion.]
- **My observation:** [Explain what I questioned, corrected, improved, or rejected.]
- **Reason:** [Explain why the original suggestion needed review.]
- **Action taken:** [Describe the change or decision I made.]
- **Evidence:** [Include the relevant test result, code change, review comment, or command output.]

This experience taught me that AI-generated code should be evaluated against requirements and verified rather than accepted automatically.

### Reflection

My main lesson from this project is that AI can help accelerate software development, but developers remain responsible for understanding, reviewing, and verifying the resulting code.

Testing, manual verification, and reviewing the implementation against the requirements helped establish confidence in the observed behavior of CampusFlow.

Going forward, I should continue to ask why a solution works, examine edge cases, and make sure that I understand the code and decisions I contribute to a project.


## 4. Team reflection

The CampusFlow work demonstrated that AI can accelerate implementation and help explain unfamiliar programming concepts, but its suggestions still require human judgment.

Testing helped us evaluate behavior rather than relying only on explanations. Manual testing helped us verify how the components worked together. Reviewing documentation and Git history also showed that completing the code is not the same as completing every project requirement.

One important lesson was that a passing test suite is evidence of the behavior covered by those tests, not proof that the application is completely free of defects.

The team should continue to verify requirements, review generated code, document genuine decisions, and ensure that each engineer understands the contributions recorded under their name.

## 5. Evidence summary

Evidence observed during the work included:

- 12 passing ticket tests.
- 8 passing workflow tests.
- 7 passing storage tests.
- 3 passing report tests.
- 30 passing tests in the complete suite.
- A manually created ticket that remained available after restarting the application.
- A work queue displaying the unresolved ticket with critical priority.
- A report showing the expected ticket, status, and priority counts.
- Git status and commit-history output showing the state of the repository.

These results document the checks actually performed during this development session. Additional requirements, including the team's pull requests and reciprocal reviews, must be verified separately before the project is declared fully compliant.

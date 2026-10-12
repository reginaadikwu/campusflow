# CampusFlow — Design Decisions

**Status:** Updated design document — implementation details should be verified against the final code  
**Engineers:** Regina Adikwu (Engineer A) and Regina (Engineer B)  
**Agreement date:** 11 October 2026

## 1. Purpose and Architecture

CampusFlow is a Python command-line helpdesk ticket management application. It enables users to create and manage support tickets, assign tickets to staff, track ticket status, view unresolved work, and generate summary reports.

The application uses JSON for persistent storage and Python's built-in `unittest` framework for automated testing. It is designed to use the Python standard library without requiring an external database or web framework.

The project is organized into the following modules:

- `main.py` — provides the interactive command-line interface and coordinates application operations.
- `campusflow/tickets.py` — handles ticket creation, input validation, and priority calculation.
- `campusflow/workflow.py` — handles assignment, status transitions, reopening, and unresolved work queue operations.
- `campusflow/storage.py` — handles JSON loading, validation of persisted records, and saving tickets.
- `campusflow/reports.py` — calculates ticket totals and summaries grouped by status and priority.
- `tests/` — contains automated tests for the application's behaviour.
- `docs/` — contains project design decisions and AI learning logs.

Each module should have a clear responsibility. The command-line interface should coordinate operations rather than duplicate business rules implemented in the application modules.

## 2. Ticket Data Structure

Tickets are represented as Python dictionaries, and the application's ticket collection is managed as a list of dictionaries.

Each ticket contains these eight fields:

| Field | Purpose |
|---|---|
| `id` | Unique ticket identifier, such as `T001`. |
| `title` | Short description of the reported problem. |
| `category` | Type of issue being reported. |
| `urgency` | Reported urgency level. |
| `affected_users` | Number of users affected. |
| `priority` | Priority calculated from urgency and affected users. |
| `status` | Current state of the ticket. |
| `assigned_to` | Staff member assigned to the ticket, or `None`. |

The field names form the agreed ticket data contract. They should remain consistent across ticket creation, workflow operations, persistence, reporting, and tests.

## 3. Input Validation

The application validates ticket input before accepting a new ticket.

- Titles must not be blank or contain only whitespace.
- Categories must be `Network`, `Hardware`, `Software`, or `Other`.
- Urgency must be `low`, `medium`, or `high`.
- Valid category and urgency inputs are normalized consistently.
- `affected_users` must be a positive integer. Booleans, zero, negative numbers, decimals, and text are rejected.
- Newly created tickets begin with status `open` and `assigned_to` set to `None`.

Invalid input must be rejected clearly. A failed operation must not leave the ticket collection in a partially updated state.

## 4. Priority Calculation

Ticket priority is calculated from urgency and the number of affected users. The rules are evaluated in the following order:

1. High urgency **and** at least 10 affected users → `critical`.
2. Otherwise, high urgency **or** at least 10 affected users → `high`.
3. Otherwise, medium urgency **or** at least 3 affected users → `medium`.
4. Otherwise → `low`.

The order is important because the first rule is more specific than the rules that follow it.

Priority is calculated by the ticket business logic rather than independently reimplemented in the command-line interface or reporting module.

## 5. Ticket Identifiers

Ticket identifiers use the format `T001`, `T002`, `T003`, and so on.

- New identifiers must be unique among existing tickets.
- Existing identifiers must be preserved when tickets are saved and loaded.
- Creating a ticket after loading previously saved tickets must not duplicate an existing identifier.
- Queue ordering must compare the numeric portion of an identifier rather than relying on ordinary alphabetical sorting.

## 6. Workflow and Ticket Mutations

The supported statuses are:

- `open`
- `in_progress`
- `resolved`

The agreed workflow rules are:

- A ticket must be assigned before it can move from `open` to `in_progress`.
- An assigned ticket can progress from `open` to `in_progress` and then to `resolved`.
- Assignment does not automatically change the ticket's status.
- A resolved ticket cannot be modified until it has been explicitly reopened.
- Reopening is an explicit operation, not an automatic side effect of assignment or modification.
- Invalid status transitions and other rejected operations must not partially mutate ticket data.

The workflow module owns assignment and status-transition rules. Ticket creation and validation belong to the ticket module.

These responsibilities should remain separate so that the same business rules apply whether an operation is initiated through the CLI or tested directly.

## 7. Function Contracts and Error Handling

Application modules communicate through Python functions and ordinary Python data structures.

The shared design conventions are:

- Ticket operations work with ticket records and the ticket collection according to their defined function contracts.
- Functions that create or update tickets should make their outcomes clear to the caller.
- Invalid user input and invalid workflow operations must be reported without silently accepting the operation.
- The CLI is responsible for presenting understandable messages to the user.
- Storage failures must be distinguishable from ordinary validation errors so that the application does not treat failed persistence as a successful save.
- Function names, parameters, return values, and exception types must remain consistent between implementation and tests.

The exact function signatures and exception conventions must match the final source code. They should not be documented as settled until they have been checked against the implemented functions.

## 8. JSON Persistence

JSON is the application's persistence format. The storage module owns loading and saving ticket records.

The agreed behaviour is:

- A missing JSON file represents an empty ticket collection.
- Existing ticket data must be preserved across application restarts.
- Loaded records must be validated before being used by the application.
- Malformed JSON must produce a clear error and must not be silently replaced with an empty collection.
- Saving should write to a temporary file and use atomic replacement where supported.
- File-reading and file-writing errors must be handled clearly.
- Saving and reloading must preserve ticket identifiers and the relevant ticket fields.

Storage tests should use temporary directories and files so that test execution does not depend on or damage the application's real ticket data.

## 9. Unresolved Work Queue

The work queue contains unresolved tickets, excluding tickets whose status is `resolved`.

Tickets are ordered by:

1. Priority: `critical`, `high`, `medium`, then `low`.
2. Numeric ticket identifier in ascending order when priorities are equal.

For example, `T002` must appear before `T010` when both have the same priority.

The queue should use the application's established ticket data and priority rules rather than introducing a separate, inconsistent priority calculation.

## 10. Reporting

The reporting module provides a summary of the ticket collection.

Reports include:

- Total number of tickets.
- Ticket counts grouped by status.
- Ticket counts grouped by priority.

Reporting should calculate summaries from the supplied ticket data and should not modify the underlying tickets.

Empty collections must be handled correctly and should produce meaningful zero-count summaries rather than errors.

## 11. Testing Strategy

The project uses Python's built-in `unittest` framework.

The complete test suite is run with:

`python -m unittest discover -s tests -v`

Tests cover:

- Ticket creation and input validation.
- Priority calculation and boundary conditions.
- Ticket assignment and valid or invalid status transitions.
- Explicit reopening and modification restrictions.
- Work queue filtering and ordering.
- JSON persistence, including missing files and malformed data.
- Reporting calculations and empty collections.
- Integration between the command-line interface and application modules where appropriate.

Business logic should be tested directly through functions rather than requiring interactive terminal input for every test. Storage tests should use isolated temporary files.

A test result should only be described as passing when the command has actually been executed and its result observed.

## 12. Team Responsibilities

### Regina Adikwu — Engineer A

- Ticket creation and input validation.
- Priority calculation.
- Tests in `tests/test_tickets.py`.

### Regina — Engineer B

- Ticket assignment and status transitions.
- Reopening and unresolved work queue.
- Tests in `tests/test_workflow.py`.

### Shared responsibilities

- JSON storage and reporting integration.
- Application integration.
- Meaningful code contributions and automated tests.
- Reviewing each other's work.
- Documentation and final verification.

AI assistance may support either engineer, but each engineer remains responsible for understanding, verifying, and being able to explain their own contributions. The project history, tests, and reviews should provide truthful evidence of the work completed by each person.

## 13. Git Collaboration and Integration

The `main` branch is the reviewed integration branch.

The existence of code on GitHub alone does not establish that the required reviews or branch workflow were completed.

The thing is that i work it out my self 

## 14. Reviewing and Updating Decisions

This document records the team's intended design and the implementation details that need to be confirmed against the final source code.

If implementation differs from a recorded decision, the team should determine whether the code or the documented decision needs to change. Any agreed change should be reflected in the relevant source code, tests, and documentation.
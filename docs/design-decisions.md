# CampusFlow — Design Decisions

**Status:** Agreed by both engineers  
**Engineers:** Regina (Engineer A) and Wisdom (Engineer B)  
**Agreement date:** 11 October 2026

This document records the shared architecture and technical decisions for CampusFlow. Both engineers have verbally agreed to the proposed design.

## 1. Project Architecture

CampusFlow is a Python command-line helpdesk ticket management application. It will use JSON for persistence and Python's built-in `unittest` framework for testing.

The project will use the following structure:

- `main.py` — command-line interface and application coordination.
- `campusflow/tickets.py` — ticket creation, input validation, and priority calculation.
- `campusflow/workflow.py` — ticket assignment, status transitions, reopening, and unresolved work queue.
- `campusflow/storage.py` — JSON loading and saving.
- `campusflow/reports.py` — ticket totals and status and priority summaries.
- `tests/` — automated tests.
- `docs/` — design decisions and AI learning logs.

## 2. Ticket Data Structure

Each ticket will be represented by a Python dictionary containing exactly these required fields:

- `id`
- `title`
- `category`
- `urgency`
- `affected_users`
- `priority`
- `status`
- `assigned_to`

Tickets will be managed as a list of dictionaries.

## 3. Ticket Validation

- Titles must not be blank.
- Categories must be `Network`, `Hardware`, `Software`, or `Other`.
- Urgency must be `low`, `medium`, or `high`.
- `affected_users` must be a positive integer. Booleans, zero, negative numbers, decimals, and text must be rejected.
- Valid category and urgency inputs will be normalized consistently.
- New tickets will start with status `open` and `assigned_to` set to `None`.

## 4. Priority Calculation

Priority rules will be evaluated in this exact order:

1. High urgency AND at least 10 affected users → `critical`.
2. Otherwise, high urgency OR at least 10 affected users → `high`.
3. Otherwise, medium urgency OR at least 3 affected users → `medium`.
4. Otherwise → `low`.

## 5. Ticket Identifiers

Ticket IDs will use the format `T001`, `T002`, and so on.

New IDs must be unique across all loaded tickets. Existing IDs must be preserved when tickets are saved and loaded.

## 6. Workflow Rules

- Supported statuses are `open`, `in_progress`, and `resolved`.
- Tickets must be assigned before moving to `in_progress`.
- Assignment does not automatically change ticket status.
- Resolved tickets cannot be modified until explicitly reopened.
- Invalid operations must not partially mutate ticket data.
- Reopening must be an explicit operation.

## 7. Unresolved Work Queue

The work queue will contain unresolved tickets sorted by:

1. Priority descending: `critical`, `high`, `medium`, `low`.
2. Numeric ticket ID ascending when priorities are equal.

## 8. JSON Persistence

- A missing JSON file represents an empty ticket collection.
- Malformed JSON must produce a clear error and must not be silently overwritten.
- Loaded ticket records must be validated.
- Saving should use a temporary file and atomic replacement where supported.
- File I/O errors must be handled clearly.
- Ticket records and identifiers must persist across application restarts.

## 9. Reporting

Reports will include:

- Total number of tickets.
- Counts grouped by status.
- Counts grouped by priority.

## 10. Testing

Tests will use Python's built-in `unittest` framework.

The test suite will be run with:

`python -m unittest discover -s tests -v`

Tests will cover normal operations, invalid inputs, priority boundaries, workflow restrictions, queue ordering, JSON persistence, and reporting.

## 11. Team Responsibilities

**Regina — Engineer A**
- Ticket creation and validation.
- Priority calculation.
- Tests in `tests/test_tickets.py`.

**Wisdom — Engineer B**
- Ticket assignment and status transitions.
- Reopening and unresolved work queue.
- Tests in `tests/test_workflow.py`.

**Shared responsibilities**
- JSON storage and reporting integration.
- Application integration.
- Code review and testing.
- Documentation and GitHub collaboration.

Function signatures and detailed return/error conventions will be confirmed before implementation.

## 12. Review and Changes

Both engineers have verbally agreed to this proposed architecture and these core rules. Detailed function contracts remain to be finalized.

Any later design changes must be discussed, recorded, and reflected in the relevant tests.

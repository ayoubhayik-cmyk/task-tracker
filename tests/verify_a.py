"""
Verification A: run with `python -m tests.verify_a`
Every line should print PASS. If any line prints FAIL, fix app/models.py
(or app/storage.py) before moving on to Part 2.2.
"""

from pydantic import ValidationError

from app.models import TaskCreate, TaskPriority, TaskStatus, TaskUpdate

results: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    results.append((name, condition))


# 1. Whitespace title rejected
try:
    TaskCreate(title="   ")
    check("1. Whitespace title rejected", False)
except ValidationError:
    check("1. Whitespace title rejected", True)

# 2. Empty title rejected
try:
    TaskCreate(title="")
    check("2. Empty title rejected", False)
except ValidationError:
    check("2. Empty title rejected", True)

# 3. Title over 200 characters rejected
try:
    TaskCreate(title="x" * 201)
    check("3. Title over 200 characters rejected", False)
except ValidationError:
    check("3. Title over 200 characters rejected", True)

# 4. Defaults applied: status ToDo, priority Medium, empty description
task = TaskCreate(title="Valid task")
check(
    "4. Defaults applied (ToDo/Medium/empty description)",
    task.status == TaskStatus.TODO
    and task.priority == TaskPriority.MEDIUM
    and task.description == "",
)

# 5. Extra field rejected on TaskCreate
try:
    TaskCreate(title="Valid task", extra_field="nope")
    check("5. Extra field rejected on TaskCreate", False)
except ValidationError:
    check("5. Extra field rejected on TaskCreate", True)

# 6. id rejected on TaskCreate
try:
    TaskCreate(title="Valid task", id="123")
    check("6. id rejected on TaskCreate", False)
except ValidationError:
    check("6. id rejected on TaskCreate", True)

# 7. created_at rejected on TaskUpdate
try:
    TaskUpdate(created_at="2024-01-01T00:00:00Z")
    check("7. created_at rejected on TaskUpdate", False)
except ValidationError:
    check("7. created_at rejected on TaskUpdate", True)

# 8. Invalid status rejected
try:
    TaskCreate(title="Valid task", status="Archived")
    check("8. Invalid status rejected", False)
except ValidationError:
    check("8. Invalid status rejected", True)


def main() -> None:
    for name, passed in results:
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
    if all(passed for _, passed in results):
        print("\nAll checks passed.")
    else:
        print("\nSome checks failed. Fix app/models.py before continuing.")


if __name__ == "__main__":
    main()

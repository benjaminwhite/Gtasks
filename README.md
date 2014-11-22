# Gtasks: a better Google Tasks Package
[![Latest Version](https://pypip.in/version/gtasks/badge.svg?style=flat)](https://pypi.python.org/pypi/gtasks/)
[![Downloads](https://pypip.in/download/gtasks/badge.svg?style=flat)](https://pypi.python.org/pypi/gtasks/)
## Overview

Gtasks is a Google Tasks python package that emphasizes simplicity and ease of use. If you've ever felt frustrated with Google's [Tasks API Client Library](https://developers.google.com/api-client-library/python/apis/tasks/v1), then Gtasks is for you.

Gtasks allows you to easily manage your tasks and task lists. Everything is represented as python objects. No need to worry about JSON dictionaries, task IDs, RFC3339 datetime formating, or API credentials (unless you want to).

Heres a small sample of what Gtasks can do:

```python
from datetime import date
from gtasks import Gtasks

gt = Gtasks()
scotch = gt.get_list('Scotch')
scotch.new_task('Ardbeg 10 Years Old', date.today())
for task in scotch:
    if 'Highland Park' in task.title:
        task.complete = True
```

## Installation

```bash
pip install gtasks
```

## Features

* Supports Python 2 and 3
* Changes are automatically pushed to Google
* Batch edit mode for modifying multiple task properties at once

##### Tasks:

* Get all or some tasks from any task list
* Create a new task
* Mark a task as complete or incomplete
* Modify a task's title, notes, due date, completion date, or parent
* Delete or undelete a task
* Unhide a task (after it was "cleared")

##### Task Lists:

* Create a new task list
* Modify a task list's title
* Clear a task list's completed tasks
* Get a task list's tasks

## How To's

Here are a few examples on how to accomplish various actions with Gtasks.
All code assumes you've imported Gtasks and have have an intantiated Gtasks object.

```python
from gtasks import Gtasks
gt = Gtasks()
```
##### Get all tasks from your default task list:

```python
tasks = gt.get_tasks()
```

##### Get all tasks from your "Books" task list, with due dates ranging from yesterday to tomorrow

```python
from datetime import date, timedelta
yesterday = date.today() - timedelta(days=1)
tomorrow = date.today() + timedelta(days=1)

tasks = gt.get_tasks(task_list='Books', due_min=yesterday, due_max=tomorrow)
```

##### Check if you've completed all of your tasks for today

```python
from datetime import date
today = date.today()

any_left = gt.get_tasks(include_completed = False, due_min=today, due_max=today, max_results=1)
if any_left:
    print('Still have work to do...')
```

##### Get all tasks that were updated within the last ten minutes

```python
from datetime import datetime, timedelta
ten_mins_ago = datetime.now() - timedelta(minutes=10)

tasks = gt.get_tasks(updated_min=ten_mins_ago)
```

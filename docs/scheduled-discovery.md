# Optional scheduled searches

`find-and-track-jobs` can search on demand. A user may also run the same search criteria on a schedule in ChatGPT scheduled tasks or another scheduler.

A scheduled run should return source-linked leads, not create claims of application or submission. Each lead needs the exact role, organization, primary URL when available, observation date, location, vacancy status, and missing evidence. The user chooses which leads enter the application workflow.

GitHub Actions in this repository runs privacy, schema, and unit checks only. It does not search for a user's jobs or access private candidate files.

OpenAI's scheduled tasks walkthrough explains how an external schedule controls when a task runs: <https://developers.openai.com/training/walkthroughs/scheduled-tasks>

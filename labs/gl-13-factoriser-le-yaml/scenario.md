# Scenario

The `pipeline-craft` pipeline works. It works well, even: a useful cache, jobs
that no longer wait for each other, coverage reported, image published,
deployments in place.

It repeats itself. Two Python jobs declare the same image and the same cache,
word for word. The Docker variables block sits in one place today, and will sit
in three once a second build job arrives.

Nothing is broken, and that is the problem: **duplication breaks nothing until
someone changes one of the copies**. The day somebody updates the image in one
job and forgets the other, the pipeline keeps passing, and two jobs run on two
versions of Python.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Factor it, without changing the behaviour.

Two mechanisms, and their difference is this lab's lesson:

- **`extends:`** merges **jobs**. It is a GitLab mechanism: it understands the
  keys it merges, it goes deep, and it shows in the UI. A **hidden job**, whose
  name starts with a dot, never runs on its own and exists to be extended;
- **a YAML anchor** copies a **fragment**, whatever it is. It is a mechanism of
  the format, not of GitLab: it is resolved before GitLab even reads the file.
  That is what lets you factor a variables block, which is not a job.

The lab asks for both so that the difference registers.

## What the lab checks, and why it looks at your file

This is the **only lab in the series** whose grading reads the
`.gitlab-ci.yml`. Everywhere else it reads the state left on the forge. Here
the state cannot serve as a measure, and that is the lab's very subject:
`extends` and anchors are **resolved** before execution. The configuration
GitLab produces is identical before and after, and that is exactly what you are
asked to ensure.

1. the file carries a **hidden job extended** by at least one job, and an
   **anchor merged** with `<<:`;
2. the behaviour **has not changed**: the jobs still run, none fails, and
   coverage still reaches GitLab.

The second point matters most. A refactoring that changes behaviour is not a
refactoring, it is a regression.

## A trap that only shows afterwards

`coverage:` belongs to the **job**, not to the cache nor the image. If you move
the test job into a hidden one and forget that line, the pipeline stays green
and the coverage vanishes without a word. The lab checks it.

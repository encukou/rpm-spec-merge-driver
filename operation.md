# RPM Spec merge driver operation

This document explains details of rpm-spec-merge-driver's
behavior.


## Assumptions

Your spec file must be UTF-8 encoded
and contain exactly one each of the following lines:

```
Version: ...
Release: ...
%changelog
```

Any number of spaces is allowed after the `:`.

Everything after `%changelog` is entries separated by lines in the
*changelog header* format,
`* Day-of-Week Month Day Year Full Name <email> - Version-Release`.
(This is apparently only one of the possible formats.
If you use another one—patches welcome!)
These header lines don't repeat.
New blocks are only added at the top.
Very old blocks might be removed from the bottom.


## Merging

The driver merges two versions of the spec file,
which are assumed to come from two branches,
which I'll call MAIN and NEW.

The driver cares about the order of the two branches it's merging:
the MAIN branch, whch you *are on* when you call `git merge`,
should be the one that was pushed to dist-git and possibly  built from;
NEW is the one and you're merging in.
NEW can be rebased/squashed on top of MAIN if that's your workflow.

The driver also looks at the *common ancestor*,
or the version where the two branches diverged.
I'll call that the BASE.

The driver adjusts the Version and Release lines and the %changelog section.
All other changes are passed to Git's built-in 3-way merge (`git merge-file`).


### Merging the Version and Release

The merge driver selects the *highest* version from the files being merged,
as determined by `rpmdev-vercmp`.

If MAIN has the highest version,
Release is set to MAIN's release bumped by `rpmdev-bumpspec`.

Otherwise if NEW has the hightest version, Release is set to NEW's release.

Otherwise (BASE has a higher version than any of the two branches),
the driver fails.


### Merging the Changelog

The first non-empty line of BASE's changelog is the TOP.
This line must appear in the changelog of both branches,
otherwise the driver fails.

For each branch (BASE, MAIN, NEW),
everything above the TOP is *new* part and everything below is *old*.

The *old* parts are left to be merged using Git's built-in 3-way merge.
(This can lead to conflicts,
but it also means timestamp fixes or old history deletion
is taken from both the branches.)

The BASE's *new* part must be empty.

The MAIN's *new* part is added as-is.

From NEW, the order of the *new* changelog blocks is reversed,
the header lines are removed,
and the content is added to the beginning of the changelog.
A new header line is added using the author of the original change,
the current date, and the new version and release.
If more changelogs are merged in, the last one in the file
(the first one chronologically) is used.
The current date is overridable using `$CURRENT_DATE` in a format
suitable for Python's `datetime.datetime.fromisoformat`, e.g.
`YYYY-MM-DD`.

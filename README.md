# RPM Spec merge driver

This is a [Git merge driver] for [RPM spec files].

It is designed to be very simple;
it only handles the most common cases of spec file conflicts.
All else is delegated to Git's internal merge driver.

[Git merge driver]: https://git-scm.com/docs/gitattributes#_performing_a_three_way_merge
[RPM spec files]: https://rpm-packaging-guide.github.io/#what-is-a-spec-file

## Usage

After installation (either in a single repo or globally),
simple conflicts in spec files are resolved automatically:
* Release bumps
* Additions to the changelog

If the driver's heuristics fail, Git's standard merge driver
will be used and you will need to handle conflicts as usual.

Details of how the driver works are explained in [operation.md].

[operation.md]: ./operation.md


## Command line usage

The merge driver can be used as a standalone tool.
This should be useful it you're merging something other than Git branches
(but note that you might still need to be in a Git repo).
Call the command with `--help` for details.


## Repo setup

To test stuff out, add the following to `$GIT_DIR/info/attributes`
(usually, `.git/info/attributes`) in your repository:

```
*.spec  merge=rpm-spec
```

To share the config with everybody, add the line to `.gitattributes`
and add it to your your repository.

Everyone who clones the repo (including you)
also needs to do the *Installation* below.
(Git does not use scripts/commands you pulled from the internet,
until you explicitly opt in.)


## Installation

Put `rpm-spec-merge-driver` on your `PATH`
(or use an absolute path for `rpm-spec-merge-driver` below).

Add this section to your Git config:

```
[merge "rpm-spec"]
    name = RPM spec file merge driver
    driver = rpm-spec-merge-driver %O %A %B %L %P
    recursive = text
```

Your Git config is either:

* `$HOME/.gitconfig`, if you want to set this up globally, or
* `$GIT_DIR/config` (usually `.git/config`) for a single repo.

(Note: Adding the section is equivalent to three commands like
`git config [--global] merge.rpm-spec.recursive binary`.)


## Caveats

If you are merging branches with different `Epoch`s,
the driver might misbehave.
Check and fix the result manually.


## Tests

Run `pytest` for the tests.


## Licence

The tool is available under the MIT license, see `LICENSE.MIT`.
May it serve you well.


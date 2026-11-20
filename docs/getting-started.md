# Getting started

From a fresh machine to your first pull request on Vidocq, step by step, on macOS, Linux and
Windows.

The code of Vidocq lives in one repository, the monorepo
[`Vidocq/vidocq`](https://codefloe.com/Vidocq/vidocq): every component, their parent POM and the runtime. The
workspace gathers it with the repositories around it (documentation, site, CI, governance, `erasmus`, `tassis`,
`verne`, the VCU extensions).

Everyone starts as a **contributor**: you propose changes from your own fork of a Vidocq
repository, most often the monorepo. After a period of contributions, the maintainers may invite you to become a
**maintainer**; you then follow the
[maintainer guide](https://codefloe.com/Vidocq/governance/src/branch/main/MAINTAINERS.md) of the
governance repository. Steps 1 to 6 are the same for both; step 7 is for contributors.

The examples use a fictional contributor: **Jane Doe**, Codefloe username **`janedoe`**, email
**`jane.doe@example.com`**. Replace them with yours.

---

## Contents

1. [Your platform](#1-your-platform)
2. [Account, keys and CLA](#2-account-keys-and-cla)
3. [Install the tools](#3-install-the-tools)
4. [Clone the workspace](#4-clone-the-workspace)
5. [Configure Maven for the Vidocq snapshots](#5-configure-maven-for-the-vidocq-snapshots)
6. [Build the monorepo](#6-build-the-monorepo)
7. [Your first contribution, from a fork](#7-your-first-contribution-from-a-fork)
8. [Working with a coding agent](#8-working-with-a-coding-agent)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Your platform

- **macOS** and **Linux**: run the commands as shown.
- **Windows**: work in **WSL 2** (Windows Subsystem for Linux). The workspace tooling (mani
  tasks, git hooks, `mvnw`, TCK scripts) is written for a POSIX shell. In a PowerShell window
  opened with **Run as administrator**:

  ```powershell
  wsl --install -d Ubuntu
  ```

  Restart Windows, open **Ubuntu** from the Start menu and create your Linux user. Then run every
  command of this guide in that Ubuntu terminal, following the Linux (Debian/Ubuntu) variants.
  Keep the workspace in your Linux home (`~/vidocq-workspace`), not under `/mnt/c/`: builds are
  much faster there and the file permissions are right. IntelliJ IDEA and VS Code (with its WSL
  extension) open projects stored in WSL.

---

## 2. Account, keys and CLA

Before anything else, you need a Codefloe account with an SSH key, a GPG key that signs your
commits, and your signature of the Contributor License Agreement (CLA). Every pull request is
checked for all three.

Follow the [one-time setup](https://codefloe.com/Vidocq/governance/src/branch/main/README.md#one-time-setup)
of the governance repository, Steps 1 to 4, then come back here. The CLA (Step 4) can wait until
you are ready to open your first pull request, but not longer: the checks of your pull request
fail until your signature is merged.

---

## 3. Install the tools

| Tool | Why | Version |
|---|---|---|
| Git | version control | 2.34 or later |
| GnuPG | signs your commits | installed in step 2 |
| A Java 25 JDK | builds Vidocq | Eclipse Temurin 25 |
| [mani](https://manicli.com) | clones and drives all the repositories of the workspace | any recent version |

You do not need to install Maven: each repository ships a Maven wrapper (`./mvnw`) that downloads
the version it pins on first use (3.10.0 in the monorepo).

### macOS

With [Homebrew](https://brew.sh):

```bash
brew install git mani
curl -s "https://get.sdkman.io" | bash      # SDKMAN, to install and switch JDKs
```

Open a new terminal, then install Java 25 (next section).

### Linux and Windows (WSL 2)

```bash
sudo apt update && sudo apt install -y git curl zip unzip       # Debian, Ubuntu, WSL 2
sudo dnf install -y git curl zip unzip                          # Fedora
sudo pacman -S --needed git curl zip unzip                      # Arch Linux

curl -sfL https://raw.githubusercontent.com/alajmo/mani/main/install.sh | sh   # mani
curl -s "https://get.sdkman.io" | bash                                         # SDKMAN
```

The mani script asks where to install the binary: by default `~/.local/bin` when that directory
is on your `PATH`, otherwise `/usr/local/bin` (with `sudo`). On Arch Linux, `yay -S mani` works
too. Open a new terminal, then install Java 25.

### Java 25, with SDKMAN (all platforms)

List the Temurin builds and install the latest Java 25 one. At the time of writing it is
`25.0.4.1+1-tem`:

```bash
sdk list java | grep -- "-tem"
sdk install java 25.0.4.1+1-tem
```

Answer `Y` when SDKMAN offers to make it the default. Then check the three tools:

```bash
git --version     # git version 2.34 or later
java -version     # openjdk version "25.0.4..." ... Temurin
mani --version
```

---

## 4. Clone the workspace

The workspace is the root directory of all the Vidocq repositories. It holds what they share:
the rules for humans and coding agents (`AGENTS.md`), the git hooks, the mani configuration
(`mani.yaml`) and these guides.

```bash
cd ~
git clone git@codefloe.com:Vidocq/vidocq-workspace.git
cd vidocq-workspace
mani sync                    # clones every project of mani.yaml into <repo>/main/
mani run -a install-hooks    # makes every repository use the shared git hooks
```

`mani sync` clones each repository in its own `main/` directory. They stay independent git
repositories, ignored by the workspace repository:

```text
vidocq-workspace/
├── AGENTS.md  CLAUDE.md  README.md  mani.yaml  .githooks/  docs/
├── vidocq/
│   └── main/          ← clone of Vidocq/vidocq (the monorepo), on branch main
├── vidocq-docs/
│   └── main/
└── ...
```

The hooks add the `Signed-off-by:` line to each of your commits and refuse a commit without it.
To keep everything up to date later:

```bash
mani run -a sync-all         # fetch and fast-forward every repository
```

The mani commands, the worktrees and the IntelliJ setup are described in
[Working with mani & worktrees](working-with-mani-and-worktrees.md).

---

## 5. Configure Maven for the Vidocq snapshots

Between two releases, the monorepo's modules, its parent `io.vidocq:vidocq-parent` included, are
`-SNAPSHOT` versions. The CI publishes them on every push to `main` to the Vidocq snapshot
repository, `maven.vidocq.dev` (a copy is kept at `maven.bak.vidocq.dev`), and copies them to the
Maven Central snapshot repository every night. A branch build of the monorepo resolves there the
modules it does not rebuild, and `erasmus`, `tassis`, `verne` and the VCU extensions resolve their
parent and the components there. Maven does not search those repositories by default: declare
them in `~/.m2/settings.xml`, as the CI does.

If you have no `~/.m2/settings.xml` yet, create it with this content. If you already have one,
add the `<profile>` to its `<profiles>` and the `<activeProfile>` to its `<activeProfiles>`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings>
  <profiles>
    <profile>
      <id>vidocq-snapshots</id>
      <repositories>
        <repository>
          <id>vidocq-snapshots</id>
          <url>https://maven.vidocq.dev/snapshots</url>
          <releases><enabled>false</enabled></releases>
          <snapshots><enabled>true</enabled></snapshots>
        </repository>
        <repository>
          <id>vidocq-snapshots-bak</id>
          <url>https://maven.bak.vidocq.dev/snapshots</url>
          <releases><enabled>false</enabled></releases>
          <snapshots><enabled>true</enabled></snapshots>
        </repository>
        <repository>
          <id>central-snapshots</id>
          <url>https://central.sonatype.com/repository/maven-snapshots/</url>
          <releases><enabled>false</enabled></releases>
          <snapshots><enabled>true</enabled></snapshots>
        </repository>
      </repositories>
      <pluginRepositories>
        <pluginRepository>
          <id>vidocq-snapshots</id>
          <url>https://maven.vidocq.dev/snapshots</url>
          <releases><enabled>false</enabled></releases>
          <snapshots><enabled>true</enabled></snapshots>
        </pluginRepository>
        <pluginRepository>
          <id>central-snapshots</id>
          <url>https://central.sonatype.com/repository/maven-snapshots/</url>
          <releases><enabled>false</enabled></releases>
          <snapshots><enabled>true</enabled></snapshots>
        </pluginRepository>
      </pluginRepositories>
    </profile>
  </profiles>
  <activeProfiles>
    <activeProfile>vidocq-snapshots</activeProfile>
  </activeProfiles>
</settings>
```

These repositories are public: no credentials are needed. Without them, a build outside the
monorepo stops with `Non-resolvable parent POM ... io.vidocq:vidocq-parent:pom:...-SNAPSHOT`.

---

## 6. Build the monorepo

The monorepo is one Maven build, from its root, with its wrapper. There is no root POM in the
workspace itself.

```bash
cd ~/vidocq-workspace/vidocq/main
./mvnw -ntp clean install -DskipTests      # everything, without the tests: the quickest first build
```

The build ends with `BUILD SUCCESS`. The first run is slower: Maven downloads itself and the
dependencies. On `main` the build covers the whole reactor. On any other branch the
[gitflow-incremental-builder](https://github.com/gitflow-incremental-builder/gitflow-incremental-builder)
extension builds only the modules your branch changed (compared with `origin/main`: fetch first)
and the modules that depend on them, with their tests:

```bash
./mvnw -ntp clean verify                                                      # what the branch changed, and its dependents
./mvnw -ntp -pl vidocq-components/vidocq-components-transport/chappe/chappe-core -am verify   # one module and what it needs
./mvnw -ntp clean verify -Dgib.disable=true                                   # everything
```

Build with `clean`: a stale `target/` directory can hide a failure or invent one. The monorepo's
`README.md` and `AGENTS.md` describe its layout; each component folder (its path is in
`components.json`) has its own `README.md`, `AGENTS.md` and TCK scripts.

**Changing two components together** is one branch and one build: the incremental build rebuilds
and tests every module that depends on what you changed.

**Trying a monorepo change in `erasmus`, `tassis` or `verne`** before it is merged: install the
monorepo into a private local repository, then build the other repository against it with `-nsu`
(no snapshot updates), so that Maven uses your build instead of a published SNAPSHOT. Keep your
own `~/.m2` out of it: a branch installed there would shadow the published SNAPSHOTs for
everything you build next.

```bash
cd ~/vidocq-workspace/vidocq/<branch>
./mvnw -ntp clean install -DskipTests -Dgib.disable=true \
  -Dmaven.repo.local=$HOME/m2-try -Dmaven.repo.local.tail=$HOME/.m2/repository
cd ~/vidocq-workspace/erasmus/main
./mvnw -ntp -nsu clean install \
  -Dmaven.repo.local=$HOME/m2-try -Dmaven.repo.local.tail=$HOME/.m2/repository
```

`maven.repo.local.tail` needs Maven 3.9 or later; every Vidocq wrapper pins one.

---

## 7. Your first contribution, from a fork

Contributors push to their own fork; maintainers skip the fork and push to the Vidocq repository,
as described in the
[maintainer guide](https://codefloe.com/Vidocq/governance/src/branch/main/MAINTAINERS.md).
The example fixes issue #42 of the monorepo, in Chappe, the HTTP server
(`vidocq-components/vidocq-components-transport/chappe`).

1. **Fork the repository.** On [Vidocq/vidocq](https://codefloe.com/Vidocq/vidocq), click
   **Fork**, then **Fork repository**: you get `janedoe/vidocq`.
2. **Add your fork as a remote**, next to `origin` (the Vidocq repository, read-only for you):

   ```bash
   cd ~/vidocq-workspace/vidocq/main
   git remote add fork git@codefloe.com:janedoe/vidocq.git
   ```

3. **Create a branch from the latest `main`**, in a worktree next to `main/` (the directory has
   the name of the branch):

   ```bash
   git fetch origin
   BRANCH=fix/42-header-without-colon BASE=origin/main mani run wt-add -p vidocq
   cd ../fix/42-header-without-colon
   ```

4. **Write the test first**, make it pass, then clean up. Prove it: the incremental build
   rebuilds Chappe and tests every module that depends on it.

   ```bash
   ./mvnw -ntp clean verify
   ```

5. **Commit.** Git signs the commit and the hook adds the `Signed-off-by:` line:

   ```bash
   git add -A
   git commit -m "fix(http): reject a header line without a colon (#42)"
   git log --show-signature -1     # gpg: Good signature from "Jane Doe <jane.doe@example.com>"
   ```

6. **Push to your fork and open the pull request:**

   ```bash
   git push -u fork fix/42-header-without-colon
   ```

   On `https://codefloe.com/janedoe/vidocq`, click **New pull request**, check that it goes
   **into** `Vidocq/vidocq` `main` **from** `janedoe/vidocq` `fix/42-header-without-colon`, and
   describe what the change does and why. The title starts with the tag of each component you
   touch (listed in the monorepo's `components.json`), then the commit-style title:
   `[CHAPPE] fix(http): reject a header line without a colon (#42)`. Put `[WIP]` first while it
   is not ready for review.
7. **Follow the checks and the review.** The checks verify your CLA, your signatures, the title,
   and the build and tests of Chappe and of every module that depends on it. No TCK runs on a
   pull request. They start once a maintainer has
   approved them: Codefloe holds the workflows of a pull request from a fork until then. If
   `main` moves on, rebase and push again; never use the **Update branch** button, it breaks the
   signatures:

   ```bash
   git fetch origin
   git rebase --gpg-sign origin/main
   git push --force-with-lease fork fix/42-header-without-colon
   ```

   When the review is done and the checks are green, a maintainer merges your pull request.

The details, with how to fix each failing check, are in the
[contributor guide](https://codefloe.com/Vidocq/governance/src/branch/main/CONTRIBUTING.md#contribute-from-a-fork).

---

## 8. Working with a coding agent

Open your coding agent at the root of the workspace. Codex reads `AGENTS.md` directly; Claude
Code reads `CLAUDE.md`, which imports `AGENTS.md`, and also gets the shared agents and skills of
`.claude/`. Each repository carries its own `AGENTS.md` too, for an agent started inside
`<repo>/main/`; in the monorepo, so does each component folder.

Your personal Claude Code settings go in `.claude/settings.local.json`, which git ignores. If an
agent helped you write a commit, record it with a `Co-Authored-By:` trailer that names the tool;
you remain the author and the committer.

---

## 9. Troubleshooting

**`Permission denied (publickey)` during `git clone` or `mani sync`.** Your SSH key is not on
your Codefloe account: see Step 1 of the
[governance one-time setup](https://codefloe.com/Vidocq/governance/src/branch/main/README.md#one-time-setup),
then check with `ssh -T git@codefloe.com`.

**`error: gpg failed to sign the data` when you commit.** See the
[troubleshooting of the contributor guide](https://codefloe.com/Vidocq/governance/src/branch/main/CONTRIBUTING.md#troubleshooting).

**`Non-resolvable parent POM ... io.vidocq:vidocq-parent:pom:...-SNAPSHOT`.** Maven does not know
the snapshot repository: see [step 5](#5-configure-maven-for-the-vidocq-snapshots).

**SDKMAN says `java 25-tem is not available` in a repository.** The repositories carry a
`.sdkmanrc` file, which pins the JDK for `sdk env`. If it names a build that SDKMAN no longer
distributes, ignore the message: any Temurin 25 build is fine, and `./mvnw` uses your default
JDK.

**`mani: command not found` after the installation.** The directory of the binary is not on your
`PATH`. Open a new terminal; with the install script, re-run it and choose a directory of your
`PATH` (`echo $PATH` lists them).

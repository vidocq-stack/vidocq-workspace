# Getting started

From a fresh machine to your first pull request on Vidocq, step by step, on macOS, Linux and
Windows.

Everyone starts as a **contributor**: you propose changes from your own fork of a Vidocq
repository. After a period of contributions, the maintainers may invite you to become a
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
6. [Build a first repository](#6-build-a-first-repository)
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
the right version, 3.9.16, on first use.

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
├── chappe/
│   └── main/          ← clone of Vidocq/chappe, on branch main
├── vauban/
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

Between two releases, the repositories depend on each other in `-SNAPSHOT` versions, and the
parent of every repository, `io.vidocq:vidocq-parent`, is a SNAPSHOT too. The CI publishes them
on every push to `main`, in the Maven Central snapshot repository. Maven does not search that
repository by default: declare it in `~/.m2/settings.xml`, as the CI does.

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
          <id>central-snapshots</id>
          <url>https://central.sonatype.com/repository/maven-snapshots/</url>
          <releases><enabled>false</enabled></releases>
          <snapshots><enabled>true</enabled></snapshots>
        </repository>
      </repositories>
      <pluginRepositories>
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

The repository is public: no credentials are needed. Without it, the first build stops with
`Non-resolvable parent POM ... io.vidocq:vidocq-parent:pom:...-SNAPSHOT`.

---

## 6. Build a first repository

Chappe, the HTTP server, depends on no other Vidocq repository: it is a good first build.

```bash
cd ~/vidocq-workspace/chappe/main
./mvnw -ntp clean install
```

The build ends with `BUILD SUCCESS`. The first run is slower: Maven downloads itself and the
dependencies.

Each repository is an independent Maven build: there is no root POM in the workspace. Always
`cd` into the repository you work on, and always build with `clean install`: a stale `target/`
directory can hide a failure or invent one. Each repository's `README.md` and `AGENTS.md`
describe its modules, its TCK scripts and its own rules.

**Changing two repositories together.** To try a change of Chappe in Foy before both are
merged, install Chappe locally, then build Foy with `-nsu` (no snapshot updates), so that Maven
uses your local Chappe instead of a newer one from the snapshot repository:

```bash
cd ~/vidocq-workspace/chappe/main && ./mvnw -ntp clean install
cd ~/vidocq-workspace/foy/main && ./mvnw -ntp -nsu clean install
```

---

## 7. Your first contribution, from a fork

Contributors push to their own fork; maintainers skip the fork and push to the Vidocq repository,
as described in the
[maintainer guide](https://codefloe.com/Vidocq/governance/src/branch/main/MAINTAINERS.md).
The example fixes issue #42 of Chappe.

1. **Fork the repository.** On [Vidocq/chappe](https://codefloe.com/Vidocq/chappe), click
   **Fork**, then **Fork repository**: you get `janedoe/chappe`.
2. **Add your fork as a remote**, next to `origin` (the Vidocq repository, read-only for you):

   ```bash
   cd ~/vidocq-workspace/chappe/main
   git remote add fork git@codefloe.com:janedoe/chappe.git
   ```

3. **Create a branch from the latest `main`**, in a worktree next to `main/` (the directory has
   the name of the branch):

   ```bash
   git fetch origin
   BRANCH=fix/42-header-without-colon BASE=origin/main mani run wt-add -p chappe
   cd ../fix/42-header-without-colon
   ```

4. **Write the test first**, make it pass, then clean up. Prove it:

   ```bash
   ./mvnw -ntp clean install
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

   On `https://codefloe.com/janedoe/chappe`, click **New pull request**, check that it goes
   **into** `Vidocq/chappe` `main` **from** `janedoe/chappe` `fix/42-header-without-colon`, and
   describe what the change does and why.
7. **Follow the checks and the review.** The checks verify your CLA, your signatures and the
   build of Chappe and of every repository that depends on it. If `main` moves on, rebase and
   push again; never use the **Update branch** button, it breaks the signatures:

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
`<repo>/main/`.

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

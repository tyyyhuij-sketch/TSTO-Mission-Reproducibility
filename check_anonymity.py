from pathlib import Path
import re


TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".toml",
    ".cff",
    ".csv",
    ".yml",
    ".yaml",
}

# Hard-fail patterns: these are strong identity/deanonymization signals.
EMAIL_RE = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)

ORCID_RE = re.compile(
    r"\b(?:https?://orcid\.org/)?"
    r"\d{4}-\d{4}-\d{4}-[\dX]{4}\b",
    re.IGNORECASE,
)

IDENTIFYING_URL_RE = re.compile(
    r"https?://(?:www\.)?"
    r"(?:github\.com|gitlab\.com|gitee\.com|researchgate\.net|"
    r"scholar\.google\.[^/\s]+|orcid\.org)/[^\s)>\]\"']+",
    re.IGNORECASE,
)

LOCAL_WINDOWS_PATH_RE = re.compile(
    r"\b[A-Za-z]:\\(?:Users|PyCharm|Anaconda)\\",
    re.IGNORECASE,
)

# Advisory-only affiliation signals. They may occur innocently in prose,
# so they are reported for manual review rather than treated as automatic
# failures.
AFFILIATION_WORD_RE = re.compile(
    r"\b(?:University|Institute|Laboratory|Department|School|College|"
    r"Academy|Research Center|Research Centre)\b",
    re.IGNORECASE,
)


def iter_public_text_files(root):
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        # This checker contains the search expressions themselves.
        if path.name == "check_anonymity.py":
            continue

        # Do not scan generated Python caches or Git metadata.
        if "__pycache__" in path.parts or ".git" in path.parts:
            continue

        if path.suffix.lower() in TEXT_SUFFIXES or path.name == "LICENSE":
            yield path


def main():
    root = Path(__file__).resolve().parent

    hard_findings = []
    advisory_findings = []

    # An active CITATION.cff can directly expose author identity.
    active_citation = root / "CITATION.cff"
    if active_citation.exists():
        hard_findings.append(
            "Active CITATION.cff is present during double-anonymous review."
        )

    # The clean reviewer package should not carry a Git history/remote.
    if (root / ".git").exists():
        hard_findings.append(
            ".git metadata is present. Commit authors/remotes can reveal identity."
        )

    for path in iter_public_text_files(root):
        rel = path.relative_to(root)

        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        for label, regex in [
            ("email address", EMAIL_RE),
            ("ORCID identifier", ORCID_RE),
            ("identifying profile/repository URL", IDENTIFYING_URL_RE),
            ("local Windows path", LOCAL_WINDOWS_PATH_RE),
        ]:
            match = regex.search(text)
            if match:
                hard_findings.append(
                    f"{rel}: {label} -> {match.group(0)}"
                )

        if AFFILIATION_WORD_RE.search(text):
            advisory_findings.append(
                f"{rel}: contains a possible affiliation keyword; review manually."
            )

    print()
    print("=== RF-2 DOUBLE-ANONYMOUS PACKAGE CHECK ===")

    if advisory_findings:
        print()
        print("Manual-review advisories:")
        for item in advisory_findings:
            print("  -", item)
    else:
        print("Manual-review advisories      = 0")

    if hard_findings:
        print()
        print("HARD ANONYMITY FINDINGS:")
        for item in hard_findings:
            print("  -", item)

        raise AssertionError(
            "RF-2 anonymity check FAILED. Remove the identifying material "
            "before reviewer-facing distribution."
        )

    print()
    print("Email addresses               = 0")
    print("ORCID identifiers             = 0")
    print("Identifying profile URLs      = 0")
    print("Local Windows paths           = 0")
    print("Active CITATION.cff           = absent")
    print("Git metadata (.git)           = absent")
    print()
    print(
        "IMPORTANT MANUAL CHECK: a public repository hosted under an "
        "identifying account can reveal authorship even when file contents "
        "are anonymous."
    )
    print("RF-2 DOUBLE-ANONYMOUS PACKAGE CHECK: PASS")


if __name__ == "__main__":
    main()

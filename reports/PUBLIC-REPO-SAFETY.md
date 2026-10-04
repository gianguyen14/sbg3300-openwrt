# Public repository safety audit

Audit scope: current tracked files, Git-reachable commit/blob history, checked
patches/docs/scripts/configs, ignored artifact locations, and the local RD-1
archive member list. Scan was performed locally; no content was uploaded to an
external scanning service.

## Result

- Git history scanned: all reachable project commits/blobs; no matches for private-key
  PEM headers, common credential assignment fields, GitHub/OpenAI token
  patterns, or colon/hyphen MAC-address patterns.
- The original Git author/committer email was replaced with the account's
  GitHub noreply address across commit metadata and every historical version
  of the checked-in OpenWrt patch mails. Rewritten history preserves the
  commit sequence/tree changes; old refs/reflogs were pruned locally before
  publication.
- Tracked tree: source code written for this project, OpenWrt patches, DTS,
  configs, sanitized reports, and documentation. No firmware, extracted
  rootfs, CFE/NVRAM dump, stock `.ko`, build directory, or calibration blob is
  tracked.
- Working-tree ignored areas include local firmware/rootfs/backups/builds,
  vendor source checkouts, and release artifacts. `.gitignore` excludes them;
  they must remain untracked.
- Local RD-1 archive contains 24 regular files: the SBG3300 initramfs ELF, its
  DTB, project patches/config/docs/reports, and build script. A local pattern
  scan found no private-key, token, MAC-pattern, or credential-assignment
  matches. No stock image, extracted stock binary, or device backup appeared.
  It is not being uploaded because legal/source-completeness review for a
  binary bundle is outside the evidence available here.
- Device/private identifiers: project docs intentionally omit actual MAC,
  serial, credentials, calibration values, and NVRAM content.
- Workstation paths were found in reports and have been replaced with portable
  or relative wording.
- The current `tools/public-safety-scan.py` checks tracked files and all
  reachable Git blobs locally. It prints finding types and paths only, never
  matched values.
- GitHub was not empty: the fetched remote had two commits containing a README
  and Apache-2.0 `LICENSE`, with no firmware or device data. Preserve that
  history and license by a non-force reconciliation; do not overwrite remote
  state.

## Excluded classes

Passwords, PPP/Wi-Fi credentials, tokens/API keys, private keys/certificates,
cookies/sessions, actual MAC/serial identifiers, device calibration, NVRAM/CFE
dumps, firmware images, extracted proprietary firmware trees, stock kernel
modules, full OpenWrt checkout/build outputs, and unreviewed vendor blobs.

## Limitations

Secret scanning is heuristic and is not a legal determination. Review every
new file and Git diff before publishing. The local release archive was not
published. Broadcom family source is documented by provenance/hash but not
included. If new files are added, rerun the scan on current content and Git
history before another push.

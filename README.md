# Sims 4 Mod Doctor — Windows desktop application

This is a real desktop GUI project. GitHub Actions produces a standalone `Sims4ModDoctor.exe` on a Windows runner; the source ZIP itself is **not** an executable.

## Features
- Detects the normal and OneDrive Sims 4 Mods locations; supports browsing elsewhere.
- Scans `.package` DBPF header/index bounds and `.ts4script` ZIP integrity.
- Finds byte-identical duplicate files with SHA-256.
- Quarantines selected files into `The Sims 4/Mod Doctor Quarantine/<batch>` without deleting them.
- Restores selected quarantine batches without overwriting files.
- Offers guided half-folder isolation and JSON report export.

## Build
Create a GitHub repository and upload the contents of this project, **including** `.github/workflows/windows-build.yml`. Open **Actions → Build Windows EXE → Run workflow**, then download the `Sims4ModDoctor-Windows` artifact. Extract it to get `Sims4ModDoctor.exe`. The EXE needs no Python installation or terminal on the user's PC.

## Safety and limits
A package with a valid header can still be incompatible with a game patch. This scanner does **not** guarantee the cause of a startup failure or automatically fix corrupted game files. A 50/50 test moves half the scanned files and requires manually launching the game to observe the outcome. **Do not save a game while custom content is temporarily missing.** Quarantine is outside Mods, but inside the user-data folder. Always back up saves first.

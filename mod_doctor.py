"""Sims 4 Mod Doctor - offline, non-destructive Windows mod diagnostics."""
import hashlib
import traceback
import json
import os
import shutil
import struct
import threading
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP = 'Sims 4 Mod Doctor'
VALID_EXT = {'.package', '.ts4script'}

def default_mods():
    home = Path.home()
    options = [home / 'Documents' / 'Electronic Arts' / 'The Sims 4' / 'Mods', home / 'OneDrive' / 'Documents' / 'Electronic Arts' / 'The Sims 4' / 'Mods']
    return next((p for p in options if p.is_dir()), options[0])

def inspect_package(path):
    size = path.stat().st_size
    if size < 96:
        return 'ERROR', 'Package too small for a DBPF header'
    with path.open('rb') as f:
        header = f.read(96)
        if header[:4] != b'DBPF':
            return 'ERROR', 'Missing DBPF signature'
        major, minor = struct.unpack_from('<II', header, 4)
        if major not in (1, 2):
            return 'WARNING', f'Unexpected DBPF version {major}.{minor}'
        # DBPF index fields: entry count at 0x24, index offset at 0x28,
        # index size at 0x2C. Some Sims 4 packages use 64-bit index offset at 0x40.
        count = struct.unpack_from('<I', header, 0x24)[0]
        off32 = struct.unpack_from('<I', header, 0x28)[0]
        index_size = struct.unpack_from('<I', header, 0x2C)[0]
        off64 = struct.unpack_from('<Q', header, 0x40)[0]
        offsets = [o for o in (off32, off64) if o and o < size]
        if count == 0:
            return 'WARNING', 'DBPF package has zero indexed resources'
        if not offsets:
            return 'ERROR', 'Resource index offset is outside file'
        if index_size and not any(o + index_size <= size for o in offsets):
            return 'ERROR', 'Resource index extends beyond file'
        if size < 1024:
            return 'WARNING', f'Unusually small package ({size} bytes); inspect before installing'
    return 'OK', f'DBPF {major}.{minor}; {count} indexed resources'

def inspect_script(path):
    if not zipfile.is_zipfile(path):
        return 'ERROR', 'Not a valid ZIP-based ts4script archive'
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if not names:
                return 'ERROR', 'Empty script archive'
            for member in z.infolist():
                if member.flag_bits & 1:
                    return 'WARNING', 'Encrypted ZIP entry (game cannot load normally)'
            bad = z.testzip()
            if bad:
                return 'ERROR', f'CRC error in {bad}'
            py = [n for n in names if n.endswith(('.py', '.pyc'))]
            if not py:
                return 'WARNING', 'No Python modules in archive'
            return 'OK', f'{len(py)} Python module(s); ZIP integrity passed'
    except Exception as exc:
        return 'ERROR', f'Cannot read script: {exc}'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def scan(mods, report):
    paths = sorted(p for p in mods.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix.lower() in VALID_EXT)
    results = []
    groups = defaultdict(list)
    for p in paths:
        try:
            status, reason = inspect_package(p) if p.suffix.lower() == '.package' else inspect_script(p)
            size = p.stat().st_size
            checksum = digest(p)
            groups[(size, checksum)].append(len(results))
            results.append({'path': str(p), 'relative': str(p.relative_to(mods)), 'status': status, 'reason': reason, 'bytes': size, 'sha256': checksum})
        except Exception as exc:
            results.append({'path': str(p), 'relative': str(p.relative_to(mods)), 'status': 'ERROR', 'reason': f'Unreadable: {exc}', 'bytes': 0, 'sha256': ''})
    for ids in groups.values():
        if len(ids) > 1:
            for i in ids:
                if results[i]['status'] == 'OK': results[i]['status'] = 'DUPLICATE'
                results[i]['reason'] += f'; exact duplicate ({len(ids)} copies)'
    return results

class Doctor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.geometry('1060x700')
        self.minsize(780, 520)
        self.configure(bg='#101b27')
        self.mods = tk.StringVar(value=str(default_mods()))
        self.status = tk.StringVar(value='Select your Sims 4 Mods folder, then scan.')
        self.rows = []
        self._build()

    def _build(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview', background='#172635', foreground='#eaf3fb', fieldbackground='#172635', rowheight=27)
        style.configure('Treeview.Heading', background='#284158', foreground='white')
        style.map('Treeview', background=[('selected', '#29638c')])
        top = tk.Frame(self, bg='#101b27', padx=18, pady=14)
        top.pack(fill='x')
        tk.Label(top, text='SIMS 4 MOD DOCTOR', bg='#101b27', fg='#f0f7ff', font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        tk.Label(top, text='Offline diagnostics • No files are deleted • Quarantine requires your confirmation', bg='#101b27', fg='#9fb7cb').pack(anchor='w')
        folder = tk.Frame(self, bg='#101b27', padx=18)
        folder.pack(fill='x')
        tk.Entry(folder, textvariable=self.mods, font=('Segoe UI', 10)).pack(side='left', fill='x', expand=True, ipady=5)
        tk.Button(folder, text='Browse', command=self.browse).pack(side='left', padx=6)
        self.scan_btn = tk.Button(folder, text='Scan Mods', command=self.start_scan, bg='#2b8dca', fg='white', padx=16)
        self.scan_btn.pack(side='left')
        frame = tk.Frame(self, bg='#101b27', padx=18, pady=12)
        frame.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(frame, columns=('status', 'file', 'details'), show='headings', selectmode='extended')
        for col, width in [('status', 110), ('file', 350), ('details', 530)]:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=width, minwidth=80, stretch=col != 'status')
        self.tree.tag_configure('ERROR', foreground='#ff9b9b')
        self.tree.tag_configure('WARNING', foreground='#ffd28c')
        self.tree.tag_configure('DUPLICATE', foreground='#b7c9ff')
        self.tree.pack(side='left', fill='both', expand=True)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        scroll.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scroll.set)
        controls = tk.Frame(self, bg='#101b27', padx=18, pady=8)
        controls.pack(fill='x')
        tk.Button(controls, text='Quarantine Selected', command=self.quarantine).pack(side='left', padx=(0, 8))
        tk.Button(controls, text='Restore Quarantine', command=self.restore).pack(side='left', padx=(0, 8))
        tk.Button(controls, text='Export Report', command=self.export).pack(side='left', padx=(0, 8))
        tk.Button(controls, text='Prepare 50/50 Test', command=self.half_test).pack(side='left')
        tk.Label(self, textvariable=self.status, bg='#101b27', fg='#a9c5d9', anchor='w', padx=18, pady=10).pack(fill='x')

    def browse(self):
        path = filedialog.askdirectory(title='Select The Sims 4 Mods folder', initialdir=str(Path(self.mods.get()).parent))
        if path: self.mods.set(path)

    def start_scan(self):
        mods = Path(self.mods.get()).expanduser()
        if not mods.is_dir():
            messagebox.showerror(APP, 'Mods folder not found. Browse to the correct folder.')
            return
        self.scan_btn.config(state='disabled')
        self.status.set('Scanning packages and scripts...')
        def worker():
            try:
                data = scan(mods, None)
                self.after(0, lambda data=data: self.show(data))
            except Exception as exc:
                msg = str(exc)
                self.after(0, lambda msg=msg: self.scan_failed(msg))
        threading.Thread(target=worker, daemon=True).start()

    def scan_failed(self, message):
        self.scan_btn.config(state='normal')
        self.status.set('Scan failed: ' + message)
        messagebox.showerror(APP, message)

    def show(self, data):
        self.rows = data
        self.tree.delete(*self.tree.get_children())
        priority = {'ERROR': 0, 'WARNING': 1, 'DUPLICATE': 2, 'OK': 3}
        for i, r in sorted(enumerate(data), key=lambda x: (priority[x[1]['status']], x[1]['relative'].lower())):
            self.tree.insert('', 'end', iid=str(i), values=(r['status'], r['relative'], r['reason']), tags=(r['status'],))
        counts = {s: sum(r['status'] == s for r in data) for s in ('ERROR', 'WARNING', 'DUPLICATE', 'OK')}
        self.status.set(f"{len(data)} files scanned  |  {counts['ERROR']} errors  |  {counts['WARNING']} warnings  |  {counts['DUPLICATE']} duplicate copies  |  {counts['OK']} passed structure checks")
        self.scan_btn.config(state='normal')

    def backup_root(self):
        # Outside Mods, within the same Sims 4 user-data folder.
        return Path(self.mods.get()).resolve().parent / 'Mod Doctor Quarantine'

    def quarantine(self):
        ids = self.tree.selection()
        if not ids: return messagebox.showinfo(APP, 'Select one or more files first.')
        if not messagebox.askyesno(APP, f'Move {len(ids)} selected file(s) OUT of Mods?\n\nThey will be backed up in Mod Doctor Quarantine. Nothing will be deleted.'):
            return
        root = self.backup_root() / datetime.now().strftime('%Y%m%d_%H%M%S')
        moved, failed = 0, []
        for iid in ids:
            row = self.rows[int(iid)]
            src = Path(row['path'])
            dest = root / row['relative']
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists(): raise FileExistsError(str(dest))
                shutil.move(str(src), str(dest))
                moved += 1
            except Exception as exc: failed.append(f'{src.name}: {exc}')
        messagebox.showinfo(APP, f'Moved {moved} file(s) to:\n{root}\n' + ('\nErrors:\n' + '\n'.join(failed[:8]) if failed else ''))
        self.start_scan()

    def restore(self):
        root = self.backup_root()
        if not root.is_dir():
            return messagebox.showinfo(APP, 'No quarantine backups found.')
        selected = filedialog.askdirectory(title='Select a Mod Doctor quarantine batch to restore', initialdir=str(root), mustexist=True)
        if not selected:
            return
        batch = Path(selected).resolve()
        if batch == root.resolve() or root.resolve() not in batch.parents:
            return messagebox.showerror(APP, 'Select a batch folder inside Mod Doctor Quarantine.')
        sources = [p for p in batch.rglob('*') if p.is_file() and p.suffix.lower() in VALID_EXT]
        if not sources:
            return messagebox.showinfo(APP, 'No package or script files found in this batch.')
        if not messagebox.askyesno(APP, f'Restore {len(sources)} files into Mods? Existing files will NOT be overwritten.'):
            return
        dest_root = Path(self.mods.get()).resolve()
        moved, errors = 0, []
        for src in sources:
            dest = dest_root / src.relative_to(batch)
            if dest.exists():
                errors.append(f'{dest.name}: already exists')
                continue
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
                moved += 1
            except Exception as exc:
                errors.append(f'{src.name}: {exc}')
        messagebox.showinfo(APP, f'Restored {moved} files. ' + (f'{len(errors)} skipped or failed.\n' + '\n'.join(errors[:8]) if errors else ''))
        self.start_scan()

    def export(self):
        if not self.rows: return messagebox.showinfo(APP, 'Scan the folder first.')
        target = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON report', '*.json')], initialfile='sims4_mod_doctor_report.json')
        if target:
            Path(target).write_text(json.dumps({'generated': datetime.now().isoformat(), 'mods': self.mods.get(), 'results': self.rows}, indent=2), encoding='utf-8')
            messagebox.showinfo(APP, 'Report saved.')

    def half_test(self):
        if not self.rows: return messagebox.showinfo(APP, 'Scan the folder first.')
        if not messagebox.askyesno(APP, 'Prepare a 50/50 test?\n\nHalf of the scanned files will be moved to a reversible quarantine folder outside Mods. Start the game manually afterward.\n\nDo not save your game while CC is missing.'):
            return
        root = self.backup_root() / ('half_test_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
        chosen = sorted(self.rows, key=lambda r: r['relative'].lower())[::2]
        moved = 0
        for row in chosen:
            src = Path(row['path'])
            dest = root / row['relative']
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
                moved += 1
            except Exception as exc:
                messagebox.showerror(APP, f'Unable to move {src}: {exc}')
                break
        messagebox.showinfo(APP, f'Moved {moved} files to:\n{root}\n\nLaunch The Sims 4 manually. Do not save your game with CC missing. Restore files from quarantine when finished.')
        self.start_scan()

if __name__ == '__main__':
    Doctor().mainloop()

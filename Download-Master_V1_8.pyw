import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import subprocess
import os
import threading
import sys
import re
import json
import shutil

# ── Gestion creationflags Windows uniquement ──────────────────────────────────
CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


class YTDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Download Master - V1.8")
        self.root.geometry("850x1020")
        self.root.configure(bg="#f4f4f4")

        self.script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.settings_file = os.path.join(self.script_dir, "settings_yt.json")
        self.saved_settings = self.load_settings()

        self.base_dest     = tk.StringVar(value=self.saved_settings.get("dest", "D:\\youtube"))
        self.cookie_path   = tk.StringVar(value=self.saved_settings.get("cookie_file", ""))
        self.auto_clear    = tk.BooleanVar(value=self.saved_settings.get("auto_clear", False))
        self.format_choice = tk.StringVar(value=self.saved_settings.get("format", "[FULL] Qualité Max"))
        self.url_list      = []
        self._running      = False   # FIX: flag d'annulation

        # ── Zone saisie ──────────────────────────────────────────────────────
        tk.Label(root, text="Liens à télécharger :", font=("Arial", 10, "bold"), bg="#f4f4f4").pack(pady=5)
        input_frame = tk.Frame(root, bg="#f4f4f4")
        input_frame.pack(pady=5)
        self.url_input = tk.Entry(input_frame, width=50, font=("Arial", 10))
        self.url_input.pack(side=tk.LEFT, padx=5)

        tk.Button(input_frame, text="📋 Coller",  command=self.paste_url,  bg="#e1e1e1", width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(input_frame, text="✚ Ajouter", command=self.add_url,    bg="#d1d1d1", width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(input_frame, text="🗑️ Vider",   command=self.clear_all,  bg="#ffcccc", width=8).pack(side=tk.LEFT, padx=2)

        self.listbox = tk.Listbox(root, width=100, height=6, font=("Consolas", 9))
        self.listbox.pack(pady=10, padx=20)

        # ── Configuration ────────────────────────────────────────────────────
        config_frame = tk.LabelFrame(root, text=" Configuration & Destination ", bg="#f4f4f4", padx=15, pady=10)
        config_frame.pack(pady=10, fill="x", padx=40)

        tk.Label(config_frame, text="Format :", bg="#f4f4f4").pack(anchor="w")
        self.combo = ttk.Combobox(config_frame, textvariable=self.format_choice, state="readonly", width=40)
        self.combo['values'] = ("[FULL] Qualité Max", "[720p] Compressé (MP4)", "[MP3] Audio Haute Qualité")
        self.combo.pack(fill="x", pady=5)

        # FIX: Indicateur ffmpeg visible
        self.ffmpeg_lbl = tk.Label(config_frame, text="", bg="#f4f4f4", font=("Arial", 9))
        self.ffmpeg_lbl.pack(anchor="w")
        self._check_ffmpeg_label()

        tk.Label(config_frame, text="Fichier Cookies :", bg="#f4f4f4").pack(anchor="w")
        c_frame = tk.Frame(config_frame, bg="#f4f4f4")
        c_frame.pack(fill="x", pady=5)
        tk.Entry(c_frame, textvariable=self.cookie_path, font=("Arial", 9)).pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        tk.Button(c_frame, text="🍪 Cookies", command=self.browse_cookies).pack(side=tk.LEFT)

        tk.Label(config_frame, text="Dossier racine :", bg="#f4f4f4").pack(anchor="w")
        path_frame = tk.Frame(config_frame, bg="#f4f4f4")
        path_frame.pack(fill="x", pady=5)
        tk.Entry(path_frame, textvariable=self.base_dest, font=("Arial", 9)).pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        tk.Button(path_frame, text="📁 Dossier", command=self.browse_folder).pack(side=tk.LEFT, padx=2)
        tk.Button(path_frame, text="🔄 MAJ",     command=self.update_ytdlp, bg="#ffc107", font=("Arial", 8)).pack(side=tk.LEFT)

        tk.Checkbutton(config_frame, text="Vider la liste après succès", variable=self.auto_clear, bg="#f4f4f4").pack(anchor="w")

        # ── État & console ───────────────────────────────────────────────────
        self.prog_frame = tk.LabelFrame(root, text=" État de l'opération ", bg="#f4f4f4", padx=10, pady=10)
        self.prog_frame.pack(pady=10, fill="x", padx=40)
        self.status_lbl = tk.Label(self.prog_frame, text="Prêt", fg="blue", bg="#f4f4f4")
        self.status_lbl.pack(anchor="w")
        self.p_var = tk.DoubleVar()
        self.p_bar = ttk.Progressbar(self.prog_frame, variable=self.p_var, maximum=100)
        self.p_bar.pack(fill="x", side=tk.LEFT, expand=True, padx=5)
        self.p_lbl = tk.Label(self.prog_frame, text="0%", bg="#f4f4f4", width=8)
        self.p_lbl.pack(side=tk.RIGHT)

        # FIX: Boutons Lancer + Stop côte à côte
        btn_row = tk.Frame(root, bg="#f4f4f4")
        btn_row.pack(pady=10, fill="x", padx=40)
        self.btn_start = tk.Button(btn_row, text="🚀 LANCER LE TRAITEMENT", command=self.start_task,
                                   bg="#ccffcc", font=("Arial", 11, "bold"), pady=10)
        self.btn_start.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        self.btn_stop = tk.Button(btn_row, text="⛔ STOP", command=self.stop_task,
                                  bg="#ffcccc", font=("Arial", 11, "bold"), pady=10, state=tk.DISABLED, width=10)
        self.btn_stop.pack(side=tk.LEFT)

        self.console = scrolledtext.ScrolledText(root, width=100, height=20,
                                                  bg="black", fg="#00ff00", font=("Consolas", 9))
        self.console.pack(pady=10, padx=20)

        self._current_proc = None  # FIX: référence au sous-processus courant

    # ── ffmpeg check ─────────────────────────────────────────────────────────
    def _find_ffmpeg(self):
        """
        FIX PRINCIPAL : cherche ffmpeg dans l'ordre :
        1. Même dossier que yt-dlp.exe (Windows portable)
        2. PATH système
        Retourne le chemin ou None.
        """
        local = os.path.join(self.script_dir, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        if os.path.exists(local):
            return local
        return shutil.which("ffmpeg")

    def _check_ffmpeg_label(self):
        ffmpeg = self._find_ffmpeg()
        if ffmpeg:
            self.ffmpeg_lbl.config(text=f"✅ ffmpeg trouvé : {ffmpeg}", fg="green")
        else:
            self.ffmpeg_lbl.config(
                text="⚠️  ffmpeg introuvable — FULL et MP3 ne fonctionneront PAS ! (placez ffmpeg.exe dans le même dossier)",
                fg="red"
            )

    # ── Paramètres ───────────────────────────────────────────────────────────
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_settings(self):
        data = {
            "dest":        self.base_dest.get(),
            "cookie_file": self.cookie_path.get(),
            "format":      self.format_choice.get(),
            "auto_clear":  self.auto_clear.get(),
        }
        with open(self.settings_file, "w") as f:
            json.dump(data, f)

    # ── Thread safety ─────────────────────────────────────────────────────────
    def _ui(self, func, *args):
        self.root.after(0, func, *args)

    def log(self, text):
        def _do():
            self.console.config(state='normal')
            self.console.insert(tk.END, text + "\n")
            self.console.see(tk.END)
            self.console.config(state='disabled')
        self._ui(_do)

    def set_status(self, text, color="blue"):
        self._ui(lambda: self.status_lbl.config(text=text, fg=color))

    def set_progress(self, perc):
        def _do():
            self.p_var.set(perc)
            self.p_lbl.config(text=f"{perc:.1f}%")
        self._ui(_do)

    def set_btn(self, state):
        self._ui(lambda: self.btn_start.config(state=state))
        self._ui(lambda: self.btn_stop.config(state=tk.NORMAL if state == tk.DISABLED else tk.DISABLED))

    # ── Annulation ───────────────────────────────────────────────────────────
    def stop_task(self):
        """FIX: arrêt propre — tue le sous-processus yt-dlp en cours."""
        self._running = False
        if self._current_proc and self._current_proc.poll() is None:
            self._current_proc.terminate()
            self.log("⛔ Arrêt demandé par l'utilisateur.")
        self.set_status("Annulé", "red")
        self.set_btn(tk.NORMAL)

    # ── Gestion liste ────────────────────────────────────────────────────────
    def clear_all(self):
        self.url_list = []
        self.listbox.delete(0, tk.END)

    def paste_url(self):
        try:
            self.url_input.delete(0, tk.END)
            self.url_input.insert(0, self.root.clipboard_get().strip())
            self.add_url()
        except:
            pass

    def add_url(self):
        u = self.url_input.get().strip()
        if u:
            self.url_list.append(u)
            self.listbox.insert(tk.END, f"• {u}")
            self.url_input.delete(0, tk.END)

    # ── Navigation fichiers ──────────────────────────────────────────────────
    def browse_folder(self):
        f = filedialog.askdirectory()
        if f:
            self.base_dest.set(os.path.normpath(f))
            self.save_settings()

    def browse_cookies(self):
        f = filedialog.askopenfilename(filetypes=[("TXT", "*.txt")])
        if f:
            self.cookie_path.set(f)
            self.save_settings()

    # ── Mise à jour yt-dlp ───────────────────────────────────────────────────
    def update_ytdlp(self):
        exe = os.path.join(self.script_dir, "yt-dlp.exe")
        if not os.path.exists(exe):
            messagebox.showerror("yt-dlp introuvable", f"yt-dlp.exe non trouvé dans :\n{self.script_dir}")
            return
        self.log("\n>>> Mise à jour yt-dlp...")

        def run():
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/f", "/im", "yt-dlp.exe"],
                               capture_output=True, creationflags=CREATE_NO_WINDOW)
            p = subprocess.Popen([exe, "-U"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, creationflags=CREATE_NO_WINDOW)
            for line in iter(p.stdout.readline, ''):
                self.log(line.strip())
            p.wait()
            self.log(">>> Mise à jour terminée.")
            self.set_status("Prêt", "blue")

        threading.Thread(target=run, daemon=True).start()

    # ── Lancement ────────────────────────────────────────────────────────────
    def start_task(self):
        if not self.url_list:
            messagebox.showwarning("Liste vide", "Ajoutez au moins un lien avant de lancer.")
            return

        exe = os.path.join(self.script_dir, "yt-dlp.exe")
        if not os.path.exists(exe):
            messagebox.showerror("yt-dlp introuvable", f"yt-dlp.exe non trouvé dans :\n{self.script_dir}")
            return

        # FIX PRINCIPAL : avertir si ffmpeg absent et mode FULL/MP3 sélectionné
        choice = self.format_choice.get()
        if ("[FULL]" in choice or "[MP3]" in choice) and not self._find_ffmpeg():
            if not messagebox.askyesno(
                "ffmpeg introuvable",
                "Le mode FULL QUALITÉ et MP3 nécessitent ffmpeg pour fusionner les pistes.\n\n"
                "ffmpeg n'a pas été trouvé dans le dossier du script ni dans le PATH.\n\n"
                "➡️  Placez ffmpeg.exe dans le même dossier que yt-dlp.exe\n\n"
                "Continuer quand même (risque d'échec) ?"
            ):
                return

        self.save_settings()
        self._running = True
        self.set_btn(tk.DISABLED)
        threading.Thread(target=self.worker, daemon=True).start()

    # ── Worker (thread) ──────────────────────────────────────────────────────
    def worker(self):
        exe = os.path.join(self.script_dir, "yt-dlp.exe")
        choice = self.format_choice.get()
        sub = "FULL" if "FULL" in choice else ("720p" if "720p" in choice else "MP3")
        final_dest = os.path.join(self.base_dest.get(), sub)
        os.makedirs(final_dest, exist_ok=True)

        ffmpeg_path = self._find_ffmpeg()

        urls = list(self.url_list)
        total = len(urls)
        errors = []

        for idx, url in enumerate(urls, 1):
            if not self._running:
                break

            self.set_status(f"Téléchargement {idx}/{total}...", "darkorange")
            self.log(f"\n{'─'*60}")
            self.log(f"[{idx}/{total}] {url}")
            self.set_progress(0)

            cmd = [exe, "--newline", "--ignore-errors", "--no-playlist", "--no-check-certificate"]

            # FIX: passer le chemin ffmpeg explicitement si trouvé
            if ffmpeg_path:
                cmd += ["--ffmpeg-location", os.path.dirname(ffmpeg_path)]

            if self.cookie_path.get():
                cmd += ["--cookies", self.cookie_path.get()]

            if "[FULL]" in choice:
                # FIX PRINCIPAL :
                # 1. Préférer mp4+m4a (containers compatibles ffmpeg sans reencoder)
                # 2. Fallback sur bestvideo+bestaudio si pas de mp4 dispo
                # 3. Dernier fallback : best (stream combiné)
                # 4. Output en MKV pour accepter tous les codecs sans ré-encodage
                cmd += [
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
                    "--merge-output-format", "mkv",
                    # FIX: éviter ré-encodage inutile (source des blocages/lenteurs)
                    "--no-post-overwrites",
                ]
            elif "[720p]" in choice:
                cmd += [
                    "-f", "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best",
                    "--merge-output-format", "mp4",
                ]
            else:  # MP3
                cmd += [
                    "-f", "bestaudio/best",
                    "-x", "--audio-format", "mp3",
                    "--audio-quality", "0",
                ]

            cmd += ["-o", os.path.join(final_dest, "%(title)s.%(ext)s"), url]

            # Log commande complète pour debug
            self.log(f"CMD: {' '.join(cmd)}")

            try:
                self._current_proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding='utf-8', errors='replace',
                    creationflags=CREATE_NO_WINDOW
                )
                for line in iter(self._current_proc.stdout.readline, ''):
                    if not self._running:
                        self._current_proc.terminate()
                        break
                    line = line.strip()
                    if line:
                        self.log(line)
                        # FIX: détecter les erreurs ffmpeg explicitement
                        if "ERROR" in line or "error" in line.lower():
                            if "ffmpeg" in line.lower():
                                self.log("❌ ERREUR FFMPEG — Vérifiez que ffmpeg.exe est dans le dossier du script !")
                    m = re.search(r'(\d+(?:\.\d+)?)%', line)
                    if m:
                        self.set_progress(float(m.group(1)))

                self._current_proc.wait()
                rc = self._current_proc.returncode

                if not self._running:
                    break
                elif rc == 0:
                    self.log(f"✅ Terminé : {url}")
                else:
                    self.log(f"⚠️  Code retour {rc} : {url}")
                    errors.append(url)
            except Exception as e:
                self.log(f"❌ Erreur : {e}")
                errors.append(url)
            finally:
                self._current_proc = None

        # ── Fin de traitement ────────────────────────────────────────────────
        self.set_progress(100)
        if self._running:
            status_txt = f"Terminé — {total} URL(s) traitée(s)"
            if errors:
                status_txt += f" — ⚠️ {len(errors)} erreur(s)"
                self.log(f"\n⚠️ URLs en erreur :")
                for e in errors:
                    self.log(f"   • {e}")
            self.set_status(status_txt, "green" if not errors else "darkorange")
        self.log(f"\n{'='*60}")
        self.log(f"{'✅' if not errors else '⚠️ '} Traitement terminé. Dossier : {final_dest}")
        self._running = False
        self.set_btn(tk.NORMAL)

        if self.auto_clear.get():
            self._ui(self.clear_all)


if __name__ == "__main__":
    root = tk.Tk()
    app = YTDownloader(root)
    root.mainloop()

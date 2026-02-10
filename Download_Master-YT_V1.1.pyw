import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import subprocess, os, threading, sys, re, socket

class YTDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Master - Version 1.1")
        self.root.geometry("650x600")
        self.root.configure(bg="#f4f4f4")
        
        # Le dossier où se trouve ton script/ton .exe
        self.script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.base_dest = tk.StringVar(value="C:\\youtube")
        self.auto_clear = tk.BooleanVar(value=False) 
        self.format_choice = tk.StringVar(value="[MP3] Audio Haute Qualité")
        self.url_list = []

        # --- UI ---
        tk.Label(root, text="Liens à télécharger :", font=("Arial", 10, "bold"), bg="#f4f4f4").pack(pady=5)
        input_frame = tk.Frame(root, bg="#f4f4f4")
        input_frame.pack(pady=5)
        self.url_input = tk.Entry(input_frame, width=40, font=("Arial", 10))
        self.url_input.pack(side=tk.LEFT, padx=5)
        
        tk.Button(input_frame, text="📋 Coller", command=self.paste_url, bg="#e1e1e1", width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(input_frame, text="✚ Ajouter", command=self.add_url, bg="#d1d1d1", width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(input_frame, text="🗑️ Vider", command=self.clear_list, bg="#ffcccc", width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(input_frame, text="🔍 Diag", command=self.run_diag, bg="#bbdefb", width=8, font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=10)

        self.listbox = tk.Listbox(root, width=90, height=6, font=("Consolas", 9))
        self.listbox.pack(pady=10, padx=20)
        
        config_frame = tk.LabelFrame(root, text=" Configuration & Destination ", bg="#f4f4f4", padx=15, pady=10)
        config_frame.pack(pady=10, fill="x", padx=40)
        
        self.combo = ttk.Combobox(config_frame, textvariable=self.format_choice, state="readonly", width=45)
        self.combo['values'] = ("[FULL] Qualité Max (MP4)", "[720p] Compressé (MP4)", "[MP3] Audio Haute Qualité")
        self.combo.pack(fill="x", pady=5)

        path_frame = tk.Frame(config_frame, bg="#f4f4f4")
        path_frame.pack(fill="x", pady=5)
        tk.Entry(path_frame, textvariable=self.base_dest, font=("Arial", 9)).pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        tk.Button(path_frame, text="📁 Parcourir", command=self.browse_folder).pack(side=tk.LEFT)

        tk.Checkbutton(config_frame, text="Vider auto après succès", variable=self.auto_clear, bg="#f4f4f4").pack(anchor="w")

        self.prog_frame = tk.LabelFrame(root, text=" État ", bg="#f4f4f4", padx=10, pady=10)
        self.prog_frame.pack(pady=10, fill="x", padx=40)
        self.status_lbl = tk.Label(self.prog_frame, text="Prêt", fg="blue", bg="#f4f4f4", font=("Arial", 9, "bold"))
        self.status_lbl.pack(anchor="w")
        self.p_var = tk.DoubleVar()
        self.p_bar = ttk.Progressbar(self.prog_frame, variable=self.p_var, maximum=100)
        self.p_bar.pack(fill="x", side=tk.LEFT, expand=True, padx=5)
        self.p_lbl = tk.Label(self.prog_frame, text="0%", bg="#f4f4f4", width=8)
        self.p_lbl.pack(side=tk.RIGHT)

        self.btn_start = tk.Button(root, text="🚀 LANCER LE TÉLÉCHARGEMENT", command=self.start_task, bg="#ccffcc", font=("Arial", 11, "bold"), pady=10)
        self.btn_start.pack(pady=10, fill="x", padx=40)

        self.console = scrolledtext.ScrolledText(root, width=90, height=18, bg="black", fg="#00ff00", font=("Consolas", 9))
        self.console.pack(pady=10, padx=20)

    def log(self, text):
        self.console.config(state='normal'); self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END); self.console.config(state='disabled')

    def run_diag(self):
        self.log("\n" + "="*30 + "\n[DIAGNOSTIC SYSTÈME]\n" + "="*30)
        
        # 1. yt-dlp.exe
        yt_exe = os.path.join(self.script_dir, "yt-dlp.exe")
        if os.path.exists(yt_exe): self.log(f"✅ yt-dlp.exe : Trouvé dans {self.script_dir}")
        else: self.log("❌ yt-dlp.exe : INTROUVABLE !")
        
        # 2. ffmpeg.exe (Local ou Path)
        ff_exe = os.path.join(self.script_dir, "ffmpeg.exe")
        if os.path.exists(ff_exe):
            self.log(f"✅ ffmpeg.exe : Trouvé en LOCAL")
        else:
            try:
                subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                self.log("✅ FFmpeg : Détecté dans le PATH Windows")
            except:
                self.log("❌ FFmpeg : ABSENT (Ni en local, ni dans Windows)")

        # 3. Réseau
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            self.log("✅ Internet : Connecté")
        except: self.log("❌ Internet : Erreur de connexion")
        self.log("="*30 + "\n")

    def browse_folder(self):
        f = filedialog.askdirectory()
        if f: self.base_dest.set(f.replace("/", "\\"))

    def paste_url(self):
        try:
            self.url_input.delete(0, tk.END); self.url_input.insert(0, self.root.clipboard_get().strip()); self.add_url()
        except: pass

    def add_url(self):
        u = self.url_input.get().strip()
        if u: self.url_list.append(u); self.listbox.insert(tk.END, f"• {u}"); self.url_input.delete(0, tk.END)

    def clear_list(self):
        self.url_list = []; self.listbox.delete(0, tk.END); self.log("Liste vidée.")

    def start_task(self):
        if not self.url_list: return
        self.btn_start.config(state=tk.DISABLED)
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        yt_exe = os.path.join(self.script_dir, "yt-dlp.exe")
        ff_dir = self.script_dir # On définit où chercher ffmpeg
        
        choice = self.format_choice.get()
        sub = "FULL" if "FULL" in choice else ("720p" if "720p" in choice else "MP3")
        final_dest = os.path.join(self.base_dest.get(), sub)
        if not os.path.exists(final_dest): os.makedirs(final_dest, exist_ok=True)

        for url in self.url_list:
            self.log(f"\n>>> TRAITEMENT : {url}")
            self.status_lbl.config(text="⬇️ Téléchargement en cours...", fg="green")
            self.p_bar.config(mode='determinate'); self.p_var.set(0)

            # --- LA MODIF CRUCIALE : --ffmpeg-location ---
            cmd = [yt_exe, "--newline", "--ignore-errors", "--no-playlist", "--no-check-certificate",
                   "--concurrent-fragments", "5", "--restrict-filenames",
                   "--ffmpeg-location", ff_dir] # On dit à yt-dlp de regarder dans ton dossier
            
            if "[FULL]" in choice:
                cmd += ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"]
            elif "[720p]" in choice:
                cmd += ["-f", "bestvideo[height<=720]+bestaudio/best[height<=720]", "--merge-output-format", "mp4"]
            else: 
                cmd += ["-f", "bestaudio/best", "-x", "--audio-format", "mp3", "--audio-quality", "0"]

            cmd += ["-o", os.path.join(final_dest, "%(title)s.%(ext)s"), url]

            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=0x08000000)
                for line in iter(process.stdout.readline, ''):
                    clean_line = line.strip()
                    if clean_line:
                        self.log(clean_line)
                        if any(x in clean_line for x in ["[ExtractAudio]", "[Merger]", "Converting"]):
                            self.status_lbl.config(text="⚙️ Traitement final...", fg="orange")
                            self.p_bar.config(mode='indeterminate'); self.p_bar.start(10); self.p_lbl.config(text="WAIT")
                        match = re.search(r'(\d+\.\d+)%', clean_line)
                        if match and self.p_bar['mode'] == 'determinate':
                            perc = float(match.group(1))
                            self.p_var.set(perc); self.p_lbl.config(text=f"{int(perc)}%")
                process.wait()
                self.p_bar.stop(); self.p_bar.config(mode='determinate'); self.p_var.set(100); self.p_lbl.config(text="100%")
                self.status_lbl.config(text="✅ Terminé", fg="blue")
            except Exception as e: self.log(f"❌ Erreur : {str(e)}")

        self.btn_start.config(state=tk.NORMAL)
        if self.auto_clear.get():
            self.url_list = []; self.root.after(0, lambda: self.listbox.delete(0, tk.END))

if __name__ == "__main__":
    root = tk.Tk(); app = YTDownloader(root); root.mainloop()
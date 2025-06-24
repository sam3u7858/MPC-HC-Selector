import os
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from pathlib import Path


class FileListWindow:
    """顯示檔案列表的小視窗"""

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("檔案列表")
        self.window.geometry("400x300")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 創建列表框
        frame = ttk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text="目前檔案列表:").pack(anchor=tk.W)

        self.listbox = tk.Listbox(frame)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # 添加滾動條
        scrollbar = ttk.Scrollbar(
            frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # 按鈕框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="刷新",
                   command=self.refresh_list).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="刪除選中檔案", command=self.delete_selected).pack(
            side=tk.LEFT, padx=(10, 0))

        self.refresh_list()

    def refresh_list(self):
        """刷新檔案列表"""
        self.listbox.delete(0, tk.END)
        if hasattr(self.parent, 'watch_folder') and self.parent.watch_folder:
            try:
                files = []
                for file in os.listdir(self.parent.watch_folder):
                    file_path = os.path.join(self.parent.watch_folder, file)
                    if os.path.isfile(file_path):
                        files.append(file)

                # 按序號排序
                files.sort(key=lambda x: int(x.split('_')[0]) if '_' in x and x.split(
                    '_')[0].isdigit() else 999999)

                for file in files:
                    self.listbox.insert(tk.END, file)

            except Exception as e:
                self.listbox.insert(tk.END, f"錯誤: {str(e)}")

    def delete_selected(self):
        """刪除選中的檔案"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "請選擇要刪除的檔案")
            return

        filename = self.listbox.get(selection[0])
        if messagebox.askyesno("確認刪除", f"確定要刪除檔案 '{filename}' 嗎？"):
            try:
                file_path = os.path.join(self.parent.watch_folder, filename)
                os.remove(file_path)
                self.refresh_list()
                messagebox.showinfo("成功", "檔案已刪除")
            except Exception as e:
                messagebox.showerror("錯誤", f"刪除檔案失敗: {str(e)}")

    def on_closing(self):
        """視窗關閉時隱藏而不是銷毀"""
        self.window.withdraw()


class FileHandler(FileSystemEventHandler):
    """檔案系統事件處理器"""

    def __init__(self, app):
        self.app = app
        self.last_event_time = {}
        self.cooldown = 1.0

    def on_created(self, event):
        """當新檔案被創建時觸發"""
        if not event.is_directory:
            # 稍等一下確保檔案完全寫入
            now = time.time()
            last_time = self.last_event_time.get(event.src_path, 0)

            if now - last_time < self.cooldown:
                return  # 忽略過短間隔的事件

            # Use dict to store the last event time
            self.last_event_time[event.src_path] = now

            time.sleep(0.5)
            self.app.handle_new_file(event.src_path)


class FileMonitorApp:
    """主應用程序"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("檔案監聽器")
        self.root.geometry("500x400")

        self.watch_folder = None
        self.observer = None
        self.file_counter = 0
        self.config_file = "file_monitor_config.json"

        self.setup_ui()
        self.load_config()

        # 檔案列表視窗
        self.file_list_window = None

    def setup_ui(self):
        """設置使用者介面"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 標題
        title_label = ttk.Label(main_frame, text="檔案監聽器",
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 資料夾選擇區域
        folder_frame = ttk.LabelFrame(main_frame, text="監聽資料夾", padding=10)
        folder_frame.pack(fill=tk.X, pady=(0, 10))

        self.folder_label = ttk.Label(
            folder_frame, text="尚未選擇資料夾", foreground="gray")
        self.folder_label.pack(anchor=tk.W, pady=(0, 10))

        btn_frame = ttk.Frame(folder_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="選擇資料夾",
                   command=self.select_folder).pack(side=tk.LEFT)
        self.start_btn = ttk.Button(
            btn_frame, text="開始監聽", command=self.start_monitoring, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.stop_btn = ttk.Button(
            btn_frame, text="停止監聽", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(10, 0))

        # 狀態區域
        status_frame = ttk.LabelFrame(main_frame, text="狀態", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(
            status_frame, text="就緒", foreground="green")
        self.status_label.pack(anchor=tk.W)

        # 檔案計數器
        counter_frame = ttk.LabelFrame(main_frame, text="檔案計數", padding=10)
        counter_frame.pack(fill=tk.X, pady=(0, 10))

        self.counter_label = ttk.Label(counter_frame, text="檔案序號: 0")
        self.counter_label.pack(anchor=tk.W)

        ttk.Button(counter_frame, text="重設計數器", command=self.reset_counter).pack(
            anchor=tk.W, pady=(5, 0))

        # 日誌區域
        log_frame = ttk.LabelFrame(main_frame, text="活動日誌", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = ScrolledText(log_frame, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 底部按鈕
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(bottom_frame, text="顯示檔案列表",
                   command=self.show_file_list).pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="清除日誌", command=self.clear_log).pack(
            side=tk.LEFT, padx=(10, 0))
        ttk.Button(bottom_frame, text="退出",
                   command=self.on_closing).pack(side=tk.RIGHT)

        # 設置視窗關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_folder(self):
        """選擇要監聽的資料夾"""
        folder = filedialog.askdirectory(title="選擇要監聽的資料夾")
        if folder:
            self.watch_folder = folder
            self.folder_label.config(text=folder, foreground="black")
            self.start_btn.config(state=tk.NORMAL)
            self.log(f"已選擇資料夾: {folder}")
            self.save_config()
            self.update_file_counter()

    def update_file_counter(self):
        """更新檔案計數器，基於現有檔案的最大序號"""
        if not self.watch_folder:
            return

        try:
            max_counter = -1
            for file in os.listdir(self.watch_folder):
                if '_' in file:
                    try:
                        counter = int(file.split('_')[0])
                        max_counter = max(max_counter, counter)
                    except ValueError:
                        continue

            self.file_counter = max_counter + 1
            self.counter_label.config(text=f"檔案序號: {self.file_counter}")

        except Exception as e:
            self.log(f"更新計數器時發生錯誤: {str(e)}")

    def reset_counter(self):
        """重設檔案計數器"""
        if messagebox.askyesno("確認重設", "確定要重設檔案計數器為 0 嗎？"):
            self.file_counter = 0
            self.counter_label.config(text=f"檔案序號: {self.file_counter}")
            self.log("檔案計數器已重設為 0")

    def start_monitoring(self):
        """開始監聽檔案"""
        if not self.watch_folder:
            messagebox.showerror("錯誤", "請先選擇要監聽的資料夾")
            return

        try:
            self.observer = Observer()
            event_handler = FileHandler(self)
            self.observer.schedule(
                event_handler, self.watch_folder, recursive=False)
            self.observer.start()

            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="監聽中...", foreground="blue")
            self.log(f"開始監聽資料夾: {self.watch_folder}")

        except Exception as e:
            messagebox.showerror("錯誤", f"啟動監聽失敗: {str(e)}")
            self.log(f"啟動監聽失敗: {str(e)}")

    def stop_monitoring(self):
        """停止監聽檔案"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="已停止", foreground="red")
        self.log("監聽已停止")

    def handle_new_file(self, file_path):
        """處理新檔案"""
        original_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)

        # 在主線程中顯示對話框
        self.root.after(0, self.show_rename_dialog,
                        file_path, original_name, file_dir)

    def show_rename_dialog(self, file_path, original_name, file_dir):
        """顯示重命名對話框"""
        # 創建自定義對話框
        dialog = tk.Toplevel(self.root)
        dialog.title("新檔案偵測")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        # 置中顯示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() +
                        50, self.root.winfo_rooty() + 50))

        result = {"action": None, "name": ""}

        # 主框架
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 訊息
        ttk.Label(main_frame, text=f"偵測到新檔案: {original_name}").pack(
            pady=(0, 10))
        ttk.Label(main_frame, text=f"將重命名為: {self.file_counter}_<您的輸入>").pack(
            pady=(0, 10))

        # 輸入框
        ttk.Label(main_frame, text="請輸入檔案名稱:").pack(anchor=tk.W)
        name_entry = ttk.Entry(main_frame, width=40)
        name_entry.pack(fill=tk.X, pady=(5, 10))
        name_entry.focus()

        # 按鈕框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        def on_rename():
            result["action"] = "rename"
            result["name"] = name_entry.get().strip()
            dialog.destroy()

        def on_delete():
            result["action"] = "delete"
            dialog.destroy()

        def on_skip():
            result["action"] = "skip"
            dialog.destroy()

        ttk.Button(btn_frame, text="重命名", command=on_rename).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="刪除檔案", command=on_delete).pack(
            side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="跳過", command=on_skip).pack(
            side=tk.LEFT, padx=(10, 0))

        # 綁定Enter鍵
        dialog.bind('<Return>', lambda e: on_rename())

        # 等待對話框關閉
        dialog.wait_window()

        # 處理結果
        if result["action"] == "rename":
            self.rename_file(file_path, original_name, result["name"])
        elif result["action"] == "delete":
            self.delete_file(file_path, original_name)
        else:  # skip
            self.log(f"跳過檔案: {original_name}")

    def rename_file(self, file_path, original_name, new_name):
        """重命名檔案"""
        try:
            if not new_name:
                new_name = "unnamed"

            # 獲取檔案副檔名
            _, ext = os.path.splitext(original_name)

            # 構造新檔案名
            new_filename = f"{self.file_counter}_{new_name}{ext}"
            new_file_path = os.path.join(
                os.path.dirname(file_path), new_filename)

            # 檢查檔案是否已存在
            counter = 1
            while os.path.exists(new_file_path):
                new_filename = f"{self.file_counter}_{new_name}_{counter}{ext}"
                new_file_path = os.path.join(
                    os.path.dirname(file_path), new_filename)
                counter += 1

            # 重命名檔案
            os.rename(file_path, new_file_path)

            self.log(f"檔案已重命名: {original_name} -> {new_filename}")
            self.file_counter += 1
            self.counter_label.config(text=f"檔案序號: {self.file_counter}")

            # 更新檔案列表視窗
            if self.file_list_window and self.file_list_window.window.winfo_exists():
                self.file_list_window.refresh_list()

        except Exception as e:
            self.log(f"重命名檔案失敗: {str(e)}")
            messagebox.showerror("錯誤", f"重命名檔案失敗: {str(e)}")

    def delete_file(self, file_path, original_name):
        """刪除檔案"""
        try:
            os.remove(file_path)
            self.log(f"檔案已刪除: {original_name}")

            # 更新檔案列表視窗
            if self.file_list_window and self.file_list_window.window.winfo_exists():
                self.file_list_window.refresh_list()

        except Exception as e:
            self.log(f"刪除檔案失敗: {str(e)}")
            messagebox.showerror("錯誤", f"刪除檔案失敗: {str(e)}")

    def show_file_list(self):
        """顯示檔案列表視窗"""
        if not self.watch_folder:
            messagebox.showwarning("警告", "請先選擇要監聽的資料夾")
            return

        if self.file_list_window is None or not self.file_list_window.window.winfo_exists():
            self.file_list_window = FileListWindow(self)
        else:
            self.file_list_window.window.deiconify()
            self.file_list_window.refresh_list()

    def log(self, message):
        """添加日誌訊息"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)

    def clear_log(self):
        """清除日誌"""
        self.log_text.delete(1.0, tk.END)

    def save_config(self):
        """保存配置"""
        config = {
            "watch_folder": self.watch_folder,
            "file_counter": self.file_counter
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"保存配置失敗: {str(e)}")

    def load_config(self):
        """載入配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                if config.get("watch_folder") and os.path.exists(config["watch_folder"]):
                    self.watch_folder = config["watch_folder"]
                    self.folder_label.config(
                        text=self.watch_folder, foreground="black")
                    self.start_btn.config(state=tk.NORMAL)

                self.file_counter = config.get("file_counter", 0)
                self.counter_label.config(text=f"檔案序號: {self.file_counter}")

        except Exception as e:
            self.log(f"載入配置失敗: {str(e)}")

    def on_closing(self):
        """應用程序關閉時的處理"""
        self.save_config()
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.root.quit()

    def run(self):
        """運行應用程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = FileMonitorApp()
    app.run()

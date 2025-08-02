import tkinter as tk
from tkinter import messagebox
import requests
import threading
import time
from urllib.parse import urlparse
import queue

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Getter")
        self.pack()
        self.create_widgets()
        self.successful_gets = 0
        self.errors = 0
        self.running = False
        self.queue = queue.Queue()

    def create_widgets(self):
        self.url_label = tk.Label(self)
        self.url_label["text"] = "URL:"
        self.url_label.pack(side="top")

        self.url_entry = tk.Entry(self)
        self.url_entry.pack(side="top")

        self.gets_label = tk.Label(self)
        self.gets_label["text"] = "Number of GETs:"
        self.gets_label.pack(side="top")

        self.gets_entry = tk.Entry(self)
        self.gets_entry.pack(side="top")

        self.delay_label = tk.Label(self)
        self.delay_label["text"] = "Delay (ms):"
        self.delay_label.pack(side="top")

        self.delay_entry = tk.Entry(self)
        self.delay_entry.pack(side="top")

        self.port_label = tk.Label(self)
        self.port_label["text"] = "Port (optional):"
        self.port_label.pack(side="top")

        self.port_entry = tk.Entry(self)
        self.port_entry.pack(side="top")

        self.start_button = tk.Button(self)
        self.start_button["text"] = "Start"
        self.start_button["command"] = self.start_gets
        self.start_button.pack(side="top")

        self.successful_gets_label = tk.Label(self)
        self.successful_gets_label["text"] = "Successful GETs: 0"
        self.successful_gets_label.pack(side="top")

        self.errors_label = tk.Label(self)
        self.errors_label["text"] = "Errors: 0"
        self.errors_label.pack(side="top")

        self.log_label = tk.Label(self)
        self.log_label["text"] = "Log:"
        self.log_label.pack(side="top")

        self.log_text = tk.Text(self, height=20, width=60)
        self.log_text.pack(side="top")
        self.log_text.config(state="disabled")

    def start_gets(self):
        if not self.running:
            self.running = True
            self.start_button["state"] = "disabled"
            self.successful_gets = 0
            self.errors = 0
            self.successful_gets_label["text"] = "Successful GETs: 0"
            self.errors_label["text"] = "Errors: 0"
            self.log_text.config(state="normal")
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state="disabled")
            self.thread = threading.Thread(target=self.send_gets)
            self.thread.start()
            self.master.after(100, self.process_queue)

    def process_queue(self):
        try:
            msg = self.queue.get_nowait()
            if isinstance(msg, dict):
                if "success" in msg:
                    self.successful_gets += 1
                    self.successful_gets_label["text"] = f"Successful GETs: {self.successful_gets}"
                elif "error" in msg:
                    self.errors += 1
                    self.errors_label["text"] = f"Errors: {self.errors}"
                if "log" in msg:
                    self.log(msg["log"])
            elif "validation_error" in msg:
                messagebox.showerror("Error", msg["validation_error"])
                self.running = False
                self.start_button["state"] = "normal"
                return
            elif msg == "done":
                self.running = False
                self.start_button["state"] = "normal"
                return
        except queue.Empty:
            pass
        self.master.after(100, self.process_queue)

    def send_gets(self):
        try:
            inputs = self._parse_inputs()
        except ValueError as e:
            self.queue.put({"validation_error": f"Invalid input: {e}"})
            return

        self._execute_requests(inputs)
        self.queue.put("done")

    def _parse_inputs(self):
        url = self.url_entry.get()
        if not url:
            raise ValueError("URL cannot be empty.")
        num_gets = int(self.gets_entry.get())
        delay = int(self.delay_entry.get())
        port_str = self.port_entry.get()
        port = int(port_str) if port_str else None
        return {"url": url, "num_gets": num_gets, "delay": delay, "port": port}

    def _execute_requests(self, inputs):
        url = inputs["url"]
        num_gets = inputs["num_gets"]
        delay = inputs["delay"]
        port = inputs["port"]

        parsed_url = urlparse(url)
        ip = parsed_url.hostname
        if port is None:
            port = parsed_url.port if parsed_url.port else 80 if parsed_url.scheme == 'http' else 443

        # Reconstruct URL to include the correct port, preserving other parts
        url_parts = list(parsed_url)
        url_parts[1] = f"{ip}:{port}" # Update netloc
        url_with_port = urlparse.urlunparse(url_parts)

        for i in range(num_gets):
            try:
                response = requests.get(url_with_port)
                if response.status_code == 200:
                    self.queue.put({"success": True, "log": f"GET {url_with_port} successful ({response.status_code}) from {ip}:{port}"})
                else:
                    self.queue.put({"error": True, "log": f"GET {url_with_port} failed ({response.status_code}) from {ip}:{port}"})
            except requests.exceptions.RequestException as e:
                self.queue.put({"error": True, "log": f"GET {url_with_port} failed: {e} from {ip}:{port}"})
            time.sleep(delay / 1000)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

root = tk.Tk()
app = Application(master=root)
app.mainloop()

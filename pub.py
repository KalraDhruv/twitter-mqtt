import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import paho.mqtt.client as mqtt
import json
from datetime import datetime

class MQTTPublisher:
    def __init__(self, root):
        self.root = root
        self.root.title("MQTT Twitter Publisher")
        self.root.geometry("700x600")
        self.root.configure(bg="#1e293b")
        
        self.broker = "127.0.0.1"
        self.port = 9001
        self.client = None
        self.connected = False
        
        self.topics = [
            "rock",
            "anime",
            "cooking",
            "animal",
            "yahoo",
            "movie",
            "custom"  
        ]
        
        self.setup_ui()
        self.connect_mqtt()
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1e293b', foreground='#f1f5f9', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('TCombobox', font=('Segoe UI', 10))
        
        header_frame = tk.Frame(self.root, bg="#6366f1", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="MQTT Twitter Publisher", 
            font=('Segoe UI', 18, 'bold'),
            bg="#6366f1", 
            fg="white"
        )
        title_label.pack(pady=15)
        
        status_frame = tk.Frame(self.root, bg="#1e293b")
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="● Connecting to broker...",
            font=('Segoe UI', 10, 'bold'),
            bg="#1e293b",
            fg="#f59e0b"
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.broker_label = tk.Label(
            status_frame,
            text=f"Broker: {self.broker}:{self.port}",
            font=('Segoe UI', 9),
            bg="#1e293b",
            fg="#94a3b8"
        )
        self.broker_label.pack(side=tk.RIGHT)
        
        publisher_frame = tk.LabelFrame(
            self.root,
            text="  Publish Message  ",
            font=('Segoe UI', 12, 'bold'),
            bg="#1e293b",
            fg="#f1f5f9",
            relief=tk.GROOVE,
            borderwidth=2
        )
        publisher_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        topic_label = ttk.Label(publisher_frame, text="Select Topic:")
        topic_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.topic_var = tk.StringVar()
        self.topic_combo = ttk.Combobox(
            publisher_frame,
            textvariable=self.topic_var,
            values=self.topics,
            state='readonly',
            width=40,
            font=('Segoe UI', 10)
        )
        self.topic_combo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        self.topic_combo.current(0)
        self.topic_combo.bind("<<ComboboxSelected>>", self.on_topic_change)
        
        self.custom_topic_label = ttk.Label(publisher_frame, text="Custom Topic:")
        self.custom_topic_entry = tk.Entry(
            publisher_frame,
            font=('Segoe UI', 10),
            bg="#334155",
            fg="#f1f5f9",
            insertbackground="#f1f5f9",
            width=42,
            relief=tk.FLAT
        )
        
        message_label = ttk.Label(publisher_frame, text="Message:")
        message_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.NW)
        
        self.message_text = scrolledtext.ScrolledText(
            publisher_frame,
            width=40,
            height=5,
            font=('Segoe UI', 10),
            bg="#334155",
            fg="#f1f5f9",
            insertbackground="#f1f5f9",
            relief=tk.FLAT
        )
        self.message_text.grid(row=2, column=1, padx=10, pady=10)
        
        self.publish_btn = tk.Button(
            publisher_frame,
            text=" PUBLISH MESSAGE ",
            command=self.publish_message,
            bg="#10b981",
            fg="white",
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.publish_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        log_frame = tk.LabelFrame(
            self.root,
            text="  Message Log  ",
            font=('Segoe UI', 12, 'bold'),
            bg="#1e293b",
            fg="#f1f5f9",
            relief=tk.GROOVE,
            borderwidth=2
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            width=70,
            height=10,
            font=('Consolas', 9),
            bg="#0f172a",
            fg="#94a3b8",
            insertbackground="#f1f5f9",
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        clear_btn = tk.Button(
            log_frame,
            text="Clear Log",
            command=self.clear_log,
            bg="#ef4444",
            fg="white",
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        clear_btn.pack(pady=(0, 10))
        
    def on_topic_change(self, event):
        if self.topic_var.get() == "custom":
            self.custom_topic_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
            self.custom_topic_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        else:
            self.custom_topic_label.grid_remove()
            self.custom_topic_entry.grid_remove()
    
    def connect_mqtt(self):
        try:
            self.client = mqtt.Client(
                client_id="mqtt_publisher_gui",
                protocol=mqtt.MQTTv311,
                transport="websockets"
            )
            
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            
        except Exception as e:
            self.log_message(f"❌ Connection error: {str(e)}", "error")
            messagebox.showerror("Connection Error", f"Failed to connect to broker:\n{str(e)}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            self.status_label.config(text="● Connected to broker", fg="#10b981")
            self.log_message("✅ Connected to MQTT broker successfully", "success")
        else:
            self.status_label.config(text=f"● Connection failed (code: {rc})", fg="#ef4444")
            self.log_message(f"❌ Connection failed with code {rc}", "error")
    
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.status_label.config(text="● Disconnected from broker", fg="#ef4444")
        self.log_message("⚠️ Disconnected from MQTT broker", "warning")
    
    def on_publish(self, client, userdata, mid):
        self.log_message(f"✓ Message delivered (mid: {mid})", "info")
    
    def publish_message(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Not connected to MQTT broker!")
            return
        
        topic = self.topic_var.get()
        if topic == "custom":
            topic = self.custom_topic_entry.get().strip()
            if not topic:
                messagebox.showwarning("Invalid Topic", "Please enter a custom topic!")
                return
        
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Empty Message", "Please enter a message to publish!")
            return
        
        try:
            result = self.client.publish(topic, message, qos=0)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_message(
                    f"[{timestamp}] Published to '{topic}': {message}",
                    "publish"
                )
                
                self.message_text.delete("1.0", tk.END)
                
                self.publish_btn.config(bg="#059669")
                self.root.after(200, lambda: self.publish_btn.config(bg="#10b981"))
            else:
                self.log_message(f"❌ Publish failed with code {result.rc}", "error")
                
        except Exception as e:
            self.log_message(f"❌ Error publishing: {str(e)}", "error")
            messagebox.showerror("Publish Error", f"Failed to publish message:\n{str(e)}")
    
    def log_message(self, message, msg_type="info"):
        self.log_text.config(state=tk.NORMAL)
        
        colors = {
            "success": "#10b981",
            "error": "#ef4444",
            "warning": "#f59e0b",
            "info": "#94a3b8",
            "publish": "#6366f1"
        }
        
        color = colors.get(msg_type, "#94a3b8")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_message("🗑️ Log cleared", "info")
    
    def on_closing(self):
        if self.client and self.connected:
            self.client.loop_stop()
            self.client.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTPublisher(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

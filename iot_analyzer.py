
import tkinter as tk
from tkinter import messagebox, simpledialog
from collections import deque
import math


class IoTNetworkAnalyzer:

    def __init__(self, root):
        self.root = root
        self.root.title("IoT Network Connectivity Analyzer")
        self.root.geometry("1250x800")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#101522")

        self.graph = {}
        self.device_types = {}
        self.positions = {}
        self.selected_device = None

        self.bg = "#101522"
        self.panel = "#1A2233"
        self.card = "#222D42"
        self.accent = "#42D9C8"
        self.text = "#F0F4FC"
        self.muted = "#9AAAC1"
        self.red = "#FF667A"
        self.green = "#45D483"

        self.build_ui()
        self.load_demo_network()
        self.refresh_all()

    # ---------------- UI ----------------

    def button(self, parent, text, command, color=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color or self.card,
            fg=self.text,
            activebackground=self.accent,
            activeforeground=self.bg,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=8,
            pady=9,
            cursor="hand2"
        )

    def build_ui(self):

        header = tk.Frame(self.root, bg=self.panel, height=75)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="◈  IoT NETWORK ANALYZER",
            font=("Segoe UI", 20, "bold"),
            fg=self.accent,
            bg=self.panel
        ).pack(side="left", padx=22, pady=18)

        tk.Label(
            header,
            text="CONNECTIVITY MONITOR",
            font=("Segoe UI", 10, "bold"),
            fg=self.muted,
            bg=self.panel
        ).pack(side="right", padx=22)

        # Statistics
        stats = tk.Frame(self.root, bg=self.bg)
        stats.pack(fill="x", padx=15, pady=12)

        self.stat_labels = {}

        for key, title in [
            ("devices", "TOTAL DEVICES"),
            ("links", "CONNECTIONS"),
            ("groups", "CONNECTED GROUPS"),
            ("isolated", "ISOLATED DEVICES")
        ]:
            card = tk.Frame(stats, bg=self.card, padx=14, pady=10)
            card.pack(side="left", expand=True, fill="x", padx=5)

            tk.Label(
                card, text=title,
                bg=self.card, fg=self.muted,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")

            label = tk.Label(
                card, text="0",
                bg=self.card,
                fg=self.red if key == "isolated" else self.accent,
                font=("Segoe UI", 22, "bold")
            )
            label.pack(anchor="w", pady=(4, 0))
            self.stat_labels[key] = label

        # Main area
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        left = tk.Frame(main, bg=self.panel, width=240)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(
            left, text="NETWORK CONTROLS",
            bg=self.panel, fg=self.text,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=14, pady=(15, 10))

        controls = [
            ("＋  Add Device", self.add_device),
            ("＋  Connect Devices", self.add_connection),
            ("－  Disconnect Devices", self.disconnect_devices),
            ("✕  Remove Device", self.remove_device),
            ("⌕  BFS Analysis", self.run_bfs),
            ("⌕  DFS Analysis", self.run_dfs),
            ("⚠  Detect Isolated", self.detect_isolated),
            ("▦  Connected Groups", self.show_components),
            ("↻  Refresh Network", self.refresh_all)
        ]

        for label, action in controls:
            self.button(left, label, action).pack(
                fill="x", padx=10, pady=3
            )

        tk.Label(
            left,
            text="HOW TO USE",
            bg=self.panel, fg=self.accent,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=14, pady=(15, 5))

        tk.Label(
            left,
            text=(
                "1. Add devices\n"
                "2. Connect devices\n"
                "3. Disconnect a link\n"
                "4. Run BFS / DFS\n"
                "5. Check isolated devices\n\n"
                "Red node = Isolated\n"
                "Green node = Connected"
            ),
            bg=self.panel, fg=self.muted,
            justify="left",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=14)

        # Network diagram
        right = tk.Frame(main, bg=self.bg)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(
            right, text="Network Topology",
            bg=self.bg, fg=self.text,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 8))

        self.canvas = tk.Canvas(
            right,
            bg="#141C2B",
            highlightthickness=1,
            highlightbackground="#2D3B52"
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind(
            "<Configure>",
            lambda event: self.draw_network()
        )

        # Log
        bottom = tk.Frame(self.root, bg=self.panel)
        bottom.pack(fill="x", padx=15, pady=(0, 12))

        tk.Label(
            bottom,
            text="ANALYSIS / SYSTEM LOG",
            bg=self.panel, fg=self.accent,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(7, 3))

        self.log = tk.Text(
            bottom, height=4,
            bg="#111827", fg=self.text,
            font=("Consolas", 9),
            relief="flat", wrap="word"
        )
        self.log.pack(fill="x", padx=10, pady=(0, 8))
        self.log.configure(state="disabled")

    def write_log(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    # ---------------- Sample Network ----------------

    def load_demo_network(self):
        devices = {
            "D1": "Smart Gateway",
            "D2": "Temperature Sensor",
            "D3": "Humidity Sensor",
            "D4": "Smart Light",
            "D5": "Security Camera",
            "D6": "Air Quality Sensor"
        }

        for device, kind in devices.items():
            self.graph[device] = []
            self.device_types[device] = kind

        self.graph["D1"] = ["D2", "D3"]
        self.graph["D2"] = ["D1", "D4"]
        self.graph["D3"] = ["D1", "D4"]
        self.graph["D4"] = ["D2", "D3"]

        self.write_log("Sample network loaded: 6 devices.")

    # ---------------- Device Management ----------------

    def add_device(self):
        name = simpledialog.askstring(
            "Add Device",
            "Enter a unique device ID:",
            parent=self.root
        )

        if name is None:
            return

        name = name.strip()

        if not name:
            messagebox.showwarning("Invalid", "Device ID cannot be empty.")
            return

        if name in self.graph:
            messagebox.showwarning("Duplicate", "Device already exists.")
            return

        kind = simpledialog.askstring(
            "Device Type",
            "Enter device type:",
            parent=self.root
        )

        if kind is None:
            kind = "IoT Device"

        self.graph[name] = []
        self.device_types[name] = kind.strip() or "IoT Device"

        self.write_log(f"Added device: {name}")
        self.refresh_all()

    def remove_device(self):
        if not self.graph:
            messagebox.showinfo("Network", "No devices available.")
            return

        name = simpledialog.askstring(
            "Remove Device",
            "Enter the device ID to remove:",
            parent=self.root
        )

        if name is None:
            return

        name = name.strip()

        if name not in self.graph:
            messagebox.showerror("Error", "Device not found.")
            return

        for neighbor in self.graph[name][:]:
            self.graph[neighbor].remove(name)

        del self.graph[name]
        del self.device_types[name]

        if self.selected_device == name:
            self.selected_device = None

        self.write_log(f"Removed device: {name}")
        self.refresh_all()

    # ---------------- Connections ----------------

    def add_connection(self):
        if len(self.graph) < 2:
            messagebox.showwarning(
                "Network",
                "Add at least two devices first."
            )
            return

        first = simpledialog.askstring(
            "Connect Devices",
            "Enter first device ID:",
            parent=self.root
        )

        if first is None:
            return

        second = simpledialog.askstring(
            "Connect Devices",
            "Enter second device ID:",
            parent=self.root
        )

        if second is None:
            return

        first = first.strip()
        second = second.strip()

        if first not in self.graph or second not in self.graph:
            messagebox.showerror(
                "Error",
                "Both devices must exist."
            )
            return

        if first == second:
            messagebox.showwarning(
                "Invalid",
                "A device cannot connect to itself."
            )
            return

        if second in self.graph[first]:
            messagebox.showinfo(
                "Connection",
                "These devices are already connected."
            )
            return

        self.graph[first].append(second)
        self.graph[second].append(first)

        self.write_log(f"Connected: {first} <-> {second}")
        self.refresh_all()

    def disconnect_devices(self):
        """Remove a connection without removing either device."""

        if len(self.graph) < 2:
            messagebox.showinfo(
                "Disconnect",
                "At least two devices are required."
            )
            return

        first = simpledialog.askstring(
            "Disconnect Devices",
            "Enter the first device ID:",
            parent=self.root
        )

        if first is None:
            return

        second = simpledialog.askstring(
            "Disconnect Devices",
            "Enter the second device ID:",
            parent=self.root
        )

        if second is None:
            return

        first = first.strip()
        second = second.strip()

        if first not in self.graph or second not in self.graph:
            messagebox.showerror(
                "Error",
                "One or both devices do not exist."
            )
            return

        if first == second:
            messagebox.showwarning(
                "Invalid",
                "Choose two different devices."
            )
            return

        if second not in self.graph[first]:
            messagebox.showinfo(
                "No Connection",
                f"{first} and {second} are not connected."
            )
            return

        # Remove the edge in BOTH directions.
        self.graph[first].remove(second)
        self.graph[second].remove(first)

        self.write_log(f"Disconnected: {first} -X- {second}")

        self.refresh_all()

        messagebox.showinfo(
            "Disconnected Successfully",
            f"Connection between {first} and {second} removed.\n\n"
            "Both devices remain in the network."
        )

    # ---------------- Graph Algorithms ----------------

    def bfs(self, start):
        visited = {start}
        queue = deque([start])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return result

    def dfs(self, start):
        visited = set()
        result = []

        def visit(device):
            visited.add(device)
            result.append(device)

            for neighbor in self.graph[device]:
                if neighbor not in visited:
                    visit(neighbor)

        visit(start)
        return result

    def choose_start(self, title):
        if not self.graph:
            messagebox.showinfo("Network", "No devices available.")
            return None

        start = simpledialog.askstring(
            title,
            "Enter starting device ID:",
            parent=self.root
        )

        if start is None:
            return None

        start = start.strip()

        if start not in self.graph:
            messagebox.showerror("Error", "Device not found.")
            return None

        return start

    def run_bfs(self):
        start = self.choose_start("BFS Analysis")

        if start is None:
            return

        result = self.bfs(start)
        self.write_log(f"BFS from {start}: {' -> '.join(result)}")
        self.show_traversal_result(result)

    def run_dfs(self):
        start = self.choose_start("DFS Analysis")

        if start is None:
            return

        result = self.dfs(start)
        self.write_log(f"DFS from {start}: {' -> '.join(result)}")
        self.show_traversal_result(result)

    def show_traversal_result(self, result):
        self.selected_device = result[0] if result else None
        self.draw_network()

        messagebox.showinfo(
            "Traversal Result",
            "Reachable devices:\n\n" + " -> ".join(result)
        )

    def connected_components(self):
        visited = set()
        components = []

        for device in self.graph:
            if device not in visited:
                group = []
                stack = [device]
                visited.add(device)

                while stack:
                    current = stack.pop()
                    group.append(current)

                    for neighbor in self.graph[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            stack.append(neighbor)

                components.append(group)

        return components

    def show_components(self):
        components = self.connected_components()

        details = "\n\n".join(
            f"Group {i}: {', '.join(group)}"
            for i, group in enumerate(components, 1)
        )

        self.write_log(f"Connected groups: {len(components)}")

        for i, group in enumerate(components, 1):
            self.write_log(f"Group {i}: {', '.join(group)}")

        messagebox.showinfo(
            "Connected Components",
            details or "No devices in the network."
        )

    def detect_isolated(self):
        isolated = [
            device for device, neighbors in self.graph.items()
            if len(neighbors) == 0
        ]

        if isolated:
            self.write_log("Isolated devices: " + ", ".join(isolated))
            messagebox.showwarning(
                "Isolated Devices",
                "Devices with no connections:\n\n"
                + "\n".join(isolated)
            )
        else:
            self.write_log("No isolated devices found.")
            messagebox.showinfo(
                "Network Status",
                "No isolated devices found."
            )

        self.draw_network()

    # ---------------- Statistics ----------------

    def refresh_all(self):
        devices = len(self.graph)

        connections = sum(
            len(neighbors) for neighbors in self.graph.values()
        ) // 2

        isolated = sum(
            1 for neighbors in self.graph.values()
            if len(neighbors) == 0
        )

        groups = len(self.connected_components())

        self.stat_labels["devices"].config(text=str(devices))
        self.stat_labels["links"].config(text=str(connections))
        self.stat_labels["groups"].config(text=str(groups))
        self.stat_labels["isolated"].config(text=str(isolated))

        self.draw_network()

    # ---------------- Network Visualization ----------------

    def canvas_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)

        if not item:
            return

        for tag in self.canvas.gettags(item[0]):
            if tag.startswith("device:"):
                self.selected_device = tag.split(":", 1)[1]
                self.write_log(f"Selected device: {self.selected_device}")
                self.draw_network()
                return

    def draw_network(self):
        if not hasattr(self, "canvas"):
            return

        self.canvas.delete("all")

        width = max(self.canvas.winfo_width(), 500)
        height = max(self.canvas.winfo_height(), 350)
        devices = list(self.graph.keys())
        count = len(devices)

        if count == 0:
            self.canvas.create_text(
                width / 2, height / 2,
                text="No devices in network\nUse Add Device to begin",
                fill=self.muted,
                font=("Segoe UI", 14),
                justify="center"
            )
            return

        cx, cy = width / 2, height / 2
        radius = min(width * 0.34, height * 0.36)

        self.positions = {}

        if count == 1:
            self.positions[devices[0]] = (cx, cy)
        else:
            for i, device in enumerate(devices):
                angle = 2 * math.pi * i / count - math.pi / 2
                self.positions[device] = (
                    cx + radius * math.cos(angle),
                    cy + radius * math.sin(angle)
                )

        # Draw each connection once.
        for device in devices:
            for neighbor in self.graph[device]:
                if devices.index(device) < devices.index(neighbor):
                    x1, y1 = self.positions[device]
                    x2, y2 = self.positions[neighbor]

                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill="#526681",
                        width=2
                    )

        # Draw devices.
        for device in devices:
            x, y = self.positions[device]
            isolated = len(self.graph[device]) == 0

            color = self.red if isolated else self.accent
            outline = (
                "#FFFFFF"
                if device == self.selected_device
                else color
            )

            r = 27

            self.canvas.create_oval(
                x-r, y-r, x+r, y+r,
                fill="#25374B",
                outline=outline,
                width=3,
                tags=(f"device:{device}",)
            )

            self.canvas.create_text(
                x, y,
                text=device,
                fill=color,
                font=("Segoe UI", 10, "bold"),
                tags=(f"device:{device}",)
            )

            self.canvas.create_text(
                x, y+42,
                text=self.device_types[device],
                fill=self.text,
                font=("Segoe UI", 8),
                width=130,
                tags=(f"device:{device}",)
            )

        self.canvas.create_text(
            12, height-12,
            text="Red = Isolated  |  Green = Connected",
            anchor="sw",
            fill=self.muted,
            font=("Segoe UI", 9)
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = IoTNetworkAnalyzer(root)
    root.mainloop()


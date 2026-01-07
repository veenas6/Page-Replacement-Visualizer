
# 🧠 Page Replacement Algorithm Visualizer (FIFO, LRU, Optimal)

A **Python Tkinter GUI application** to visually simulate and compare **Page Replacement Algorithms** used in Operating Systems:

* **FIFO (First In First Out)**
* **LRU (Least Recently Used)**
* **Optimal Page Replacement**

This tool helps students understand how pages are loaded into memory frames, how page faults occur, and how different algorithms behave step-by-step.

---

## 📌 Features

* Interactive **GUI built with Tkinter**
* Visual simulation of:

  * FIFO
  * LRU
  * Optimal algorithms
* Step-by-step navigation (**Prev / Next**)
* Automatic execution with adjustable delay (**Run All**)
* Real-time display of:

  * Current page
  * Frame contents
  * Page hits and faults
  * Total page faults per algorithm
* Color-coded visualization:

  * 🟥 Page Fault
  * 🟩 Page Hit
  * 🟨 Newly loaded page

---

## 🖥️ Technologies Used

* **Python 3**
* **Tkinter** (GUI)
* **threading** (for autoplay)
* **time**

No external libraries required.

---

## 🚀 How to Run the Project

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/page-replacement-visualizer.git
cd page-replacement-visualizer
```

### 2️⃣ Run the application

```bash
python main.py
```

*(Use `python3` if required on your system)*

---

## 🧪 How to Use

1. Enter **Frame Count** (e.g., `3`)
2. Enter **Page Request String**
   Example:

   ```
   7 0 1 2 0 3 0 4 2 3 0 3 2
   ```
3. Click **Run (prepare)** to initialize simulation
4. Use:

   * **Next / Prev** → Manual step navigation
   * **Run All** → Automatic visualization
   * **Pause** → Stop autoplay
5. Observe page faults and frame changes for each algorithm side-by-side

---

## 📊 Algorithms Explained

### 🔹 FIFO (First In First Out)

* Replaces the page that entered memory first
* Simple but may cause **Belady’s Anomaly**

### 🔹 LRU (Least Recently Used)

* Replaces the page that was least recently accessed
* Better performance than FIFO in most cases

### 🔹 Optimal

* Replaces the page that will not be used for the longest time in the future
* Gives the **minimum possible page faults**
* Used as a benchmark (not practical in real systems)

---

## 📂 Project Structure

```
page-replacement-visualizer/
│
├── main.py        # Main application code
├── README.md      # Project documentation
```

---

## 🎯 Educational Use

This project is ideal for:

* Operating System students
* Lab demonstrations
* Understanding memory management concepts
* Mini-projects and college assignments

---

## 🤝 Contribution

Contributions are welcome!

* Add more algorithms (e.g., LFU, MRU)
* Improve UI design
* Add performance graphs

Feel free to fork and submit a pull request.

---

## 📜 License

This project is open-source and available under the **MIT License**.

---

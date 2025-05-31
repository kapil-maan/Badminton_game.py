# BadmintonPy - AI Showdown 🏸

Challenge a cunning AI opponent in this fast-paced 2D Badminton game built with Python and Pygame! Experience classic shuttlecock action, develop your strategy, and aim for victory. This project was bootstrapped and iteratively developed with the assistance of Amazon Q CLI.

````markdown
# 🏸 BadmintonPy - AI Showdown

Challenge a cunning AI opponent in this fast-paced 2D Badminton game built with **Python** and **Pygame**!  
Experience arcade-style shuttlecock action, develop your strategy, and aim for victory.  
This project was iteratively developed with the assistance of **Amazon Q CLI**.

---

## 🚀 Features

- 🎮 **Classic 2D Badminton Gameplay** — Simple yet engaging mechanics.
- 🏟️ **Dynamic Court** — Visual net, clear boundaries, and aesthetic elements.
- 👤 **Responsive Player Controls**
  - `←` / `→` Arrow Keys: Move player left/right
  - `↑` Arrow Key: Jump
  - `Spacebar`: Swing racket
- 🤖 **Challenging AI Opponent**
  - Tracks shuttlecock trajectory
  - Adds variation to return shots
  - Realistic reaction time for fairness
- 🎯 **Accurate Collision Detection**
  - Racket–shuttle, shuttle–net, and court boundaries
- 🏓 **Serving & Scoring**
  - Serving rules and transitions
  - On-screen score display
- 🔄 **Reset & Restart** — Press `R` after game over.


---

## 🗂️ File Structure

```plaintext
badminton game.py/
├── Badminton_game.py                  # Main game script (or badminton_game.py)
├── README.md                # Project README
├── prompts.txt         # Prompt for Q Cli


````

---

## 🧰 Requirements

* Python or Python3 
* [Pygame](https://www.pygame.org/) (`pip install pygame`)

---

## ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/kapil-maan/Badminton game.py.git
   ```

2. **Navigate into the project folder**

   ```bash
   cd Badminton game.py
   ```

3. **Install dependencies**

   *or just:*

   ```bash
   pip install pygame
   ```

4. **Run the game**

   ```bash
   python3 Badminton_game.py
   ```

---

## 🎮 How to Play

### 🔑 Controls

| Key      | Action                     |
| -------- | -------------------------- |
| ← / →    | Move left / right          |
| ↑        | Jump / reach high shots    |
| Spacebar | Swing racket               |
| R        | Restart game (after match) |
| Esc      | Quit the game              |

### 🏆 Rules

* **Serving**: Player who wins the point serves next.
* **Rallying**: Keep the shuttlecock in play over the net.
* **Scoring**:

  * Opponent hits net or out of bounds
  * You hit a clean shot they can’t return
* **Win Condition**: First to the defined score 11 wins!

---

## 🛠️ Development Notes

This project is powered by **Pygame** and structured around key game entities:

* `Player` — Movement, control, and swing logic
* `AIPlayer` — Tracks and reacts to gameplay intelligently
* `Shuttlecock` — Physics, collisions, and trajectory
* `GameManager` — Main loop, state handling, and scorekeeping

---

## 🤖 Amazon Q CLI Integration

A key aspect of this project was rapid iteration with **Amazon Q CLI**:

* 🏗️ Scaffolded game window, classes, and loop via prompt-based generation
* 🔄 Refined logic like:

  * *“Make the AI smarter”*
  * *“Add realistic shuttle arc”*
  * *“Show the winner on screen”*
* ⏱️ Enabled quicker turnaround on core features and debugging

---

## 📈 Future Enhancements

* 🧠 Smarter AI: Add drop shots, smashes, lobs
* 🕹️ Two-Player Mode (local multiplayer)
* 🎨 Better sprites, animations, and visual polish
* 🎼 Enhanced sounds & background music
* 🧩 Game settings menu with difficulty levels

---

## 🙌 Credits

* 👨‍💻 **Developer:**  Kapil Kumar
* 🎯 **Concept:** Arcade-style badminton game
* 🧠 **AI Assistance:** Amazon Q CLI
* 💖 **Thanks:** 

---

Happy coding! 🏸💻

# Game Design Document: BulletHell Pathfinding

## 1. Gameplay Overview (Core Gameplay)
The project combines the **Maze Puzzle** and **Bullet Hell** genres, but removes the combat element.

* **Setting:** Players are trapped in a dark maze with extremely limited visibility (Fog of War).

* **Main Objective:** Survive, find your way, and locate the maze's exit.

* **Bullet Hell Elements:** The maze is not safe. Bizarre entities (enemies/bullets) will constantly spawn. They don't chase the player immediately but will "mark" the player's previous location and use algorithms to find their way back. Players must constantly move, dodging crisscrossing streams of monsters in the maze's narrow space.

---

## 2. Player Mechanics
* **Controls:** Move in 4 directions (WASD or Arrow Keys).

* **Fog of War:** Players only see a circular illuminated area (Radius) around their character. The rest of the maze is obscured by darkness. Areas already visited may be saved on the minimap or become dark again (depending on difficulty).

* **Interactions:** * No Attack.

* Touching monsters will cause HP (Health Point) loss. No HP -> Game Over.

* **Support Skills (Expected):** Use Stamina to Dash a short distance to dodge monsters in emergency situations.

---
## 3. Monster/Bullet Mechanics
Enemies act as intelligent "bullets" in Bullet Hell. They move continuously, forming a dynamic network of obstacles.

* **Spawn Mechanism:** Spawns randomly in hidden corners of the maze or at fixed "nests" far from the player.

* **Marking Mechanism:** Enemies have no "vision" or the ability to continuously chase. Instead, at the moment of spawning (Spawn), they immediately "mark" the player's coordinates at that moment. These coordinates become the **fixed target** for that search. No matter where the player runs afterward, they will relentlessly use algorithms to find the exact same marked location. (This mechanism creates streams of "bullets" that travel along complex trajectories through the maze, allowing the player to anticipate and dodge.)

* **Pathfinding Algorithm System:**

* **Type 1 - Sneaky Enemies (Using DFS - Core):** This is the most common type of enemy. Due to the nature of the **Depth-First Search** algorithm, they don't follow the shortest path. Instead, they will crawl through alleys, going to the very end of a maze branch before turning back (backtracking). This creates an extremely erratic and unpredictable movement pattern, making it easy for players to be unexpectedly "blocked."

* **Backtracking Mechanism:** Because it's blind searching, they will probe deep into the end of a maze branch. When they encounter a wall or a "dead end," they will activate the backtracking mechanism step by step to find nearby, unexplored paths.

* **Gameplay Effect:** This behavior makes the monster's trajectory extremely convoluted, illogical, and erratic. Players might breathe a sigh of relief when they see a monster stray into a dead end, only to see it "crawling backward" and block the only escape route the very next second.

* **Type 2 - Tracking Enemies (Use BFS or A* - Extended):** These spawn in smaller numbers. They calculate the shortest path to the marked location. Combined with Type 1 (DFS), they create a crisscrossing "bullet hell," forcing players to use their dodging skills.

* **Behavior after reaching the destination:** Upon reaching the marked point without hitting a player, they will continue to "mark" a new location, self-destruct, or randomly patrol (Roaming).

---

## 4. Map/Environment Mechanism
* **Structure:** Grid-based maze. Walls are impassable obstacles for both players and monsters.

* **Dynamic:** Exits and starting points are randomly placed in each level.

* **Items:** You can scatter healing items or temporary vision-enhancing items (Flare/Torch).
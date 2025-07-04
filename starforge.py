from ursina import *
import random

app = Ursina()

#Background music 
bg_music = Audio('assets/sounds/theme.mp3', loop=True, autoplay=True)

# Setup camera
camera.orthographic = True
camera.fov = 10

# Game state
game_over = False
monsters = []
bullets = []

# Background 
main_arena = Entity(
    model='quad',
    texture='assets/background/space.jpeg',
    scale_x=20,
    scale_y=10,
    position=(0, 0, 0)
)

# Player (shooter)
shooter = Entity(
    model='quad',
    texture='assets/entities/space_ship.png',
    scale=(2, 2),
    position=(0, -3.9, -1),
    collider='box'
)
# monster dying effect
def spawn_explosion(position):
    explosion = Entity(
        model='quad',
        texture='assets/entities/boom.png',
        scale=(1.5, 1.5),
        position=position,
        z=-0.5  # Ensure it's rendered in front
    )
    destroy(explosion, delay=0.3)  # destroy after short time

# Player movement and bullet speed 
speed = 10
bullet_speed = 8

# Monster class
class Monster(Entity):
    def __init__(self):
        super().__init__(
            model='quad',
            texture='assets/entities/monster.png',
            scale=(1.1, 1.1),
            position=(random.uniform(-8, 8), 6, -1),
            collider='box'
        )
        self.speed = random.uniform(1, 2)

    def update(self):
        if game_over:
            return

        self.y -= time.dt * self.speed
#Checking overlapping of player and monster
        if self.intersects(shooter).hit:
            trigger_game_over()

        if self.y < -6:
            trigger_game_over()
            destroy(self)

# Bullet class
class Bullet(Entity):
    def __init__(self):
        super().__init__(
            model='quad',
            texture='assets/entities/laser.png',
            scale=1,
            position=shooter.position + Vec3(0, 0.5, 0),
            collider='sphere'
        )
        self.speed = bullet_speed

    def update(self):
        if game_over:
            return
#Makes bullet go upward
        self.y += time.dt * self.speed

        # Check collision with monsters
        for m in monsters:
            if self.intersects(m).hit: # Checks if bullet collided with monster
                if m in monsters:
                    monsters.remove(m)
                spawn_explosion(m.position)    
                destroy(m)
                destroy(self)
                if self in bullets:
                    bullets.remove(self)
                return

        # Remove when bullets went out of the screen
        if self.y > 6:
            if self in bullets:
                bullets.remove(self)
            destroy(self)

# Spawn monster every few seconds
def spawn_monster():
    if game_over:
        return
    m = Monster()
    monsters.append(m)
    invoke(spawn_monster, delay=1)

spawn_monster()

# Game over
def trigger_game_over():
    global game_over
    game_over = True
    Text(
        text='GAME OVER',
        origin=(0, 0),
        scale=3,
        font='assets/fonts/creepy_font.ttf',
        background=True,
    )
    monsters.clear()
    invoke(application.quit, delay=5)

# Main game update loop
def update():
    if game_over:
        return

    # Movement
    if held_keys['a'] or held_keys['left arrow']:
        shooter.x -= time.dt * speed
        shooter.rotation_z = 15
    elif held_keys['d'] or held_keys['right arrow']:
        shooter.x += time.dt * speed
        shooter.rotation_z = -15
    else:
        shooter.rotation_z = 0

    if held_keys['w'] or held_keys['up arrow']:
        shooter.y += time.dt * speed
    if held_keys['s'] or held_keys['down arrow']:
        shooter.y -= time.dt * speed

    # Clamp position
    shooter.x = clamp(shooter.x, -8, 8)
    shooter.y = clamp(shooter.y, -4, -3)

    # Fire bullet
    if held_keys['space']:
        if not hasattr(shooter, 'last_bullet_time') or time.time() - shooter.last_bullet_time > 0.25:
            bullets.append(Bullet())
            Audio('assets/sounds/laser.mp3', autoplay=True)
            shooter.last_bullet_time = time.time()

    # Update monsters
    for m in monsters:
        m.update()

    # Update bullets
    for b in bullets:
        b.update()

app.run()

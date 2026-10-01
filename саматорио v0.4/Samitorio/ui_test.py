import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import core, main

pygame.init()
core.init_fonts()

g = main.G()
main.build_game(g, seed=7)
# unlock all but nothing has been researched; simulate late game
g.unlocked.update(set(core.RECIPES.keys()) | {"automation", "logistics", "steel-proc",
                                              "turrets", "electricity", "night-vision"})
for itm in list(core.ITEMS.keys()):
    g.inv.add(itm, 200)

events = []
for _ in range(4):
    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
events += [
    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_b),
    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1),
    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2),
    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r),
    pygame.event.Event(pygame.MOUSEMOTION, pos=(core.SW // 2, core.SH // 2)),
    pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(core.SW // 2, core.SH // 2), button=1),
    pygame.event.Event(pygame.MOUSEMOTION, pos=(core.SW // 2 + 30, core.SH // 2)),
    pygame.event.Event(pygame.MOUSEMOTION, pos=(core.SW // 2 - 30, core.SH // 2)),
    pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(core.SW // 2 - 30, core.SH // 2), button=1),
    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHTBRACKET),
    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e),
    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_t),
]
for e in events:
    pygame.event.post(e)

main.run(max_frames=90, start_state="game", g=g)
print("UI TEST PASSED")
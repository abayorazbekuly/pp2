import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    radius = 5
    color_mode = 'blue'
    tool = 'pen'

    points = []
    drawing = False
    start_pos = None
    current_pos = None

    font = pygame.font.SysFont("Verdana", 16)

    canvas = pygame.Surface((800, 600))
    canvas.fill((255, 255, 255))

    while True:
        pressed = pygame.key.get_pressed()

        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():

            # determin if X was clicked, or Ctrl+W or Alt+F4 was used
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_ESCAPE:
                    return

                # determine if a letter key was pressed
                if event.key == pygame.K_r:
                    color_mode = 'red'
                elif event.key == pygame.K_g:
                    color_mode = 'green'
                elif event.key == pygame.K_b:
                    color_mode = 'blue'
                elif event.key == pygame.K_k:
                    color_mode = 'black'

                # choose drawing tool
                elif event.key == pygame.K_p:
                    tool = 'pen'
                elif event.key == pygame.K_e:
                    tool = 'eraser'
                elif event.key == pygame.K_c:
                    tool = 'circle'
                elif event.key == pygame.K_t:
                    tool = 'rectangle'

                # change brush size
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    radius = min(50, radius + 1)
                elif event.key == pygame.K_MINUS:
                    radius = max(1, radius - 1)

                # clear canvas
                elif event.key == pygame.K_x:
                    canvas.fill((255, 255, 255))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drawing = True
                    start_pos = event.pos
                    current_pos = event.pos

                    # for pen and eraser start drawing immediately
                    if tool == 'pen' or tool == 'eraser':
                        points = points + [event.pos]
                        points = points[-256:]

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    current_pos = event.pos

                    # if mouse moved, add point to list for pen/eraser
                    if tool == 'pen' or tool == 'eraser':
                        position = event.pos
                        points = points + [position]
                        points = points[-256:]

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False

                    # draw final rectangle
                    if tool == 'rectangle' and start_pos is not None:
                        rect = makeRect(start_pos, event.pos)
                        pygame.draw.rect(canvas, getColor(color_mode), rect, 2)

                    # draw final circle
                    elif tool == 'circle' and start_pos is not None:
                        circle_data = makeCircle(start_pos, event.pos)
                        pygame.draw.circle(canvas, getColor(color_mode), circle_data[0], circle_data[1], 2)

                    points = []

        screen.fill((220, 220, 220))
        screen.blit(canvas, (0, 0))

        # draw all points for pen/eraser
        i = 0
        while i < len(points) - 1:
            drawLineBetween(canvas, points[i], points[i + 1], radius, color_mode, tool)
            i += 1

        # preview rectangle or circle while dragging
        if drawing and (tool == 'rectangle' or tool == 'circle') and start_pos is not None and current_pos is not None:
            temp_screen = canvas.copy()

            if tool == 'rectangle':
                rect = makeRect(start_pos, current_pos)
                pygame.draw.rect(temp_screen, getColor(color_mode), rect, 2)

            elif tool == 'circle':
                circle_data = makeCircle(start_pos, current_pos)
                pygame.draw.circle(temp_screen, getColor(color_mode), circle_data[0], circle_data[1], 2)

            screen.blit(temp_screen, (0, 0))

        drawUI(screen, font, tool, color_mode, radius)

        pygame.display.flip()
        clock.tick(60)


def getColor(color_mode):
    if color_mode == 'blue':
        return (0, 0, 255)
    elif color_mode == 'red':
        return (255, 0, 0)
    elif color_mode == 'green':
        return (0, 255, 0)
    elif color_mode == 'black':
        return (0, 0, 0)


def drawLineBetween(screen, start, end, width, color_mode, tool):
    if tool == 'eraser':
        color = (255, 255, 255)
    else:
        color = getColor(color_mode)

    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))

    if iterations == 0:
        pygame.draw.circle(screen, color, start, width)
        return

    for i in range(iterations):
        progress = 1.0 * i / iterations
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(screen, color, (x, y), width)


def makeRect(start, end):
    x1 = min(start[0], end[0])
    y1 = min(start[1], end[1])
    x2 = max(start[0], end[0])
    y2 = max(start[1], end[1])
    return pygame.Rect(x1, y1, x2 - x1, y2 - y1)


def makeCircle(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    radius = int((dx * dx + dy * dy) ** 0.5)
    return start, radius


def drawUI(screen, font, tool, color_mode, radius):
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, 800, 70))
    pygame.draw.line(screen, (150, 150, 150), (0, 70), (800, 70), 2)

    line1 = "Colors: R-red  G-green  B-blue  K-black"
    line2 = "Tools: P-pen  E-eraser  C-circle  T-rectangle"
    line3 = "Size: +/-    Clear: X    Exit: ESC"

    text1 = font.render(line1, True, (0, 0, 0))
    text2 = font.render(line2, True, (0, 0, 0))
    text3 = font.render(line3, True, (0, 0, 0))

    status = "Current tool: " + tool + " | Current color: " + color_mode + " | Size: " + str(radius)
    text4 = font.render(status, True, (0, 0, 0))

    screen.blit(text1, (10, 5))
    screen.blit(text2, (10, 22))
    screen.blit(text3, (10, 39))
    screen.blit(text4, (10, 52))


main()
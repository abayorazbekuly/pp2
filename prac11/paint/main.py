import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 650))
    clock = pygame.time.Clock()

    radius = 5
    color_mode = 'black'
    tool = 'pen'

    points = []
    drawing = False
    start_pos = None
    current_pos = None

    font = pygame.font.SysFont("Verdana", 16)

    canvas = pygame.Surface((900, 650))
    canvas.fill((255, 255, 255))

    while True:
        pressed = pygame.key.get_pressed()

        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():
            # Exit commands
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_ESCAPE:
                    return

                # Color selection
                if event.key == pygame.K_1:
                    color_mode = 'black'
                elif event.key == pygame.K_2:
                    color_mode = 'red'
                elif event.key == pygame.K_3:
                    color_mode = 'green'
                elif event.key == pygame.K_4:
                    color_mode = 'blue'

                # Tool selection
                elif event.key == pygame.K_p:
                    tool = 'pen'
                elif event.key == pygame.K_e:
                    tool = 'eraser'
                elif event.key == pygame.K_c:
                    tool = 'circle'
                elif event.key == pygame.K_t:
                    tool = 'rectangle'
                elif event.key == pygame.K_s:
                    tool = 'square'
                elif event.key == pygame.K_r:
                    tool = 'right_triangle'
                elif event.key == pygame.K_q:
                    tool = 'equilateral_triangle'
                elif event.key == pygame.K_h:
                    tool = 'rhombus'

                # Change brush size
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    radius = min(50, radius + 1)
                elif event.key == pygame.K_MINUS:
                    radius = max(1, radius - 1)

                # Clear canvas
                elif event.key == pygame.K_x:
                    canvas.fill((255, 255, 255))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Do not draw on top control panel
                    if event.pos[1] < 80:
                        continue

                    drawing = True
                    start_pos = event.pos
                    current_pos = event.pos

                    # Pen and eraser start drawing immediately
                    if tool == 'pen' or tool == 'eraser':
                        points = points + [event.pos]
                        points = points[-256:]

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    current_pos = event.pos

                    # Add points for pen and eraser
                    if tool == 'pen' or tool == 'eraser':
                        position = event.pos
                        points = points + [position]
                        points = points[-256:]

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and start_pos is not None:
                    drawing = False

                    # Draw rectangle
                    if tool == 'rectangle':
                        rect = makeRect(start_pos, event.pos)
                        pygame.draw.rect(canvas, getColor(color_mode), rect, 2)

                    # Draw circle
                    elif tool == 'circle':
                        center, rad = makeCircle(start_pos, event.pos)
                        pygame.draw.circle(canvas, getColor(color_mode), center, rad, 2)

                    # Draw square
                    elif tool == 'square':
                        square = makeSquare(start_pos, event.pos)
                        pygame.draw.rect(canvas, getColor(color_mode), square, 2)

                    # Draw right triangle
                    elif tool == 'right_triangle':
                        points_triangle = makeRightTriangle(start_pos, event.pos)
                        pygame.draw.polygon(canvas, getColor(color_mode), points_triangle, 2)

                    # Draw equilateral triangle
                    elif tool == 'equilateral_triangle':
                        points_triangle = makeEquilateralTriangle(start_pos, event.pos)
                        pygame.draw.polygon(canvas, getColor(color_mode), points_triangle, 2)

                    # Draw rhombus
                    elif tool == 'rhombus':
                        points_rhombus = makeRhombus(start_pos, event.pos)
                        pygame.draw.polygon(canvas, getColor(color_mode), points_rhombus, 2)

                    points = []

        screen.fill((220, 220, 220))
        screen.blit(canvas, (0, 0))

        # Draw freehand pen/eraser
        i = 0
        while i < len(points) - 1:
            drawLineBetween(canvas, points[i], points[i + 1], radius, color_mode, tool)
            i += 1

        # Draw preview for shapes while dragging mouse
        if drawing and start_pos is not None and current_pos is not None:
            temp_screen = canvas.copy()

            if tool == 'rectangle':
                rect = makeRect(start_pos, current_pos)
                pygame.draw.rect(temp_screen, getColor(color_mode), rect, 2)

            elif tool == 'circle':
                center, rad = makeCircle(start_pos, current_pos)
                pygame.draw.circle(temp_screen, getColor(color_mode), center, rad, 2)

            elif tool == 'square':
                square = makeSquare(start_pos, current_pos)
                pygame.draw.rect(temp_screen, getColor(color_mode), square, 2)

            elif tool == 'right_triangle':
                points_triangle = makeRightTriangle(start_pos, current_pos)
                pygame.draw.polygon(temp_screen, getColor(color_mode), points_triangle, 2)

            elif tool == 'equilateral_triangle':
                points_triangle = makeEquilateralTriangle(start_pos, current_pos)
                pygame.draw.polygon(temp_screen, getColor(color_mode), points_triangle, 2)

            elif tool == 'rhombus':
                points_rhombus = makeRhombus(start_pos, current_pos)
                pygame.draw.polygon(temp_screen, getColor(color_mode), points_rhombus, 2)

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
    else:
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


def makeSquare(start, end):
    x1, y1 = start
    x2, y2 = end

    side = min(abs(x2 - x1), abs(y2 - y1))

    if x2 < x1:
        x = x1 - side
    else:
        x = x1

    if y2 < y1:
        y = y1 - side
    else:
        y = y1

    return pygame.Rect(x, y, side, side)


def makeRightTriangle(start, end):
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]


def makeEquilateralTriangle(start, end):
    x1, y1 = start
    x2, y2 = end

    side = abs(x2 - x1)
    if side == 0:
        side = 1

    height = int((3 ** 0.5) / 2 * side)

    if x2 >= x1:
        left_x = x1
        right_x = x1 + side
    else:
        left_x = x1 - side
        right_x = x1

    base_y = y2
    top_x = (left_x + right_x) // 2
    top_y = base_y - height

    return [(left_x, base_y), (right_x, base_y), (top_x, top_y)]


def makeRhombus(start, end):
    x1, y1 = start
    x2, y2 = end

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    half_width = abs(x2 - x1) // 2
    half_height = abs(y2 - y1) // 2

    return [
        (center_x, center_y - half_height),
        (center_x + half_width, center_y),
        (center_x, center_y + half_height),
        (center_x - half_width, center_y)
    ]


def drawUI(screen, font, tool, color_mode, radius):
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, 900, 80))
    pygame.draw.line(screen, (150, 150, 150), (0, 80), (900, 80), 2)

    line1 = "Colors: 1-black  2-red  3-green  4-blue"
    line2 = "Tools: P-pen  E-eraser  C-circle  T-rectangle  S-square"
    line3 = "R-right triangle  Q-equilateral triangle  H-rhombus"
    line4 = "Size: +/-   Clear: X   Exit: ESC"

    text1 = font.render(line1, True, (0, 0, 0))
    text2 = font.render(line2, True, (0, 0, 0))
    text3 = font.render(line3, True, (0, 0, 0))
    text4 = font.render(line4, True, (0, 0, 0))

    status = "Current tool: " + tool + " | Current color: " + color_mode + " | Size: " + str(radius)
    text5 = font.render(status, True, (0, 0, 0))

    screen.blit(text1, (10, 5))
    screen.blit(text2, (10, 23))
    screen.blit(text3, (10, 41))
    screen.blit(text4, (10, 59))
    screen.blit(text5, (520, 5))


main()
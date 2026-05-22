import asyncio
import random

from dataclasses import dataclass

from playwright.async_api import Page


@dataclass
class MouseState:
    x: float
    y: float


def calculate_bezier_point(
    progress: float,
    start_x: float,
    start_y: float,
    control_x1: float,
    control_y1: float,
    control_x2: float,
    control_y2: float,
    end_x: float,
    end_y: float,
) -> tuple[float, float]:
    inverse = 1 - progress
    point_x = (
        (inverse ** 3) * start_x
        + 3 * (inverse ** 2) * progress * control_x1
        + 3 * inverse * (progress ** 2) * control_x2
        + (progress ** 3) * end_x
    )
    point_y = (
        (inverse ** 3) * start_y
        + 3 * (inverse ** 2) * progress * control_y1
        + 3 * inverse * (progress ** 2) * control_y2
        + (progress ** 3) * end_y
    )
    return point_x, point_y


async def random_pause(minimum: float = 0.8, maximum: float = 2.2) -> None:
    await asyncio.sleep(random.uniform(minimum, maximum))


async def move_mouse_to_coordinates(
    page: Page,
    target_x: float,
    target_y: float,
    mouse_state: MouseState
) -> None:
    start_x = mouse_state.x
    start_y = mouse_state.y

    travel_distance = ((target_x - start_x) ** 2 + (target_y - start_y) ** 2) ** 0.5
    arc_variance = travel_distance * random.uniform(0.2, 0.4)

    control_x1 = start_x + (target_x - start_x) * 0.3 + random.uniform(-arc_variance, arc_variance)
    control_y1 = start_y + (target_y - start_y) * 0.3 + random.uniform(-arc_variance, arc_variance)
    control_x2 = start_x + (target_x - start_x) * 0.7 + random.uniform(-arc_variance, arc_variance)
    control_y2 = start_y + (target_y - start_y) * 0.7 + random.uniform(-arc_variance, arc_variance)

    steps = random.randint(25, 40)

    for step_index in range(steps + 1):
        progress = step_index / steps
        eased_progress = progress * progress * (3 - 2 * progress)

        move_x, move_y = calculate_bezier_point(
            eased_progress,
            start_x, start_y,
            control_x1, control_y1,
            control_x2, control_y2,
            target_x, target_y,
        )

        await page.mouse.move(move_x, move_y)

        speed_factor = 1 - abs(progress - 0.5) * 2
        step_delay = random.uniform(0.008, 0.025) * (1.5 - speed_factor * 0.8)
        await asyncio.sleep(step_delay)

    mouse_state.x = target_x
    mouse_state.y = target_y


async def click_at_current_position(page: Page) -> None:
    await asyncio.sleep(random.uniform(0.05, 0.15))
    await page.mouse.down()
    await asyncio.sleep(random.uniform(0.05, 0.12))
    await page.mouse.up()


async def human_move_and_click(
    page: Page,
    selector: str,
    mouse_state: MouseState
) -> None:
    target_element = page.locator(selector)
    bounding_box = await target_element.bounding_box()

    if bounding_box is None:
        await target_element.click()
        return

    target_x = bounding_box["x"] + bounding_box["width"] * random.uniform(0.35, 0.65)
    target_y = bounding_box["y"] + bounding_box["height"] * random.uniform(0.35, 0.65)

    await move_mouse_to_coordinates(page, target_x, target_y, mouse_state)
    await click_at_current_position(page)


async def human_move_and_click_locator(
    page: Page,
    target_element,
    mouse_state: MouseState
) -> None:
    bounding_box = await target_element.bounding_box()

    if bounding_box is None:
        await target_element.click()
        return

    target_x = bounding_box["x"] + bounding_box["width"] * random.uniform(0.35, 0.65)
    target_y = bounding_box["y"] + bounding_box["height"] * random.uniform(0.35, 0.65)

    await move_mouse_to_coordinates(page, target_x, target_y, mouse_state)
    await click_at_current_position(page)


async def human_type(page: Page, text: str) -> None:
    await asyncio.sleep(random.uniform(0.2, 0.7))

    for character in text:
        if random.random() < 0.05 and character.isalpha():
            wrong_character = random.choice('asdfghjkl')
            await page.keyboard.type(wrong_character)
            await asyncio.sleep(random.uniform(0.08, 0.2))
            await page.keyboard.press('Backspace')
            await asyncio.sleep(random.uniform(0.05, 0.15))

        await page.keyboard.type(character)

        if character in (' ', '@', '.', '_', '-'):
            await asyncio.sleep(random.uniform(0.20, 0.35))
        else:
            await asyncio.sleep(random.uniform(0.06, 0.20))

        if random.random() < 0.04:
            await asyncio.sleep(random.uniform(0.4, 1.3))


async def human_scroll(page: Page, scroll_distance: int = 300) -> None:
    steps = random.randint(5, 12)
    scroll_direction = 1 if scroll_distance >= 0 else -1
    absolute_distance = abs(scroll_distance)
    base_step_distance = absolute_distance / steps

    for step_index in range(steps):
        progress = step_index / steps
        eased_speed = progress * progress * (3 - 2 * progress)

        jitter = random.randint(0, 10)
        step_distance = (base_step_distance + jitter) * scroll_direction

        await page.mouse.wheel(0, step_distance)

        step_delay = random.uniform(0.08, 0.18) * (1.5 - eased_speed * 0.8)
        await asyncio.sleep(step_delay)

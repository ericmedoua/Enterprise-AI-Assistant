from time import sleep

from app.observability.timer import Timer


timer = Timer()

sleep(0.4)

print()

print(
    timer.elapsed_ms(),
    "ms",
)

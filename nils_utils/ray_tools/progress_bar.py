# largely from: https://docs.ray.io/en/latest/ray-core/examples/progress_bar.html


from asyncio import Event
from typing import Tuple
from time import sleep

import ray

# For typing purposes
from ray.actor import ActorHandle
from tqdm import tqdm

try:
    import py.test
except ImportError:
    pass


@ray.remote
class ProgressBarActor:
    counter: int
    delta: int
    event: Event

    def __init__(self) -> None:
        self.counter = 0
        self.delta = 0
        self.event = Event()

    def update(self, num_items_completed: int) -> None:
        """Updates the ProgressBar with the incremental
        number of items that were just completed.
        """
        self.counter += num_items_completed
        self.delta += num_items_completed
        self.event.set()

    async def wait_for_update(self) -> Tuple[int, int]:
        """Blocking call.

        Waits until somebody calls `update`, then returns a tuple of
        the number of updates since the last call to
        `wait_for_update`, and the total number of completed items.
        """
        await self.event.wait()
        self.event.clear()
        saved_delta = self.delta
        self.delta = 0
        return saved_delta, self.counter

    def get_counter(self) -> int:
        """
        Returns the total number of complete items.
        """
        return self.counter


# Back on the local node, once you launch your remote Ray tasks, call
# `print_until_done`, which will feed everything back into a `tqdm` counter.


class ProgressBar:
    progress_actor: ActorHandle
    total: int
    description: str
    pbar: tqdm

    def __init__(self, total: int, description: str = ""):
        # Ray actors don't seem to play nice with mypy, generating
        # a spurious warning for the following line,
        # which we need to suppress. The code is fine.
        self.progress_actor = ProgressBarActor.remote()  # type: ignore
        self.total = total
        self.description = description

    @property
    def actor(self) -> ActorHandle:
        """Returns a reference to the remote `ProgressBarActor`.

        When you complete tasks, call `update` on the actor.
        """
        return self.progress_actor

    def print_until_done(self) -> None:
        """Blocking call.

        Do this after starting a series of remote Ray tasks, to which you've
        passed the actor handle. Each of them calls `update` on the actor.
        When the progress meter reaches 100%, this method returns.
        """
        pbar = tqdm(desc=self.description, total=self.total)
        while True:
            delta, counter = ray.get(self.actor.wait_for_update.remote())
            pbar.update(delta)
            if counter >= self.total:
                pbar.close()
                return


def test_progress_bar():
    @ray.remote
    def sleep_then_increment(i: int, pba: ActorHandle) -> int:
        sleep(i / 2.0)
        pba.update.remote(1)
        return i

    def run():
        ray.init()
        num_ticks = 6
        pb = ProgressBar(num_ticks)
        actor = pb.actor
        # You can replace this with any arbitrary Ray task/actor.
        tasks_pre_launch = [
            sleep_then_increment.remote(i, actor) for i in range(0, num_ticks)
        ]

        pb.print_until_done()
        tasks = ray.get(tasks_pre_launch)

        assert tasks == list(range(num_ticks))
        assert num_ticks == ray.get(actor.get_counter.remote())

    run()
